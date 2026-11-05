using Babesiosis.Console.Data;
using Babesiosis.Console.Embedding;
using Babesiosis.Console.Source;
using Out = System.Console;

namespace Babesiosis.Console
{
  /// <summary>
  /// Loads each article's own text (data/markdown/&lt;ID&gt;.md, or the translation &lt;ID&gt;.en.md)
  /// into dbo.article_section as passages, embeds the passages, and sets the text columns on
  /// dbo.article. Runs after <see cref="ArticleLoader"/>: only articles already in dbo.article
  /// are loaded. An article is reloaded only when its passages change (text_hash), when some of
  /// its passages have no vector, or with --reembed.
  /// </summary>
  internal sealed class SectionLoader(LoaderSettings settings, LoaderOptions options)
  {
    private readonly List<string> _errors = [];
    private readonly List<string> _warnings = [];

    /// <summary>Runs the load and prints a report. Returns the process exit code.</summary>
    public async Task<int> RunAsync(CancellationToken cancellationToken)
    {
      var folder = Path.Combine(settings.ReviewRoot, "data", "markdown");
      Out.WriteLine();
      Out.WriteLine($"Reading article text from {folder}");

      var counts = new TextCounts();
      if (!Directory.Exists(folder))
      {
        _errors.Add($"Folder {folder} not found. Run scripts/to_markdown.py first.");
        PrintReport(counts, options.DryRun);
        return 1;
      }

      var repository = new SectionRepository(settings.ConnectionString, settings.Dimensions);
      var existing = new Dictionary<string, ExistingText>(StringComparer.OrdinalIgnoreCase);

      if (await repository.SchemaExistsAsync(cancellationToken))
      {
        existing = await repository.GetExistingAsync(cancellationToken);
      }
      else if (options.DryRun)
      {
        _warnings.Add("Table dbo.article_section not found: article rows and stored hashes were not checked. Run Database/schema.sql before a real load.");
      }
      else
      {
        _errors.Add("Table dbo.article_section (or the text columns on dbo.article) not found. Run Database/schema.sql first.");
        PrintReport(counts);
        return 1;
      }

      // Which files to read: every article in the database (retired and excluded IDs have files too), narrowed by --only.
      var fileCodes = Directory.EnumerateFiles(folder, "*.md")
        .Select(Path.GetFileName)
        .Where(n => !n!.EndsWith(".en.md", StringComparison.OrdinalIgnoreCase))
        .Select(n => Path.GetFileNameWithoutExtension(n)!)
        .ToHashSet(StringComparer.OrdinalIgnoreCase);
      counts.Files = fileCodes.Count;

      bool Wanted(string code) =>
        (options.Only is null || options.Only.Contains(code)) &&
        (existing.Count == 0 || existing.ContainsKey(code));

      counts.NoArticleRow = existing.Count == 0 ? 0 : fileCodes.Count(c => !existing.ContainsKey(c));
      counts.NoTextFile = existing.Keys.Where(c => !fileCodes.Contains(c) && (options.Only is null || options.Only.Contains(c))).Order().ToList();

      var items = SectionSource.Load(settings.ReviewRoot, settings.EmbeddingModel, Wanted, _errors);
      foreach (var item in items)
        _warnings.AddRange(item.Warnings.Select(w => $"{item.Code}: {w}"));

      counts.Translations = items.Count(i => i.Translated);
      counts.FullText = items.Count(i => i.HasFullText);
      counts.AbstractOnly = items.Count(i => !i.HasFullText && i.Passages.Count > 0);
      counts.NoText = items.Count(i => i.Passages.Count == 0);

      var plans = items.Select(item =>
      {
        var current = existing.GetValueOrDefault(item.Code);
        var hashChanged = current?.TextHash is null || !current.TextHash.AsSpan().SequenceEqual(item.ContentHash);
        var needsEmbedding = !options.SkipEmbeddings && item.Passages.Count > 0 &&
                             (options.Reembed || hashChanged || current is { UnembeddedCount: > 0 });
        return new TextPlan(item, current, hashChanged || needsEmbedding, needsEmbedding);
      }).ToList();

      counts.Unchanged = plans.Count(p => !p.NeedsWrite);

      if (options.DryRun)
      {
        counts.Loaded = plans.Count(p => p.NeedsWrite);
        counts.PassagesWritten = plans.Where(p => p.NeedsWrite).Sum(p => p.Item.Passages.Count);
        counts.PassagesEmbedded = plans.Where(p => p.NeedsEmbedding).Sum(p => p.Item.Passages.Count);
        PrintReport(counts, dryRun: true);
        return _errors.Count > 0 ? 1 : 0;
      }

      Embedder? embedder = null;
      if (plans.Any(p => p.NeedsEmbedding))
      {
        settings.RequireAzure();
        embedder = new Embedder(settings.AzureEndpoint!, settings.AzureApiKey!, settings.AzureDeployment!, settings.Dimensions);
      }

      var processed = 0;
      foreach (var plan in plans.Where(p => p.NeedsWrite))
      {
        float[][]? vectors = null;
        if (plan.NeedsEmbedding)
        {
          try
          {
            vectors = await EmbedAsync(embedder!, plan.Item, cancellationToken);
          }
          catch (Exception ex) when (ex is not OperationCanceledException)
          {
            // A failed embedding call (bad key, wrong deployment, quota) would fail every article: stop here.
            _errors.Add($"Embedding failed for {plan.Item.Code}: {ex.Message}");
            _errors.Add("Text load stopped. Articles already written were saved.");
            PrintReport(counts);
            return 1;
          }
        }

        try
        {
          await repository.ReplaceAsync(plan.Existing!.ArticleId, plan.Item, vectors, settings.EmbeddingModel, cancellationToken);
          counts.Loaded++;
          counts.PassagesWritten += plan.Item.Passages.Count;
          if (vectors is not null)
            counts.PassagesEmbedded += vectors.Length;
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
          counts.Failed++;
          _errors.Add($"{plan.Item.Code}: {ex.Message}");
        }

        if (++processed % 25 == 0)
          Out.WriteLine($"  {processed} of {plans.Count(p => p.NeedsWrite)} articles processed");
      }

      PrintReport(counts);
      return _errors.Count > 0 ? 1 : 0;
    }

