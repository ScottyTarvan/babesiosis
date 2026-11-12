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
  /// The Gaps and questions screen: the category by study-design matrix, the gap figures,
  /// and the cross-cutting themes and research questions as written.
  /// Anonymous, like the rest of Review: the web application has no sign-in for now.
  /// </summary>
  public class GetReviewGaps : HttpFunctionBase
  {
    const string NAME = "review-gaps-get";
    private readonly GetReviewGapsController _controller;

    public GetReviewGaps(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider,
      ILogger<GetReviewGaps> logger,
      GetReviewGapsController controller)
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
        var command = JsonConvert.DeserializeObject<GetReviewGapsCommand>(requestBody) ?? new GetReviewGapsCommand();

        var data = await this._controller.HandleCommand(Guid.Empty, command);
        return new OkObjectResult(data);
      }, requireJwt: false, "Failed to get the gaps and questions");
    }
  }
}
