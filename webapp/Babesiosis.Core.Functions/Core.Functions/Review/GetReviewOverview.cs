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
  /// The Overview screen: headline figures, articles per year, one row per topic and the
  /// study design, species, country and sample-size cards, counted from canine articles.
  /// Anonymous, like the rest of Review: the web application has no sign-in for now.
  /// </summary>
  public class GetReviewOverview : HttpFunctionBase
  {
    const string NAME = "review-overview-get";
    private readonly GetReviewOverviewController _controller;

    public GetReviewOverview(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider,
      ILogger<GetReviewOverview> logger,
      GetReviewOverviewController controller)
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
        var command = JsonConvert.DeserializeObject<GetReviewOverviewCommand>(requestBody) ?? new GetReviewOverviewCommand();

        var data = await this._controller.HandleCommand(Guid.Empty, command);
        return new OkObjectResult(data);
      }, requireJwt: false, "Failed to get the review overview");
    }
  }
}
