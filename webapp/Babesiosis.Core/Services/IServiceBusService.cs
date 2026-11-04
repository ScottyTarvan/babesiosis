using Azure.Messaging.ServiceBus;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Babesiosis.Core.Services
{
  public interface IServiceBusService
  {
    Task<string> AddMessageAsync(
      string queueName,
      string sessionId,
      string messageBody,
      string subject = null,
      IDictionary<string, object> applicationProperties = null,
      int retryCount = 3);

    Task<string> AddMessagesAsync(
      string queueName,
      string sessionId,
      IList<string> messageBodies,
      string subject = null,
      IDictionary<string, object> applicationProperties = null,
      int retryCount = 3);

    Task<string> AddTopicAsync(
      string topicName,
      string sessionId,
      string messageBody,
      string subject = null,
      IDictionary<string, object> applicationProperties = null,
      int retryCount = 3);

    Task<string> AddScheduledMessageAsync(string queueName,
      string sessionId,
      string messageBody,
      DateTime scheduledTime,
      int retryCount = 3);

    string GetPayload(ServiceBusReceivedMessage message);
  }
}
