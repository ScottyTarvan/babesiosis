using System;
using System.Linq;
using System.Threading.Tasks;
using Babesiosis.Core.Api.Auth.Commands;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Data;
using Babesiosis.Core.Security;
using Microsoft.EntityFrameworkCore;

namespace Babesiosis.Core.Api.Auth.Controllers
{
  public class ResetPasswordController
  {
    private readonly IAppSettings _appSettings;
    private readonly IDbContextService _dbContextService;
    private readonly IPasswordEncryptor _passwordEncryptor;
    public ResetPasswordController(IAppSettingsService appSettingsService,
      IDbContextService dbContextService,
      IPasswordEncryptor passwordEncryptor)
    {
      this._appSettings = appSettingsService.GetAppSettings();
      this._dbContextService = dbContextService;
      this._passwordEncryptor = passwordEncryptor;
    }

    public async Task HandleCommand(ResetPasswordCommand command)
    {
      using var dbContext = _dbContextService.CreateDbContext<AuthDbContext>();

      Guid token = Guid.Parse(TextEncryptor.Decrypt(command.Token, _appSettings.Security.EncryptionKey));

      var passwordReset = await dbContext.PasswordResets
        .FirstOrDefaultAsync(p => p.Token == token);

      Assertion.IsNotNull(passwordReset, "Reset Password", "Could not reset password, try again");
      Assertion.True((DateTime.UtcNow - passwordReset.CreatedDate) <= _appSettings.Security.ResetPasswordExpiryTimeSpan, "Reset Link Has Expired, Please Try Again");

      var user = await dbContext.Users
        .Where(u => u.IsDeleted != true)
        .FirstOrDefaultAsync(u => u.Id == passwordReset.UserId);

      user.Password = _passwordEncryptor.EncryptAndHashPassword
      (
        command.Password,
        user.IV,
        user.Salt
      );

      dbContext.Users.Update(user);
      dbContext.PasswordResets.Remove(passwordReset);

      await dbContext.SaveChangesAsync();

    }
  }
}
