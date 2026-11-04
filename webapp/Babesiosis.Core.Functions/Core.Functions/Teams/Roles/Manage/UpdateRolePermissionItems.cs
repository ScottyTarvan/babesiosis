using Babesiosis.Core.Api.Teams.Roles.Manage.Commands;
using Babesiosis.Core.Api.Teams.Roles.Manage.Controllers;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Permissions.Attributes;
using Babesiosis.Core.Permissions.Configs;
using Babesiosis.Core.Security;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;

namespace Babesiosis.Core.Functions.Teams.Roles.Manage
{
  public class UpdateRolePermissionItems : HttpFunctionBase
  {
    const string NAME = "teams-role-permissions-update";
    private readonly UpdateRolePermissionItemsController _controller;

    public UpdateRolePermissionItems(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider,
      ILogger<UpdateRolePermissionItems> logger,
      UpdateRolePermissionItemsController controller)
    : base(appSettingsService, tokenProvider, logger)
    {
      this._controller = controller;
    }

    [Function(NAME)]
    [RequiredPermission(TeamsPermissions.RolePermissionEditId)]
    public async Task<IActionResult> Run(
      [HttpTrigger(AuthorizationLevel.Function, "post", Route = NAME)] HttpRequest req)
    {
      return await ExecuteRequest(req, async (req) =>
      {
        string requestBody = await new StreamReader(req.Body).ReadToEndAsync();
        var command = JsonConvert.DeserializeObject<UpdateRolePermissionsCommand>(requestBody);

        await this._controller.HandleCommand(GetUserId(req), command);
        return new OkResult();
      }, "Failed to update role permissions");
    }
  }
}
