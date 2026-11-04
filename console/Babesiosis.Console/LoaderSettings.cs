using Microsoft.Extensions.Configuration;

namespace Babesiosis.Console
{
  /// <summary>Settings from appsettings.json and appsettings.Local.json.</summary>
  internal sealed class LoaderSettings
  {
    public required string ReviewRoot { get; init; }
    public required string ConnectionString { get; init; }
    public required string EmbeddingModel { get; init; }
    public required int Dimensions { get; init; }
    public required int BatchSize { get; init; }
    public required IReadOnlySet<string> ExcludeScopes { get; init; }
    public required IReadOnlySet<string> ExcludeCodes { get; init; }
    public string? AzureEndpoint { get; init; }
    public string? AzureDeployment { get; init; }
    public string? AzureApiKey { get; init; }

    public static LoaderSettings Load()
    {
      var config = new ConfigurationBuilder()
        .SetBasePath(AppContext.BaseDirectory)
        .AddJsonFile("appsettings.json", optional: false)
        .AddJsonFile("appsettings.Local.json", optional: true)
        .Build();

      return new LoaderSettings
      {
        ReviewRoot = Required(config, "Articles:ReviewRoot"),
        ConnectionString = Required(config, "ConnectionStrings:Babesiosis"),
        EmbeddingModel = Required(config, "Embedding:Model"),
        Dimensions = int.Parse(Required(config, "Embedding:Dimensions")),
        BatchSize = int.Parse(Required(config, "Embedding:BatchSize")),
        ExcludeScopes = List(config, "Articles:ExcludeScopes"),
        ExcludeCodes = List(config, "Articles:ExcludeCodes"),
        AzureEndpoint = Optional(config, "AzureOpenAI:Endpoint"),
        AzureDeployment = Optional(config, "AzureOpenAI:Deployment"),
        AzureApiKey = Optional(config, "AzureOpenAI:ApiKey")
      };
    }

    /// <summary>Throws when the Azure OpenAI settings needed for embedding are missing.</summary>
    public void RequireAzure()
    {
      var missing = new[]
      {
        ("AzureOpenAI:Endpoint", AzureEndpoint),
        ("AzureOpenAI:Deployment", AzureDeployment),
        ("AzureOpenAI:ApiKey", AzureApiKey)
      }.Where(s => s.Item2 is null).Select(s => s.Item1).ToList();

      if (missing.Count > 0)
        throw new InvalidOperationException(
          $"Missing setting(s) {string.Join(", ", missing)} in appsettings.Local.json. Use --skip-embeddings to load without vectors.");
    }

    private static string Required(IConfiguration config, string key) =>
      Optional(config, key) ?? throw new InvalidOperationException($"Missing setting '{key}' (appsettings.json or appsettings.Local.json).");

    private static string? Optional(IConfiguration config, string key) =>
      string.IsNullOrWhiteSpace(config[key]) ? null : config[key];

    /// <summary>Reads a JSON array setting; missing or empty entries give an empty set.</summary>
    private static HashSet<string> List(IConfiguration config, string key) =>
      config.GetSection(key).GetChildren()
        .Select(c => c.Value?.Trim())
        .OfType<string>()
        .Where(v => v.Length > 0)
        .ToHashSet(StringComparer.OrdinalIgnoreCase);
  }
}
