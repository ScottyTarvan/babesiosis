using Babesiosis.Console.Data;
using Babesiosis.Console.Embedding;
using Babesiosis.Console.Source;
using Out = System.Console;

namespace Babesiosis.Console
{
  /// <summary>Reads the article files, embeds changed articles and upserts them into the database.</summary>
  internal sealed class ArticleLoader(LoaderSettings settings, LoaderOptions options)
  {
    private readonly List<string> _errors = [];
    private readonly List<string> _warnings = [];

    /// <summary>Runs the load and prints a report. Returns the process exit code.</summary>
    public async Task<int> RunAsync(CancellationToken cancellationToken)
    {
      Out.WriteLine($"Reading articles from {settings.ReviewRoot}");
      var items = ArticleSource.Load(settings.ReviewRoot, settings.EmbeddingModel, _errors);
      var sourceCodes = items.Select(i => i.Code).ToHashSet(StringComparer.OrdinalIgnoreCase);

      // Out of scope for this database (Articles:ExcludeScopes / ExcludeCodes): never loaded.
      foreach (var code in settings.ExcludeCodes.Where(c => !sourceCodes.Contains(c)).Order())
        _warnings.Add($"{code}: in Articles:ExcludeCodes but not in articles.jsonl");
      var excludedCodes = items.Where(i => IsExcluded(i.Record)).Select(i => i.Code).ToHashSet(StringComparer.OrdinalIgnoreCase);
      items = items.Where(i => !excludedCodes.Contains(i.Code)).ToList();

      if (options.Only is not null)
      {
        foreach (var code in options.Only.Where(c => !sourceCodes.Contains(c)))
          _errors.Add($"{code}: not found in articles.jsonl (--only)");
        foreach (var code in options.Only.Where(excludedCodes.Contains))
          _warnings.Add($"{code}: excluded by Articles:ExcludeScopes or ExcludeCodes; not loaded (--only)");
        items = items.Where(i => options.Only.Contains(i.Code)).ToList();
      }

      foreach (var item in items)
        _warnings.AddRange(item.Warnings.Select(w => $"{item.Code}: {w}"));

      var repository = new ArticleRepository(settings.ConnectionString, settings.Dimensions);
      Dictionary<string, int>? categoryIds = null;
      var existing = new Dictionary<string, ExistingArticle>(StringComparer.OrdinalIgnoreCase);

      if (await repository.SchemaExistsAsync(cancellationToken))
      {
        categoryIds = await repository.GetCategoryIdsAsync(cancellationToken);
        existing = await repository.GetExistingAsync(cancellationToken);
      }
      else if (options.DryRun)
      {
        _warnings.Add("schema.sql has not been run: category codes and stored hashes were not checked");
      }
      else
      {
        _errors.Add("Tables dbo.category, dbo.article and dbo.article_category not found. Run Database/schema.sql first.");
        PrintReport(new LoadCounts());
        return 1;
      }

      var plans = items.Select(item => Plan(item, categoryIds, existing)).ToList();
      var counts = new LoadCounts
      {
        Read = items.Count,
        Excluded = excludedCodes.Count,
        NoPrimaryCategory = plans.Count(p => p.PrimaryCategoryId is null),
        Orphans = options.Only is null
          ? existing.Keys.Where(code => !sourceCodes.Contains(code)).Order().ToList()
          : [],
        ExcludedInDatabase = existing.Keys.Where(excludedCodes.Contains).Order().ToList()
      };

      if (options.DryRun)
      {
        counts.Inserted = plans.Count(p => p.Existing is null);
        counts.Updated = plans.Count - counts.Inserted;
        counts.Embedded = plans.Count(p => p.NeedsEmbedding);
        PrintReport(counts, dryRun: true);
        return _errors.Count > 0 ? 1 : 0;
      }

      Embedder? embedder = null;
      if (!options.SkipEmbeddings && plans.Any(p => p.NeedsEmbedding))
      {
        settings.RequireAzure();
        embedder = new Embedder(settings.AzureEndpoint!, settings.AzureApiKey!, settings.AzureDeployment!, settings.Dimensions);
      }

      foreach (var batch in plans.Chunk(settings.BatchSize))
      {
        var toEmbed = embedder is null ? [] : batch.Where(p => p.NeedsEmbedding).ToList();
        var vectors = new Dictionary<string, float[]>();

        if (toEmbed.Count > 0)
        {
          float[][] result;
          try
          {
            result = await embedder!.EmbedAsync(toEmbed.Select(p => p.Item.EmbeddingText).ToList(), cancellationToken);
          }
          catch (Exception ex) when (ex is not OperationCanceledException)
          {
            // A failed embedding call (bad key, wrong deployment, quota) would fail every batch: stop here.
            _errors.Add($"Embedding failed for {string.Join(", ", toEmbed.Select(p => p.Item.Code))}: {ex.Message}");
            _errors.Add("Load stopped. Articles in earlier batches were saved.");
            PrintReport(counts);
            return 1;
          }

          for (var i = 0; i < toEmbed.Count; i++)
            vectors[toEmbed[i].Item.Code] = result[i];
        }

        foreach (var plan in batch)
        {
          var vector = vectors.GetValueOrDefault(plan.Item.Code);
          var action = vector is not null ? EmbeddingAction.Set
            : plan.Existing is { HasEmbedding: true } && plan.HashChanged ? EmbeddingAction.Clear
            : EmbeddingAction.Keep;

          try
          {
            var inserted = await repository.UpsertAsync(
              plan.Item, plan.PrimaryCategoryId, plan.Tags, action, vector, settings.EmbeddingModel, cancellationToken);

            if (inserted) counts.Inserted++; else counts.Updated++;
            if (action == EmbeddingAction.Set) counts.Embedded++;
            if (action == EmbeddingAction.Clear) counts.Cleared++;
          }
          catch (Exception ex) when (ex is not OperationCanceledException)
          {
            counts.Failed++;
            _errors.Add($"{plan.Item.Code}: {ex.Message}");
          }
        }

        Out.WriteLine($"  {counts.Inserted + counts.Updated + counts.Failed} of {plans.Count} processed");
      }

      PrintReport(counts);
      return _errors.Count > 0 ? 1 : 0;
    }

