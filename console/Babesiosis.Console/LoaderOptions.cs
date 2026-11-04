namespace Babesiosis.Console
{
  /// <summary>Command-line options. See <see cref="Usage"/>.</summary>
  internal sealed class LoaderOptions
  {
    public bool DryRun { get; private set; }
    public bool SkipEmbeddings { get; private set; }
    public bool Reembed { get; private set; }
    public HashSet<string>? Only { get; private set; }
    public bool ShowHelp { get; private set; }

    public const string Usage = """
      Loads the review's articles into babesiosis-db (tables: article, article_category), then the
      per-article terms from data/terms (tables: term, article_term; column article.text_source).

      Usage: Babesiosis.Console [options]

        --dry-run           Parse and validate only. No database writes, no Azure OpenAI calls.
        --skip-embeddings   Load the data without calling Azure OpenAI. Changed articles lose
                            their stale vector and are embedded on the next full run.
        --reembed           Re-embed every article, even when its text is unchanged.
        --only CODES        Load only these articles, comma-separated (e.g. CB001,CB046).
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
