using Azure.Security.KeyVault.Secrets;
using Babesiosis.Core.Configurations;
using Microsoft.Extensions.Logging;
using System;
using System.Threading.Tasks;

namespace Babesiosis.Core.Services.Impl
{
  internal class AzureKeyVaultService : IKeyVaultService
  {
    private readonly IAppSettings _appSettings;
    private readonly KeyVaultClientManager _clientManager;
    private readonly ILogger<AzureKeyVaultService> _logger;

    public AzureKeyVaultService(
      IAppSettings appSettings,
      KeyVaultClientManager clientManager,
      ILogger<AzureKeyVaultService> logger)
    {
      _appSettings = appSettings ?? throw new ArgumentNullException(nameof(appSettings));
      _clientManager = clientManager ?? throw new ArgumentNullException(nameof(clientManager));
      _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }
    
    public async Task<string> GetSecretAsync(string secretName)
    {
      try
      {
        _logger.LogInformation("Getting secret {SecretName} from Key Vault", secretName);
        var client = _clientManager.GetSecretClient();
        var secret = await client.GetSecretAsync(secretName);
        _logger.LogInformation("Successfully retrieved secret {SecretName}", secretName);
        return secret.Value.Value;
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to get secret {SecretName} from Key Vault", secretName);
        throw;
      }
    }

    public async Task SetSecretAsync(string secretName, string secretValue)
    {
      try
      {
        _logger.LogInformation("Setting secret {SecretName} in Key Vault", secretName);
        var client = _clientManager.GetSecretClient();
        await client.SetSecretAsync(secretName, secretValue);
        _logger.LogInformation("Successfully set secret {SecretName}", secretName);
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to set secret {SecretName} in Key Vault", secretName);
        throw;
      }
    }

    public async Task DeleteSecretAsync(string secretName)
    {
      try
      {
        _logger.LogInformation("Deleting secret {SecretName} from Key Vault", secretName);
        var client = _clientManager.GetSecretClient();
        await client.StartDeleteSecretAsync(secretName);
        _logger.LogInformation("Successfully deleted secret {SecretName}", secretName);
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to delete secret {SecretName} from Key Vault", secretName);
        throw;
      }
    }

    public async Task PurgeSecretAsync(string secretName)
    {
      try
      {
        _logger.LogInformation("Purging deleted secret {SecretName} from Key Vault", secretName);
        var client = _clientManager.GetSecretClient();
        await client.PurgeDeletedSecretAsync(secretName);
        _logger.LogInformation("Successfully purged secret {SecretName}", secretName);
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to purge secret {SecretName} from Key Vault", secretName);
        throw;
      }
    }
  }
}
