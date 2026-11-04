using System;

namespace Babesiosis.Core.Permissions.Attributes
{
  /// <summary>
  /// Declares the permission(s) a function entry point requires. Enforced by
  /// <c>RequiredPermissionsMiddleware</c> in the function app before the
  /// function body runs.
  ///
  /// Multiple ids are OR-ed — the caller needs any one of them.
  ///
  /// A function with no attribute is not permission-checked by the middleware
  /// at all. That is what keeps every legacy endpoint behaving exactly as it
  /// did before this attribute existed.
  /// </summary>
  [AttributeUsage(AttributeTargets.Method, AllowMultiple = false)]
  public class RequiredPermissionAttribute : Attribute
  {
    public RequiredPermissionAttribute(params string[] permissionIds)
    {
      PermissionIds = permissionIds;
    }

    public string[] PermissionIds { get; }

    public override string ToString()
    {
      return string.Join(" or ", PermissionIds);
    }
  }
}
