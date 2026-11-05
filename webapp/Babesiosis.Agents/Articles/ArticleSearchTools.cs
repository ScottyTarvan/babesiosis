using System.Collections.Concurrent;
using System.ComponentModel;
using System.Text;
using Microsoft.Extensions.AI;

namespace Babesiosis.Agents.Articles
{
  /// <summary>
  /// The functions the article agent can call. One instance serves one question and records
  /// the codes of every article the tools returned, with the sections of the paper's own text
  /// the model read for each.
  ///
  /// Two layers: the review's record of each article (search_articles, get_article_details), and
  /// the paper's own text in passages (search_passages, get_article_outline, get_article_section,
  /// get_article_full_text). The text tools are offered only when <c>fullText</c> is on.
  /// </summary>
  internal sealed class ArticleSearchTools
  {
    public const int MaxResults = 20;
    public const int MaxDetails = 10;
    public const int MaxPassageResults = 20;
    public const int MaxPassageArticles = 20;

    /// <summary>Characters of text per get_article_section result; longer sections come in parts.</summary>
    public const int SectionPartChars = 12_000;
    /// <summary>Characters of text per get_article_full_text result; longer papers come in parts.</summary>
    public const int FullTextPartChars = 30_000;

    public static readonly IReadOnlySet<string> SectionKinds = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
    {
      "abstract", "introduction", "methods", "results", "results_discussion", "discussion",
      "conclusion", "case", "limitations", "abbreviations", "body", "other"
    };

    private readonly ArticleSearchRepository _repository;
    private readonly IReadOnlySet<string> _categoryCodes;
    private readonly bool _fullText;
    private readonly ConcurrentDictionary<string, ConcurrentDictionary<string, byte>> _seen = new(StringComparer.OrdinalIgnoreCase);

    public ArticleSearchTools(ArticleSearchRepository repository, IReadOnlySet<string> categoryCodes, bool fullText)
    {
      _repository = repository;
      _categoryCodes = categoryCodes;
      _fullText = fullText;
    }

    /// <summary>How many distinct articles the tools have returned so far.</summary>
    public int SeenCount => _seen.Count;

    /// <summary>The section kinds of <paramref name="code"/>'s own text that the model read, in no particular order.</summary>
    public IReadOnlyList<string> SectionsRead(string code) =>
      _seen.TryGetValue(code, out var sections) ? sections.Keys.Order().ToList() : [];

    public IList<AITool> AsTools()
    {
      var tools = new List<AITool>
      {
        AIFunctionFactory.Create(SearchArticlesAsync, "search_articles"),
        AIFunctionFactory.Create(GetArticleDetailsAsync, "get_article_details")
      };

      if (_fullText)
      {
        tools.Add(AIFunctionFactory.Create(SearchPassagesAsync, "search_passages"));
        tools.Add(AIFunctionFactory.Create(GetArticleOutlineAsync, "get_article_outline"));
        tools.Add(AIFunctionFactory.Create(GetArticleSectionAsync, "get_article_section"));
        tools.Add(AIFunctionFactory.Create(GetArticleFullTextAsync, "get_article_full_text"));
      }

      return tools;
    }

    // ---------------------------------------------------------------------------------------------------------
    // The review's record
    // ---------------------------------------------------------------------------------------------------------

    [Description(
      "Semantic search over the canine babesiosis review's articles. Embeds the query and ranks " +
      "articles by cosine distance to a stored embedding of each article's title, key finding, " +
      "abstract summary, conclusions, interpretation and limitations. Returns the closest articles " +
      "with their one-sentence finding and whether the paper's own full text is available " +
      "(hasFullText). Distance runs from 0 (same meaning) to 2; below about 0.6 is usually on " +
      "topic. Run several searches with different wording for broad questions.")]
    private async Task<IReadOnlyList<ArticleSearchHit>> SearchArticlesAsync(
      [Description("What to look for, in plain words, e.g. 'urinary markers of tubular injury'.")]
      string query,
      [Description("How many articles to return, 1 to 20. Default 8.")]
      int top = 8,
      [Description("Optional three-letter topic category code to restrict the search to, e.g. REN.")]
      string? categoryCode = null,
      [Description("Optional earliest publication year.")]
      int? fromYear = null,
      [Description("Optional latest publication year.")]
      int? toYear = null,
      CancellationToken cancellationToken = default)
    {
      if (string.IsNullOrWhiteSpace(query))
        throw new ArgumentException("query is required.");

      categoryCode = NormaliseCategory(categoryCode);

      var hits = await _repository.SearchAsync(
        query.Trim(), Math.Clamp(top, 1, MaxResults), categoryCode, fromYear, toYear, maxDistance: null, cancellationToken);

      foreach (var hit in hits)
        Seen(hit.Code);

      return hits;
    }

