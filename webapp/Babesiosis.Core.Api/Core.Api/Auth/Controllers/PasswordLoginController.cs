using System.Linq;
using System.Threading.Tasks;
using AutoMapper;
using Babesiosis.Core.Api.Auth.Commands;
using Babesiosis.Core.Api.Auth.ViewModels;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Data;
using Babesiosis.Core.Models.Teams;
using Babesiosis.Core.Security;
using Babesiosis.Core.Services;
using Babesiosis.Core.ViewModels;
using Microsoft.EntityFrameworkCore;

namespace Babesiosis.Core.Api.Auth.Controllers
{
    public class PasswordLoginController : UserLoginController
  {
    private readonly IAppSettings _appSettings;
    private readonly IDbContextService _dbContextService;
    private readonly IPasswordEncryptor _passwordEncryptor;
    private readonly IJwtTokenGenerator _jwtTokenGenerator;
    private readonly IMapper _mapper;

    public PasswordLoginController(IAppSettingsService appSettingsService,
      IDbContextService dbContextService,
      IPasswordEncryptor passwordEncryptor,
      IJwtTokenGenerator jwtTokenGenerator,
      IUserPermissionsCacheService userPermissionsCacheService,
      IPermissionsConfigService permissionsConfigService,
      IMapper mapper)
      : base(userPermissionsCacheService, permissionsConfigService)
    {
      _appSettings = appSettingsService.GetAppSettings();
      _dbContextService = dbContextService;
      _passwordEncryptor = passwordEncryptor;
      _jwtTokenGenerator = jwtTokenGenerator;
      _mapper = mapper;
    }

    public async Task<LoginViewModel> HandleCommand(PasswordLoginCommand command)
    {
      using var dbContext = this._dbContextService.CreateDbContext<AuthDbContext>();

      User user = await dbContext.Users
        .Where(u => u.IsDeleted != true)
        .FirstOrDefaultAsync(a => a.Email == command.Email);

      if (user == null)
      {
        return new LoginViewModel()
        {
          Passed = false,
          Message = "Login failed, email or password is invalid [Code: 2500]"
        };
      }

      string passwordHash = _passwordEncryptor.EncryptAndHashPassword(command.Password, user.IV, user.Salt);

      if (!string.Equals(user.Password, passwordHash))
      {
        return new LoginViewModel()
        {
          Passed = false,
          Message = "Login failed, email or password is invalid [Code: 3500]"
        };
      }

      string token = _jwtTokenGenerator.CreateToken(user.InstanceId, _appSettings.Jwt.ExpiryTimeSpan);
      string refreshToken = _jwtTokenGenerator.CreateToken(user.InstanceId, _appSettings.Jwt.RefreshTokenExpiryTimeSpan);
      var userViewModel = _mapper.Map<UserViewModel>(user);
      userViewModel.Permissions = await RefreshPermissionsAsync(user);

      return new LoginViewModel()
      {
        Passed = true,
        Message = "Login successful",
        User = userViewModel,
        AuthToken = token,
        RefreshToken = refreshToken,
      };
    }
  }
}
