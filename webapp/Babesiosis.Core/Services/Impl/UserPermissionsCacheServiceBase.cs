using Babesiosis.Core.Data;
using Babesiosis.Core.Permissions;
using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace Babesiosis.Core.Services.Impl
{
  /// <summary>
  /// Shared plumbing for the blob-backed and in-memory implementations of
  /// <see cref="IUserPermissionsCacheService"/>: loading a fresh record from
  /// SQL, resolving a record into an effective permission set, and the 24-hour
  /// staleness check both implementations honour.
  /// <para>
  /// A subclass owns everything about how a record is stored and how long it
  /// is trusted without re-verification (the blob implementation's 5-minute L1
  /// TTL, for one) — that is its <see cref="GetUserPermissionsFromCacheAsync"/>
  /// and <see cref="SaveEntryAsync"/>. What is identical everywhere — the SQL
  /// query, the admin rule, and "is this record too old to trust at all" — lives
  /// here.
  /// </para>
  /// </summary>
  internal abstract class UserPermissionsCacheServiceBase : IUserPermissionsCacheService
  {
    private readonly IDbContextService _dbContextService;
    private readonly IPermissionsConfigService _permissionsConfigService;

    protected const string CACHE_KEY_PREFIX = "permissions:user:";

    /// <summary>
    /// A cached record older than this is reloaded from SQL regardless of any
    /// shorter-lived trust window in front of it — a self-heal for any missed
    /// invalidation. Shared by both implementations.
    /// </summary>
    protected static readonly TimeSpan MaxEntryAge = TimeSpan.FromHours(24);

    protected readonly TimeProvider Clock;

    protected UserPermissionsCacheServiceBase(IDbContextService dbContextService,
      IPermissionsConfigService permissionsConfigService,
      TimeProvider timeProvider)
    {
      _dbContextService = dbContextService;
      _permissionsConfigService = permissionsConfigService;
      Clock = timeProvider ?? TimeProvider.System;
    }

    public abstract Task<HashSet<Guid>> GetUserPermissionsFromCacheAsync(Guid userId);

    public abstract Task ClearUserPermissionsFromCacheAsync(Guid userId);

    public abstract Task RetryClearUserPermissionsFromCacheAsync(Guid userId);

    public abstract Task RetireUserPermissionsFromCacheAsync(Guid userId);

    public abstract Task RemoveUserPermissionsFromCacheAsync(Guid userId);

    /// <summary>
    /// How many per-user invalidations a role-level fan-out runs at once. Each is one
    /// small blob write, so the bound exists to keep a large role from opening hundreds
    /// of connections at once, not to throttle for cost.
    /// </summary>
    protected const int FAN_OUT_CONCURRENCY = 16;

    /// <summary>Writes a freshly loaded record to whatever store the subclass owns.</summary>
    protected abstract Task SaveEntryAsync(Guid userId, UserPermissionsCacheEntry entry);

    public virtual async Task<HashSet<Guid>> RefreshUserPermissionsCacheAsync(Guid userId)
    {
      UserPermissionsCacheEntry entry = await LoadEntryFromDbAsync(userId);

      await SaveEntryAsync(userId, entry);

      return Resolve(entry);
    }

    public virtual async Task ClearUsersInRoleFromCacheAsync(int roleId)
    {
      using var dbContext = _dbContextService.CreateDbContext<DbContextBase>();

      List<Guid> userIds = await dbContext.UserRoles
        .Where(ur => ur.RoleId == roleId)
        .Select(ur => ur.User.InstanceId)
        .ToListAsync();

      // One blob write per member, bounded-parallel: sequential writes made a role edit
      // wait one round trip per member, which is a visible stall past a few dozen members.
      // Each per-user clear swallows and logs its own failure (and enqueues a retry), so a
      // single bad write never stops the rest of the role from being invalidated.
      using var gate = new SemaphoreSlim(FAN_OUT_CONCURRENCY);

      IEnumerable<Task> clears = userIds.Select(async userId =>
      {
        await gate.WaitAsync();
        try
        {
          await ClearUserPermissionsFromCacheAsync(userId);
        }
        finally
        {
          gate.Release();
        }
      });

      await Task.WhenAll(clears);
    }

    /// <summary>Builds a fresh record from SQL. Never returns null.</summary>
    protected async Task<UserPermissionsCacheEntry> LoadEntryFromDbAsync(Guid userId)
    {
      using var dbContext = _dbContextService.CreateDbContext<DbContextBase>();

      var user = await dbContext.Users
        .FirstOrDefaultAsync(u => u.InstanceId == userId);

      // A deleted or unknown user holds no permissions, regardless of the roles still linked to them.
      if (user == null || user.IsDeleted)
      {
        return new UserPermissionsCacheEntry
        {
          Exists = false,
          RefreshedAtUtc = Clock.GetUtcNow()
        };
      }

      HashSet<Guid> grantedIds = await dbContext.UserRoles
        .Where(ur => ur.User.InstanceId == userId)
        .Join(dbContext.RolePermissionItems,
            ur => ur.RoleId,
            rp => rp.RoleId,
            (ur, rp) => rp.PermissionId)
        .Distinct()
        .ToHashSetAsync();

      return new UserPermissionsCacheEntry
      {
        Exists = true,
        IsAdministrator = user.IsAdministrator,
        IsSuperAdministrator = user.IsSuperAdministrator,
        GrantedIds = grantedIds,
        RefreshedAtUtc = Clock.GetUtcNow()
      };
    }

    /// <summary>
    /// THE ONE ADMIN RULE. An unknown/deleted record holds nothing. Otherwise,
    /// for each declared item: a <c>SuperAdminOnly</c> item is held only by a
    /// super administrator; every other item is held by a super administrator,
    /// an administrator, or a user whose roles granted it directly. A role
    /// grant never confers a <c>SuperAdminOnly</c> item.
    /// </summary>
    protected HashSet<Guid> Resolve(UserPermissionsCacheEntry entry)
    {
      if (entry == null || !entry.Exists)
      {
        return new HashSet<Guid>();
      }

      Dictionary<Guid, PermissionItem> declared = _permissionsConfigService.GetPermissions();
      var result = new HashSet<Guid>();

      foreach (var kv in declared)
      {
        PermissionItem item = kv.Value;

        bool held = item.SuperAdminOnly
          ? entry.IsSuperAdministrator
          : entry.IsSuperAdministrator || entry.IsAdministrator || entry.GrantedIds.Contains(item.Id);

        if (held)
        {
          result.Add(item.Id);
        }
      }

      return result;
    }

    /// <summary>True when the record is older than <see cref="MaxEntryAge"/> and must be reloaded from SQL.</summary>
    protected bool IsStale(UserPermissionsCacheEntry entry)
    {
      return Clock.GetUtcNow() - entry.RefreshedAtUtc > MaxEntryAge;
    }

    protected string GetCacheKey(Guid userId)
    {
      return $"{CACHE_KEY_PREFIX}{userId}";
    }
  }
}
