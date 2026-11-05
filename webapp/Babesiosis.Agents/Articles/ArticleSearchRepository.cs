using System.Data;
using System.Text.Json;
using Babesiosis.Core.Configurations;
using Microsoft.Data.SqlClient;

namespace Babesiosis.Agents.Articles
{
  /// <summary>
  /// Read-only access to the review's articles for the agent's tools.
  ///
  /// Semantic search goes through <c>dbo.search_articles</c> (one row per article, ranked on
  /// <c>article.embedding</c>) and <c>dbo.search_passages</c> (one row per passage of the papers'
  /// own text, ranked on <c>article_section.embedding</c>). Both procedures embed the question
  /// inside SQL Server (AI_GENERATE_EMBEDDINGS with the <c>babesiosis_embedding</c> external
  /// model), so the question is embedded with the same model and deployment as the stored
  /// vectors and no embedding key is needed here. See console/Babesiosis.Console/Database.
  /// </summary>
  public sealed class ArticleSearchRepository
  {
    // The procedures make a live call to the embedding endpoint before they search.
    private const int SearchCommandTimeoutSeconds = 60;

    private readonly IAppSettingsService _appSettingsService;
    private IReadOnlyList<CategoryInfo>? _categories;

    public ArticleSearchRepository(IAppSettingsService appSettingsService)
    {
      _appSettingsService = appSettingsService;
    }

    /// <summary>The closest articles to <paramref name="question"/> by meaning, nearest first.</summary>
    public async Task<IReadOnlyList<ArticleSearchHit>> SearchAsync(
      string question, int top, string? categoryCode, int? fromYear, int? toYear, double? maxDistance,
      CancellationToken cancellationToken)
    {
      await using var connection = await OpenAsync(cancellationToken);
      await using var command = new SqlCommand("dbo.search_articles", connection)
      {
        CommandType = CommandType.StoredProcedure,
        CommandTimeout = SearchCommandTimeoutSeconds
      };
      command.Parameters.Add("@question", SqlDbType.NVarChar, 4000).Value = question;
      command.Parameters.Add("@top", SqlDbType.Int).Value = top;
      command.Parameters.Add("@category_code", SqlDbType.Char, 3).Value = (object?)categoryCode ?? DBNull.Value;
      command.Parameters.Add("@from_year", SqlDbType.SmallInt).Value = (object?)fromYear ?? DBNull.Value;
      command.Parameters.Add("@to_year", SqlDbType.SmallInt).Value = (object?)toYear ?? DBNull.Value;
      command.Parameters.Add("@max_distance", SqlDbType.Float).Value = (object?)maxDistance ?? DBNull.Value;

      var hits = new List<ArticleSearchHit>();
      await using var reader = await command.ExecuteReaderAsync(cancellationToken);
      while (await reader.ReadAsync(cancellationToken))
      {
        hits.Add(new ArticleSearchHit(
          Code: reader.GetString("article_code"),
          Title: reader.GetString("title"),
          Year: NullableInt(reader, "pub_year"),
          Journal: NullableString(reader, "journal"),
          PrimaryCategory: NullableString(reader, "primary_category"),
          Distance: (double)reader.GetDecimal("distance"),
          Finding: NullableString(reader, "one_sentence_finding"),
          Doi: NullableString(reader, "doi"),
          HasFullText: Flag(reader, "has_full_text")));
      }

      return hits;
    }

