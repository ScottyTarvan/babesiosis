using System;
using System.Linq;
using System.Threading.Tasks;
using Babesiosis.Core.Api.Auth.Commands;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Data;
using Babesiosis.Core.Models.Domain;
using Babesiosis.Core.Services;
using Microsoft.EntityFrameworkCore;
using Newtonsoft.Json;

namespace Babesiosis.Core.Api.Auth.Controllers
{
  public class ForgotPasswordController
  {
    private readonly IAppSettings _appSettings;
    private readonly IDbContextService _dbContextService;
    private readonly IServiceBusService _serviceBusService;
    public ForgotPasswordController(IAppSettingsService appSettingsService,
      IDbContextService dbContextService,
      IServiceBusService serviceBusService)
    {
      this._appSettings = appSettingsService.GetAppSettings();
      this._dbContextService = dbContextService;
      this._serviceBusService = serviceBusService;
    }

    public async Task<bool> HandleCommand(ForgotPasswordCommand command)
    {
      using var dbContext = _dbContextService.CreateDbContext<AuthDbContext>();

      var user = await dbContext.Users
        .Where(u => u.IsDeleted != true)
        .FirstOrDefaultAsync(u => u.Email == command.Email);

      if (user != null)
      {
        var message = new EmailMessage()
        {
          UserId = user.InstanceId,
          MessageType = MessageType.ForgotPassword
        };

        await _serviceBusService.AddMessageAsync
              (
                _appSettings.Queues.Email,
                Guid.NewGuid().ToString(),
                JsonConvert.SerializeObject(message),
                MessageType.ForgotPassword.ToString()
              );

        return true;
      }
      else
      {
        return false;
      }
    }
  }
}
