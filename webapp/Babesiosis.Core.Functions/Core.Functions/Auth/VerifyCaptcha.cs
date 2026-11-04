using Babesiosis.Core.Api.Auth.Commands;
using Babesiosis.Core.Api.Auth.Controllers;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Security;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace Babesiosis.Core.Functions.Auth
{
  public class VerifyCaptcha : HttpFunctionBase
  {
    const string NAME = "auth-verify-captcha";
    private readonly VerifyCaptchaController _controller;

    public VerifyCaptcha(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider, 
      ILogger<VerifyCaptcha> logger,
      VerifyCaptchaController controller)
    : base(appSettingsService, tokenProvider, logger)
    {
      this._controller = controller;
    }

    [Function(NAME)]
    public async Task<IActionResult> Run([HttpTrigger(AuthorizationLevel.Function, "post", Route = NAME)] VerifyCaptchaCommand command)
    {
      try
      {
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
