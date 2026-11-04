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
  public class UpdateRole : HttpFunctionBase
  {
    const string NAME = "teams-role-edit";
    private readonly UpdateRoleController _controller;

    public UpdateRole(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider,
      ILogger<UpdateRole> logger,
      UpdateRoleController controller)
    : base(appSettingsService, tokenProvider, logger)
    {
      this._controller = controller;
    }

    [Function(NAME)]
    [RequiredPermission(TeamsPermissions.RoleEditId)]
    public async Task<IActionResult> Run(
      [HttpTrigger(AuthorizationLevel.Function, "post", Route = NAME)] HttpRequest req)
    {
      return await ExecuteRequest(req, async (req) =>
      {
        string requestBody = await new StreamReader(req.Body).ReadToEndAsync();
        var command = JsonConvert.DeserializeObject<RoleItemCommand>(requestBody);

        var data = await this._controller.HandleCommand(GetUserId(req), command);
        return new OkObjectResult(data);
      }, "Failed to update role");
    }
  }
}
