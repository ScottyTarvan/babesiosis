using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Babesiosis.Core.Services
{
  /// <summary>
  /// The shared per-user permissions cache that backs <c>[RequiredPermission]</c>
  /// authorisation. SQL remains the source of truth; this resolves the
  /// effective permission set from a cached record — Blob Storage, with a
  /// per-instance L1 in front of it — instead of querying SQL on every
  /// request. See <c>UserPermissionsCacheServiceBase</c> for the resolution
  /// rule (THE ONE ADMIN RULE) and the staleness policy.
  /// </summary>
  public interface IUserPermissionsCacheService
  {
    /// <summary>
    /// The effective set of permission ids the user currently holds, resolved
    /// at read time against the declared permission catalogue.
    /// </summary>
    Task<HashSet<Guid>> GetUserPermissionsFromCacheAsync(Guid userId);

    /// <summary>
    /// Invalidates the cached record for a specific user — the per-instance L1
    /// entry and the shared (blob) entry alike.
    /// </summary>
    Task ClearUserPermissionsFromCacheAsync(Guid userId);

    /// <summary>
    /// Invalidates the cached record for every user currently assigned the
    /// given role. Mutation controllers call this, after <c>SaveChangesAsync</c>,
    /// whenever a role's permission grants change.
    /// </summary>
    Task ClearUsersInRoleFromCacheAsync(int roleId);

    /// <summary>
    /// Second attempt at an invalidation whose first attempt could not reach the shared
    /// cache. Unlike <see cref="ClearUserPermissionsFromCacheAsync"/> this THROWS on
    /// failure, so a queue-triggered caller can let the message be redelivered and, after
    /// the delivery limit, dead-lettered rather than silently dropped.
    /// </summary>
    Task RetryClearUserPermissionsFromCacheAsync(Guid userId);

    /// <summary>
    /// The user has been deleted: revoke now (a tombstone, exactly as
    /// <see cref="ClearUserPermissionsFromCacheAsync"/>) and arrange for the record to be
    /// removed from the shared cache later, once no reload that read SQL before the delete
    /// can still be in flight. Never throws.
    /// </summary>
    Task RetireUserPermissionsFromCacheAsync(Guid userId);

    /// <summary>
    /// Deletes the user's record from the shared cache. THROWS on failure, for the same
    /// reason <see cref="RetryClearUserPermissionsFromCacheAsync"/> does. Safe to call for a
    /// user that was later restored: the next read simply reloads from SQL.
    /// </summary>
    Task RemoveUserPermissionsFromCacheAsync(Guid userId);

    /// <summary>
    /// Reloads the user's record from the database and writes it to the
    /// cache, replacing any existing entry. Returns the freshly resolved
    /// effective permission set.
    /// </summary>
    Task<HashSet<Guid>> RefreshUserPermissionsCacheAsync(Guid userId);
  }
}