    private bool IsExcluded(ArticleRecord record) =>
      settings.ExcludeCodes.Contains(record.Id) ||
      (record.ScopeLabel is not null && settings.ExcludeScopes.Contains(record.ScopeLabel.Trim()));

    /// <summary>Resolves category codes and decides whether the article needs a new embedding.</summary>
    private ArticlePlan Plan(ArticleItem item, Dictionary<string, int>? categoryIds, Dictionary<string, ExistingArticle> existing)
    {
      var record = item.Record;
      int? primaryCategoryId = null;

      if (categoryIds is not null && !string.IsNullOrWhiteSpace(record.PrimaryCategory))
      {
        if (categoryIds.TryGetValue(record.PrimaryCategory.Trim(), out var id))
          primaryCategoryId = id;
        else
          _warnings.Add($"{item.Code}: primary_category '{record.PrimaryCategory}' is not a category code; stored as NULL");
      }

      var tags = new List<TagRow>();
      if (categoryIds is not null)
      {
        void AddTags(IEnumerable<string>? codes, string tagType)
        {
          foreach (var code in (codes ?? []).Select(c => c.Trim()).Distinct(StringComparer.OrdinalIgnoreCase))
          {
            if (categoryIds.TryGetValue(code, out var id))
              tags.Add(new TagRow(id, tagType));
            else
              _warnings.Add($"{item.Code}: {tagType} tag '{code}' is not a category code; skipped");
          }
        }

        AddTags(record.SecondaryTags, "secondary");
        AddTags(record.ComparatorCategories, "comparator");
      }

      var current = existing.GetValueOrDefault(item.Code);
      var hashChanged = current is null || !current.ContentHash.AsSpan().SequenceEqual(item.ContentHash);
      var needsEmbedding = !options.SkipEmbeddings && (options.Reembed || hashChanged || current is { HasEmbedding: false });

      return new ArticlePlan(item, primaryCategoryId, tags, current, hashChanged, needsEmbedding);
    }

    private void PrintReport(LoadCounts counts, bool dryRun = false)
    {
      Out.WriteLine();
      Out.WriteLine(dryRun ? "Dry run (nothing written)" : "Load summary");

      static void Row(string label, int value) => Out.WriteLine($"  {(label + ":").PadRight(24)}{value}");

      Row("Articles read", counts.Read);
      Row("Excluded by settings", counts.Excluded);
      Row(dryRun ? "Would insert" : "Inserted", counts.Inserted);
      Row(dryRun ? "Would update" : "Updated", counts.Updated);
      Row(dryRun ? "Would embed" : "Embedded", counts.Embedded);
      if (!dryRun)
      {
        Row("Stale vectors cleared", counts.Cleared);
        Row("Failed", counts.Failed);
      }
      Row("No primary category", counts.NoPrimaryCategory);

      if (counts.Orphans.Count > 0)
        Out.WriteLine($"  In database but not in articles.jsonl (not deleted): {string.Join(", ", counts.Orphans)}");
      if (counts.ExcludedInDatabase.Count > 0)
        Out.WriteLine($"  Excluded but still in database (not deleted): {string.Join(", ", counts.ExcludedInDatabase)}");

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

    private sealed record ArticlePlan(
      ArticleItem Item,
      int? PrimaryCategoryId,
      List<TagRow> Tags,
      ExistingArticle? Existing,
      bool HashChanged,
      bool NeedsEmbedding);

    private sealed class LoadCounts
    {
      public int Read { get; set; }
      public int Excluded { get; set; }
      public int Inserted { get; set; }
      public int Updated { get; set; }
      public int Embedded { get; set; }
      public int Cleared { get; set; }
      public int Failed { get; set; }
      public int NoPrimaryCategory { get; set; }
      public List<string> Orphans { get; set; } = [];
      public List<string> ExcludedInDatabase { get; set; } = [];
    }
  }
}
