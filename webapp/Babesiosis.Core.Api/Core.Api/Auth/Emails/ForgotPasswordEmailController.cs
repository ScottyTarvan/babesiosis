using System;
using System.Linq;
using System.Threading.Tasks;
using System.Web;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Data;
using Babesiosis.Core.Models.Auth;
using Babesiosis.Core.Models.Domain;
using Babesiosis.Core.Models.Teams;
using Babesiosis.Core.Security;
using Babesiosis.Core.Services;
using Microsoft.EntityFrameworkCore;

namespace Babesiosis.Core.Api.Auth.Emails
{
    public class ForgotPasswordEmailController
  {
    private readonly IDbContextService _dbContextService;
    private readonly IAppSettings _appSettings;
    private readonly IEmailFactory _emailFactory;
    private readonly IEmailService _emailService;

    public ForgotPasswordEmailController(IDbContextService dbContextService,
      IAppSettingsService appSettingsService,
      IEmailFactory emailFactory,
      IEmailService emailService)
    {
      _dbContextService = dbContextService;
      _emailFactory = emailFactory;
      _emailService = emailService;
      _appSettings = appSettingsService.GetAppSettings();
    }

    public async Task Handle(EmailMessage message)
    {
      using var dbContext = _dbContextService.CreateDbContext<AuthDbContext>();

      User user = await dbContext.Users
        .Where(u => u.IsDeleted != true)
        .FirstOrDefaultAsync(u => u.InstanceId == message.UserId);

      Assertion.IsNotNull(user, $"User id {message.UserId} is invalid");

      Guid toEncrypt = Guid.NewGuid();

      string token = TextEncryptor.Encrypt(toEncrypt.ToString(), _appSettings.Security.EncryptionKey);
      string encodedToken = HttpUtility.UrlEncode(token);

      PasswordReset passwordReset = await dbContext.PasswordResets.FirstOrDefaultAsync(u => u.UserId == user.Id);

      if (passwordReset == null)
      {
        passwordReset = new PasswordReset()
        {
          UserId = user.Id,
          Token = toEncrypt
        };

        dbContext.PasswordResets.Add(passwordReset);
      }
      else
      {
        passwordReset.Token = toEncrypt;
        dbContext.PasswordResets.Update(passwordReset);
      }


      await dbContext.SaveChangesAsync();

      var email = await _emailFactory.CreateForgotPasswordEmailAsync(user, encodedToken);

      await _emailService.SendAsync(email);
    }
  }

}
