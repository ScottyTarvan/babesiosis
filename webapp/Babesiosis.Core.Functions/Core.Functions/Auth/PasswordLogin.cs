using Babesiosis.Core.Api.Auth.Commands;
using Babesiosis.Core.Api.Auth.Controllers;
using Babesiosis.Core.Api.Teams.Users.Commands;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Security;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;

namespace Babesiosis.Core.Functions.Auth
{
  public class PasswordLogin : HttpFunctionBase
  {
    const string NAME = "auth-password-login";
    private readonly PasswordLoginController _controller;

    public PasswordLogin(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider, 
      ILogger<PasswordLogin> logger,
      PasswordLoginController controller)
    : base(appSettingsService, tokenProvider, logger)
    {
      this._controller = controller;
    }

    [Function(NAME)]
    public async Task<IActionResult> Run([HttpTrigger(AuthorizationLevel.Function, "post", Route = NAME)] HttpRequest req)
    {
      return await ExecuteRequest(
        req,  
        async (req) =>
        {
          string requestBody = await new StreamReader(req.Body).ReadToEndAsync();
          var command = JsonConvert.DeserializeObject<PasswordLoginCommand>(requestBody);
          var result = await _controller.HandleCommand(command);
          return new OkObjectResult(result);
        }, 
        requireJwt: false,
        "Login failed");
    }
  }
}
