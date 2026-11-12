using System.Data;
using System.Text;
using System.Text.RegularExpressions;
using Microsoft.Data.SqlClient;
using Out = System.Console;

namespace Babesiosis.Console
{
  /// <summary>
  /// Loads the narrative syntheses in core/search/synthesis into dbo.synthesis_section, split by
  /// heading, with the text kept as written (Markdown). Reads the eleven category files
  /// (&lt;CODE&gt;.md), CROSS.md and QUESTIONS.md; the *_secondary_digest.md working files are not
  /// loaded. Touches no other table. One transaction per document: its rows are replaced.
  ///
  /// Splitting rules:
  ///   - category file: the "### CODE — Name" title line is dropped; each line that is only a bold
  ///     phrase ("**Evidence base**") starts a section.
  ///   - CROSS.md: the text before the first theme is the "intro" section; each paragraph that
  ///     starts "**N. Title.**" starts section theme-N, its heading the title and its body the rest.
  ///   - QUESTIONS.md: the text before the first "## " heading is the "intro" section; each "## "
  ///     heading starts a section ("## Q1. …" is key q1 with the heading after "Q1. ").
  /// </summary>
  internal sealed partial class SynthesisLoader(LoaderSettings settings, LoaderOptions options)
  {
    private static readonly string[] CategoryCodes =
      ["ERY", "INF", "END", "COA", "REN", "PUL", "NEU", "CAR", "MET", "OXO", "SEV"];

    private readonly List<string> _errors = [];
    private readonly List<string> _warnings = [];

    internal sealed record Section(string Key, string Heading, string Body);

    public async Task<int> RunAsync(CancellationToken cancellationToken)
    {
      var folder = Path.Combine(settings.ReviewRoot, "search", "synthesis");
      Out.WriteLine();
      Out.WriteLine($"Reading syntheses from {folder}");

      if (!Directory.Exists(folder))
      {
        _warnings.Add($"Folder {folder} not found. Nothing loaded.");
        PrintReport(0, 0);
        return 0;
      }

      var documents = CategoryCodes.Select(code => (Code: code, File: $"{code}.md", Split: (Func<string, List<Section>>)SplitCategory))
        .Append(("CROSS", "CROSS.md", SplitCross))
        .Append(("QUESTIONS", "QUESTIONS.md", SplitQuestions));

      int loaded = 0, sections = 0;
      foreach (var (code, fileName, split) in documents)
      {
        cancellationToken.ThrowIfCancellationRequested();
        if (options.Only is not null && !options.Only.Contains(code))
          continue;

        var path = Path.Combine(folder, fileName);
        if (!File.Exists(path))
        {
          _warnings.Add($"{fileName} not found; its rows are left as they are.");
          continue;
        }

        List<Section> parts;
        try
        {
          parts = split(File.ReadAllText(path, Encoding.UTF8));
          if (parts.Count == 0)
            throw new InvalidDataException("no sections found");
          var duplicate = parts.GroupBy(p => p.Key).FirstOrDefault(g => g.Count() > 1);
          if (duplicate is not null)
            throw new InvalidDataException($"section key '{duplicate.Key}' appears twice");
        }
        catch (InvalidDataException ex)
        {
          _errors.Add($"{fileName}: {ex.Message}");
          continue;
        }

        Out.WriteLine($"  {code}: {parts.Count} sections ({string.Join(", ", parts.Select(p => p.Key))})");
        loaded++;
        sections += parts.Count;

        if (options.DryRun)
          continue;

        try
        {
          await WriteAsync(code, $"search/synthesis/{fileName}", File.GetLastWriteTimeUtc(path), parts, cancellationToken);
        }
        catch (SqlException ex)
        {
          _errors.Add($"{code}: {ex.Message}");
        }
      }

      PrintReport(loaded, sections);
      return _errors.Count == 0 ? 0 : 1;
    }

    private async Task WriteAsync(string code, string sourceFile, DateTime modifiedUtc, List<Section> parts,
      CancellationToken cancellationToken)
    {
      await using var connection = new SqlConnection(settings.ConnectionString);
      await connection.OpenAsync(cancellationToken);
      await using var transaction = (SqlTransaction)await connection.BeginTransactionAsync(cancellationToken);

      await using (var delete = new SqlCommand("DELETE FROM dbo.synthesis_section WHERE document_code = @code;", connection, transaction))
      {
        delete.Parameters.Add("@code", SqlDbType.VarChar, 10).Value = code;
        await delete.ExecuteNonQueryAsync(cancellationToken);
      }

      const string insertSql = """
        INSERT INTO dbo.synthesis_section (document_code, section_order, section_key, heading, body, source_file, file_modified_at)
        VALUES (@code, @order, @key, @heading, @body, @file, @modified);
        """;
      for (var i = 0; i < parts.Count; i++)
      {
        await using var insert = new SqlCommand(insertSql, connection, transaction);
        insert.Parameters.Add("@code", SqlDbType.VarChar, 10).Value = code;
        insert.Parameters.Add("@order", SqlDbType.SmallInt).Value = (short)(i + 1);
        insert.Parameters.Add("@key", SqlDbType.VarChar, 60).Value = parts[i].Key;
        insert.Parameters.Add("@heading", SqlDbType.NVarChar, 400).Value = parts[i].Heading;
        insert.Parameters.Add("@body", SqlDbType.NVarChar, -1).Value = parts[i].Body;
        insert.Parameters.Add("@file", SqlDbType.NVarChar, 200).Value = sourceFile;
        insert.Parameters.Add("@modified", SqlDbType.DateTime2).Value = new DateTime(modifiedUtc.Ticks - modifiedUtc.Ticks % TimeSpan.TicksPerSecond, DateTimeKind.Utc);
        await insert.ExecuteNonQueryAsync(cancellationToken);
      }

      await transaction.CommitAsync(cancellationToken);
    }

