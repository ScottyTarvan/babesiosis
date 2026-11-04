using Babesiosis.Core.Api.Teams.Users.Controllers;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Permissions.Attributes;
using Babesiosis.Core.Permissions.Configs;
using Babesiosis.Core.Security;
using Babesiosis.Core.Teams.Users.Commands;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;

namespace Babesiosis.Core.Functions.Teams.Users.Manage
{
  /// <summary>
  /// New web application endpoint. Enforced by the code-declared permission
  /// model via [RequiredPermission]; the equivalent legacy endpoint is left
  /// untouched for FIT.Angular.
  /// </summary>
  public class RestoreUserItem : HttpFunctionBase
  {
    const string NAME = "teams-user-restore";
    private readonly RestoreUserController _controller;

    public RestoreUserItem(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider,
      ILogger<RestoreUserItem> logger,
      RestoreUserController controller)
    : base(appSettingsService, tokenProvider, logger)
    {
      this._controller = controller;
    }

    // Delete and restore are the same switch pointed two ways, so they take one
    // grant — the same reasoning permission-keys.ts documents for the reports
    // canArchive key, which covers archive and restore together. Before this,
    // a role with Edit-but-not-Delete could reverse a deletion it could not
    // itself perform.
    [Function(NAME)]
    [RequiredPermission(TeamsPermissions.UserDeleteId)]
    public async Task<IActionResult> Run(
      [HttpTrigger(AuthorizationLevel.Function, "post", Route = NAME)] HttpRequest req)
    {
      return await ExecuteRequest(req, async (req) =>
      {
        string requestBody = await new StreamReader(req.Body).ReadToEndAsync();
        var command = JsonConvert.DeserializeObject<RestoreUserCommand>(requestBody);

        await this._controller.HandleCommand(GetUserId(req), command);
        return new OkResult();
      }, "Failed to restore user");
    }
  }
}
