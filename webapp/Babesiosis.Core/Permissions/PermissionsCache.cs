using System;
using System.Collections.Generic;

namespace Babesiosis.Core.Permissions
{
  /// <summary>
  /// An immutable-in-practice lookup of <see cref="PermissionItem"/> by Id.
  /// Used twice: once as the process-wide registry of every declared
  /// permission (<c>PermissionsConfigService</c>), and once per user as the set
  /// they actually hold (<c>IUserPermissionItemsService</c>).
  /// </summary>
  public class PermissionsCache
  {
    private readonly Dictionary<Guid, PermissionItem> _cache;

    public PermissionsCache()
    {
      _cache = new Dictionary<Guid, PermissionItem>();
    }

    public PermissionsCache(IEnumerable<PermissionItem> permissions)
    {
      _cache = new Dictionary<Guid, PermissionItem>();

      foreach (var permission in permissions)
      {
        AddPermission(permission);
      }
    }

    public void AddPermission(PermissionItem permission)
    {
      _cache.Add(permission.Id, permission);
    }

    public IEnumerable<PermissionItem> GetPermissions()
    {
      return _cache.Values;
    }

    public PermissionItem GetPermission(Guid instanceId)
    {
      return _cache.TryGetValue(instanceId, out var permission) ? permission : null;
    }

    public PermissionItem GetPermission(PermissionItem permission)
    {
      return permission == null ? null : GetPermission(permission.Id);
    }

    public bool HasPermission(Guid instanceId)
    {
      return GetPermission(instanceId) != null;
    }

    public bool HasPermission(PermissionItem permission)
    {
      return GetPermission(permission) != null;
    }
  }
}
