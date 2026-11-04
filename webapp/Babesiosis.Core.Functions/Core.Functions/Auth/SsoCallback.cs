using Babesiosis.Core.Api.Auth.Commands;
using Babesiosis.Core.Api.Auth.Controllers;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Security;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace Babesiosis.Core.Functions.Auth
{
  public class SsoCallback : HttpFunctionBase
  {
    const string NAME = "auth-sso-callback";
    private readonly SsoCallbackController _controller;

    public SsoCallback(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider,
      ILogger<SsoCallback> logger,
      SsoCallbackController controller)
    : base(appSettingsService, tokenProvider, logger)
    {
      this._controller = controller;
    }

    [Function(NAME)]
    public async Task<IActionResult> Run(
            [HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = NAME)] HttpRequest req)
    {
      var code = req.Query["code"].ToString();

      if (string.IsNullOrEmpty(code))
      {
        return new BadRequestObjectResult("Authorization code is missing...");
      }

      var command = new SsoCallbackCommand { Code = code };
      var redirectUrl = await _controller.HandleCommand(command);
      return new RedirectResult(redirectUrl);
    }
  }
}
