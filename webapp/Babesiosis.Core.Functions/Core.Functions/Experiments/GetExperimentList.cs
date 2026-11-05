using Babesiosis.Core.Api.Experiments.Commands;
using Babesiosis.Core.Api.Experiments.Controllers;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Security;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;

namespace Babesiosis.Core.Functions.Experiments
{
  /// <summary>
  /// The experiment runs for the Experiments screen's left-hand panel. Anonymous, like
  /// Review and Articles: the web application has no sign-in for now.
  /// </summary>
  public class GetExperimentList : HttpFunctionBase
  {
    const string NAME = "experiments-list-get";
    private readonly GetExperimentListController _controller;

    public GetExperimentList(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider,
      ILogger<GetExperimentList> logger,
      GetExperimentListController controller)
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
        var command = JsonConvert.DeserializeObject<GetExperimentListCommand>(requestBody) ?? new GetExperimentListCommand();

        var data = await this._controller.HandleCommand(Guid.Empty, command);
        return new OkObjectResult(data);
      }, requireJwt: false, "Failed to get experiments");
    }
  }
}
