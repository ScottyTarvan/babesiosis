using Babesiosis.Core.Api.Teams.Users.Commands;
using Babesiosis.Core.Api.Teams.Users.Controllers;
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
  public class GetUserRoleList : HttpFunctionBase
  {
    const string NAME = "teams-user-roles-get";
    private readonly GetUserRolesController _controller;

    public GetUserRoleList(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider,
      ILogger<GetUserRoleList> logger,
      GetUserRolesController controller)
    : base(appSettingsService, tokenProvider, logger)
    {
      this._controller = controller;
    }

    [Function(NAME)]
    [RequiredPermission(TeamsPermissions.UserRoleReadId)]
    public async Task<IActionResult> Run(
      [HttpTrigger(AuthorizationLevel.Function, "post", Route = NAME)] HttpRequest req)
    {
      return await ExecuteRequest(req, async (req) =>
      {
        string requestBody = await new StreamReader(req.Body).ReadToEndAsync();
        var command = JsonConvert.DeserializeObject<GetUserRolesCommand>(requestBody);

        var data = await this._controller.HandleCommand(GetUserId(req), command);
        return new OkObjectResult(data);
      }, "Failed to get user roles");
    }
  }
}
