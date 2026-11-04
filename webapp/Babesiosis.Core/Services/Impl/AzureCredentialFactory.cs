using Azure.Core;
using Azure.Identity;
using Babesiosis.Core.Extensions;
using System;
using System.Collections.Concurrent;
using System.Diagnostics;

namespace Babesiosis.Core.Services.Impl
{
  /// <summary>
  /// Builds and caches the TokenCredential used by the Azure client managers.
  ///
  /// Three things this exists to guarantee:
  ///
  /// 1. One credential instance per configuration, for the life of the process.
  ///    Azure.Identity caches tokens *inside* the credential instance, so creating a new
  ///    DefaultAzureCredential per client re-walks the whole probe chain and can land on a
  ///    different credential - and therefore a different tenant - each time.
  ///
  /// 2. An explicit tenant. Each developer credential (Visual Studio, Azure CLI, Azure PowerShell,
  ///    azd) otherwise defaults to whichever tenant *it* is signed into. When the target resource
  ///    lives outside the developer's home tenant, whichever credential happens to win the chain
  ///    decides whether the token is valid, which shows up as intermittent 401/403s.
  ///
  /// 3. Managed identity whenever we are not being debugged. The developer credential chain cannot
  ///    acquire a token on an Azure host, so selecting it there fails outright with
  ///    CredentialUnavailableException. We only ever run locally under the debugger, so the absence
  ///    of one means "deployed". Deliberately not configurable: a config key that must be set for a
  ///    deployed app to authenticate at all is a key that will eventually be missing.
  /// </summary>
  internal static class AzureCredentialFactory
  {
    private static readonly ConcurrentDictionary<string, TokenCredential> _credentials
      = new ConcurrentDictionary<string, TokenCredential>();

    /// <summary>
    /// Gets a cached credential for the given settings.
    /// </summary>
    /// <param name="tenantId">Entra tenant that owns the target resource. Required when it is not the developer's home tenant.</param>
    /// <param name="managedIdentityClientId">Client id of a user-assigned managed identity. Null/empty uses the system-assigned identity.</param>
    public static TokenCredential GetCredential(string tenantId, string managedIdentityClientId = null)
    {
      // No debugger attached means we are not on a developer machine, so managed identity is the
      // only credential that can succeed.
      var useManagedIdentity = !Debugger.IsAttached;
      var cacheKey = $"{useManagedIdentity}::{tenantId}::{managedIdentityClientId}";

      return _credentials.GetOrAdd(cacheKey, _ => Build(useManagedIdentity, tenantId, managedIdentityClientId));
    }

    /// <summary>
    /// Clears cached credentials - primarily for testing purposes.
    /// </summary>
    public static void ClearCache()
    {
      _credentials.Clear();
    }

    private static TokenCredential Build(bool useManagedIdentity, string tenantId, string managedIdentityClientId)
    {
      if (useManagedIdentity)
      {
        // Deployed: ManagedIdentityCredential is explicit, secure and skips the probe chain.
        return managedIdentityClientId.HasValue()
          ? new ManagedIdentityCredential(managedIdentityClientId)
          : new ManagedIdentityCredential();
      }

      // Local debugging only: DefaultAzureCredential (Visual Studio, Azure CLI, Azure PowerShell, azd).
      var options = new DefaultAzureCredentialOptions
      {
        ExcludeVisualStudioCredential = false,
        // Never pop a browser: fail with a clear Azure.Identity error instead of hanging on a login prompt.
        ExcludeInteractiveBrowserCredential = true,
        // These never succeed on a dev machine but are probed first and can stall on corporate networks.
        ExcludeManagedIdentityCredential = true,
        ExcludeWorkloadIdentityCredential = true
      };

      if (tenantId.HasValue())
      {
        options.TenantId = tenantId;
        // Required since Azure.Identity 1.7: without this, a credential whose home tenant differs
        // throws "The current credential is not configured to acquire tokens for tenant ...".
        options.AdditionallyAllowedTenants.Add(tenantId);
      }
      else
      {
        // No tenant configured - allow cross-tenant so a foreign-tenant challenge does not hard fail.
        options.AdditionallyAllowedTenants.Add("*");
      }

      return new DefaultAzureCredential(options);
    }
  }
}
