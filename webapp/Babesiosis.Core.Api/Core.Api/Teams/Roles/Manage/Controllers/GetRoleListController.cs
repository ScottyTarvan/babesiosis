using AutoMapper;
using Babesiosis.Core.Api.Teams.Roles.Manage.Commands;
using Babesiosis.Core.Api.Teams.Roles.ViewModels;
using Babesiosis.Core.Data;
using Babesiosis.Core.Extensions;
using Babesiosis.Core.Permissions.Configs;
using Babesiosis.Core.Services;
using Babesiosis.Core.ViewModels;
using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Teams.Roles.Manage.Controllers
{
  /// <summary>
  /// Roles list for the new web application. Rows come straight off
  /// <c>Roles</c>, wrapped in the <c>{ page, permissions }</c> envelope the new
  /// grids bind to, with the capability echo that decides which toolbar and row
  /// actions are enabled. (It used to be described as the legacy
  /// <c>GetRolesController</c> reshaped; that controller went with FIT.Angular.)
  /// </summary>
  public class GetRoleListController
  {
    private readonly IDbContextService _dbContextService;
    private readonly IMapper _mapper;
    private readonly IUserPermissionItemsService _userPermissionsService;

    public GetRoleListController(IDbContextService dbContextService,
      IMapper mapper,
      IUserPermissionItemsService userPermissionsService)
    {
      _dbContextService = dbContextService;
      _mapper = mapper;
      _userPermissionsService = userPermissionsService;
    }

    public async Task<ItemsViewModel<RoleViewModel>> HandleCommand(Guid userId, GetRoleListCommand command)
    {
      using var dbContext = _dbContextService.CreateDbContext<TeamsDbContext>();

      var loadOptions = command?.LoadOptions ?? new DevExtreme.AspNet.Data.DataSourceLoadOptionsBase();

      var page = await loadOptions.LoadPageAsync(dbContext.Roles.Include(r => r.Permissions));

      var permissions = await _userPermissionsService.GetUserPermissionsAsync(userId);

      return new ItemsViewModel<RoleViewModel>
      {
        Page = new PagedItemsViewModel<RoleViewModel>
        {
          Items = page.Results.Select(r => _mapper.Map<RoleViewModel>(r)).ToList(),
          Paging = new PagingViewModel(page.TotalRecordCount, loadOptions.Skip, loadOptions.Take)
        },
        Permissions = new Dictionary<string, bool>
        {
          { "canAdd", permissions.HasPermission(Guid.Parse(TeamsPermissions.RoleAddId)) },
          { "canEdit", permissions.HasPermission(Guid.Parse(TeamsPermissions.RoleEditId)) },
          { "canDelete", permissions.HasPermission(Guid.Parse(TeamsPermissions.RoleDeleteId)) },
          { "canViewPermissions", permissions.HasPermission(Guid.Parse(TeamsPermissions.RolePermissionReadId)) },
          { "canManageMembers", permissions.HasPermission(Guid.Parse(TeamsPermissions.RoleMemberReadId)) },
          // Grid Export was ungated before 2026-09-21.
          { "canExport", permissions.HasPermission(Guid.Parse(TeamsPermissions.RoleDownloadId)) }
        }
      };
    }
  }
}
