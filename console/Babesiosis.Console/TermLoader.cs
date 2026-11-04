using System.Data;
using System.Globalization;
using System.Text;
using System.Text.Json;
using Microsoft.Data.SqlClient;
using Out = System.Console;

namespace Babesiosis.Console
{
  /// <summary>
  /// Loads the per-article disorder terms (data/terms/&lt;ID&gt;.json) and the curated display map
  /// (data/terms/term_display.csv) into dbo.term and dbo.article_term, and sets dbo.article.text_source.
  /// Runs after <see cref="ArticleLoader"/>: it only fills terms for articles already in dbo.article.
  /// </summary>
  internal sealed class TermLoader(LoaderSettings settings, LoaderOptions options)
  {
    /// <summary>Sections where an affirmed mention makes the term "studied" in the article.</summary>
    private static readonly HashSet<string> StudiedSections = new(StringComparer.OrdinalIgnoreCase) { "title", "results", "case", "conclusion" };

    private const string AbstractOnlyFormat = "abstract";

    private readonly List<string> _errors = [];
    private readonly List<string> _warnings = [];

    /// <summary>Runs the load and prints a report. Returns the process exit code.</summary>
    public async Task<int> RunAsync(CancellationToken cancellationToken)
    {
      var termsFolder = Path.Combine(settings.ReviewRoot, "data", "terms");
      Out.WriteLine();
      Out.WriteLine($"Reading terms from {termsFolder}");

      if (!Directory.Exists(termsFolder))
      {
        _errors.Add($"Folder {termsFolder} not found. Run scripts/extract_terms.py first.");
        PrintReport(new TermCounts(), options.DryRun);
        return 1;
      }

      var display = ReadDisplayMap(Path.Combine(termsFolder, "term_display.csv"));
      var excludedCodes = ReadExcludedCodes();
      var files = ReadTermFiles(termsFolder);

      var counts = new TermCounts { Files = files.Count };

      // Excluded articles (human comparators, Articles:ExcludeCodes) are never loaded.
      files = files.Where(f => !excludedCodes.Contains(f.Code)).ToList();
      counts.Excluded = counts.Files - files.Count;

      if (options.Only is not null)
        files = files.Where(f => options.Only.Contains(f.Code)).ToList();

      // Terms: every CUI seen in a loaded file (negated-only terms included, so the table matches the display map).
      var terms = new Dictionary<string, TermRow>(StringComparer.OrdinalIgnoreCase);
      foreach (var term in files.SelectMany(f => f.Terms))
      {
        if (terms.ContainsKey(term.Cui))
          continue;
        var map = display.GetValueOrDefault(term.Cui);
        terms[term.Cui] = new TermRow(term.Cui, term.Concept, term.SemanticType, map?.DisplayName, map?.Hidden ?? false, map?.Note);
      }
      // CUIs seen only in excluded articles are expected; only a curated row that matches nothing is worth a warning.
      foreach (var (cui, row) in display.Where(d => !terms.ContainsKey(d.Key) && options.Only is null && (d.Value.Hidden || d.Value.DisplayName is not null || d.Value.Note is not null)).OrderBy(d => d.Key))
        _warnings.Add($"{cui}: curated row in term_display.csv, but no loaded article has this term");

      counts.Terms = terms.Count;
      counts.Hidden = terms.Values.Count(t => t.Hidden);
      counts.DisplayNames = terms.Values.Where(t => t.DisplayName is not null).Select(t => t.DisplayName).Distinct().Count();

      if (!await SchemaExistsAsync(cancellationToken))
      {
        if (options.DryRun)
        {
          _warnings.Add("Tables dbo.term and dbo.article_term not found: article rows were not matched. Run Database/schema.sql before a real load.");
          counts.ArticleTerms = files.Sum(f => f.Terms.Count(t => t.MentionsAffirmed > 0));
          counts.Studied = files.Sum(f => f.Terms.Count(t => t.MentionsAffirmed > 0 && t.Studied));
          PrintReport(counts, dryRun: true);
          return _errors.Count > 0 ? 1 : 0;
        }

        _errors.Add("Tables dbo.term and dbo.article_term (or column dbo.article.text_source) not found. Run Database/schema.sql first.");
        PrintReport(counts);
        return 1;
      }

      var articleIds = await GetArticleIdsAsync(cancellationToken);
      var existingCuis = await GetExistingCuisAsync(cancellationToken);

      foreach (var file in files.Where(f => !articleIds.ContainsKey(f.Code)))
        _warnings.Add($"{file.Code}: term file has no row in dbo.article; skipped");
      var loadable = files.Where(f => articleIds.ContainsKey(f.Code)).ToList();

      var fileCodes = files.Select(f => f.Code).ToHashSet(StringComparer.OrdinalIgnoreCase);
      counts.ArticlesWithoutTermFile = articleIds.Keys
        .Where(code => !fileCodes.Contains(code) && !excludedCodes.Contains(code) && (options.Only is null || options.Only.Contains(code)))
        .Order().ToList();

      counts.Articles = loadable.Count;
      counts.AbstractOnly = loadable.Count(f => IsAbstractOnly(f.SourceFormat));
      // The dashboard's denominators: canine articles with at least one affirmed term, and how many are abstract-only.
      var canine = loadable.Where(f => f.Code.StartsWith("CB", StringComparison.OrdinalIgnoreCase) && f.Terms.Any(t => t.MentionsAffirmed > 0)).ToList();
      counts.CanineWithTerms = canine.Count;
      counts.CanineAbstractOnly = canine.Count(f => IsAbstractOnly(f.SourceFormat));
      counts.ArticleTerms = loadable.Sum(f => f.Terms.Count(t => t.MentionsAffirmed > 0));
      counts.Studied = loadable.Sum(f => f.Terms.Count(t => t.MentionsAffirmed > 0 && t.Studied));
      counts.NegatedOnly = loadable.Sum(f => f.Terms.Count(t => t.MentionsAffirmed == 0));
      counts.NewTerms = terms.Keys.Count(c => !existingCuis.Contains(c));

      if (options.DryRun)
      {
        PrintReport(counts, dryRun: true);
        return _errors.Count > 0 ? 1 : 0;
      }

      try
      {
        await WriteAsync(terms.Values.ToList(), loadable, articleIds, cancellationToken);
      }
      catch (Exception ex) when (ex is not OperationCanceledException)
      {
        _errors.Add($"Term load failed and was rolled back: {ex.Message}");
      }

      PrintReport(counts);
      return _errors.Count > 0 ? 1 : 0;
    }