    [Description(
      "Full review record for specific articles: authors, study design, host, country, sample " +
      "size, abstract summary, authors' conclusion, the reviewer's interpretation and key " +
      "limitations, plus the full-text status (hasFullText, textSource, textQuality, " +
      "textLanguage, textTranslated). Call it for the articles you rely on before answering.")]
    private async Task<IReadOnlyList<ArticleDetails>> GetArticleDetailsAsync(
      [Description("Article codes from search_articles, e.g. [\"CB001\", \"BG002\"]. At most 10.")]
      string[] articleCodes,
      CancellationToken cancellationToken = default)
    {
      var codes = NormaliseCodes(articleCodes, MaxDetails, "articleCodes");
      var details = await _repository.GetDetailsAsync(codes, cancellationToken);

      foreach (var article in details)
        Seen(article.Code);

      return details;
    }

    // ---------------------------------------------------------------------------------------------------------
    // The paper's own text
    // ---------------------------------------------------------------------------------------------------------

    [Description(
      "Semantic search over the papers' own text, one passage (about a paragraph to a page) per " +
      "result, with the article code, section and heading it comes from. Use it to find what a " +
      "paper measured, how, and the numbers, after search_articles has given you candidate " +
      "articles: pass their codes in articleCodes to stay inside them, or leave articleCodes " +
      "empty to search every paper. Only articles with full text have passages beyond the " +
      "abstract. At most 3 passages per article are returned, so a broad question spreads over " +
      "several papers; call again with articleCodes set to one article to go deeper into it.")]
    private async Task<IReadOnlyList<PassageHit>> SearchPassagesAsync(
      [Description("What to look for, in plain words, e.g. 'how acute kidney injury was defined'.")]
      string query,
      [Description("Optional article codes to search within, e.g. [\"CB004\", \"CB010\"]. At most 20. Empty = all articles.")]
      string[]? articleCodes = null,
      [Description("Optional section kinds to search within: abstract, introduction, methods, results, results_discussion, discussion, conclusion, case, limitations, other.")]
      string[]? sections = null,
      [Description("How many passages to return, 1 to 20. Default 8.")]
      int top = 8,
      [Description("Optional three-letter topic category code to restrict the search to, e.g. REN.")]
      string? categoryCode = null,
      [Description("Optional earliest publication year.")]
      int? fromYear = null,
      [Description("Optional latest publication year.")]
      int? toYear = null,
      CancellationToken cancellationToken = default)
    {
      if (string.IsNullOrWhiteSpace(query))
        throw new ArgumentException("query is required.");

      var codes = articleCodes is { Length: > 0 } ? NormaliseCodes(articleCodes, MaxPassageArticles, "articleCodes") : null;
      var kinds = NormaliseSections(sections);
      categoryCode = NormaliseCategory(categoryCode);

      var hits = await _repository.SearchPassagesAsync(
        query.Trim(), Math.Clamp(top, 1, MaxPassageResults), codes, kinds, maxPerArticle: 3,
        categoryCode, fromYear, toYear, cancellationToken);

      foreach (var hit in hits)
        Seen(hit.Code, hit.Section);

      return hits;
    }

    [Description(
      "What text the database holds for one article: whether the paper's full text is available " +
      "(hasFullText), its source and quality, its language and whether the text is a machine " +
      "translation, and one line per section with the paper's own heading and its length in " +
      "words. Cheap: call it to decide which section to read before get_article_section.")]
    private async Task<ArticleOutline> GetArticleOutlineAsync(
      [Description("One article code, e.g. \"CB004\".")]
      string articleCode,
      CancellationToken cancellationToken = default)
    {
      var code = NormaliseCode(articleCode);
      var outline = await _repository.GetOutlineAsync(code, cancellationToken)
        ?? throw new ArgumentException($"Article {code} does not exist.");

      Seen(code);
      return outline;
    }

