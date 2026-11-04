using System;
using System.Linq;
using System.Threading.Tasks;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Data;
using Microsoft.EntityFrameworkCore;

namespace Babesiosis.Core.Api.Auth.Controllers
{
  public class ClearPasswordResetsController
  {
    private readonly IAppSettings _appSettings;
    private readonly IDbContextService _dbContextService;
    public ClearPasswordResetsController(IAppSettingsService appSettingsService,
      IDbContextService dbContextService)
    {
      this._appSettings = appSettingsService.GetAppSettings();
      this._dbContextService = dbContextService;
    }

    public async Task HandleCommand()
    {
      using var dbContext = _dbContextService.CreateDbContext<AuthDbContext>();

      var expiryBoundry = DateTime.UtcNow - _appSettings.Security.ResetPasswordExpiryTimeSpan;
      var passwordResets = await dbContext.PasswordResets.Where(p => p.CreatedDate < expiryBoundry).ToListAsync();

      dbContext.PasswordResets.RemoveRange(passwordResets);
      await dbContext.SaveChangesAsync();
    }
  }
}