    // ---- Splitting ----------------------------------------------------------------------

    [GeneratedRegex(@"^\*\*([^*].*?)\*\*\s*$")]
    private static partial Regex BoldLine();

    [GeneratedRegex(@"^\*\*(\d+)\.\s+(.*?)\.?\*\*(?!\*)\s*(.*)$")]
    private static partial Regex NumberedTheme();

    [GeneratedRegex(@"^##\s+(.+?)\s*$")]
    private static partial Regex H2();

    [GeneratedRegex(@"^Q(\d+)\.\s+(.+)$")]
    private static partial Regex QuestionHeading();

    [GeneratedRegex(@"[^a-z0-9]+")]
    private static partial Regex NonSlug();

    internal static List<Section> SplitCategory(string text)
    {
      var lines = Lines(text);
      // Drop the "### CODE — Name" title; the category table holds the name.
      if (lines.Count > 0 && lines[0].StartsWith("#"))
        lines.RemoveAt(0);

      var result = new List<Section>();
      string? heading = null;
      var body = new List<string>();
      foreach (var line in lines)
      {
        var match = BoldLine().Match(line);
        if (match.Success)
        {
          Flush(result, heading, body, Slug);
          heading = match.Groups[1].Value.Trim();
          body.Clear();
        }
        else if (heading is not null)
        {
          body.Add(line);
        }
      }
      Flush(result, heading, body, Slug);
      return result;
    }

    internal static List<Section> SplitCross(string text)
    {
      var lines = Lines(text);
      var result = new List<Section>();
      var title = lines.Count > 0 && lines[0].StartsWith("# ") ? lines[0][2..].Trim() : "Cross-cutting themes";
      if (lines.Count > 0 && lines[0].StartsWith("# "))
        lines.RemoveAt(0);

      string key = "intro", heading = title;
      var body = new List<string>();
      foreach (var line in lines)
      {
        var match = NumberedTheme().Match(line);
        if (match.Success)
        {
          AddSection(result, key, heading, body);
          key = $"theme-{match.Groups[1].Value}";
          heading = match.Groups[2].Value.Trim();
          body.Clear();
          if (match.Groups[3].Value.Length > 0)
            body.Add(match.Groups[3].Value);
        }
        else
        {
          body.Add(line);
        }
      }
      AddSection(result, key, heading, body);
      return result;
    }

    internal static List<Section> SplitQuestions(string text)
    {
      var lines = Lines(text);
      var result = new List<Section>();
      var title = lines.Count > 0 && lines[0].StartsWith("# ") ? lines[0][2..].Trim() : "Candidate research questions";
      if (lines.Count > 0 && lines[0].StartsWith("# "))
        lines.RemoveAt(0);

      string key = "intro", heading = title;
      var body = new List<string>();
      foreach (var line in lines)
      {
        var match = H2().Match(line);
        if (match.Success)
        {
          AddSection(result, key, heading, body);
          var h = match.Groups[1].Value;
          var q = QuestionHeading().Match(h);
          key = q.Success ? $"q{q.Groups[1].Value}" : Slug(h);
          heading = q.Success ? q.Groups[2].Value.Trim() : h;
          body.Clear();
        }
        else
        {
          body.Add(line);
        }
      }
      AddSection(result, key, heading, body);
      return result;
    }

    private static List<string> Lines(string text) =>
      text.Replace("\r\n", "\n").Split('\n').ToList();

    private static void Flush(List<Section> result, string? heading, List<string> body, Func<string, string> keyOf)
    {
      if (heading is not null)
        AddSection(result, keyOf(heading), heading, body);
    }

    /// <summary>Adds a section with blank lines and horizontal rules trimmed from both ends of its body.</summary>
    private static void AddSection(List<Section> result, string key, string heading, List<string> body)
    {
      var lines = body.ToList();
      static bool Blank(string l) => string.IsNullOrWhiteSpace(l) || l.Trim() == "---";
      while (lines.Count > 0 && Blank(lines[0])) lines.RemoveAt(0);
      while (lines.Count > 0 && Blank(lines[^1])) lines.RemoveAt(lines.Count - 1);
      if (lines.Count == 0 && key == "intro")
        return;
      result.Add(new Section(key, heading, string.Join("\n", lines)));
    }

    /// <summary>"Question this direction asks" → "question-this-direction-asks".</summary>
    private static string Slug(string heading)
    {
      var slug = NonSlug().Replace(heading.ToLowerInvariant(), "-").Trim('-');
      return slug.Length > 60 ? slug[..60].TrimEnd('-') : slug;
    }

    private void PrintReport(int documents, int sections)
    {
      Out.WriteLine();
      Out.WriteLine("Synthesis load summary");
      Out.WriteLine($"  {"Documents:".PadRight(24)}{documents}");
      Out.WriteLine($"  {"Sections:".PadRight(24)}{sections}");
      if (options.DryRun)
        Out.WriteLine("  Dry run: nothing was written.");
      foreach (var warning in _warnings)
        Out.WriteLine($"  Warning: {warning}");
      foreach (var error in _errors)
        Out.Error.WriteLine($"  Error: {error}");
    }
  }
}
