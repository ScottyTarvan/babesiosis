using Babesiosis.Core.Api.Teams.Users.Commands;
using Babesiosis.Core.Api.Teams.Users.Manage.Controllers;
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
  public class CreateUser : HttpFunctionBase
  {
    const string NAME = "teams-user-add";
    private readonly CreateUserController _controller;

    public CreateUser(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider,
      ILogger<CreateUser> logger,
      CreateUserController controller)
    : base(appSettingsService, tokenProvider, logger)
    {
      this._controller = controller;
    }

    [Function(NAME)]
    [RequiredPermission(TeamsPermissions.UserAddId)]
    public async Task<IActionResult> Run(
      [HttpTrigger(AuthorizationLevel.Function, "post", Route = NAME)] HttpRequest req)
    {
      return await ExecuteRequest(req, async (req) =>
      {
        string requestBody = await new StreamReader(req.Body).ReadToEndAsync();
        var command = JsonConvert.DeserializeObject<UserCommand>(requestBody);

        var data = await this._controller.HandleCommand(GetUserId(req), command);
        return new OkObjectResult(data);
      }, "Failed to create user");
    }
  }
}
