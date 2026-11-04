using Babesiosis.Core.Permissions;
using System;
using System.Threading.Tasks;

namespace Babesiosis.Core.Services
{
  /// <summary>
  /// Resolves the set of code-declared permissions a user holds.
  ///
  /// This is the new permission model's counterpart to
  /// <see cref="IUserPermissionsService"/>, which resolves the legacy
  /// subject/action grants. Both exist; the legacy one is untouched and still
  /// backs every Babesiosis.Angular endpoint.
  ///
  /// The implementation is a thin adapter over <see cref="IUserPermissionsCacheService"/>:
  /// it does not query SQL itself, it maps the cache service's resolved id set
  /// back to full <see cref="PermissionItem"/>s.
  /// </summary>
  public interface IUserPermissionItemsService
  {
    /// <summary>
    /// Every permission the user holds, keyed by id. Administrators receive
    /// every permission that is not <c>SuperAdminOnly</c>; super administrators
    /// receive all of them; everyone else receives what their roles grant.
    /// </summary>
    Task<PermissionsCache> GetUserPermissionsAsync(Guid userId);

    /// <summary>Convenience check for a single permission id.</summary>
    Task<bool> HasPermissionAsync(Guid userId, Guid permissionId);
  }
}
