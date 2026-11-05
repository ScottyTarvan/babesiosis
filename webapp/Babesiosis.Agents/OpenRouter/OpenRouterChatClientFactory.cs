using System.ClientModel;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Configurations.Configurations;
using OpenAI;
using OpenAI.Chat;

namespace Babesiosis.Agents.OpenRouter
{
  /// <summary>
  /// Creates OpenAI SDK chat clients that talk to OpenRouter. OpenRouter exposes an
  /// OpenAI-compatible Chat Completions API, so the stock SDK works once its endpoint is
  /// pointed at <see cref="AiAgentsConfiguration.BaseUrl"/>.
  ///
  /// Settings are read on every call, as <see cref="IAppSettings.AiAgents"/> intends, so a
  /// configuration refresh can change the key or a tier's model without a restart.
  /// </summary>
  public sealed class OpenRouterChatClientFactory
  {
    private readonly IAppSettingsService _appSettingsService;

    public OpenRouterChatClientFactory(IAppSettingsService appSettingsService)
    {
      _appSettingsService = appSettingsService;
    }

    /// <summary>The chat client for <paramref name="tier"/>, and the model id it resolved to.</summary>
    /// <exception cref="AgentConfigurationException">
    /// The agents are disabled, the API key is missing or the tier has no model.
    /// </exception>
    public (ChatClient Client, string Model) Create(AgentModelTier tier)
    {
      var config = _appSettingsService.GetAppSettings().AiAgents;

      if (!config.Enabled)
        throw new AgentConfigurationException("AI agents are disabled. Set AppSettings:AiAgents:Enabled to true.");
      if (string.IsNullOrWhiteSpace(config.ApiKey))
        throw new AgentConfigurationException("AppSettings:AiAgents:ApiKey is not set.");

      var model = ResolveModel(config.Models, tier);
      if (string.IsNullOrWhiteSpace(model))
        throw new AgentConfigurationException($"AppSettings:AiAgents:Models:{tier} has no OpenRouter model id.");

      var options = new OpenAIClientOptions
      {
        Endpoint = new Uri(config.BaseUrl),
        // Per HTTP call. One question can make several model calls (one per tool round).
        NetworkTimeout = TimeSpan.FromSeconds(config.TimeoutSeconds)
      };

      var client = new OpenAIClient(new ApiKeyCredential(config.ApiKey), options).GetChatClient(model);
      return (client, model);
    }

    private static string? ResolveModel(AiAgentsModelsConfiguration models, AgentModelTier tier) => tier switch
    {
      AgentModelTier.Low => models.Low,
      AgentModelTier.Medium => models.Medium,
      AgentModelTier.High => models.High,
      AgentModelTier.Max => models.Max,
      _ => throw new ArgumentOutOfRangeException(nameof(tier), tier, null)
    };
  }

  /// <summary>The AI agent settings are missing or turn the agents off.</summary>
  public sealed class AgentConfigurationException(string message) : InvalidOperationException(message);
}
