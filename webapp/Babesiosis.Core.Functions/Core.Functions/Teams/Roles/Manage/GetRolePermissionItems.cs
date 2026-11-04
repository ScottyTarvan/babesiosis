using Babesiosis.Core.Api.Teams.Roles.Manage.Controllers;
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

namespace Babesiosis.Core.Functions.Teams.Roles.Manage
{
  /// <summary>
  /// The role-permissions matrix for the new web application. Distinct from
  /// the legacy <c>teams-roles-permissions-get</c>, which serves the old
  /// subject/action tree from the <c>team.Permission</c> table and is still
  /// what FIT.Angular calls.
  /// </summary>
  public class GetRolePermissionItems : HttpFunctionBase
  {
    const string NAME = "teams-role-permissions-get";
    private readonly GetRolePermissionItemsController _controller;

    public GetRolePermissionItems(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider,
      ILogger<GetRolePermissionItems> logger,
      GetRolePermissionItemsController controller)
    : base(appSettingsService, tokenProvider, logger)
    {
      this._controller = controller;
    }

    [Function(NAME)]
    [RequiredPermission(TeamsPermissions.RolePermissionReadId)]
    public async Task<IActionResult> Run(
      [HttpTrigger(AuthorizationLevel.Function, "post", Route = NAME)] HttpRequest req)
    {
      return await ExecuteRequest(req, async (req) =>
      {
        string requestBody = await new StreamReader(req.Body).ReadToEndAsync();
        var command = JsonConvert.DeserializeObject<ActionItemCommand>(requestBody);

        var data = await this._controller.HandleCommand(GetUserId(req), command);
        return new OkObjectResult(data);
      }, "Failed to get role permissions");
    }
  }
}
