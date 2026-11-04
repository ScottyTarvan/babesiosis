using Babesiosis.Core.Api.Review.Commands;
using Babesiosis.Core.Api.Review.Controllers;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Security;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;

namespace Babesiosis.Core.Functions.Review
{
  /// <summary>
  /// Article counts per clinical syndrome or sign (studied and mentioned only) for the
  /// Review dashboard. Anonymous, like the rest of Review: the web application has no sign-in for now.
  /// </summary>
  public class GetTermCounts : HttpFunctionBase
  {
    const string NAME = "review-term-counts-get";
    private readonly GetTermCountsController _controller;

    public GetTermCounts(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider,
      ILogger<GetTermCounts> logger,
      GetTermCountsController controller)
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
        var command = JsonConvert.DeserializeObject<GetTermCountsCommand>(requestBody) ?? new GetTermCountsCommand();

        var data = await this._controller.HandleCommand(Guid.Empty, command);
        return new OkObjectResult(data);
      }, requireJwt: false, "Failed to get term counts");
    }
  }
}
