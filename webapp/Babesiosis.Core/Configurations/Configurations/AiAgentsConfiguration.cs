namespace Babesiosis.Core.Configurations.Configurations
{
  /// <summary>
  /// Settings for the platform AI agent service, read from <c>AppSettings:AiAgents:</c> on every
  /// call (platform/ai-agents.md §3.5). <see cref="Enabled"/> defaults to false so an
  /// unconfigured environment never calls the provider.
  /// </summary>
  public class AiAgentsConfiguration
  {
    public const string DefaultBaseUrl = "https://openrouter.ai/api/v1";
    public const int DefaultTimeoutSeconds = 30;

    public bool Enabled { get; set; }
    public string ApiKey { get; set; }
    public string BaseUrl { get; set; } = DefaultBaseUrl;
    public int TimeoutSeconds { get; set; } = DefaultTimeoutSeconds;
    public AiAgentsModelsConfiguration Models { get; set; } = new AiAgentsModelsConfiguration();
    public bool BodyStorageAllowed { get; set; }

    /// <summary>
    /// Whether the article agent may read the papers' own text (dbo.article_section) through its
    /// passage search, outline, section and full-text tools. Defaults to true; set
    /// <c>AppSettings:AiAgents:FullText</c> to false to limit the agent to the review's records,
    /// for example where the full texts may not be exposed.
    /// </summary>
    public bool FullText { get; set; } = true;
  }

  /// <summary>Model tier to OpenRouter model id (platform/ai-agents.md §3.2). Null or empty means unmapped.</summary>
  public class AiAgentsModelsConfiguration
  {
    public string Low { get; set; }
    public string Medium { get; set; }
    public string High { get; set; }
    public string Max { get; set; }
  }
}