    private static bool IsAbstractOnly(string? sourceFormat) =>
      string.Equals(sourceFormat, AbstractOnlyFormat, StringComparison.OrdinalIgnoreCase);

    /// <summary>
    /// Decision 2 of the widget plan: studied = affirmed mention in title, results, case or conclusion, or in the
    /// abstract when the article is abstract-only. The term files count mentions per section without splitting
    /// negated from affirmed, so a section counts when it has any mention and the term has an affirmed mention.
    /// </summary>
    private static bool IsStudied(int mentionsAffirmed, IReadOnlyDictionary<string, int> sections, bool abstractOnly) =>
      mentionsAffirmed > 0 && sections.Any(s => s.Value > 0 &&
        (StudiedSections.Contains(s.Key) || (abstractOnly && s.Key.Equals("abstract", StringComparison.OrdinalIgnoreCase))));

    // ---------------------------------------------------------------------------------------------------------
    // Source files
    // ---------------------------------------------------------------------------------------------------------

    private sealed record DisplayRow(string? DisplayName, bool Hidden, string? Note);

    private sealed record TermFile(string Code, string? SourceFormat, List<FileTerm> Terms);

    private sealed record FileTerm(
      string Cui, string Concept, string? SemanticType, int Mentions, int MentionsAffirmed, int MentionsNegated,
      bool Studied, string? SectionsJson, string? FormsJson, decimal? BestScore);

    private sealed record TermRow(string Cui, string Concept, string? SemanticType, string? DisplayName, bool Hidden, string? Note);

