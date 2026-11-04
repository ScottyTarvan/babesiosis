using Babesiosis.Core.Permissions;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Babesiosis.Core.Services
{
  public interface IPermissionsConfigService
  {
    public void AddPermissionConfiguration(Type permission);
    public Dictionary<Guid, PermissionItem> GetPermissions();
  }
}
