using Babesiosis.Core.Api.Auth.Commands;
using Babesiosis.Core.Api.Auth.Controllers;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Security;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;

namespace Babesiosis.Core.Functions.Auth
{
  public class SsoExchange : HttpFunctionBase
  {
    const string NAME = "auth-sso-exchange";
    private readonly SsoExchangeController _controller;

    public SsoExchange(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider,
      ILogger<SsoExchange> logger,
      SsoExchangeController controller)
    : base(appSettingsService, tokenProvider, logger)
    {
      this._controller = controller;
    }

    [Function(NAME)]
    public async Task<IActionResult> Run([HttpTrigger(AuthorizationLevel.Function, "post", Route = NAME)] HttpRequest req)
    {
      try
      {
        string requestBody = await new StreamReader(req.Body).ReadToEndAsync();
        var command = JsonConvert.DeserializeObject<SsoExchangeCommand>(requestBody);
        var data = await this._controller.HandleCommand(command);
        return new OkObjectResult(data);
      }
      catch (Exception ex)
      {
        Logger.LogError($"{NAME} failed: [{ex.Message}]");
        Logger.LogError($"{NAME} trace: [{ex.StackTrace}]");
        return new ServerErrorResult(ex.Message);
      }
    }
  }
}
