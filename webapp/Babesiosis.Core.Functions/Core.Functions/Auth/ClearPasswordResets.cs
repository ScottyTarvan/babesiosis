using Babesiosis.Core.Api.Auth.Controllers;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Security;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace Babesiosis.Core.Functions.Auth
{
  public class ClearPasswordResets : HttpFunctionBase
  {
    const string NAME = "auth-passwordresets-clear-timer";
    private readonly ClearPasswordResetsController _controller;

    public ClearPasswordResets(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider, 
      ILogger<ClearPasswordResets> logger,
      ClearPasswordResetsController controller)
    : base(appSettingsService, tokenProvider, logger)
    {
      this._controller = controller;
    }

    [Function(NAME)]
    public async Task Run(
            [TimerTrigger("0 0 0 * * *")] TimerInfo timer)
    {
      try
      {
        await this._controller.HandleCommand();
      }
      catch (Exception ex)
      {
        Logger.LogError($"{NAME} failed: [{ex.Message}]");
        Logger.LogError($"{NAME} trace: [{ex.StackTrace}]");
      }
    }
  }
}
