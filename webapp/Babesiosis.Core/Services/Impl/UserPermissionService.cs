using Babesiosis.Core.Assertions;
using Babesiosis.Core.Data;
using Babesiosis.Core.Models.Teams;
using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;

namespace Babesiosis.Core.Services.Impl
{
  internal class UserPermissionService : IUserPermissionsService
  {
    private readonly IDbContextService _dbContextService;
    private readonly IPermissionContext _permissionContext;
    private Dictionary<Guid, Dictionary<string, HashSet<string>>> _permissionCache = new Dictionary<Guid, Dictionary<string, HashSet<string>>>();
    private User _userCache;

    public UserPermissionService(IDbContextService dbContextService,
      IPermissionContext permissionContext = null)
    {
      _dbContextService = dbContextService;
      _permissionContext = permissionContext;
    }

    public bool Can(Guid userId, string action, string subject)
    {
      var permissions = BuildPermissions(userId);

      HashSet<string> actions;
      bool admin = permissions.TryGetValue("all", out actions) && actions.Contains("manage");
      bool read = permissions.TryGetValue("all", out actions) && actions.Contains("read") && action == "read";
      bool manage = permissions.TryGetValue(subject, out actions) && actions.Contains("manage");
      bool rule = permissions.TryGetValue(subject, out actions) && actions.Contains(action);

      return admin || read || manage || rule;
    }

    public void Assert(Guid userId, string action, string subject)
    {
      // Already decided at the function layer by [RequiredPermission] against
      // the code-declared permission model — see IPermissionContext. Requests
      // from the legacy application never set this, so their behaviour is
      // unchanged.
      if (_permissionContext?.IsPreAuthorized == true)
      {
        return;
      }

      var can = IsAdministrator(userId) || Can(userId, action, subject);
      Assertion.True(can, $"You do not have access to {action} {subject}");
    }


    public bool IsAdministrator(Guid userId)
    {
      if(_userCache != null)
      {
        return _userCache.IsAdministrator;
      }
      else
      {
        using var dbContext = _dbContextService.CreateDbContext<DbContextBase>();

        var user = dbContext.Users.FirstOrDefault(u => u.InstanceId == userId);
        Assertion.IsNotNull(user, $"User with id '{userId}' is invalid");

        _userCache = user;
        return user.IsAdministrator;
      }
    }

    private Dictionary<string, HashSet<string>> BuildPermissions(Guid userId)
    {
      if (!_permissionCache.ContainsKey(userId))
      {
        using var dbContext = _dbContextService.CreateDbContext<DbContextBase>();

        var user = dbContext.Users.FirstOrDefault(u => u.InstanceId == userId);
        Assertion.IsNotNull(user, $"User with id '{userId}' is invalid");

        var permissions = dbContext.UserRoles
         .Include(r => r.User)
         .Include(r => r.Role)
           .ThenInclude(r => r.Permissions)
         .Where(ur => ur.UserId == user.Id)
         .SelectMany(rp => rp.Role.Permissions)
         .Select(r => r.Permission)
         .Distinct()
         .ToList();

        var value = permissions
        .GroupBy(p => p.Subject)
        .ToDictionary(g => g.Key, g => new HashSet<string>(g.Select(i => i.Action)));

        _permissionCache[userId] = value;
      }

      return _permissionCache[userId];
    }
  }
}
