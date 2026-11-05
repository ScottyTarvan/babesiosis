using System.Text.Json;
using System.Text.RegularExpressions;
using Babesiosis.Agents.OpenRouter;
using Babesiosis.Core.Configurations;
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Abstractions;
using OpenAI.Chat;

namespace Babesiosis.Agents.Articles
{
  /// <summary>Answers questions from the canine babesiosis review's articles.</summary>
  public interface IArticleQuestionAgent
  {
    Task<ArticleAnswer> AskAsync(ArticleQuestion request, CancellationToken cancellationToken = default);
  }

  /// <param name="Question">The user's question.</param>
  /// <param name="Tier">Which configured OpenRouter model answers.</param>
  /// <param name="Conversation">
  /// <see cref="ArticleAnswer.Conversation"/> from the previous answer, to ask a follow-up in the
  /// same conversation. Null starts a new one.
  /// </param>
  public sealed record ArticleQuestion(
    string Question,
    AgentModelTier Tier = AgentModelTier.Medium,
    string? Conversation = null);

  /// <param name="Answer">The answer, citing article codes in square brackets, e.g. [CB001].</param>
  /// <param name="Sources">The cited articles that exist in the database, in order of first citation.</param>
  /// <param name="Model">The OpenRouter model id that answered.</param>
  /// <param name="Conversation">Opaque state to pass back in <see cref="ArticleQuestion.Conversation"/> for a follow-up.</param>
  public sealed record ArticleAnswer(
    string Answer,
    IReadOnlyList<ArticleSource> Sources,
    string Model,
    string Conversation,
    long? InputTokens,
    long? OutputTokens);

  /// <param name="ArticleId">dbo.article.article_id, for linking to the article in the web app.</param>
  /// <param name="HasFullText">Whether the paper's own full text is in the database.</param>
  /// <param name="SectionsRead">
  /// The sections of the paper's own text the agent read while answering (results, methods, ...),
  /// empty when it used the review's record only.
  /// </param>
  public sealed record ArticleSource(
    int ArticleId, string Code, string Title, int? Year, string? Journal, string? Doi, string? Pmid,
    bool HasFullText = false, IReadOnlyList<string>? SectionsRead = null)
  {
    public IReadOnlyList<string> SectionsRead { get; init; } = SectionsRead ?? [];

    public string? DoiUrl => string.IsNullOrWhiteSpace(Doi) ? null : $"https://doi.org/{Doi}";
  }

  /// <summary>
  /// A Microsoft Agent Framework <see cref="ChatClientAgent"/> on an OpenRouter model, with tools
  /// over the article table (semantic search on the <c>embedding</c> vector column and a details
  /// lookup) and, when <c>AppSettings:AiAgents:FullText</c> is on, over the papers' own text in
  /// <c>dbo.article_section</c> (passage search, outline, section and full text). The agent is
  /// built per question, which is cheap and picks up configuration changes; the conversation
  /// history travels in <see cref="ArticleAnswer.Conversation"/>.
  /// </summary>
  public sealed partial class ArticleQuestionAgent : IArticleQuestionAgent
  {
    /// <summary>Model round trips per question, so a confused model cannot loop on tool calls.</summary>
    public const int MaxToolRounds = 8;

    private const int MaxQuestionLength = 4000;

    private readonly OpenRouterChatClientFactory _chatClientFactory;
    private readonly ArticleSearchRepository _repository;
    private readonly IAppSettingsService _appSettingsService;
    private readonly ILoggerFactory _loggerFactory;
    private readonly ILogger _logger;

    public ArticleQuestionAgent(
      OpenRouterChatClientFactory chatClientFactory,
      ArticleSearchRepository repository,
      IAppSettingsService appSettingsService,
      ILoggerFactory? loggerFactory = null)
    {
      _chatClientFactory = chatClientFactory;
      _repository = repository;
      _appSettingsService = appSettingsService;
      _loggerFactory = loggerFactory ?? NullLoggerFactory.Instance;
      _logger = _loggerFactory.CreateLogger<ArticleQuestionAgent>();
    }

