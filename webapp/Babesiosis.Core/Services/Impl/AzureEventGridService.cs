using Azure.Messaging.EventGrid;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Extensions;
using Babesiosis.Core.Models.Events;
using Microsoft.Extensions.Logging;
using System;
using System.Threading.Tasks;

namespace Babesiosis.Core.Services.Impl
{
  internal class AzureEventGridService : IEventGridService
  {
    private readonly IAppSettings _appSettings;
    private readonly EventGridClientManager _clientManager;
    private readonly ILogger<AzureEventGridService> _logger;

    public AzureEventGridService(
      IAppSettings appSettings,
      EventGridClientManager clientManager,
      ILogger<AzureEventGridService> logger)
    {
      _appSettings = appSettings ?? throw new ArgumentNullException(nameof(appSettings));
      _clientManager = clientManager ?? throw new ArgumentNullException(nameof(clientManager));
      _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public async Task Connect(string endPoint, string accessKey)
    {
      try
      {
        _logger.LogInformation("Testing Event Grid connection");
        endPoint = endPoint.HasValue() ? endPoint : _appSettings.EventGrid.EndPoint;
        accessKey = accessKey.HasValue() ? accessKey : _appSettings.EventGrid.Key;

        var client = _clientManager.GetPublisherClient(endPoint, accessKey);

        EventGridEvent eventGridEvent = new EventGridEvent(
          subject: "TEST",
          eventType: "BABESIOSIS.TEST",
          dataVersion: "2.0",
          data: "X");

        await client.SendEventAsync(eventGridEvent);
        _logger.LogInformation("Event Grid connection test successful");
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to connect to Event Grid");
        throw;
      }
    }

    public async Task PublishEventAsync(EventMessage message, string endPoint = null, string accessKey = null)
    {
      try
      {
        _logger.LogInformation("Publishing event to Event Grid - Type: {EventType}, Subject: {Subject}", message.EventType, message.Subject);
        endPoint = endPoint.HasValue() ? endPoint : _appSettings.EventGrid.EndPoint;
        accessKey = accessKey.HasValue() ? accessKey : _appSettings.EventGrid.Key;

        var client = _clientManager.GetPublisherClient(endPoint, accessKey);

        EventGridEvent eventGridEvent = new EventGridEvent(
          subject: message.Subject,
          eventType: message.EventType,
          dataVersion: "2.0",
          data: message.Data);

        await client.SendEventAsync(eventGridEvent);
        _logger.LogInformation("Successfully published event - Type: {EventType}, Subject: {Subject}", message.EventType, message.Subject);
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to publish event to Event Grid - Type: {EventType}, Subject: {Subject}", message.EventType, message.Subject);
        throw;
      }
    }
  }
}
