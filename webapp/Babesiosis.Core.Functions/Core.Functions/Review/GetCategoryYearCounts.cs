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
  /// Article counts per category per year for the Review dashboard heat map.
  /// Anonymous, like the rest of Review: the web application has no sign-in for now.
  /// </summary>
  public class GetCategoryYearCounts : HttpFunctionBase
  {
    const string NAME = "review-category-year-counts-get";
    private readonly GetCategoryYearCountsController _controller;

    public GetCategoryYearCounts(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider,
      ILogger<GetCategoryYearCounts> logger,
      GetCategoryYearCountsController controller)
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
        var command = JsonConvert.DeserializeObject<GetCategoryYearCountsCommand>(requestBody) ?? new GetCategoryYearCountsCommand();

        var data = await this._controller.HandleCommand(Guid.Empty, command);
        return new OkObjectResult(data);
      }, requireJwt: false, "Failed to get category counts by year");
    }
  }
}
