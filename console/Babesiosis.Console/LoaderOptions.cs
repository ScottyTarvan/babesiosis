namespace Babesiosis.Console
{
  /// <summary>Command-line options. See <see cref="Usage"/>.</summary>
  internal sealed class LoaderOptions
  {
    public bool DryRun { get; private set; }
    public bool SkipEmbeddings { get; private set; }
    public bool Reembed { get; private set; }
    public bool DatasetsOnly { get; private set; }
    public HashSet<string>? Only { get; private set; }
    public bool ShowHelp { get; private set; }

    public const string Usage = """
      Loads the review's articles into babesiosis-db (tables: article, article_category), then each
      article's own text from data/markdown as embedded passages (table: article_section; columns
      article.has_full_text, text_*), then the per-article terms from data/terms (tables: term,
      article_term; column article.text_source), then the tidy datasets from data/tidy (tables:
      dataset, variable, subject, observation) and the experiment results from data/experiments
      (tables: experiment, association, cluster_assignment, experiment_result).

      Usage: Babesiosis.Console [options]

        --dry-run           Parse and validate only. No database writes, no Azure OpenAI calls.
        --skip-embeddings   Load the data without calling Azure OpenAI. Changed articles lose
                            their stale vector; passages are stored without one. Both are
                            embedded on the next full run.
        --reembed           Re-embed every article and passage, even when the text is unchanged.
        --datasets-only     Skip the articles, passages and terms; load only the datasets and experiments.
        --only CODES        Load only these articles, comma-separated (e.g. CB001,CB046). With
                            --datasets-only, these are dataset or experiment codes (e.g. DS05).
        --help              Show this help.

      Settings come from appsettings.json, then appsettings.Local.json (not in source control).
      """;

    public static LoaderOptions Parse(string[] args)
    {
      var options = new LoaderOptions();

      for (var i = 0; i < args.Length; i++)
      {
        switch (args[i].ToLowerInvariant())
        {
          case "--dry-run":
            options.DryRun = true;
            break;
          case "--skip-embeddings":
            options.SkipEmbeddings = true;
            break;
          case "--reembed":
            options.Reembed = true;
            break;
          case "--datasets-only":
            options.DatasetsOnly = true;
            break;
          case "--only":
            if (i + 1 >= args.Length)
              throw new ArgumentException("--only needs a comma-separated list of article codes.");
            options.Only = args[++i]
              .Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
              .ToHashSet(StringComparer.OrdinalIgnoreCase);
            break;
          case "--help":
          case "-h":
          case "/?":
            options.ShowHelp = true;
            break;
          default:
            throw new ArgumentException($"Unknown option '{args[i]}'.");
        }
      }

      if (options.SkipEmbeddings && options.Reembed)
        throw new ArgumentException("--skip-embeddings and --reembed cannot be used together.");

      return options;
    }
  }
}