    /// <summary>Reads term_display.csv (cui, concept, articles, action, display_name, note). Missing file = show every term.</summary>
    private Dictionary<string, DisplayRow> ReadDisplayMap(string path)
    {
      var map = new Dictionary<string, DisplayRow>(StringComparer.OrdinalIgnoreCase);
      if (!File.Exists(path))
      {
        _warnings.Add("term_display.csv not found: every term is shown under its UMLS name. Run scripts/build_term_display.py.");
        return map;
      }

      var rows = ParseCsv(File.ReadAllText(path, Encoding.UTF8));
      if (rows.Count == 0)
        return map;

      var header = rows[0].Select(h => h.Trim().ToLowerInvariant()).ToList();
      int Col(string name)
      {
        var index = header.IndexOf(name);
        if (index < 0)
          throw new InvalidOperationException($"term_display.csv has no '{name}' column.");
        return index;
      }

      int cuiCol = Col("cui"), actionCol = Col("action"), nameCol = Col("display_name"), noteCol = Col("note");
      for (var i = 1; i < rows.Count; i++)
      {
        var row = rows[i];
        string Cell(int index) => index < row.Count ? row[index].Trim() : "";

        var cui = Cell(cuiCol);
        if (cui.Length == 0)
          continue;

        var action = Cell(actionCol).ToLowerInvariant();
        if (action is not ("show" or "hide" or ""))
          _warnings.Add($"term_display.csv line {i + 1}: action '{action}' is not show or hide; treated as show");

        map[cui] = new DisplayRow(NullIfEmpty(Cell(nameCol)), action == "hide", NullIfEmpty(Cell(noteCol)));
      }

      return map;
    }

    /// <summary>Codes excluded by Articles:ExcludeCodes or, through articles.jsonl, by Articles:ExcludeScopes.</summary>
    private HashSet<string> ReadExcludedCodes()
    {
      var excluded = new HashSet<string>(settings.ExcludeCodes, StringComparer.OrdinalIgnoreCase);
      var jsonlPath = Path.Combine(settings.ReviewRoot, "articles.jsonl");
      if (!File.Exists(jsonlPath))
      {
        _warnings.Add("articles.jsonl not found: only Articles:ExcludeCodes applied");
        return excluded;
      }

      foreach (var line in File.ReadLines(jsonlPath, Encoding.UTF8))
      {
        if (string.IsNullOrWhiteSpace(line))
          continue;
        try
        {
          using var doc = JsonDocument.Parse(line);
          var root = doc.RootElement;
          if (root.TryGetProperty("id", out var id) && id.ValueKind == JsonValueKind.String &&
              root.TryGetProperty("scope_label", out var scope) && scope.ValueKind == JsonValueKind.String &&
              settings.ExcludeScopes.Contains(scope.GetString()!.Trim()))
            excluded.Add(id.GetString()!);
        }
        catch (JsonException)
        {
          // Reported by the article loader.
        }
      }

      return excluded;
    }

    private List<TermFile> ReadTermFiles(string folder)
    {
      var files = new List<TermFile>();

      foreach (var path in Directory.EnumerateFiles(folder, "*.json").Order(StringComparer.OrdinalIgnoreCase))
      {
        try
        {
          using var doc = JsonDocument.Parse(File.ReadAllText(path, Encoding.UTF8));
          var root = doc.RootElement;
          var code = root.TryGetProperty("id", out var id) && id.ValueKind == JsonValueKind.String
            ? id.GetString()!
            : Path.GetFileNameWithoutExtension(path);
          var sourceFormat = root.TryGetProperty("source_format", out var sf) && sf.ValueKind == JsonValueKind.String ? sf.GetString() : null;
          var abstractOnly = IsAbstractOnly(sourceFormat);

          if (sourceFormat is null)
            _warnings.Add($"{code}: term file has no source_format; terms treated as full text");

          var terms = new List<FileTerm>();
          if (root.TryGetProperty("terms", out var termArray) && termArray.ValueKind == JsonValueKind.Array)
          {
            foreach (var t in termArray.EnumerateArray())
            {
              var cui = t.GetProperty("term").GetString()!;
              var sections = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
              if (t.TryGetProperty("sections", out var s) && s.ValueKind == JsonValueKind.Object)
                foreach (var p in s.EnumerateObject())
                  sections[p.Name] = p.Value.TryGetInt32(out var n) ? n : 0;

              var affirmed = Int(t, "mentions_affirmed");
              var semanticTypes = t.TryGetProperty("semantic_types", out var st) && st.ValueKind == JsonValueKind.Array
                ? string.Join("; ", st.EnumerateArray().Select(e => e.GetString()).OfType<string>())
                : null;

              terms.Add(new FileTerm(
                cui,
                t.TryGetProperty("concept", out var c) && c.ValueKind == JsonValueKind.String ? c.GetString()! : cui,
                NullIfEmpty(semanticTypes),
                Int(t, "mentions"),
                affirmed,
                Int(t, "mentions_negated"),
                IsStudied(affirmed, sections, abstractOnly),
                Raw(t, "sections"),
                Raw(t, "forms"),
                t.TryGetProperty("best_score", out var bs) && bs.ValueKind == JsonValueKind.Number ? Math.Round(bs.GetDecimal(), 3) : null));
            }
          }

          files.Add(new TermFile(code, sourceFormat, terms));
        }
        catch (Exception ex) when (ex is JsonException or KeyNotFoundException or InvalidOperationException or FormatException)
        {
          _errors.Add($"{Path.GetFileName(path)}: cannot read ({ex.Message}); skipped");
        }
      }

      return files;

      static int Int(JsonElement e, string name) => e.TryGetProperty(name, out var v) && v.TryGetInt32(out var n) ? n : 0;
      static string? Raw(JsonElement e, string name) => e.TryGetProperty(name, out var v) && v.ValueKind == JsonValueKind.Object ? v.GetRawText() : null;
    }

