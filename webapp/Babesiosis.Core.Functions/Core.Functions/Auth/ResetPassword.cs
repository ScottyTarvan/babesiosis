using Babesiosis.Core.Api.Auth.Commands;
using Babesiosis.Core.Api.Auth.Controllers;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Security;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace Babesiosis.Core.Functions.Auth
{
  public class ResetPassword : HttpFunctionBase
  {
    const string NAME = "auth-password-reset";
    private readonly ResetPasswordController _controller;

    public ResetPassword(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider, 
      ILogger<ResetPassword> logger,
      ResetPasswordController controller)
    : base(appSettingsService, tokenProvider, logger)
    {
      this._controller = controller;
    }

    [Function(NAME)]
    public async Task<IActionResult> Run(
            [HttpTrigger(AuthorizationLevel.Function, "post", Route = NAME)] ResetPasswordCommand command)
    {
      try
      {
        await this._controller.HandleCommand(command);
        return new OkResult();
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
