namespace Babesiosis.Core.Configurations.Configurations
{
  // Server-side only. Holds the upstream Azure Function base URLs and their
  // function keys, used by the Babesiosis.Proxy.App YARP BFF to forward browser requests
  // with the key injected. The keys are NEVER sent to the browser. Also carries the
  // browser origins the gateway's CORS policy allows.
  public class ProxyConfiguration
  {
    public string CoreApiUrl { get; set; }
    public string CoreApiKey { get; set; }
    public string ReportsApiUrl { get; set; }
    public string ReportsApiKey { get; set; }

    // Comma-separated list of browser origins allowed by the gateway's CORS policy,
    // e.g. "https://app.example.com,https://uat.example.com". The gateway normalizes
    // each to scheme://host[:port] and falls back to WebApp.Url when this is empty.
    public string AllowedOrigins { get; set; }
  }
}