    /// <summary>The closest passages of the papers' own text to <paramref name="question"/>, nearest first.</summary>
    public async Task<IReadOnlyList<PassageHit>> SearchPassagesAsync(
      string question, int top, IReadOnlyCollection<string>? articleCodes, IReadOnlyCollection<string>? sectionKinds,
      int? maxPerArticle, string? categoryCode, int? fromYear, int? toYear, CancellationToken cancellationToken)
    {
      await using var connection = await OpenAsync(cancellationToken);
      await using var command = new SqlCommand("dbo.search_passages", connection)
      {
        CommandType = CommandType.StoredProcedure,
        CommandTimeout = SearchCommandTimeoutSeconds
      };
      command.Parameters.Add("@question", SqlDbType.NVarChar, 4000).Value = question;
      command.Parameters.Add("@top", SqlDbType.Int).Value = top;
      command.Parameters.Add("@article_codes", SqlDbType.NVarChar, -1).Value =
        articleCodes is { Count: > 0 } ? JsonSerializer.Serialize(articleCodes) : DBNull.Value;
      command.Parameters.Add("@section_kinds", SqlDbType.NVarChar, 400).Value =
        sectionKinds is { Count: > 0 } ? JsonSerializer.Serialize(sectionKinds) : DBNull.Value;
      command.Parameters.Add("@max_per_article", SqlDbType.Int).Value = (object?)maxPerArticle ?? DBNull.Value;
      command.Parameters.Add("@category_code", SqlDbType.Char, 3).Value = (object?)categoryCode ?? DBNull.Value;
      command.Parameters.Add("@from_year", SqlDbType.SmallInt).Value = (object?)fromYear ?? DBNull.Value;
      command.Parameters.Add("@to_year", SqlDbType.SmallInt).Value = (object?)toYear ?? DBNull.Value;
      command.Parameters.Add("@max_distance", SqlDbType.Float).Value = DBNull.Value;

      var hits = new List<PassageHit>();
      await using var reader = await command.ExecuteReaderAsync(cancellationToken);
      while (await reader.ReadAsync(cancellationToken))
      {
        hits.Add(new PassageHit(
          Code: reader.GetString("article_code"),
          Title: reader.GetString("title"),
          Year: NullableInt(reader, "pub_year"),
          PrimaryCategory: NullableString(reader, "primary_category"),
          HasFullText: Flag(reader, "has_full_text"),
          Section: reader.GetString("section_kind"),
          Heading: NullableString(reader, "heading"),
          Part: reader.GetInt16("chunk_index"),
          Parts: reader.GetInt16("chunk_count"),
          Distance: (double)reader.GetDecimal("distance"),
          Words: reader.GetInt32("word_count"),
          Text: reader.GetString("body")));
      }

      return hits;
    }

    /// <summary>The review's narrative fields for each code that exists, in the order asked.</summary>
    public async Task<IReadOnlyList<ArticleDetails>> GetDetailsAsync(
      IReadOnlyCollection<string> codes, CancellationToken cancellationToken)
    {
      if (codes.Count == 0)
        return [];

      const string sql = """
        SELECT a.article_id, a.article_code, a.title, a.authors, a.journal, a.pub_year, a.doi, a.pmid,
               a.study_type, a.design, a.host, a.country, a.species_summary, a.sample_size,
               c.category_code AS primary_category, a.one_sentence_finding, a.abstract_summary,
               a.authors_conclusion, a.reviewer_interpretation, a.key_limitations,
               a.has_full_text, a.text_source, a.text_quality, a.text_language, a.text_translated, a.text_word_count
        FROM dbo.article AS a
        JOIN OPENJSON(@codes) AS j ON j.value = a.article_code
        LEFT JOIN dbo.category AS c ON c.category_id = a.primary_category_id
        ORDER BY CAST(j.[key] AS INT);
        """;

      await using var connection = await OpenAsync(cancellationToken);
      await using var command = new SqlCommand(sql, connection);
      command.Parameters.Add("@codes", SqlDbType.NVarChar, -1).Value = JsonSerializer.Serialize(codes);

      var details = new List<ArticleDetails>();
      await using var reader = await command.ExecuteReaderAsync(cancellationToken);
      while (await reader.ReadAsync(cancellationToken))
      {
        details.Add(new ArticleDetails(
          Id: reader.GetInt32("article_id"),
          Code: reader.GetString("article_code"),
          Title: reader.GetString("title"),
          Authors: NullableString(reader, "authors"),
          Journal: NullableString(reader, "journal"),
          Year: NullableInt(reader, "pub_year"),
          Doi: NullableString(reader, "doi"),
          Pmid: NullableString(reader, "pmid"),
          StudyType: NullableString(reader, "study_type"),
          Design: NullableString(reader, "design"),
          Host: NullableString(reader, "host"),
          Country: NullableString(reader, "country"),
          Species: NullableString(reader, "species_summary"),
          SampleSize: NullableString(reader, "sample_size"),
          PrimaryCategory: NullableString(reader, "primary_category"),
          Finding: NullableString(reader, "one_sentence_finding"),
          AbstractSummary: NullableString(reader, "abstract_summary"),
          AuthorsConclusion: NullableString(reader, "authors_conclusion"),
          ReviewerInterpretation: NullableString(reader, "reviewer_interpretation"),
          KeyLimitations: NullableString(reader, "key_limitations"),
          HasFullText: Flag(reader, "has_full_text"),
          TextSource: NullableString(reader, "text_source"),
          TextQuality: NullableString(reader, "text_quality"),
          TextLanguage: NullableString(reader, "text_language"),
          TextTranslated: Flag(reader, "text_translated"),
          TextWordCount: NullableInt(reader, "text_word_count")));
      }

      return details;
    }

