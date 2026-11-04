using Babesiosis.Core.Configurations;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;

namespace Babesiosis.Core.Services.Impl
{
  internal class LocalKeyVaultService : IKeyVaultService
  {
    private readonly IAppSettings _appSettings;
    private readonly string _localPath;
    private readonly AzureKeyVaultService _azureKeyVaultService;

    public LocalKeyVaultService(
      string localPath,
      IAppSettings appSettings,
      KeyVaultClientManager clientManager,
      ILogger<AzureKeyVaultService> azureLogger)
    {
      _appSettings = appSettings ?? throw new ArgumentNullException(nameof(appSettings));
      _localPath = localPath;

      _azureKeyVaultService = new AzureKeyVaultService(appSettings, clientManager, azureLogger);
    }

    public async Task<string> GetSecretAsync(string secretName)
    {
      var keyValues = ReadKeyValues();
      if (keyValues.Exists(a => a.Key == secretName))
      {
        return keyValues.Find(a => a.Key == secretName).Value;
      }
      else
      {
        try
        {
          var result = await _azureKeyVaultService.GetSecretAsync(secretName);
          await SetSecretAsync(secretName, result);
          return result;
        }
        catch (Exception)
        {
          return null;
        }
      }
    }

    public async Task SetSecretAsync(string secretName, string secretValue)
    {
      var keyValues = ReadKeyValues();
      if (keyValues.Exists(a => a.Key == secretName))
      {
        var keyValue = keyValues.Find(a => a.Key == secretName);
        keyValues.Remove(keyValue);
      }

      keyValues.Add(new KeyValue() { Key = secretName, Value = secretValue });
      WriteKeyValues(keyValues);
      await _azureKeyVaultService.SetSecretAsync(secretName, secretValue);
    }

    public async Task DeleteSecretAsync(string secretName)
    {
      var keyValues = ReadKeyValues();
      if (keyValues.Exists(a => a.Key == secretName))
      {
        var keyValue = keyValues.Find(a => a.Key == secretName);
        keyValues.Remove(keyValue);
      }
      WriteKeyValues(keyValues);
      await _azureKeyVaultService.DeleteSecretAsync(secretName);
    }

    public async Task PurgeSecretAsync(string secretName)
    {
      var keyValues = ReadKeyValues();
      if (keyValues.Exists(a => a.Key == secretName))
      {
        var keyValue = keyValues.Find(a => a.Key == secretName);
        keyValues.Remove(keyValue);
      }

      WriteKeyValues(keyValues);
    }

    private List<KeyValue> ReadKeyValues()
    {
      var directory = new DirectoryInfo(_localPath);
      var root = directory.Parent.Parent.Parent.Parent;
      string path = Path.Combine(root.FullName, "Configurations", "keyvault.json");

      if (File.Exists(path))
      {
        var json = File.ReadAllText(path);
        return Newtonsoft.Json.JsonConvert.DeserializeObject<List<KeyValue>>(json);
      }
      else
      {
        var keyValues = new List<KeyValue>();
        File.WriteAllText(path, Newtonsoft.Json.JsonConvert.SerializeObject(keyValues));
        return keyValues;
      }
    }

    private void WriteKeyValues(List<KeyValue> keyValues)
    {
      var directory = new DirectoryInfo(_localPath);
      var root = directory.Parent.Parent.Parent.Parent;
      string path = Path.Combine(root.FullName, "Configurations", "keyvault.json");

      File.WriteAllText(path, Newtonsoft.Json.JsonConvert.SerializeObject(keyValues));
    }

    private class KeyValue
    {
      public string Key { get; set; }
      public string Value { get; set; }
    }
  }
}
