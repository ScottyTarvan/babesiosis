using Babesiosis.Core.Api.Teams.Users.Controllers;
using Babesiosis.Core.Commands;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Permissions.Attributes;
using Babesiosis.Core.Permissions.Configs;
using Babesiosis.Core.Security;
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
  public class RemoveUser : HttpFunctionBase
  {
    const string NAME = "teams-user-delete";
    private readonly DeleteUserController _controller;

    public RemoveUser(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider,
      ILogger<RemoveUser> logger,
      DeleteUserController controller)
    : base(appSettingsService, tokenProvider, logger)
    {
      this._controller = controller;
    }

    [Function(NAME)]
    [RequiredPermission(TeamsPermissions.UserDeleteId)]
    public async Task<IActionResult> Run(
      [HttpTrigger(AuthorizationLevel.Function, "post", Route = NAME)] HttpRequest req)
    {
      return await ExecuteRequest(req, async (req) =>
      {
        string requestBody = await new StreamReader(req.Body).ReadToEndAsync();
        var command = JsonConvert.DeserializeObject<ActionItemCommand>(requestBody);

        var data = await this._controller.HandleCommand(GetUserId(req), command);
        return new OkObjectResult(data);
      }, "Failed to delete user");
    }
  }
}