    [Description(
      "One section of a paper's own text, as Markdown: methods, results, discussion and so on. " +
      "Returns at most 12,000 characters at a time; when a section is longer the " +
      "result says how many parts there are, and you call again with the next part. Prefer " +
      "search_passages when you need a specific fact; read a section when you need the whole " +
      "method or all the results.")]
    private async Task<ArticleTextPart> GetArticleSectionAsync(
      [Description("One article code, e.g. \"CB004\".")]
      string articleCode,
      [Description("Section kind: abstract, introduction, methods, results, results_discussion, discussion, conclusion, case, limitations, body or other.")]
      string section,
      [Description("Which part of a long section to return, from 1. Default 1.")]
      int part = 1,
      CancellationToken cancellationToken = default)
    {
      var code = NormaliseCode(articleCode);
      var kind = NormaliseSection(section);

      var passages = await _repository.GetPassagesAsync(code, kind, cancellationToken);
      if (passages.Count == 0)
        return await ExplainMissingTextAsync(code, kind, cancellationToken);

      Seen(code, kind);
      return Assemble(code, kind, passages, part, SectionPartChars, includeHeadings: true);
    }

    [Description(
      "The whole of a paper's own text, section by section, as Markdown. Dear: a paper is " +
      "several thousand words, so use it only to summarise or appraise one specific paper, and " +
      "read one paper at a time. Returns at most 30,000 characters per call; the " +
      "result says how many parts there are, and you call again with the next part. For a fact " +
      "or a figure use search_passages; for one section use get_article_section.")]
    private async Task<ArticleTextPart> GetArticleFullTextAsync(
      [Description("One article code, e.g. \"CB004\".")]
      string articleCode,
      [Description("Which part of a long paper to return, from 1. Default 1.")]
      int part = 1,
      CancellationToken cancellationToken = default)
    {
      var code = NormaliseCode(articleCode);

      var passages = await _repository.GetPassagesAsync(code, null, cancellationToken);
      if (passages.Count == 0)
        return await ExplainMissingTextAsync(code, null, cancellationToken);

      foreach (var kind in passages.Select(p => p.Section).Distinct())
        Seen(code, kind);

      return Assemble(code, "full_text", passages, part, FullTextPartChars, includeHeadings: true);
    }

    /// <summary>
    /// Joins passages into Markdown and returns the part asked for. Parts break at passage
    /// boundaries, so one part can exceed <paramref name="maxChars"/> by at most one passage.
    /// </summary>
    private static ArticleTextPart Assemble(
      string code, string section, IReadOnlyList<ArticlePassage> passages, int part, int maxChars, bool includeHeadings)
    {
      var parts = new List<(StringBuilder Text, int Words)>();
      string? lastHeading = null;

      foreach (var passage in passages)
      {
        var piece = new StringBuilder();
        if (includeHeadings && passage.Heading is not null && passage.Heading != lastHeading)
        {
          piece.Append("## ").Append(passage.Heading).Append("\n\n");
          lastHeading = passage.Heading;
        }
        piece.Append(passage.Text);

        if (parts.Count == 0 || parts[^1].Text.Length + piece.Length + 2 > maxChars)
          parts.Add((new StringBuilder(), 0));

        var current = parts[^1];
        if (current.Text.Length > 0)
          current.Text.Append("\n\n");
        current.Text.Append(piece);
        parts[^1] = (current.Text, current.Words + passage.Words);
      }

      if (part < 1 || part > parts.Count)
        throw new ArgumentException($"part must be between 1 and {parts.Count} for {code} {section}.");

      var (text, words) = parts[part - 1];
      var note = parts.Count > 1
        ? part < parts.Count
          ? $"Part {part} of {parts.Count}. Call again with part = {part + 1} for the rest."
          : $"Part {part} of {parts.Count}: the end of the {section.Replace('_', ' ')}."
        : null;

      return new ArticleTextPart(code, section, part, parts.Count, words, text.ToString(), note);
    }

