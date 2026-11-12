using System.Text.Json;
using System.Text.RegularExpressions;
using Babesiosis.Agents.Clinical;
using Babesiosis.Agents.Experiments;
using Babesiosis.Agents.OpenRouter;
using Babesiosis.Core.Configurations;
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Abstractions;
using OpenAI.Chat;

namespace Babesiosis.Agents.Articles
{
  /// <summary>
  /// Answers questions from the canine babesiosis review's articles, the project's experiments
  /// and the clinical manual.
  /// </summary>
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

  /// <param name="Answer">
  /// The answer, citing its sources in square brackets: article codes ([CB001]), experiment codes
  /// ([SV-05-01-age-death]) and clinical manual pages ([SY05]).
  /// </param>
  /// <param name="Sources">The cited articles that exist in the database, in order of first citation.</param>
  /// <param name="Model">The OpenRouter model id that answered.</param>
  /// <param name="Conversation">Opaque state to pass back in <see cref="ArticleQuestion.Conversation"/> for a follow-up.</param>
  public sealed record ArticleAnswer(
    string Answer,
    IReadOnlyList<ArticleSource> Sources,
    string Model,
    string Conversation,
    long? InputTokens,
    long? OutputTokens)
  {
    /// <summary>The cited experiments that exist in the database, in order of first citation.</summary>
    public IReadOnlyList<ExperimentSource> Experiments { get; init; } = [];

    /// <summary>The cited pages of the clinical manual, in order of first citation.</summary>
    public IReadOnlyList<ClinicalPageSource> ClinicalPages { get; init; } = [];
  }

  /// <param name="Code">dbo.experiment.experiment_code: the web app shows it at /experiments/{Code}.</param>
  /// <param name="ShortCode">The short form the answer may use instead (SV-05-01), or null.</param>
  public sealed record ExperimentSource(string Code, string? ShortCode, string Name, string Method);

  /// <param name="Id">The page ID (SY05, TX00): the web app shows it at /clinical/{Id}.</param>
  public sealed record ClinicalPageSource(string Id, string Title, string Group);

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
  /// over three sources:
  /// the article table (semantic search on the <c>embedding</c> vector column and a details
  /// lookup) and, when <c>AppSettings:AiAgents:FullText</c> is on, the papers' own text in
  /// <c>dbo.article_section</c> (passage search, outline, section and full text);
  /// the experiments in <c>dbo.experiment</c> and <c>dbo.experiment_result</c>
  /// (<see cref="ExperimentTools"/>); and the clinical manual, the page files of the web app's
  /// Clinical screen (<see cref="ClinicalManualTools"/>).
  /// The agent is built per question, which is cheap and picks up configuration changes; the
  /// conversation history travels in <see cref="ArticleAnswer.Conversation"/>.
  /// </summary>
  public sealed partial class ArticleQuestionAgent : IArticleQuestionAgent
  {
    /// <summary>Model round trips per question, so a confused model cannot loop on tool calls.</summary>
    public const int MaxToolRounds = 8;

    private const int MaxQuestionLength = 4000;

    private readonly OpenRouterChatClientFactory _chatClientFactory;
    private readonly ArticleSearchRepository _repository;
    private readonly ExperimentRepository _experiments;
    private readonly ClinicalManual _clinicalManual;
    private readonly IAppSettingsService _appSettingsService;
    private readonly ILoggerFactory _loggerFactory;
    private readonly ILogger _logger;

