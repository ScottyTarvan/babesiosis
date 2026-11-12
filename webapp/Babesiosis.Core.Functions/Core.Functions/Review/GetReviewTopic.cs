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
  /// One topic page: the category's figures, its narrative synthesis as written and its
  /// canine articles.
  /// Anonymous, like the rest of Review: the web application has no sign-in for now.
  /// </summary>
  public class GetReviewTopic : HttpFunctionBase
  {
    const string NAME = "review-topic-get";
    private readonly GetReviewTopicController _controller;

    public GetReviewTopic(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider,
      ILogger<GetReviewTopic> logger,
      GetReviewTopicController controller)
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
        var command = JsonConvert.DeserializeObject<GetReviewTopicCommand>(requestBody) ?? new GetReviewTopicCommand();

        var data = await this._controller.HandleCommand(Guid.Empty, command);
        return new OkObjectResult(data);
      }, requireJwt: false, "Failed to get the topic");
    }
  }
}
