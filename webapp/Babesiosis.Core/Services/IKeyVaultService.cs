using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Babesiosis.Core.Services
{
  public interface IKeyVaultService
  {
    public Task<string> GetSecretAsync(string secretName);
    public Task SetSecretAsync(string secretName, string secretValue);
    public Task DeleteSecretAsync(string secretName);
    public Task PurgeSecretAsync(string secretName);
  }
}
