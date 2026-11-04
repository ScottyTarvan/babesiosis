using Babesiosis.Core.Models.Teams;
using Babesiosis.Core.Permissions;
using Babesiosis.Core.Permissions.Configs;
using Babesiosis.Core.Services;
using Babesiosis.Core.ViewModels;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Auth.Controllers
{
  /// <summary>
  /// Shared login tail for every authentication path — password and SSO alike.
  ///
  /// Authorisation runs off the cached permission set: <c>RequiredPermissionsMiddleware</c>
  /// reads it on every request and never touches the database, so a login that
  /// does not seed the cache leaves the user holding nothing and every gated
  /// endpoint answers 403. Seeding it is therefore not optional bookkeeping —
  /// it is the step that makes the session usable.
  /// </summary>
  public abstract class UserLoginController
  {
    private const string MANAGE = "manage";
    private const string PIPELINES = "pipelines";
    private const string REPORTS = "reports";
    private const string SETUP = "setup";
    private const string TEAMS = "teams";

    private readonly IUserPermissionsCacheService _userPermissionsCacheService;
    private readonly IPermissionsConfigService _permissionsConfigService;

    protected UserLoginController(IUserPermissionsCacheService userPermissionsCacheService,
      IPermissionsConfigService permissionsConfigService)
    {
      _userPermissionsCacheService = userPermissionsCacheService;
      _permissionsConfigService = permissionsConfigService;
    }

    /// <summary>
    /// Rebuilds the user's cached permissions from the database and returns the
    /// coarse navigation flags the shell renders its module switcher from.
    ///
    /// The flags are derived from the same set that was just cached, so what the
    /// sidebar offers and what the middleware admits cannot drift apart. A
    /// category is "viewable" when the user holds any permission declared under
    /// it — the per-screen gating is finer than this and arrives on each
    /// endpoint's own response.
    /// </summary>
    protected async Task<UserPermissionsViewModel> RefreshPermissionsAsync(User user)
    {
      HashSet<Guid> granted = await _userPermissionsCacheService.RefreshUserPermissionsCacheAsync(user.InstanceId);

      Dictionary<Guid, PermissionItem> declared = _permissionsConfigService.GetPermissions();

      //ensure that permissions in cache are still valid 
      HashSet<string> categories = granted
        .Where(declared.ContainsKey)
        .Select(id => declared[id].Category)
        .ToHashSet(StringComparer.OrdinalIgnoreCase);

      // The resolved set already carries the single admin rule (administrators hold
      // every non-SuperAdminOnly item), so these item checks need no admin branch.
      return new UserPermissionsViewModel()
      {
        CanViewManage = categories.Contains(MANAGE),
        CanViewPipelines = categories.Contains(PIPELINES),
        CanViewReporting = categories.Contains(REPORTS),
        CanViewSetup = categories.Contains(SETUP),
        CanViewTeams = categories.Contains(TEAMS),
        CanViewDataHealth = HoldsAny(granted, DataHealthDashboardReadId, DataHealthDashboardEditId),
        CanViewStatistics = HoldsAny(granted, DataHealthCollectorSettingsReadId, DataHealthCollectorSettingsEditId),
      };
    }

    private static readonly Guid DataHealthDashboardReadId = Guid.Parse(SetupPermissions.DataHealthDashboardReadId);
    private static readonly Guid DataHealthDashboardEditId = Guid.Parse(SetupPermissions.DataHealthDashboardEditId);
    private static readonly Guid DataHealthCollectorSettingsReadId = Guid.Parse(SetupPermissions.DataHealthCollectorSettingsReadId);
    private static readonly Guid DataHealthCollectorSettingsEditId = Guid.Parse(SetupPermissions.DataHealthCollectorSettingsEditId);

    /// <summary>Edit implies Read: either item of the pair shows the entry.</summary>
    private static bool HoldsAny(HashSet<Guid> granted, Guid readId, Guid editId)
    {
      return granted.Contains(readId) || granted.Contains(editId);
    }
  }
}
