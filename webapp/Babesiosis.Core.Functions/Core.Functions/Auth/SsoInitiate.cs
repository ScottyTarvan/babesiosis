using Babesiosis.Core.Configurations;
using Babesiosis.Core.Security;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace Babesiosis.Core.Functions.Auth
{
  public class SsoInitiate : HttpFunctionBase
  {
    const string NAME = "auth-sso-initiate";
    private readonly SsoInitiateController _controller;

    public SsoInitiate(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider,
      ILogger<SsoInitiate> logger,
      SsoInitiateController controller)
    : base(appSettingsService, tokenProvider, logger)
    {
      _controller = controller;
    }

    [Function(NAME)]
    public async Task<IActionResult> Run(
            [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = NAME)] HttpRequest req)
    {
      try
      {
        var data = await _controller.InitiateSsoLogin();
        return new RedirectResult(data.RedirectUrl);
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