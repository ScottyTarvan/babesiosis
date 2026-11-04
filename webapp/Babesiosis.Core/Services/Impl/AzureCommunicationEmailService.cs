using Azure;
using Azure.Communication.Email;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Models.Email;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Babesiosis.Core.Services.Impl
{
  internal class AzureCommunicationEmailService : IEmailService
  {
    private readonly IAppSettingsService _appSettingsService;

    public AzureCommunicationEmailService(IAppSettingsService appSettingsService)
    {
      _appSettingsService = appSettingsService;
    }

    public async Task SendAsync(Email email)
    {
      var appSettings = _appSettingsService.GetAppSettings();
      var config = appSettings.AzureCommunicationEmail;

      var emailClient = new EmailClient(config.ConnectionString);

      var senderAddress = string.IsNullOrWhiteSpace(email.FromAddress)
        ? config.SenderAddress
        : email.FromAddress;

      var content = new EmailContent(email.Subject)
      {
        Html = email.Body,
        PlainText = email.Body
      };

      var recipients = new EmailRecipients(new List<EmailAddress>
      {
        new EmailAddress(email.ToAddress)
      });

      var message = new EmailMessage(senderAddress, recipients, content);

      foreach (var attachment in email.Attachments ?? Enumerable.Empty<EmailFileAttachment>())
      {
        message.Attachments.Add(new EmailAttachment(
          attachment.FileName,
          attachment.Type,
          BinaryData.FromBytes(Convert.FromBase64String(attachment.Content))));
      }

      await emailClient.SendAsync(WaitUntil.Completed, message);
    }
  }
}