    public async Task<ArticleAnswer> AskAsync(ArticleQuestion request, CancellationToken cancellationToken = default)
    {
      ArgumentNullException.ThrowIfNull(request);
      if (string.IsNullOrWhiteSpace(request.Question))
        throw new ArgumentException("A question is required.", nameof(request));
      if (request.Question.Length > MaxQuestionLength)
        throw new ArgumentException($"The question is longer than {MaxQuestionLength} characters.", nameof(request));

      var (chatClient, model) = _chatClientFactory.Create(request.Tier);
      var fullText = _appSettingsService.GetAppSettings().AiAgents.FullText;
      var categories = await _repository.GetCategoriesAsync(cancellationToken);
      var tools = new ArticleSearchTools(
        _repository, categories.Select(c => c.Code).ToHashSet(StringComparer.OrdinalIgnoreCase), fullText);

      AIAgent agent = chatClient.AsAIAgent(
        new ChatClientAgentOptions
        {
          Name = "babesiosis-article-agent",
          Description = "Answers questions from the canine babesiosis scoping review's articles.",
          ChatOptions = new ChatOptions
          {
            Instructions = BuildInstructions(categories, fullText),
            Tools = tools.AsTools()
          }
        },
        loggerFactory: _loggerFactory);

      var functions = agent.GetService<FunctionInvokingChatClient>();
      if (functions is not null)
        functions.MaximumIterationsPerRequest = MaxToolRounds;
      else
        _logger.LogWarning("The agent has no function-invoking client; the {Max}-round tool limit is not applied.", MaxToolRounds);

      AgentSession session = request.Conversation is null
        ? await agent.CreateSessionAsync(cancellationToken)
        : await agent.DeserializeSessionAsync(ParseConversation(request.Conversation), cancellationToken: cancellationToken);

      var response = await agent.RunAsync(request.Question.Trim(), session, cancellationToken: cancellationToken);
      var answer = response.Text.Trim();

      var sources = await ResolveSourcesAsync(answer, tools, cancellationToken);
      var conversation = (await agent.SerializeSessionAsync(session, cancellationToken: cancellationToken)).GetRawText();

      _logger.LogInformation(
        "Article agent answered with {Model}: {Seen} articles retrieved, {Cited} cited, {InputTokens}/{OutputTokens} tokens.",
        model, tools.SeenCount, sources.Count, response.Usage?.InputTokenCount, response.Usage?.OutputTokenCount);

      return new ArticleAnswer(
        answer, sources, model, conversation, response.Usage?.InputTokenCount, response.Usage?.OutputTokenCount);
    }

    /// <summary>
    /// The articles the answer mentions, in order of first mention, read from the database in
    /// one query. Titles and DOIs come from the table, never from the model's text, and codes
    /// that do not exist are dropped, so an invented citation never reaches the caller.
    /// </summary>
    private async Task<IReadOnlyList<ArticleSource>> ResolveSourcesAsync(
      string answer, ArticleSearchTools tools, CancellationToken cancellationToken)
    {
      var cited = ArticleCode().Matches(answer).Select(m => m.Value).Distinct().ToList();
      if (cited.Count == 0)
        return [];

      return (await _repository.GetDetailsAsync(cited, cancellationToken))
        .Select(d => new ArticleSource(
          d.Id, d.Code, d.Title, d.Year, d.Journal, d.Doi, d.Pmid, d.HasFullText, tools.SectionsRead(d.Code)))
        .ToList();
    }

    private static JsonElement ParseConversation(string conversation)
    {
      try
      {
        using var document = JsonDocument.Parse(conversation);
        return document.RootElement.Clone();
      }
      catch (JsonException ex)
      {
        throw new ArgumentException("The conversation state is not valid; start a new conversation.", nameof(conversation), ex);
      }
    }

    private static string BuildInstructions(IReadOnlyList<CategoryInfo> categories, bool fullText) => $"""
      You answer questions about canine babesiosis using the articles of a scoping review of its
      pathophysiology. The articles are your only source of evidence.

      How to work:
      - Always call search_articles before answering. For broad or multi-part questions, search
        several times with different wording, and use a category filter when the topic is clear.
      - Call get_article_details for the articles you rely on, to read their abstract summary,
        conclusions, limitations, design, host and sample size.
      - Judge relevance from the content, not only the distance score.
      {(fullText ? FullTextInstructions : "")}
      How to answer:
      - Answer only from what the tools returned. Do not add facts from general knowledge. If the
        articles do not answer the question, say so plainly and describe what the review covers,
        without citing articles that do not address the question.
      - Cite every claim with the article code in square brackets, e.g. [CB001] or [CB001, CB024].
        Only cite codes that a tool returned, and only for claims those articles support.
        {(fullText ? "When a claim comes from the paper's own text, add the section after the code, e.g. [CB004 Results]." : "")}
      - Say how strong the evidence is: study design, Babesia species, number of dogs, natural
        versus experimental infection, and any limitations or disagreement between studies.
      - Be concise. Use short paragraphs or bullet points. Write in British English.
      - Do not give treatment or dosing advice for an individual animal; summarise what the
        studies report instead.

      Topic category codes for the categoryCode filter:
      {string.Join(Environment.NewLine, categories.Select(c => $"- {c.Code}: {c.Name}"))}
      """;

    /// <summary>Added to the instructions when AppSettings:AiAgents:FullText is on.</summary>
    private const string FullTextInstructions = """
      - The review's record is a summary. When the question needs what a paper actually measured,
        how it was done, the numbers, or an exact definition, read the paper's own text, from
        cheapest to dearest:
        1. search_passages with the question and the candidate article codes: it returns the
           paragraphs closest to the question, with their section. This answers most detail
           questions. Leave articleCodes empty to search every paper's text at once.
        2. get_article_outline to see which sections an article has and how long they are.
        3. get_article_section for one section (methods, results, discussion, ...). Long sections
           come in parts; ask for the next part only if the first did not answer.
        4. get_article_full_text only when asked to summarise or appraise one whole paper, and
           one paper at a time.
      - Only articles with hasFullText = true have their own text; the others have an abstract
        passage at most. Say when a claim rests on an abstract or on the review's summary only.
      - Text marked textTranslated is a machine translation: quote it with care and say so.
      """;

    [GeneratedRegex(@"\b[A-Z]{2}\d{3}\b")]
    private static partial Regex ArticleCode();
  }
}
