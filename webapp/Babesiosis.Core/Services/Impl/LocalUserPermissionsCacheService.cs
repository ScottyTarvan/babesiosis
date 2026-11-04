using Babesiosis.Core.Data;
using Babesiosis.Core.Permissions;
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Babesiosis.Core.Services.Impl
{
  // In-memory cache used when running under the debugger to avoid slow blob storage round-trips.
  // Registered as a singleton, so the dictionary lives for the duration of the debug session.
  internal class LocalUserPermissionsCacheService : UserPermissionsCacheServiceBase
  {
    private readonly ConcurrentDictionary<Guid, UserPermissionsCacheEntry> _cache = new ConcurrentDictionary<Guid, UserPermissionsCacheEntry>();

    public LocalUserPermissionsCacheService(IDbContextService dbContextService,
      IPermissionsConfigService permissionsConfigService,
      TimeProvider timeProvider = null)
      : base(dbContextService, permissionsConfigService, timeProvider ?? TimeProvider.System)
    {
    }

    public override async Task<HashSet<Guid>> GetUserPermissionsFromCacheAsync(Guid userId)
    {
      if (_cache.TryGetValue(userId, out UserPermissionsCacheEntry entry) && !IsStale(entry))
      {
        return Resolve(entry);
      }

      entry = await LoadEntryFromDbAsync(userId);
      await SaveEntryAsync(userId, entry);

      return Resolve(entry);
    }

    public override Task ClearUserPermissionsFromCacheAsync(Guid userId)
    {
      _cache.TryRemove(userId, out _);
      return Task.CompletedTask;
    }

    // In-memory removal cannot fail, so a retry is just another clear.
    public override Task RetryClearUserPermissionsFromCacheAsync(Guid userId)
    {
      return ClearUserPermissionsFromCacheAsync(userId);
    }

    // Nothing to schedule: there is no shared store to drain later.
    public override Task RetireUserPermissionsFromCacheAsync(Guid userId)
    {
      return ClearUserPermissionsFromCacheAsync(userId);
    }

    public override Task RemoveUserPermissionsFromCacheAsync(Guid userId)
    {
      return ClearUserPermissionsFromCacheAsync(userId);
    }

    protected override Task SaveEntryAsync(Guid userId, UserPermissionsCacheEntry entry)
    {
      _cache[userId] = entry;
      return Task.CompletedTask;
    }
  }
}
