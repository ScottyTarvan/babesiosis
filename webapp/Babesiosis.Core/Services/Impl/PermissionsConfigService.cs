using Babesiosis.Core.Permissions;
using NPOI.HSSF.Record.Aggregates;
using System;
using System.Collections.Generic;

namespace Babesiosis.Core.Services.Impl
{
  public class PermissionsConfigService : IPermissionsConfigService
  {
    private readonly Dictionary<Guid, PermissionItem> _permissions = new Dictionary<Guid, PermissionItem>();

    public PermissionsConfigService()
    {
    }

    public void AddPermissionConfiguration(Type permissionConfiguration)
    {
      IEnumerable<PermissionItem> items = PermissionsExtractor.GetPermissionItems(permissionConfiguration);
      foreach (var value in items)
      {
        _permissions[value.Id] = value;
      }
    }

    public Dictionary<Guid, PermissionItem> GetPermissions()
    {
      return _permissions;
    }
  }
}