    private static string? NullIfEmpty(string? value) => string.IsNullOrWhiteSpace(value) ? null : value;

    /// <summary>Minimal RFC 4180 reader: quoted fields, doubled quotes, commas and line breaks inside quotes.</summary>
    private static List<List<string>> ParseCsv(string text)
    {
      var rows = new List<List<string>>();
      var row = new List<string>();
      var field = new StringBuilder();
      var quoted = false;

      for (var i = 0; i < text.Length; i++)
      {
        var ch = text[i];
        if (quoted)
        {
          if (ch == '"' && i + 1 < text.Length && text[i + 1] == '"') { field.Append('"'); i++; }
          else if (ch == '"') quoted = false;
          else field.Append(ch);
          continue;
        }

        switch (ch)
        {
          case '"': quoted = true; break;
          case ',': row.Add(field.ToString()); field.Clear(); break;
          case '\r': break;
          case '\n':
            row.Add(field.ToString()); field.Clear();
            rows.Add(row); row = [];
            break;
          case '﻿' when i == 0: break;
          default: field.Append(ch); break;
        }
      }

      if (field.Length > 0 || row.Count > 0)
      {
        row.Add(field.ToString());
        rows.Add(row);
      }

      return rows;
    }

    // ---------------------------------------------------------------------------------------------------------
    // Database
    // ---------------------------------------------------------------------------------------------------------

    private async Task<SqlConnection> OpenAsync(CancellationToken cancellationToken)
    {
      var connection = new SqlConnection(settings.ConnectionString);
      await connection.OpenAsync(cancellationToken);
      return connection;
    }

    private async Task<bool> SchemaExistsAsync(CancellationToken cancellationToken)
    {
      const string sql = """
        SELECT CASE WHEN OBJECT_ID(N'dbo.term', N'U') IS NOT NULL
                     AND OBJECT_ID(N'dbo.article_term', N'U') IS NOT NULL
                     AND COL_LENGTH(N'dbo.article', N'text_source') IS NOT NULL
                    THEN 1 ELSE 0 END;
        """;

      await using var connection = await OpenAsync(cancellationToken);
      await using var command = new SqlCommand(sql, connection);
      return (int)(await command.ExecuteScalarAsync(cancellationToken))! == 1;
    }

    private async Task<Dictionary<string, int>> GetArticleIdsAsync(CancellationToken cancellationToken)
    {
      await using var connection = await OpenAsync(cancellationToken);
      await using var command = new SqlCommand("SELECT article_code, article_id FROM dbo.article;", connection);
      await using var reader = await command.ExecuteReaderAsync(cancellationToken);

      var ids = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
      while (await reader.ReadAsync(cancellationToken))
        ids[reader.GetString(0)] = reader.GetInt32(1);
      return ids;
    }

    private async Task<HashSet<string>> GetExistingCuisAsync(CancellationToken cancellationToken)
    {
      await using var connection = await OpenAsync(cancellationToken);
      await using var command = new SqlCommand("SELECT cui FROM dbo.term;", connection);
      await using var reader = await command.ExecuteReaderAsync(cancellationToken);

      var cuis = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
      while (await reader.ReadAsync(cancellationToken))
        cuis.Add(reader.GetString(0));
      return cuis;
    }

