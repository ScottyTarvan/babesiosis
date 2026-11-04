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
  /// The Articles list. Anonymous, like Review: the web application has no
  /// sign-in for now, so no JWT is required and there is no user to pass on.
  /// </summary>
  public class GetArticleList : HttpFunctionBase
  {
    const string NAME = "articles-list-get";
    private readonly GetArticleListController _controller;

    public GetArticleList(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider,
      ILogger<GetArticleList> logger,
      GetArticleListController controller)
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
        var command = JsonConvert.DeserializeObject<GetArticleListCommand>(requestBody) ?? new GetArticleListCommand();

        var data = await this._controller.HandleCommand(Guid.Empty, command);
        return new OkObjectResult(data);
      }, requireJwt: false, "Failed to get articles");
    }
  }
}
