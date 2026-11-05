namespace Babesiosis.Agents
{
  /// <summary>
  /// The model tiers that <c>AppSettings:AiAgents:Models</c> maps to OpenRouter model ids.
  /// Callers pick a tier, never a model id, so a model can be swapped in configuration.
  /// </summary>
  public enum AgentModelTier
  {
    Low,
    Medium,
    High,
    Max
  }
}