    /// <summary>
    /// One transaction: merge dbo.term, then for every loaded article replace its dbo.article_term rows and set
    /// dbo.article.text_source. Rows go through temp tables with SqlBulkCopy.
    /// </summary>
    private async Task WriteAsync(
      List<TermRow> terms, List<TermFile> files, Dictionary<string, int> articleIds, CancellationToken cancellationToken)
    {
      await using var connection = await OpenAsync(cancellationToken);
      await using var transaction = (SqlTransaction)await connection.BeginTransactionAsync(cancellationToken);

      async Task Exec(string sql)
      {
        await using var command = new SqlCommand(sql, connection, transaction) { CommandTimeout = 300 };
        await command.ExecuteNonQueryAsync(cancellationToken);
      }

      await Exec("""
        CREATE TABLE #term (cui VARCHAR(10) NOT NULL PRIMARY KEY, concept NVARCHAR(200) NOT NULL, semantic_type NVARCHAR(100) NULL,
                            display_name NVARCHAR(200) NULL, hidden BIT NOT NULL, note NVARCHAR(400) NULL);
        CREATE TABLE #article (article_id INT NOT NULL PRIMARY KEY, text_source VARCHAR(20) NULL);
        CREATE TABLE #article_term (article_id INT NOT NULL, cui VARCHAR(10) NOT NULL, mentions INT NOT NULL, mentions_affirmed INT NOT NULL,
                                    mentions_negated INT NOT NULL, studied BIT NOT NULL, sections NVARCHAR(MAX) NULL, forms NVARCHAR(MAX) NULL,
                                    best_score DECIMAL(4,3) NULL, PRIMARY KEY (article_id, cui));
        """);

      var termTable = new DataTable();
      termTable.Columns.Add("cui", typeof(string));
      termTable.Columns.Add("concept", typeof(string));
      termTable.Columns.Add("semantic_type", typeof(string));
      termTable.Columns.Add("display_name", typeof(string));
      termTable.Columns.Add("hidden", typeof(bool));
      termTable.Columns.Add("note", typeof(string));
      foreach (var t in terms)
        termTable.Rows.Add(t.Cui, t.Concept, (object?)t.SemanticType ?? DBNull.Value, (object?)t.DisplayName ?? DBNull.Value, t.Hidden, (object?)t.Note ?? DBNull.Value);

      var articleTable = new DataTable();
      articleTable.Columns.Add("article_id", typeof(int));
      articleTable.Columns.Add("text_source", typeof(string));

      var articleTermTable = new DataTable();
      articleTermTable.Columns.Add("article_id", typeof(int));
      articleTermTable.Columns.Add("cui", typeof(string));
      articleTermTable.Columns.Add("mentions", typeof(int));
      articleTermTable.Columns.Add("mentions_affirmed", typeof(int));
      articleTermTable.Columns.Add("mentions_negated", typeof(int));
      articleTermTable.Columns.Add("studied", typeof(bool));
      articleTermTable.Columns.Add("sections", typeof(string));
      articleTermTable.Columns.Add("forms", typeof(string));
      articleTermTable.Columns.Add("best_score", typeof(decimal));

      foreach (var file in files)
      {
        var articleId = articleIds[file.Code];
        articleTable.Rows.Add(articleId, (object?)file.SourceFormat ?? DBNull.Value);

        // Decision 3: a term with only negated mentions is not a term of this article.
        foreach (var t in file.Terms.Where(t => t.MentionsAffirmed > 0))
          articleTermTable.Rows.Add(articleId, t.Cui, t.Mentions, t.MentionsAffirmed, t.MentionsNegated, t.Studied,
            (object?)t.SectionsJson ?? DBNull.Value, (object?)t.FormsJson ?? DBNull.Value, (object?)t.BestScore ?? DBNull.Value);
      }

      async Task Bulk(string table, DataTable data)
      {
        using var bulk = new SqlBulkCopy(connection, SqlBulkCopyOptions.Default, transaction) { DestinationTableName = table, BulkCopyTimeout = 300 };
        foreach (DataColumn column in data.Columns)
          bulk.ColumnMappings.Add(column.ColumnName, column.ColumnName);
        await bulk.WriteToServerAsync(data, cancellationToken);
      }

      await Bulk("#term", termTable);
      await Bulk("#article", articleTable);
      await Bulk("#article_term", articleTermTable);

      await Exec("""
        MERGE dbo.term WITH (HOLDLOCK) AS t
        USING #term AS s ON t.cui = s.cui
        WHEN MATCHED AND (t.concept <> s.concept
                          OR ISNULL(t.semantic_type, N'') <> ISNULL(s.semantic_type, N'')
                          OR ISNULL(t.display_name, N'') <> ISNULL(s.display_name, N'')
                          OR t.hidden <> s.hidden
                          OR ISNULL(t.note, N'') <> ISNULL(s.note, N'')) THEN
          UPDATE SET concept = s.concept, semantic_type = s.semantic_type, display_name = s.display_name, hidden = s.hidden, note = s.note
        WHEN NOT MATCHED BY TARGET THEN
          INSERT (cui, concept, semantic_type, display_name, hidden, note)
          VALUES (s.cui, s.concept, s.semantic_type, s.display_name, s.hidden, s.note);

        DELETE at
        FROM dbo.article_term AS at
        JOIN #article AS a ON a.article_id = at.article_id;

        INSERT INTO dbo.article_term (article_id, term_id, mentions, mentions_affirmed, mentions_negated, studied, sections, forms, best_score)
        SELECT s.article_id, t.term_id, s.mentions, s.mentions_affirmed, s.mentions_negated, s.studied, s.sections, s.forms, s.best_score
        FROM #article_term AS s
        JOIN dbo.term AS t ON t.cui = s.cui;

        UPDATE a SET text_source = s.text_source
        FROM dbo.article AS a
        JOIN #article AS s ON s.article_id = a.article_id;
        """);

      await transaction.CommitAsync(cancellationToken);
    }

