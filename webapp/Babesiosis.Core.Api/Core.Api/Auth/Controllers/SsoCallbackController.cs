using AutoMapper;
using Babesiosis.Core.Api.Auth.Commands;
using Babesiosis.Core.Api.Auth.ViewModels;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Data;
using Babesiosis.Core.Models.Teams;
using Babesiosis.Core.Security;
using Babesiosis.Core.Services;
using Babesiosis.Core.ViewModels;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using Microsoft.Identity.Client;
using System;
using System.IdentityModel.Tokens.Jwt;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Auth.Controllers
{
  public class SsoCallbackController : UserLoginController
  {
    private readonly IAppSettings _appSettings;
    private readonly IDbContextService _dbContextService;
    private readonly IJwtTokenGenerator _jwtTokenGenerator;
    private readonly IMapper _mapper;
    private readonly IBlobStorageService _blobStorageService;
    private readonly ILogger _logger;

    public SsoCallbackController(IAppSettingsService appSettingsService,
      IDbContextService dbContextService,
      IJwtTokenGenerator jwtTokenGenerator,
      IMapper mapper,
      IBlobStorageService blobStorageService,
      IUserPermissionsCacheService userPermissionsCacheService,
      IPermissionsConfigService permissionsConfigService,
      ILogger<SsoCallbackController> logger)
      : base(userPermissionsCacheService, permissionsConfigService)
    {
      this._appSettings = appSettingsService.GetAppSettings();
      this._dbContextService = dbContextService;
      this._jwtTokenGenerator = jwtTokenGenerator;
      this._mapper = mapper;
      this._blobStorageService = blobStorageService;
      this._logger = logger;
    }

    public async Task<string> HandleCommand(SsoCallbackCommand command)
    {
      try
      {
        var app = ConfidentialClientApplicationBuilder
          .Create(_appSettings.Security.EntraIdClientId)
          .WithClientSecret(_appSettings.Security.EntraIdClientSecret)
          .WithAuthority(AzureCloudInstance.AzurePublic, _appSettings.Security.EntraIdTenantId)
          .WithRedirectUri(_appSettings.Security.EntraIdRedirectUri)
          .Build();

        var scopes = new[] { "openid", "profile", "email" };

        var result = await app.AcquireTokenByAuthorizationCode(scopes, command.Code)
          .ExecuteAsync();

        var email = result.Account?.Username;

        if (string.IsNullOrEmpty(email) && !string.IsNullOrEmpty(result.IdToken))
        {
          var handler = new JwtSecurityTokenHandler();
          var jwtToken = handler.ReadJwtToken(result.IdToken);
          email = jwtToken.Claims.FirstOrDefault(c => c.Type == "email")?.Value;
        }

        if (string.IsNullOrEmpty(email))
        {
          return BuildErrorRedirectUrl("No valid email claim found in authentication response.");
        }

        using var dbContext = _dbContextService.CreateDbContext<AuthDbContext>();

        User user = await dbContext.Users
         .Include(u => u.UserRoles)
         .Where(u => u.IsDeleted != true)
         .FirstOrDefaultAsync(a => a.Email == email);

        Assertion.IsNotNull(user, "User email is invalid");

        string token = _jwtTokenGenerator.CreateToken(user.InstanceId, _appSettings.Jwt.ExpiryTimeSpan);
        string refreshToken = _jwtTokenGenerator.CreateToken(user.InstanceId, _appSettings.Jwt.RefreshTokenExpiryTimeSpan);
        var userViewModel = _mapper.Map<UserViewModel>(user);
        userViewModel.Permissions = await RefreshPermissionsAsync(user);

        var loginViewModel = new LoginViewModel()
        {
          Passed = true,
          Message = "Login successful",
          User = userViewModel,
          AuthToken = token,
          RefreshToken = refreshToken
        };

        return await BuildRedirectUrl(loginViewModel);
      }
      catch (Exception ex)
      {
        _logger.LogError($"auth-sso-callback failed: [{ex.Message}]");
        _logger.LogError($"auth-sso-callback trace: [{ex.StackTrace}]");
        return BuildErrorRedirectUrl(ex.Message);
      }
    }

    private async Task<string> BuildRedirectUrl(LoginViewModel loginViewModel)
    {
      // Persist the login payload (incl. tokens) to blob storage keyed by a one-time
      // code, so the redirect URL stays short and tokens never travel in the query string.
      var code = Guid.NewGuid().ToString("N");
      var envelope = new SsoLoginEnvelope { CreatedUtc = DateTime.UtcNow, Login = loginViewModel };
      var json = JsonSerializer.Serialize(envelope, new JsonSerializerOptions
      {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase
      });

      using var stream = new MemoryStream(Encoding.UTF8.GetBytes(json));
      await _blobStorageService.AddBlobAsync(_appSettings.Containers.SsoLogin, $"{code}.json", stream, "application/json");

      //calls back into the angular web app with this route
      return $"{_appSettings.WebApp.Url.TrimEnd('/')}/auth/sso-callback?code={code}";
    }

    private string BuildErrorRedirectUrl(string errorMessage)
    {
      //calls back into the angular web app with this route 
      var escapedMessage = Uri.EscapeDataString(errorMessage);
      return $"{_appSettings.WebApp.Url.TrimEnd('/')}/auth/sso-callback?error={escapedMessage}";
    }
  }
}
