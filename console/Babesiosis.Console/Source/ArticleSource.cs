using System.Globalization;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace Babesiosis.Console.Source
{
  /// <summary>An article ready to load: the JSONL record, its markdown and the text to embed.</summary>
  internal sealed class ArticleItem
  {
    public required ArticleRecord Record { get; init; }
    public required string SourceJson { get; init; }
    public required string Markdown { get; init; }
    public required ArticleMarkdown Sections { get; init; }
    public required string EmbeddingText { get; init; }
    public required byte[] ContentHash { get; init; }
    public List<string> Warnings { get; } = [];

    public string Code => Record.Id;
  }

  /// <summary>Reads articles.jsonl and the matching .md files from the review folder.</summary>
  internal static class ArticleSource
  {
    /// <summary>
    /// Loads every article. Records that cannot be read (bad JSON, missing .md file) are
    /// returned in <paramref name="errors"/> and skipped.
    /// </summary>
    public static List<ArticleItem> Load(string reviewRoot, string embeddingModel, List<string> errors)
    {
      var jsonlPath = Path.Combine(reviewRoot, "articles.jsonl");
      var items = new List<ArticleItem>();
      var lineNumber = 0;

      foreach (var line in File.ReadLines(jsonlPath, Encoding.UTF8))
      {
        lineNumber++;
        if (string.IsNullOrWhiteSpace(line))
          continue;

        ArticleRecord? record;
        try
        {
          record = JsonSerializer.Deserialize<ArticleRecord>(line, ArticleRecord.JsonOptions);
        }
        catch (JsonException ex)
        {
          errors.Add($"articles.jsonl line {lineNumber}: invalid JSON ({ex.Message})");
          continue;
        }

        if (record is null || string.IsNullOrWhiteSpace(record.Id))
        {
          errors.Add($"articles.jsonl line {lineNumber}: record has no id");
          continue;
        }

        var markdownPath = Path.Combine(reviewRoot, record.Filename.Replace('/', Path.DirectorySeparatorChar));
        if (!File.Exists(markdownPath))
        {
          errors.Add($"{record.Id}: article file not found ({record.Filename})");
          continue;
        }

        var markdown = File.ReadAllText(markdownPath, Encoding.UTF8);
        var warnings = new List<string>();
        var sections = MarkdownParser.Parse(markdown, warnings);
        var embeddingText = BuildEmbeddingText(record, sections);

        var item = new ArticleItem
        {
          Record = record,
          SourceJson = line,
          Markdown = markdown,
          Sections = sections,
          EmbeddingText = embeddingText,
          ContentHash = SHA256.HashData(Encoding.UTF8.GetBytes(embeddingModel + "\n" + embeddingText))
        };
        item.Warnings.AddRange(warnings);
        items.Add(item);
      }

      return items;
    }

    /// <summary>Findings and appraisal: the text the article's embedding is generated from.</summary>
    private static string BuildEmbeddingText(ArticleRecord record, ArticleMarkdown sections)
    {
      var text = new StringBuilder();

      void Append(string label, string? value)
      {
        if (!string.IsNullOrWhiteSpace(value))
          text.Append(label).Append(": ").AppendLine(value.Trim());
      }

      Append("Title", record.Title);
      Append("Finding", record.OneSentenceFinding);
      Append("Summary", sections.AbstractSummary);
      Append("Authors' conclusion", sections.AuthorsConclusion);
      Append("Interpretation", sections.ReviewerInterpretation);
      Append("Limitations", sections.KeyLimitations);
      Append("Relevance", sections.Relevance);

      return text.ToString().TrimEnd();
    }

    /// <summary>
    /// Parses first_pub_date ("YYYY", "YYYY-MM" or "YYYY-MM-DD") into the first day of the
    /// period and its precision: D, M or Y.
    /// </summary>
    public static (DateOnly? Date, char? Precision) ParsePublicationDate(string? value)
    {
      if (string.IsNullOrWhiteSpace(value))
        return (null, null);

      var formats = new (string Format, char Precision)[] { ("yyyy-MM-dd", 'D'), ("yyyy-MM", 'M'), ("yyyy", 'Y') };
      foreach (var (format, precision) in formats)
      {
        if (DateOnly.TryParseExact(value.Trim(), format, CultureInfo.InvariantCulture, DateTimeStyles.None, out var date))
          return (date, precision);
      }

      return (null, null);
    }

    public static DateOnly? ParseDate(string? value) =>
      DateOnly.TryParseExact(value?.Trim(), "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out var date)
        ? date
        : null;
  }
}
