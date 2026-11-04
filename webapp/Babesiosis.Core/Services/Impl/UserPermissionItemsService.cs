using Babesiosis.Core.Diagnostics;
using Babesiosis.Core.Permissions;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Babesiosis.Core.Services.Impl
{
  /// <summary>
  /// Thin adapter over <see cref="IUserPermissionsCacheService"/>: resolves the
  /// declared <see cref="PermissionItem"/>s a user holds from the cached,
  /// resolved id set, rather than querying SQL itself.
  ///
  /// The cache service already applies THE ONE ADMIN RULE (administrator holds
  /// everything except <c>SuperAdminOnly</c>, super administrator holds
  /// everything, everyone else holds what their roles grant); this class only
  /// maps the resolved ids back to full <see cref="PermissionItem"/>s and
  /// memoises the result. The service is registered transient, so the memo
  /// lives for one function invocation.
  /// </summary>
  internal class UserPermissionItemsService : IUserPermissionItemsService
  {
    private readonly IUserPermissionsCacheService _userPermissionsCacheService;
    private readonly IPermissionsConfigService _permissionsConfigService;
    private readonly Dictionary<Guid, PermissionsCache> _cache = new Dictionary<Guid, PermissionsCache>();

    internal UserPermissionItemsService(IUserPermissionsCacheService userPermissionsCacheService,
      IPermissionsConfigService permissionsConfigService)
    {
      _userPermissionsCacheService = userPermissionsCacheService;
      _permissionsConfigService = permissionsConfigService;
    }

    public async Task<PermissionsCache> GetUserPermissionsAsync(Guid userId)
    {
      if (_cache.TryGetValue(userId, out var cached))
      {
        return cached;
      }

      // Below the memo, so the span appears once per service instance rather than
      // once per call. The service is transient — a second `permissions.resolve`
      // in one request means a second instance was built, which is worth seeing.
      using var timing = RequestTimings.Time("permissions.resolve");

      HashSet<Guid> grantedIds = await _userPermissionsCacheService.GetUserPermissionsFromCacheAsync(userId);
      Dictionary<Guid, PermissionItem> declared = _permissionsConfigService.GetPermissions();

      var permissions = declared
        .Where(p => grantedIds.Contains(p.Key))
        .Select(p => p.Value)
        .ToList();

      return Store(userId, new PermissionsCache(permissions));
    }

    public async Task<bool> HasPermissionAsync(Guid userId, Guid permissionId)
    {
      var permissions = await GetUserPermissionsAsync(userId);
      return permissions.HasPermission(permissionId);
    }

    private PermissionsCache Store(Guid userId, PermissionsCache permissions)
    {
      _cache[userId] = permissions;
      return permissions;
    }
  }
}
