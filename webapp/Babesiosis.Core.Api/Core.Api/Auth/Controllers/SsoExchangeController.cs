using Babesiosis.Core.Api.Auth.Commands;
using Babesiosis.Core.Api.Auth.ViewModels;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Services;
using Microsoft.Extensions.Logging;
using System;
using System.IO;
using System.Text.Json;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Auth.Controllers
{
  public class SsoExchangeController
  {
    // A code is single-use, but also reject anything older than this as a safety net.
    private static readonly TimeSpan CodeLifetime = TimeSpan.FromMinutes(5);

    private readonly IAppSettings _appSettings;
    private readonly IBlobStorageService _blobStorageService;
    private readonly ILogger _logger;

    public SsoExchangeController(IAppSettingsService appSettingsService,
      IBlobStorageService blobStorageService,
      ILogger<SsoExchangeController> logger)
    {
      this._appSettings = appSettingsService.GetAppSettings();
      this._blobStorageService = blobStorageService;
      this._logger = logger;
    }

    public async Task<LoginViewModel> HandleCommand(SsoExchangeCommand command)
    {
      if (string.IsNullOrEmpty(command?.Code))
      {
        return Failed("SSO login failed");
      }

      var container = _appSettings.Containers.SsoLogin;
      var blobName = $"{command.Code}.json";

      string json;
      try
      {
        var stream = await _blobStorageService.DownloadBlobAsync(container, blobName);
        if (stream == null)
        {
          return Failed("SSO login expired or already used");
        }

        using var reader = new StreamReader(stream);
        json = await reader.ReadToEndAsync();
      }
      catch (Exception ex)
      {
        _logger.LogError($"auth-sso-exchange download failed: [{ex.Message}]");
        return Failed("SSO login expired or already used");
      }

      // One-time use: remove the blob immediately so the code can't be replayed.
      try
      {
        await _blobStorageService.DeleteBlobAsync(container, blobName);
      }
      catch (Exception ex)
      {
        _logger.LogError($"auth-sso-exchange cleanup failed: [{ex.Message}]");
      }

      SsoLoginEnvelope envelope;
      try
      {
        envelope = JsonSerializer.Deserialize<SsoLoginEnvelope>(json, new JsonSerializerOptions
        {
          PropertyNameCaseInsensitive = true
        });
      }
      catch (Exception ex)
      {
        _logger.LogError($"auth-sso-exchange deserialize failed: [{ex.Message}]");
        return Failed("SSO login failed");
      }

      if (envelope?.Login == null)
      {
        return Failed("SSO login failed");
      }

      if (DateTime.UtcNow - envelope.CreatedUtc > CodeLifetime)
      {
        return Failed("SSO login expired");
      }

      return envelope.Login;
    }

    private static LoginViewModel Failed(string message)
    {
      return new LoginViewModel { Passed = false, Message = message };
    }
  }
}
