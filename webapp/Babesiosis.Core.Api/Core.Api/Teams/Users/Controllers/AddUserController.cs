using System;
using System.Threading.Tasks;
using AutoMapper;
using Babesiosis.Core.Api.Teams.Users.Commands;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Data;
using Babesiosis.Core.Extensions;
using Babesiosis.Core.Models.Teams;
using Babesiosis.Core.Security;
using Babesiosis.Core.Services;
using Babesiosis.Core.ViewModels;
using Microsoft.EntityFrameworkCore;

namespace Babesiosis.Core.Api.Teams.Users.Controllers
{
  public class AddUserController
  {
    private readonly IMapper _mapper;
    private readonly IDbContextService _dbContextService;
    private readonly IPasswordEncryptor _passwordEncryptor;
    private readonly IUserPermissionsService _permissionsService;

    public AddUserController(IDbContextService dbContextService,
      IMapper mapper,
      IPasswordEncryptor passwordEncryptor,
      IUserPermissionsService permissionsService)
    {
      _dbContextService = dbContextService;
      _mapper = mapper;
      _passwordEncryptor = passwordEncryptor;
      _permissionsService = permissionsService;
    }

    public async Task<UserViewModel> HandleCommand(Guid userId, UserCommand command)
    {
      _permissionsService.Assert(userId, "create", "teams-user");
      
      using var dbContext = _dbContextService.CreateDbContext<TeamsDbContext>();

      var duplicate = await dbContext.Users.AnyAsync(a => a.Email == command.User.Email);
      Assertion.False(duplicate, $"User with email: {command.User.Email} already exists");

      User user = _mapper.Map<User>(command.User);
      user.IV = _passwordEncryptor.GenerateSalt();
      user.Salt = _passwordEncryptor.GenerateSalt();
      user.CreatedDate = DateTime.UtcNow;
      user.Password = _passwordEncryptor.EncryptAndHashPassword
      (
        command.User.Password,
        user.IV,
        user.Salt
      );

      dbContext.Add(user);
      await dbContext.SaveChangesAsync();

      var result = _mapper.Map<UserViewModel>(user);
      return result;
    }

  }
}
