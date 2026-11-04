using System.Text.RegularExpressions;

namespace Babesiosis.Console.Source
{
  /// <summary>Narrative sections taken from an article .md file.</summary>
  internal sealed record ArticleMarkdown(
    string? AbstractSummary,
    string? AuthorsConclusion,
    string? ReviewerInterpretation,
    string? KeyLimitations,
    string? Relevance,
    string? EvidenceBasis);

  /// <summary>
  /// Parses the article files. Each file has three "## " sections: "Abstract-derived summary",
  /// "Critical interpretation" (single-line "- **Label:** text" bullets) and "Evidence basis".
  /// </summary>
  internal static partial class MarkdownParser
  {
    private const string SummaryHeading = "Abstract-derived summary";
    private const string InterpretationHeading = "Critical interpretation";
    private const string EvidenceHeading = "Evidence basis";

    [GeneratedRegex(@"^- \*\*(?<label>[^*]+):\*\*\s*(?<text>.*)$")]
    private static partial Regex BulletRegex();

    public static ArticleMarkdown Parse(string markdown, List<string> warnings)
    {
      var sections = SplitSections(markdown);

      foreach (var heading in new[] { SummaryHeading, InterpretationHeading, EvidenceHeading })
      {
        if (!sections.ContainsKey(heading))
          warnings.Add($"missing section '## {heading}'");
      }

      var bullets = sections.TryGetValue(InterpretationHeading, out var interpretation)
        ? ParseBullets(interpretation)
        : new Dictionary<string, string>();

      return new ArticleMarkdown(
        AbstractSummary: sections.GetValueOrDefault(SummaryHeading),
        AuthorsConclusion: bullets.GetValueOrDefault("Authors' conclusion"),
        ReviewerInterpretation: bullets.GetValueOrDefault("Reviewer interpretation"),
        KeyLimitations: bullets.GetValueOrDefault("Key limitations (from available information)")
          ?? bullets.GetValueOrDefault("Key limitations"),
        Relevance: bullets.GetValueOrDefault("Relevance to canine babesiosis")
          ?? bullets.GetValueOrDefault("Relevance"),
        EvidenceBasis: sections.GetValueOrDefault(EvidenceHeading));
    }

    /// <summary>Maps each "## " heading to its trimmed body text.</summary>
    private static Dictionary<string, string> SplitSections(string markdown)
    {
      var sections = new Dictionary<string, string>();
      string? heading = null;
      var body = new List<string>();

      void Flush()
      {
        if (heading is not null)
          sections[heading] = string.Join('\n', body).Trim();
      }

      foreach (var line in markdown.Replace("\r\n", "\n").Split('\n'))
      {
        if (line.StartsWith("## ", StringComparison.Ordinal))
        {
          Flush();
          heading = line[3..].Trim();
          body.Clear();
        }
        else if (heading is not null)
        {
          body.Add(line);
        }
      }

      Flush();
      return sections;
    }

    private static Dictionary<string, string> ParseBullets(string section)
    {
      var bullets = new Dictionary<string, string>();
      foreach (var line in section.Split('\n'))
      {
        var match = BulletRegex().Match(line.TrimEnd());
        if (match.Success)
          bullets.TryAdd(match.Groups["label"].Value.Trim(), match.Groups["text"].Value.Trim());
      }
      return bullets;
    }
  }
}
