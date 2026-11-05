using Babesiosis.Agents.Articles;
using Babesiosis.Agents.OpenRouter;
using Microsoft.Extensions.DependencyInjection;

namespace Babesiosis.Agents
{
  public static class AgentsServiceCollectionExtensions
  {
    /// <summary>
    /// Registers the article question agent and its dependencies. Needs an
    /// <see cref="Babesiosis.Core.Configurations.IAppSettingsService"/> in the container, which
    /// <c>AddBabesiosisCore()</c> provides. Settings: <c>AppSettings:AiAgents</c> (OpenRouter key,
    /// base URL, tier-to-model map) and <c>AppSettings:Connections:Database</c>.
    /// </summary>
    public static IServiceCollection AddBabesiosisAgents(this IServiceCollection services)
    {
      services.AddSingleton<OpenRouterChatClientFactory>();
      services.AddSingleton<ArticleSearchRepository>();
      services.AddTransient<IArticleQuestionAgent, ArticleQuestionAgent>();
      return services;
    }
  }
}
