using Babesiosis.Core.Api.Auth.ViewModels;
using Babesiosis.Core.Configurations;
using Microsoft.Identity.Client;
using System;
using System.Threading.Tasks;

public class SsoInitiateController
{
  private readonly IAppSettings _appSettings;

  public SsoInitiateController(IAppSettingsService appSettingsService)
  {
    _appSettings = appSettingsService.GetAppSettings();
  }

  public async Task<SsoInitiateViewModel> InitiateSsoLogin()
  {
    var app = ConfidentialClientApplicationBuilder
      .Create(_appSettings.Security.EntraIdClientId)
      .WithClientSecret(_appSettings.Security.EntraIdClientSecret)
      .WithAuthority(AzureCloudInstance.AzurePublic, _appSettings.Security.EntraIdTenantId)
      .WithRedirectUri(_appSettings.Security.EntraIdRedirectUri)
      .Build();

    var scopes = new[] { "openid", "profile", "email" };

    var authUrl = await app.GetAuthorizationRequestUrl(scopes)
    .WithRedirectUri(_appSettings.Security.EntraIdRedirectUri)
    .WithPrompt(Prompt.ForceLogin)
    .ExecuteAsync();

    var requestId = Guid.NewGuid().ToString();

    return new SsoInitiateViewModel
    {
      RedirectUrl = authUrl.ToString(),
      RequestId = requestId
    };
  }
}