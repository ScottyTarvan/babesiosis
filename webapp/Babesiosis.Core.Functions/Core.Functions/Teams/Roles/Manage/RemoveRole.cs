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
  public class RemoveRole : HttpFunctionBase
  {
    const string NAME = "teams-role-delete";
    private readonly RemoveRoleController _controller;

    public RemoveRole(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider,
      ILogger<RemoveRole> logger,
      RemoveRoleController controller)
    : base(appSettingsService, tokenProvider, logger)
    {
      this._controller = controller;
    }

    [Function(NAME)]
    [RequiredPermission(TeamsPermissions.RoleDeleteId)]
    public async Task<IActionResult> Run(
      [HttpTrigger(AuthorizationLevel.Function, "post", Route = NAME)] HttpRequest req)
    {
      return await ExecuteRequest(req, async (req) =>
      {
        string requestBody = await new StreamReader(req.Body).ReadToEndAsync();
        var command = JsonConvert.DeserializeObject<ActionItemCommand>(requestBody);

        await this._controller.HandleCommand(GetUserId(req), command);
        return new OkResult();
      }, "Failed to delete role");
    }
  }
}
