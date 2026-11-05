using Babesiosis.Core.Api.Articles.Commands;
using Babesiosis.Core.Api.Articles.Controllers;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Security;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;

namespace Babesiosis.Core.Functions.Articles
{
  /// <summary>
  /// Asks the article agent a question about the review's articles.
  ///
  /// Body: <c>{ "question": "...", "tier": "Medium", "conversation": null }</c>. Pass the
  /// previous answer's <c>conversation</c> back to ask a follow-up.
  ///
  /// Anonymous, like the Articles list: the web application has no sign-in for now, so no JWT
  /// is required. Unlike the list, every call costs OpenRouter credit, so once deployed the
  /// function key (AuthorizationLevel.Function) is the only gate; add sign-in or rate limiting
  /// before exposing it publicly. Errors: 400 for a bad request, 503 AI_AGENT_UNAVAILABLE when
  /// AppSettings:AiAgents is off or incomplete, 502 AI_AGENT_FAILED when OpenRouter fails.
  /// </summary>
  public class AskArticleAgent : HttpFunctionBase
  {
    const string NAME = "articles-agent-ask";
    private readonly AskArticleAgentController _controller;

    public AskArticleAgent(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider,
      ILogger<AskArticleAgent> logger,
      AskArticleAgentController controller)
    : base(appSettingsService, tokenProvider, logger)
    {
      this._controller = controller;
    }

    [Function(NAME)]
    public async Task<IActionResult> Run(
      [HttpTrigger(AuthorizationLevel.Function, "post", Route = NAME)] HttpRequest req)
    {
      return await ExecuteRequest(req, async (req) =>
      {
        string requestBody = await new StreamReader(req.Body).ReadToEndAsync();
        var command = JsonConvert.DeserializeObject<AskArticleAgentCommand>(requestBody) ?? new AskArticleAgentCommand();

        var data = await this._controller.HandleCommand(Guid.Empty, command, req.HttpContext.RequestAborted);
        return new OkObjectResult(data);
      }, requireJwt: false, "The AI agent could not answer");
    }
  }
}
