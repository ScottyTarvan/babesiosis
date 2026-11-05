using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace Babesiosis.Console.Source
{
  /// <summary>One article's own text (data/markdown/&lt;ID&gt;.md or &lt;ID&gt;.en.md), split into passages.</summary>
  internal sealed class ArticleText
  {
    public required string Code { get; init; }
    /// <summary>Path relative to the review root, with forward slashes, e.g. data/markdown/CB058.en.md.</summary>
    public required string File { get; init; }
    public required string Title { get; init; }
    /// <summary>abstract, jats_xml or pdf (front matter source_format).</summary>
    public required string? SourceFormat { get; init; }
    /// <summary>ok, review, abstract_only or no_text (front matter quality).</summary>
    public required string? Quality { get; init; }
    public required IReadOnlyList<string> QualityFlags { get; init; }
    /// <summary>Language of the paper itself, e.g. en or tr.</summary>
    public required string? Language { get; init; }
    /// <summary>True when the passages come from the English translation file.</summary>
    public required bool Translated { get; init; }
    public required int WordCount { get; init; }
    public required IReadOnlyList<Passage> Passages { get; init; }
    /// <summary>SHA-256 of the embedding model, the file name and every passage's embedding text.</summary>
    public required byte[] ContentHash { get; init; }
    public List<string> Warnings { get; } = [];

    /// <summary>Full text (XML or PDF) that produced usable passages, as opposed to an abstract or nothing.</summary>
    public bool HasFullText =>
      SourceFormat is SectionSource.FormatJats or SectionSource.FormatPdf
      && Quality != SectionSource.QualityNoText
      && Passages.Count > 0;
  }

  /// <param name="Order">Reading order within the article, from 1.</param>
  /// <param name="Kind">Normalised section kind: abstract, introduction, methods, results, ...</param>
  /// <param name="Heading">"Results" or "Results &gt; Pooled prevalence"; null when the text has no headings.</param>
  /// <param name="ChunkIndex">1-based part number within the H2 section.</param>
  /// <param name="ChunkCount">Parts in the H2 section; set once the section is complete.</param>
  /// <param name="EmbeddingText">Title, heading and body: what the vector is generated from.</param>
  internal sealed record Passage(
    int Order, string Kind, string? Heading, int ChunkIndex, int ChunkCount, string Body, int WordCount, string EmbeddingText);

  /// <summary>
  /// Reads the converted Markdown files written by core/scripts/to_markdown.py and splits each
  /// into passages for dbo.article_section. English translations (&lt;ID&gt;.en.md) are preferred
  /// over the original when both exist.
  ///
  /// Passages follow the H2 sections of the file. A section is one passage when it is short,
  /// and is split at H3 and paragraph boundaries into parts of about <see cref="TargetWords"/>
  /// words when it is long, so that one passage fits comfortably in a tool result and embeds
  /// well. Front matter, the H1 title line and very short fragments are dropped.
  /// </summary>
  internal static partial class SectionSource
  {
    public const string FormatAbstract = "abstract";
    public const string FormatJats = "jats_xml";
    public const string FormatPdf = "pdf";
    public const string QualityNoText = "no_text";

    /// <summary>Preferred passage size; a passage is flushed once adding the next block would pass this.</summary>
    public const int TargetWords = 500;
    /// <summary>A single block longer than this is split at paragraph breaks.</summary>
    public const int MaxBlockWords = 800;
    /// <summary>A passage is not flushed before it reaches this, so headings do not leave crumbs behind.</summary>
    private const int MinFlushWords = 120;
    /// <summary>Passages shorter than this ("Not applicable.") are dropped.</summary>
    private const int MinPassageWords = 20;
    /// <summary>Text before the first H2 (authors, affiliations) is kept only when it is this long.</summary>
    private const int MinPreambleWords = 150;

    /// <summary>
    /// Loads the text of every article whose code <paramref name="wanted"/> accepts. Files that
    /// cannot be read are reported in <paramref name="errors"/> and skipped.
    /// </summary>
    public static List<ArticleText> Load(string reviewRoot, string embeddingModel, Func<string, bool> wanted, List<string> errors)
    {
      var folder = Path.Combine(reviewRoot, "data", "markdown");
      var items = new List<ArticleText>();
      if (!Directory.Exists(folder))
      {
        errors.Add($"Folder {folder} not found. Run scripts/to_markdown.py first.");
        return items;
      }

      foreach (var path in Directory.EnumerateFiles(folder, "*.md").Order(StringComparer.OrdinalIgnoreCase))
      {
        var name = Path.GetFileName(path);
        if (name.EndsWith(".en.md", StringComparison.OrdinalIgnoreCase))
          continue; // picked up through its original below

        var code = Path.GetFileNameWithoutExtension(name);
        if (!wanted(code))
          continue;

        var translation = Path.Combine(folder, code + ".en.md");
        var chosen = System.IO.File.Exists(translation) ? translation : path;

        try
        {
          items.Add(Parse(reviewRoot, chosen, code, embeddingModel));
        }
        catch (Exception ex) when (ex is IOException or InvalidDataException or JsonException)
        {
          errors.Add($"{code}: cannot read {Path.GetFileName(chosen)} ({ex.Message}); skipped");
        }
      }

      return items;
    }

    public static ArticleText Parse(string reviewRoot, string path, string code, string embeddingModel)
    {
      var text = System.IO.File.ReadAllText(path, Encoding.UTF8);
      var (front, body) = SplitFrontMatter(text);
      var warnings = new List<string>();

      var id = Str(front, "id");
      if (id is not null && !id.Equals(code, StringComparison.OrdinalIgnoreCase))
        warnings.Add($"front matter id '{id}' differs from the file name");

      var translated = front.ContainsKey("translation_of") || front.ContainsKey("translated_from");
      var language = translated ? Str(front, "translated_from") ?? "unknown" : Str(front, "language");
      var title = Str(front, "title") ?? code;

      var passages = BuildPassages(body, title, warnings);

      var hash = new StringBuilder().Append(embeddingModel).Append('\n').Append(Path.GetFileName(path)).Append('\n');
      foreach (var passage in passages)
        hash.Append(passage.EmbeddingText).Append('\n');

      var item = new ArticleText
      {
        Code = code,
        File = Path.GetRelativePath(reviewRoot, path).Replace('\\', '/'),
        Title = title,
        SourceFormat = Str(front, "source_format"),
        Quality = Str(front, "quality"),
        QualityFlags = List(front, "quality_flags"),
        Language = language,
        Translated = translated,
        WordCount = passages.Sum(p => p.WordCount),
        Passages = passages,
        ContentHash = SHA256.HashData(Encoding.UTF8.GetBytes(hash.ToString()))
      };
      item.Warnings.AddRange(warnings);
      return item;
    }

    // ---------------------------------------------------------------------------------------------------------
    // Front matter: "key: value" lines between the first two "---" lines; values are JSON scalars or arrays.
    // ---------------------------------------------------------------------------------------------------------

    private static (Dictionary<string, JsonElement?> Front, string Body) SplitFrontMatter(string text)
    {
      var front = new Dictionary<string, JsonElement?>(StringComparer.OrdinalIgnoreCase);
      var lines = text.Split('\n');
      var i = 0;
      if (lines.Length == 0 || lines[0].TrimEnd('\r').Trim() != "---")
        throw new InvalidDataException("the file does not start with YAML front matter");

      for (i = 1; i < lines.Length; i++)
      {
        var line = lines[i].TrimEnd('\r');
        if (line.Trim() == "---")
        {
          i++;
          break;
        }

        var colon = line.IndexOf(':');
        if (colon <= 0 || line[0] == ' ')
          continue;

        var key = line[..colon].Trim();
        var raw = line[(colon + 1)..].Trim();
        front[key] = ParseScalar(raw);
      }

      if (i >= lines.Length)
        throw new InvalidDataException("the front matter is not closed");

      return (front, string.Join('\n', lines, i, lines.Length - i));
    }

    private static JsonElement? ParseScalar(string raw)
    {
      if (raw.Length == 0)
        return null;
      try
      {
        using var doc = JsonDocument.Parse(raw);
        return doc.RootElement.ValueKind == JsonValueKind.Null ? null : doc.RootElement.Clone();
      }
      catch (JsonException)
      {
        // Unquoted YAML scalar: keep it as a string.
        using var doc = JsonDocument.Parse(JsonSerializer.Serialize(raw));
        return doc.RootElement.Clone();
      }
    }

    private static string? Str(Dictionary<string, JsonElement?> front, string key) =>
      front.TryGetValue(key, out var e) && e is { } v
        ? v.ValueKind == JsonValueKind.String ? v.GetString() : v.GetRawText()
        : null;

    private static IReadOnlyList<string> List(Dictionary<string, JsonElement?> front, string key) =>
      front.TryGetValue(key, out var e) && e is { ValueKind: JsonValueKind.Array } v
        ? v.EnumerateArray().Select(x => x.ValueKind == JsonValueKind.String ? x.GetString()! : x.GetRawText()).ToList()
        : [];

    // ---------------------------------------------------------------------------------------------------------
    // Body: blocks under H2/H3 headings, then passages
    // ---------------------------------------------------------------------------------------------------------

    /// <summary>A run of text under one heading path.</summary>
    private sealed record Block(string Kind, string? Heading2, string? Heading3, string Text, int Words)
    {
      public string? Heading => Heading2 is null ? Heading3 : Heading3 is null ? Heading2 : $"{Heading2} > {Heading3}";
    }

    private static List<Passage> BuildPassages(string body, string title, List<string> warnings)
    {
      var blocks = ReadBlocks(body);
      var passages = new List<Passage>();

      // Text before the first H2 is usually the author list; keep it only when it is substantial.
      var preamble = blocks.TakeWhile(b => b.Heading2 is null).ToList();
      var sectioned = blocks.Skip(preamble.Count).ToList();
      if (sectioned.Count == 0)
      {
        // No H2 headings at all (no_sections_detected): the whole text is one "body" section.
        sectioned = preamble.Select(b => b with { Kind = "body" }).ToList();
        preamble = [];
      }
      else if (preamble.Sum(b => b.Words) >= MinPreambleWords)
      {
        sectioned.InsertRange(0, preamble.Select(b => b with { Kind = "other", Heading2 = "Preamble", Heading3 = b.Heading3 }));
      }

      foreach (var section in GroupBySection(sectioned))
      {
        var parts = new List<(string? Heading, StringBuilder Text, int Words)>();
        (string? Heading, StringBuilder Text, int Words)? current = null;

        void Flush()
        {
          if (current is { } c && c.Words > 0)
            parts.Add(c);
          current = null;
        }

        foreach (var block in section)
        {
          foreach (var (text, words) in SplitLong(block.Text, block.Words))
          {
            if (current is { } c && c.Words + words > TargetWords && c.Words >= MinFlushWords)
              Flush();

            if (current is null)
              current = (block.Heading, new StringBuilder(), 0);

            var cur = current.Value;
            if (cur.Text.Length > 0)
              cur.Text.Append("\n\n");
            // Keep the subsection title inside the text when a passage spans more than one subsection.
            if (cur.Text.Length > 0 && block.Heading3 is not null && !string.Equals(cur.Heading, block.Heading, StringComparison.Ordinal))
              cur.Text.Append("### ").Append(block.Heading3).Append("\n\n");
            cur.Text.Append(text);
            current = (cur.Heading, cur.Text, cur.Words + words);
          }
        }
        Flush();

        var kept = parts.Where(p => p.Words >= MinPassageWords).ToList();
        for (var i = 0; i < kept.Count; i++)
        {
          var (heading, text, words) = kept[i];
          var bodyText = text.ToString().Trim();
          var embeddingText = heading is null ? $"{title}\n\n{bodyText}" : $"{title}\n{heading}\n\n{bodyText}";
          passages.Add(new Passage(
            Order: passages.Count + 1,
            Kind: section[0].Kind,
            Heading: heading,
            ChunkIndex: i + 1,
            ChunkCount: kept.Count,
            Body: bodyText,
            WordCount: words,
            EmbeddingText: embeddingText));
        }
      }

      if (passages.Count == 0 && blocks.Sum(b => b.Words) > 0)
        warnings.Add("text too short to keep any passage");

      return passages;
    }

    /// <summary>Consecutive blocks that share an H2 heading (or all have none).</summary>
    private static IEnumerable<List<Block>> GroupBySection(List<Block> blocks)
    {
      var group = new List<Block>();
      foreach (var block in blocks)
      {
        if (group.Count > 0 && !string.Equals(group[0].Heading2, block.Heading2, StringComparison.Ordinal))
        {
          yield return group;
          group = [];
        }
        group.Add(block);
      }
      if (group.Count > 0)
        yield return group;
    }

    private static List<Block> ReadBlocks(string body)
    {
      var blocks = new List<Block>();
      string? h2 = null, h3 = null;
      var kind = "other";
      var text = new StringBuilder();
      var seenTitle = false;

      void Flush()
      {
        var t = text.ToString().Trim();
        if (t.Length > 0)
          blocks.Add(new Block(kind, h2, h3, t, CountWords(t)));
        text.Clear();
      }

      foreach (var rawLine in body.Split('\n'))
      {
        var line = rawLine.TrimEnd('\r');
        var heading = HeadingLine().Match(line);
        if (heading.Success)
        {
          var level = heading.Groups[1].Value.Length;
          var name = CleanHeading(heading.Groups[2].Value);

          if (level == 1 && !seenTitle)
          {
            seenTitle = true; // the article title, already in the front matter
            continue;
          }

          Flush();
          if (level <= 2)
          {
            h2 = name;
            h3 = null;
            kind = Classify(name);
          }
          else
          {
            h3 = name;
          }
          continue;
        }

        text.Append(line).Append('\n');
      }
      Flush();

      return blocks;
    }

    /// <summary>Splits a block longer than <see cref="MaxBlockWords"/> at paragraph, then line, then word boundaries.</summary>
    private static IEnumerable<(string Text, int Words)> SplitLong(string text, int words)
    {
      if (words <= MaxBlockWords)
      {
        yield return (text, words);
        yield break;
      }

      var current = new StringBuilder();
      var currentWords = 0;
      foreach (var paragraph in text.Split("\n\n", StringSplitOptions.RemoveEmptyEntries))
      {
        var paragraphWords = CountWords(paragraph);
        if (paragraphWords > MaxBlockWords)
        {
          if (currentWords > 0)
          {
            yield return (current.ToString().Trim(), currentWords);
            current.Clear();
            currentWords = 0;
          }
          foreach (var piece in SplitHard(paragraph))
            yield return piece;
          continue;
        }

        if (currentWords + paragraphWords > TargetWords && currentWords > 0)
        {
          yield return (current.ToString().Trim(), currentWords);
          current.Clear();
          currentWords = 0;
        }

        if (current.Length > 0)
          current.Append("\n\n");
        current.Append(paragraph.Trim());
        currentWords += paragraphWords;
      }

      if (currentWords > 0)
        yield return (current.ToString().Trim(), currentWords);
    }

    /// <summary>A single paragraph (or table) over the limit: split by lines, then by words.</summary>
    private static IEnumerable<(string Text, int Words)> SplitHard(string paragraph)
    {
      var current = new StringBuilder();
      var currentWords = 0;
      foreach (var line in paragraph.Split('\n'))
      {
        var lineWords = CountWords(line);
        if (lineWords > MaxBlockWords)
        {
          if (currentWords > 0)
          {
            yield return (current.ToString().Trim(), currentWords);
            current.Clear();
            currentWords = 0;
          }
          var tokens = line.Split(' ', StringSplitOptions.RemoveEmptyEntries);
          foreach (var chunk in tokens.Chunk(TargetWords))
            yield return (string.Join(' ', chunk), chunk.Length);
          continue;
        }

        if (currentWords + lineWords > TargetWords && currentWords > 0)
        {
          yield return (current.ToString().Trim(), currentWords);
          current.Clear();
          currentWords = 0;
        }
        current.Append(line).Append('\n');
        currentWords += lineWords;
      }

      if (currentWords > 0)
        yield return (current.ToString().Trim(), currentWords);
    }

    /// <summary>Maps a heading to a section kind. Unrecognised headings (topical review headings) are "other".</summary>
    public static string Classify(string heading)
    {
      var h = heading.ToLowerInvariant().Trim();
      if (h.Length == 0) return "other";
      if (h.Contains("results") && h.Contains("discussion")) return "results_discussion";
      if (h is "abstract" or "summary" or "structured abstract") return "abstract";
      if (h.StartsWith("introduction") || h is "background") return "introduction";
      if (h.Contains("method") || h.Contains("materials") || h.Contains("experimental design") || h.Contains("study design")
          || h.StartsWith("animals") || h.StartsWith("patients")) return "methods";
      if (h.StartsWith("result") || h.StartsWith("findings")) return "results";
      if (h.StartsWith("discussion")) return "discussion";
      if (h.StartsWith("conclusion") || h.StartsWith("concluding")) return "conclusion";
      if (h.StartsWith("case ") || h is "case" || h.StartsWith("clinical case") || h.StartsWith("case report")) return "case";
      if (h.StartsWith("limitation")) return "limitations";
      if (h.StartsWith("abbreviation") || h.StartsWith("list of abbreviations")) return "abbreviations";
      return "other";
    }

    /// <summary>Drops list numbering, Markdown emphasis and trailing punctuation from a heading.</summary>
    private static string CleanHeading(string heading)
    {
      var h = HeadingNumber().Replace(heading.Trim(), "");
      h = h.Replace("**", "").Replace("__", "").Trim().TrimEnd(':', '.').Trim();
      if (h.Length > 300)
        h = h[..300];
      return h;
    }

    public static int CountWords(string text)
    {
      var count = 0;
      var inWord = false;
      foreach (var ch in text)
      {
        if (char.IsWhiteSpace(ch))
          inWord = false;
        else if (!inWord)
        {
          inWord = true;
          count++;
        }
      }
      return count;
    }

    [GeneratedRegex(@"^(#{1,6})\s+(.*?)\s*#*\s*$")]
    private static partial Regex HeadingLine();

    [GeneratedRegex(@"^(?:(?:\d+(?:\.\d+)*\.?|[IVXLC]+\.|[A-Z]\.)\s+)")]
    private static partial Regex HeadingNumber();
  }
}