    /// <summary>
    /// What text the database holds for one article: its full-text status and one line per
    /// top-level section (passage and word counts). Null when the code does not exist.
    /// </summary>
    public async Task<ArticleOutline?> GetOutlineAsync(string code, CancellationToken cancellationToken)
    {
      const string sql = """
        SELECT a.article_id, a.article_code, a.title, a.pub_year, a.has_full_text, a.text_source, a.text_quality,
               a.text_flags, a.text_language, a.text_translated, a.text_word_count
        FROM dbo.article AS a
        WHERE a.article_code = @code;

        SELECT s.section_kind,
               LEFT(s.heading, CHARINDEX(' > ', s.heading + ' > ') - 1) AS heading,
               COUNT(*) AS passages,
               SUM(s.word_count) AS words,
               MIN(s.section_order) AS first_order
        FROM dbo.article_section AS s
        JOIN dbo.article AS a ON a.article_id = s.article_id
        WHERE a.article_code = @code
        GROUP BY s.section_kind, LEFT(s.heading, CHARINDEX(' > ', s.heading + ' > ') - 1)
        ORDER BY first_order;
        """;

      await using var connection = await OpenAsync(cancellationToken);
      await using var command = new SqlCommand(sql, connection);
      command.Parameters.Add("@code", SqlDbType.VarChar, 10).Value = code;

      await using var reader = await command.ExecuteReaderAsync(cancellationToken);
      if (!await reader.ReadAsync(cancellationToken))
        return null;

      var id = reader.GetInt32("article_id");
      var articleCode = reader.GetString("article_code");
      var title = reader.GetString("title");
      var year = NullableInt(reader, "pub_year");
      var hasFullText = Flag(reader, "has_full_text");
      var textSource = NullableString(reader, "text_source");
      var textQuality = NullableString(reader, "text_quality");
      var textFlags = ParseStringArray(NullableString(reader, "text_flags"));
      var textLanguage = NullableString(reader, "text_language");
      var textTranslated = Flag(reader, "text_translated");
      var wordCount = NullableInt(reader, "text_word_count") ?? 0;

      var sections = new List<OutlineSection>();
      await reader.NextResultAsync(cancellationToken);
      while (await reader.ReadAsync(cancellationToken))
      {
        sections.Add(new OutlineSection(
          Section: reader.GetString("section_kind"),
          Heading: NullableString(reader, "heading"),
          Passages: reader.GetInt32("passages"),
          Words: reader.GetInt32("words")));
      }

      return new ArticleOutline(
        id, articleCode, title, year, hasFullText, textSource, textQuality, textFlags, textLanguage, textTranslated, wordCount, sections);
    }

    /// <summary>
    /// The article's passages in reading order, optionally only those of one section kind.
    /// Empty when the article has no text of that kind (or does not exist).
    /// </summary>
    public async Task<IReadOnlyList<ArticlePassage>> GetPassagesAsync(
      string code, string? sectionKind, CancellationToken cancellationToken)
    {
      const string sql = """
        SELECT s.section_order, s.section_kind, s.heading, s.chunk_index, s.chunk_count, s.word_count, s.body
        FROM dbo.article_section AS s
        JOIN dbo.article AS a ON a.article_id = s.article_id
        WHERE a.article_code = @code
          AND (@kind IS NULL OR s.section_kind = @kind)
        ORDER BY s.section_order;
        """;

      await using var connection = await OpenAsync(cancellationToken);
      await using var command = new SqlCommand(sql, connection);
      command.Parameters.Add("@code", SqlDbType.VarChar, 10).Value = code;
      command.Parameters.Add("@kind", SqlDbType.VarChar, 20).Value = (object?)sectionKind ?? DBNull.Value;

      var passages = new List<ArticlePassage>();
      await using var reader = await command.ExecuteReaderAsync(cancellationToken);
      while (await reader.ReadAsync(cancellationToken))
      {
        passages.Add(new ArticlePassage(
          Order: reader.GetInt16("section_order"),
          Section: reader.GetString("section_kind"),
          Heading: NullableString(reader, "heading"),
          Part: reader.GetInt16("chunk_index"),
          Parts: reader.GetInt16("chunk_count"),
          Words: reader.GetInt32("word_count"),
          Text: reader.GetString("body")));
      }

      return passages;
    }

