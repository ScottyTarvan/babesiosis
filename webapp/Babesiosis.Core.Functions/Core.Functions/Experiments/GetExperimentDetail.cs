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
  /// One experiment in full (header, dataset, variables, associations, result payloads) for
  /// the Experiments screen's right-hand panel. Anonymous, like the rest of the read screens.
  /// </summary>
  public class GetExperimentDetail : HttpFunctionBase
  {
    const string NAME = "experiments-detail-get";
    private readonly GetExperimentDetailController _controller;

    public GetExperimentDetail(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider,
      ILogger<GetExperimentDetail> logger,
      GetExperimentDetailController controller)
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
        var command = JsonConvert.DeserializeObject<GetExperimentDetailCommand>(requestBody) ?? new GetExperimentDetailCommand();

        var data = await this._controller.HandleCommand(Guid.Empty, command);
        return new OkObjectResult(data);
      }, requireJwt: false, "Failed to get the experiment");
    }
  }
}