    /// <summary>A result that tells the model why there is no text, instead of an error it might retry.</summary>
    private async Task<ArticleTextPart> ExplainMissingTextAsync(string code, string? kind, CancellationToken cancellationToken)
    {
      var outline = await _repository.GetOutlineAsync(code, cancellationToken)
        ?? throw new ArgumentException($"Article {code} does not exist.");

      Seen(code);

      string note;
      if (outline.Sections.Count == 0)
      {
        note = $"No text of {code} is stored: the review has {(outline.TextQuality == "no_text" ? "an unusable (scanned or garbled) copy" : "only the review record")}. " +
               "Use get_article_details for the review's summary of it.";
      }
      else if (!outline.HasFullText)
      {
        note = $"{code} has no full text in the database, only its abstract. " +
               "Call get_article_section with section = \"abstract\", or get_article_details for the review's summary.";
      }
      else
      {
        var available = string.Join(", ", outline.Sections.Select(s => s.Heading is null ? s.Section : $"{s.Section} (\"{s.Heading}\")").Distinct());
        note = $"{code} has no \"{kind}\" section. Its sections are: {available}. " +
               "Papers that merge results and discussion use results_discussion; topical headings are under other.";
      }

      return new ArticleTextPart(code, kind ?? "full_text", 1, 0, 0, "", note);
    }

    // ---------------------------------------------------------------------------------------------------------
    // Argument checks
    // ---------------------------------------------------------------------------------------------------------

    private string? NormaliseCategory(string? categoryCode)
    {
      categoryCode = string.IsNullOrWhiteSpace(categoryCode) ? null : categoryCode.Trim().ToUpperInvariant();
      if (categoryCode is not null && !_categoryCodes.Contains(categoryCode))
        throw new ArgumentException($"Unknown categoryCode '{categoryCode}'. Use one of: {string.Join(", ", _categoryCodes)}.");
      return categoryCode;
    }

    private static string NormaliseCode(string? articleCode)
    {
      if (string.IsNullOrWhiteSpace(articleCode))
        throw new ArgumentException("articleCode is required.");
      return articleCode.Trim().ToUpperInvariant();
    }

    private static List<string> NormaliseCodes(string[]? articleCodes, int max, string name)
    {
      var codes = (articleCodes ?? [])
        .Where(c => !string.IsNullOrWhiteSpace(c))
        .Select(c => c.Trim().ToUpperInvariant())
        .Distinct()
        .ToList();

      if (codes.Count == 0)
        throw new ArgumentException($"{name} is required.");
      if (codes.Count > max)
        throw new ArgumentException($"Ask for at most {max} articles at a time.");

      return codes;
    }

    private static string NormaliseSection(string? section)
    {
      if (string.IsNullOrWhiteSpace(section))
        throw new ArgumentException("section is required.");
      var kind = section.Trim().ToLowerInvariant().Replace(' ', '_').Replace("results_and_discussion", "results_discussion");
      if (!SectionKinds.Contains(kind))
        throw new ArgumentException($"Unknown section '{section}'. Use one of: {string.Join(", ", SectionKinds)}.");
      return kind;
    }

    private static List<string>? NormaliseSections(string[]? sections)
    {
      if (sections is null || sections.Length == 0)
        return null;
      return sections.Where(s => !string.IsNullOrWhiteSpace(s)).Select(NormaliseSection).Distinct().ToList();
    }

    private void Seen(string code, string? section = null)
    {
      var sections = _seen.GetOrAdd(code, _ => new ConcurrentDictionary<string, byte>(StringComparer.OrdinalIgnoreCase));
      if (section is not null)
        sections.TryAdd(section, 0);
    }
  }

  /// <summary>One part of a paper's text, from get_article_section or get_article_full_text.</summary>
  /// <param name="Section">The section kind asked for, or full_text.</param>
  /// <param name="Parts">How many parts the text comes in; 0 when there is no text (see <paramref name="Note"/>).</param>
  /// <param name="Note">How to get the rest, or why there is no text.</param>
  public sealed record ArticleTextPart(
    string Code, string Section, int Part, int Parts, int Words, string Text, string? Note);
}
