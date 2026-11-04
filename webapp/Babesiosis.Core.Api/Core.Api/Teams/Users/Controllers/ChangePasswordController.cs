using System;
using System.Linq;
using System.Threading.Tasks;
using AutoMapper;
using Babesiosis.Core.Api.Teams.Users.Commands;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Data;
using Babesiosis.Core.Security;
using Babesiosis.Core.Services;
using Babesiosis.Core.ViewModels;
using Microsoft.EntityFrameworkCore;

namespace Babesiosis.Core.Api.Teams.Users.Controllers
{
  public class ChangePasswordController
  {
    private readonly IAppSettings _appSettings;
    private readonly IDbContextService _dbContextService;
    private readonly IMapper _mapper;
    private readonly IPasswordEncryptor _passwordEncryptor;
    private readonly IUserPermissionsService _permissionsService;

    public ChangePasswordController(IAppSettingsService appSetttingsService,
      IDbContextService dbContextService,
      IMapper mapper,
      IPasswordEncryptor passwordEncryptor,
      IUserPermissionsService permissionsService)
    {
      _appSettings = appSetttingsService.GetAppSettings();
      _dbContextService = dbContextService;
      _mapper = mapper;
      _passwordEncryptor = passwordEncryptor;
      _permissionsService = permissionsService;
    }
    public async Task<UserViewModel> HandleCommand(Guid userId, ChangePasswordCommand command)
    {
      _permissionsService.Assert(userId, "update", "teams-user-password");

      using var dbContext = _dbContextService.CreateDbContext<TeamsDbContext>();

      var user = await dbContext.Users
        .Where(u => u.InstanceId == userId)
        .FirstOrDefaultAsync();

      Assertion.IsNotNull(user, "User", $"User does not exist for id {userId}");
      Assertion.True(!string.IsNullOrEmpty(command.Password), "Password cannot be empty");

      Assertion.RowVersionCheck(user.RowVersion, command.RowVersion, "The user has changed since the page was loaded, refresh and try again");

      user.Salt = _passwordEncryptor.GenerateSalt();
      user.Password = _passwordEncryptor.EncryptAndHashPassword
      (
        command.Password,
        user.IV,
        user.Salt
      );

      dbContext.Update(user);
      await dbContext.SaveChangesAsync();

      return _mapper.Map<UserViewModel>(user);
    }
  }
}