    // ---------------------------------------------------------------------------------------------------------
    // Report
    // ---------------------------------------------------------------------------------------------------------

    private void PrintReport(TermCounts counts, bool dryRun = false)
    {
      Out.WriteLine();
      Out.WriteLine(dryRun ? "Terms dry run (nothing written)" : "Terms load summary");

      static void Row(string label, int value) => Out.WriteLine($"  {(label + ":").PadRight(34)}{value}");

      Row("Term files read", counts.Files);
      Row("Excluded by settings", counts.Excluded);
      Row(dryRun ? "Articles to load" : "Articles loaded", counts.Articles);
      Row("  of which abstract-only", counts.AbstractOnly);
      Row("CB articles with a term", counts.CanineWithTerms);
      Row("  of which abstract-only", counts.CanineAbstractOnly);
      Row("Terms (CUIs)", counts.Terms);
      Row(dryRun ? "  new terms to insert" : "  new terms inserted", counts.NewTerms);
      Row("  hidden by term_display.csv", counts.Hidden);
      Row("  display names (merged/renamed)", counts.DisplayNames);
      Row(dryRun ? "Article-term rows to write" : "Article-term rows written", counts.ArticleTerms);
      Row("  of which studied", counts.Studied);
      Row("Negated-only terms skipped", counts.NegatedOnly);
      Row("Articles with no term file", counts.ArticlesWithoutTermFile.Count);
      if (counts.ArticlesWithoutTermFile.Count > 0)
        Out.WriteLine($"    {string.Join(", ", counts.ArticlesWithoutTermFile)}");

      PrintList("Warnings", _warnings);
      PrintList("Errors", _errors);
    }

    private static void PrintList(string title, List<string> lines)
    {
      if (lines.Count == 0)
        return;
      Out.WriteLine();
      Out.WriteLine($"{title} ({lines.Count}):");
      foreach (var line in lines)
        Out.WriteLine($"  - {line}");
    }

    private sealed class TermCounts
    {
      public int Files { get; set; }
      public int Excluded { get; set; }
      public int Articles { get; set; }
      public int AbstractOnly { get; set; }
      public int CanineWithTerms { get; set; }
      public int CanineAbstractOnly { get; set; }
      public int Terms { get; set; }
      public int NewTerms { get; set; }
      public int Hidden { get; set; }
      public int DisplayNames { get; set; }
      public int ArticleTerms { get; set; }
      public int Studied { get; set; }
      public int NegatedOnly { get; set; }
      public List<string> ArticlesWithoutTermFile { get; set; } = [];
    }
  }
}