    public ArticleQuestionAgent(
      OpenRouterChatClientFactory chatClientFactory,
      ArticleSearchRepository repository,
      ExperimentRepository experiments,
      ClinicalManual clinicalManual,
      IAppSettingsService appSettingsService,
      ILoggerFactory? loggerFactory = null)
    {
      _chatClientFactory = chatClientFactory;
      _repository = repository;
      _experiments = experiments;
      _clinicalManual = clinicalManual;
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
      var experimentTools = new ExperimentTools(_experiments);
      var clinicalTools = new ClinicalManualTools(_clinicalManual);

      AIAgent agent = chatClient.AsAIAgent(
        new ChatClientAgentOptions
        {
          Name = "babesiosis-article-agent",
          Description = "Answers questions from the canine babesiosis scoping review's articles, experiments and clinical manual.",
          ChatOptions = new ChatOptions
          {
            Instructions = BuildInstructions(categories, _clinicalManual.Pages, fullText),
            Tools = [.. tools.AsTools(), .. experimentTools.AsTools(), .. clinicalTools.AsTools()]
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
      var experiments = await ResolveExperimentsAsync(answer, experimentTools, cancellationToken);
      var clinicalPages = _clinicalManual.Mentioned(answer)
        .Select(p => new ClinicalPageSource(p.Id, p.Title, p.Group))
        .ToList();
      var conversation = (await agent.SerializeSessionAsync(session, cancellationToken: cancellationToken)).GetRawText();

      _logger.LogInformation(
        "Article agent answered with {Model}: {Seen} articles retrieved, {Cited} cited; " +
        "{ExperimentsSeen} experiments read, {ExperimentsCited} cited; {PagesSeen} clinical pages read, {PagesCited} cited; " +
        "{InputTokens}/{OutputTokens} tokens.",
        model, tools.SeenCount, sources.Count, experimentTools.SeenCount, experiments.Count,
        clinicalTools.SeenCount, clinicalPages.Count, response.Usage?.InputTokenCount, response.Usage?.OutputTokenCount);

      return new ArticleAnswer(
        answer, sources, model, conversation, response.Usage?.InputTokenCount, response.Usage?.OutputTokenCount)
      {
        Experiments = experiments,
        ClinicalPages = clinicalPages
      };
    }

    /// <summary>
    /// The experiments the answer mentions by full code or by short form (SV-05-01), in order
    /// of first mention. The codes are read from the database only when the answer holds
    /// something shaped like one, and codes that do not exist are dropped.
    /// </summary>
    private static async Task<IReadOnlyList<ExperimentSource>> ResolveExperimentsAsync(
      string answer, ExperimentTools tools, CancellationToken cancellationToken)
    {
      if (!ExperimentCodeShape().IsMatch(answer))
        return [];

      var all = await tools.AllAsync(cancellationToken);

      // A short form names an experiment only when one experiment has it.
      var shortCodes = all
        .Select(e => (e.Code, Short: ExperimentRepository.ShortCodeOf(e.Code)))
        .Where(e => e.Short is not null)
        .GroupBy(e => e.Short!, StringComparer.OrdinalIgnoreCase)
        .Where(g => g.Count() == 1)
        .ToDictionary(g => g.First().Code, g => g.Key, StringComparer.OrdinalIgnoreCase);

      return all
        .Select(e =>
        {
          var shortCode = shortCodes.GetValueOrDefault(e.Code);
          var at = answer.IndexOf(e.Code, StringComparison.OrdinalIgnoreCase);
          if (at < 0 && shortCode is not null)
            at = answer.IndexOf(shortCode, StringComparison.OrdinalIgnoreCase);
          return (Experiment: e, ShortCode: shortCode, At: at);
        })
        .Where(e => e.At >= 0)
        .OrderBy(e => e.At)
        .Select(e => new ExperimentSource(e.Experiment.Code, e.ShortCode, e.Experiment.Name, e.Experiment.Method))
        .ToList();
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

    private static string BuildInstructions(
      IReadOnlyList<CategoryInfo> categories, IReadOnlyList<ClinicalPage> clinicalPages, bool fullText) => $"""
      You answer questions about canine babesiosis for the users of a scoping review of its
      pathophysiology. You have three sources, and they are your only sources of evidence:

      1. The review's articles (codes such as CB001, HU003, BG002): the published literature.
      2. The experiments (codes such as SV-05-01-age-death): this project's own analyses of public
         datasets and of the review's literature, on why some dogs develop severe disease. They
         were run by AI agents on small samples, most are exploratory or descriptive, and none is
         peer reviewed.
      3. The clinical manual (pages SY01 to SY16, one per clinical syndrome, and TX00, antibabesial
         treatment): the definition, diagnosis, approach, treatments with doses and evidence
         levels, and prognosis of each syndrome. It was compiled by AI agents from the literature,
         which is wider than the review's articles. It is not peer reviewed, and no veterinarian
         has reviewed it.

      Which source to use:
      - What the published studies found, how they were done, or what the literature leaves
        open: the articles.
      - Which experiments were run, what one of them did or found, or what the project's own
        analyses show: the experiments. Call list_experiments, then get_experiment for the ones
        that matter, and get_experiment_result only for numbers the interpretation does not give.
      - A clinical syndrome or complication, how it is recognised or diagnosed, which tests to
        run, how it is treated, a drug or a dose, or the prognosis: the clinical manual first.
        Read the sections you need with get_clinical_page, or find a drug, test or finding across
        pages with search_clinical_manual. Go to the articles as well when the question asks for
        the studies behind a statement.
      - A question that spans sources: use each one, and say which source each statement is from.
      - Always call a tool before you answer a question of content. Do not answer from memory.

      How to work with the articles:
      - Call search_articles first. For broad or multi-part questions, search several times with
        different wording, and use a category filter when the topic is clear.
      - Call get_article_details for the articles you rely on, to read their abstract summary,
        conclusions, limitations, design, host and sample size.
      - Judge relevance from the content, not only the distance score.
      {(fullText ? FullTextInstructions : "")}
      How to answer:
      - Answer only from what the tools returned. Do not add facts from general knowledge. If the
        sources do not answer the question, say so plainly and describe what they do cover,
        without citing sources that do not address the question.
      - Cite every claim with the code of its source in square brackets: an article as [CB001] or
        [CB001, CB024], an experiment by its full code as [SV-05-01-age-death], a page of the
        clinical manual as [SY05] or [TX00]. Only cite codes that a tool returned, and only for
        claims those sources support. Never cite the name of a tool.
        {(fullText ? "When a claim comes from a paper's own text, add the section after the code, e.g. [CB004 Results]." : "")}
      - A clinical manual page cites its own references as [R1]. Do not repeat those markers:
        cite the page, and name the study behind a statement (authors and year) when it matters.
        When the page says a reference is in the review, you may cite its article code as well.
      - For articles, say how strong the evidence is: study design, Babesia species, number of
        dogs, natural versus experimental infection, and any limitations or disagreement between
        studies.
      - For experiments, give the effect size with its interval and the number of dogs, the role
        (primary, replication, sensitivity or descriptive) and what the experiment does not
        show. A null or negative result is a result: report it as fully as a positive one. Do not
        present an exploratory result as established, do not call groups of dogs "subtypes" or
        "endotypes", and do not turn a result into a prediction for a dog.
      - For the clinical manual, give the status and the evidence level of each treatment you
        mention. When the question is about treatment, report the doses that the page gives:
        the drug, dose, route and frequency as written, each with its context (Babesia species,
        kind of source). Do not leave them out, and do not change or convert them. Say once in
        such an answer that the manual is compiled by AI agents and is not peer reviewed, and,
        when you give a dose, that every dose must be checked against the product label before
        use.
      - Be concise. Use short paragraphs or bullet points. Write in British English.
      - Do not choose or adjust a treatment or a dose for an individual animal (a patient the
        user describes): report what the studies and the manual say, and say that the decision
        is the attending veterinarian's.

      Topic category codes for the categoryCode filter of the article tools:
      {string.Join(Environment.NewLine, categories.Select(c => $"- {c.Code}: {c.Name}"))}

      Pages of the clinical manual:
      {string.Join(Environment.NewLine, clinicalPages.Select(p => $"- {p.Id}: {p.Title}"))}
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

    // "S-CB050" is the code of a dataset (the supplement of CB050), not a citation of the article.
    [GeneratedRegex(@"(?<!\bS-)\b[A-Z]{2}\d{3}\b")]
    private static partial Regex ArticleCode();

    /// <summary>Something shaped like an experiment code or its short form: SV-05-01, EXP01-DS05-pairwise.</summary>
    [GeneratedRegex(@"\b[A-Z]{2,5}\d{0,2}-[A-Z0-9]{1,5}-[A-Za-z0-9]+")]
    private static partial Regex ExperimentCodeShape();
  }
}
