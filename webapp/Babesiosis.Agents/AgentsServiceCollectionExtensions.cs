using Babesiosis.Agents.Articles;
using Babesiosis.Agents.Clinical;
using Babesiosis.Agents.Experiments;
using Babesiosis.Agents.OpenRouter;
using Microsoft.Extensions.DependencyInjection;

namespace Babesiosis.Agents
{
  public static class AgentsServiceCollectionExtensions
  {
    /// <summary>
    /// Registers the article question agent and its dependencies: the article and experiment
    /// repositories (database) and the clinical manual (page files embedded in this assembly). Needs an
    /// <see cref="Babesiosis.Core.Configurations.IAppSettingsService"/> in the container, which
    /// <c>AddBabesiosisCore()</c> provides. Settings: <c>AppSettings:AiAgents</c> (OpenRouter key,
    /// base URL, tier-to-model map) and <c>AppSettings:Connections:Database</c>.
    /// </summary>
    public static IServiceCollection AddBabesiosisAgents(this IServiceCollection services)
    {
      services.AddSingleton<OpenRouterChatClientFactory>();
      services.AddSingleton<ArticleSearchRepository>();
      services.AddSingleton<ExperimentRepository>();
      services.AddSingleton<ClinicalManual>(_ => new ClinicalManual());
      services.AddTransient<IArticleQuestionAgent, ArticleQuestionAgent>();
      return services;
    }
  }
}