    /// <summary>One vector per passage, in passage order, generated in batches of Embedding:BatchSize.</summary>
    private async Task<float[][]> EmbedAsync(Embedder embedder, ArticleText item, CancellationToken cancellationToken)
    {
      var vectors = new List<float[]>(item.Passages.Count);
      foreach (var batch in item.Passages.Chunk(settings.BatchSize))
        vectors.AddRange(await embedder.EmbedAsync(batch.Select(p => p.EmbeddingText).ToList(), cancellationToken));
      return vectors.ToArray();
    }

    private void PrintReport(TextCounts counts, bool dryRun = false)
    {
      Out.WriteLine();
      Out.WriteLine(dryRun ? "Text dry run (nothing written)" : "Text load summary");

      static void Row(string label, int value) => Out.WriteLine($"  {(label + ":").PadRight(34)}{value}");

      Row("Markdown files", counts.Files);
      Row("  without an article row (skipped)", counts.NoArticleRow);
      Row("  English translations used", counts.Translations);
      Row("Articles with full text", counts.FullText);
      Row("Articles with abstract only", counts.AbstractOnly);
      Row("Articles with no usable text", counts.NoText);
      Row("Unchanged (not rewritten)", counts.Unchanged);
      Row(dryRun ? "Would load" : "Loaded", counts.Loaded);
      Row(dryRun ? "  passages to write" : "  passages written", counts.PassagesWritten);
      Row(dryRun ? "  passages to embed" : "  passages embedded", counts.PassagesEmbedded);
      if (!dryRun)
        Row("Failed", counts.Failed);
      Row("Articles with no Markdown file", counts.NoTextFile.Count);
      if (counts.NoTextFile.Count > 0)
        Out.WriteLine($"    {string.Join(", ", counts.NoTextFile)}");

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

    private sealed record TextPlan(ArticleText Item, ExistingText? Existing, bool NeedsWrite, bool NeedsEmbedding);

    private sealed class TextCounts
    {
      public int Files { get; set; }
      public int NoArticleRow { get; set; }
      public int Translations { get; set; }
      public int FullText { get; set; }
      public int AbstractOnly { get; set; }
      public int NoText { get; set; }
      public int Unchanged { get; set; }
      public int Loaded { get; set; }
      public int PassagesWritten { get; set; }
      public int PassagesEmbedded { get; set; }
      public int Failed { get; set; }
      public List<string> NoTextFile { get; set; } = [];
    }
  }
}
