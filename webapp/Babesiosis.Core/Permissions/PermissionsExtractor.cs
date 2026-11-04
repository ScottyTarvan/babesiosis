using NPOI.SS.Formula.Functions;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;

namespace Babesiosis.Core.Permissions
{
  public static class PermissionsExtractor
  {
    public static IEnumerable<PermissionItem> GetPermissionItems(Type permissionConfiguration)
    {
      Type type = permissionConfiguration is Type ? permissionConfiguration : permissionConfiguration.GetType();
      return type
        .GetProperties(BindingFlags.Public | BindingFlags.Static | BindingFlags.Instance)
        .Where(p => p.PropertyType == typeof(PermissionItem))
        .Select(p => p.GetValue(p.GetMethod?.IsStatic == true ? null : permissionConfiguration) as PermissionItem)
        .Where(v => v != null);
    }
  }
}