    /// <summary>The topic categories, read once per repository instance.</summary>
    public async Task<IReadOnlyList<CategoryInfo>> GetCategoriesAsync(CancellationToken cancellationToken)
    {
      if (_categories is not null)
        return _categories;

      await using var connection = await OpenAsync(cancellationToken);
      await using var command = new SqlCommand(
        "SELECT category_code, name FROM dbo.category ORDER BY category_code", connection);

      var categories = new List<CategoryInfo>();
      await using var reader = await command.ExecuteReaderAsync(cancellationToken);
      while (await reader.ReadAsync(cancellationToken))
        categories.Add(new CategoryInfo(reader.GetString(0).Trim(), reader.GetString(1)));

      return _categories = categories;
    }

    private async Task<SqlConnection> OpenAsync(CancellationToken cancellationToken)
    {
      var connection = new SqlConnection(_appSettingsService.GetAppSettings().Connections.Database);
      await connection.OpenAsync(cancellationToken);
      return connection;
    }

    private static string? NullableString(SqlDataReader reader, string name)
    {
      var ordinal = reader.GetOrdinal(name);
      return reader.IsDBNull(ordinal) ? null : reader.GetString(ordinal);
    }

    private static int? NullableInt(SqlDataReader reader, string name)
    {
      var ordinal = reader.GetOrdinal(name);
      return reader.IsDBNull(ordinal) ? null : Convert.ToInt32(reader.GetValue(ordinal));
    }

    /// <summary>A nullable BIT read as false when NULL (articles loaded before the text columns existed).</summary>
    private static bool Flag(SqlDataReader reader, string name)
    {
      var ordinal = reader.GetOrdinal(name);
      return !reader.IsDBNull(ordinal) && reader.GetBoolean(ordinal);
    }

    private static IReadOnlyList<string> ParseStringArray(string? json)
    {
      if (string.IsNullOrWhiteSpace(json))
        return [];
      try
      {
        return JsonSerializer.Deserialize<List<string>>(json) ?? [];
      }
      catch (JsonException)
      {
        return [];
      }
    }
  }

  /// <summary>One <c>dbo.search_articles</c> row. Distance runs from 0 (same meaning) to 2.</summary>
  public sealed record ArticleSearchHit(
    string Code, string Title, int? Year, string? Journal, string? PrimaryCategory,
    double Distance, string? Finding, string? Doi, bool HasFullText);

  /// <summary>An article's citation data, the review's narrative fields and its full-text status.</summary>
  public sealed record ArticleDetails(
    int Id, string Code, string Title, string? Authors, string? Journal, int? Year, string? Doi, string? Pmid,
    string? StudyType, string? Design, string? Host, string? Country, string? Species, string? SampleSize,
    string? PrimaryCategory, string? Finding, string? AbstractSummary, string? AuthorsConclusion,
    string? ReviewerInterpretation, string? KeyLimitations,
    bool HasFullText, string? TextSource, string? TextQuality, string? TextLanguage, bool TextTranslated, int? TextWordCount);

  /// <summary>One <c>dbo.search_passages</c> row: a passage of a paper's own text.</summary>
  public sealed record PassageHit(
    string Code, string Title, int? Year, string? PrimaryCategory, bool HasFullText,
    string Section, string? Heading, int Part, int Parts, double Distance, int Words, string Text);

  /// <summary>What text the database holds for an article.</summary>
  /// <param name="TextSource">abstract, jats_xml or pdf.</param>
  /// <param name="TextQuality">ok, review, abstract_only or no_text; review means the conversion flagged problems.</param>
  /// <param name="TextLanguage">Language of the paper; the passages are English when <paramref name="TextTranslated"/> is true.</param>
  public sealed record ArticleOutline(
    int Id, string Code, string Title, int? Year, bool HasFullText, string? TextSource, string? TextQuality,
    IReadOnlyList<string> TextFlags, string? TextLanguage, bool TextTranslated, int WordCount,
    IReadOnlyList<OutlineSection> Sections);

  /// <summary>One top-level section of a paper: its kind, the paper's own heading, and its size.</summary>
  public sealed record OutlineSection(string Section, string? Heading, int Passages, int Words);

  /// <summary>One stored passage of a paper's text.</summary>
  public sealed record ArticlePassage(
    int Order, string Section, string? Heading, int Part, int Parts, int Words, string Text);

  public sealed record CategoryInfo(string Code, string Name);
}
