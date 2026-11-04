using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using Azure.Messaging.ServiceBus;
using Babesiosis.Core.Configurations;
using Microsoft.Extensions.Logging;

namespace Babesiosis.Core.Services.Impl
{
  internal class AzureServiceBusService : IServiceBusService
  {
    private readonly IAppSettings _appSettings;
    private readonly ServiceBusClientManager _clientManager;
    private readonly ILogger<AzureServiceBusService> _logger;

    internal AzureServiceBusService(
      IAppSettings appSettings,
      ServiceBusClientManager clientManager,
      ILogger<AzureServiceBusService> logger)
    {
      _appSettings = appSettings ?? throw new ArgumentNullException(nameof(appSettings));
      _clientManager = clientManager ?? throw new ArgumentNullException(nameof(clientManager));
      _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    /// <summary>
    /// Sends a message to the specified Service Bus queue with session support
    /// </summary>
    /// <param name="queueName">Target queue name</param>
    /// <param name="sessionId">Session identifier for message ordering</param>
    /// <param name="messageBody">Message content as string</param>
    /// <param name="subject">Optional message subject/label</param>
    /// <param name="applicationProperties">Optional custom properties dictionary</param>
    /// <param name="retryCount">Maximum retry attempts (default: 3)</param>
    /// <returns>Confirmation message indicating success</returns>
    public async Task<string> AddMessageAsync(string queueName,
      string sessionId,
      string messageBody,
      string subject = null,
      IDictionary<string, object> applicationProperties = null,
      int retryCount = 3)
    {
      try
      {
        _logger.LogInformation("Sending message to queue {QueueName}, SessionId: {SessionId}", queueName, sessionId);

        var retryOptions = new ServiceBusRetryOptions()
        {
          MaxRetries = retryCount,
          MaxDelay = TimeSpan.FromSeconds(_appSettings.ServiceBus.MaxDelaySeconds),
          Mode = _appSettings.ServiceBus.RetryMode?.ToLowerInvariant() == "exponential"
            ? ServiceBusRetryMode.Exponential
            : ServiceBusRetryMode.Fixed
        };

        var sender = _clientManager.GetSender(queueName, null, retryOptions);

        var message = new ServiceBusMessage(Encoding.UTF8.GetBytes(messageBody))
        {
          SessionId = sessionId,
          Subject = subject
        };

        if (applicationProperties != null)
        {
          foreach (KeyValuePair<string, object> keyValue in applicationProperties)
          {
            message.ApplicationProperties.Add(keyValue.Key, keyValue.Value);
          }
        }

        await sender.SendMessageAsync(message);

        _logger.LogInformation("Successfully sent message to queue {QueueName}", queueName);
        return $"Message '{messageBody}' sent to service bus queue {queueName}";
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to send message to queue {QueueName}", queueName);
        throw;
      }
    }

    /// <summary>
    /// Sends multiple messages to the specified Service Bus queue in optimized batches
    /// </summary>
    /// <param name="queueName">Target queue name</param>
    /// <param name="sessionId">Session identifier for message ordering</param>
    /// <param name="messageBodies">Collection of message bodies to send</param>
    /// <param name="subject">Optional message subject/label applied to all messages</param>
    /// <param name="applicationProperties">Optional custom properties applied to all messages</param>
    /// <param name="retryCount">Maximum retry attempts (default: 3)</param>
    /// <returns>Confirmation message with count of messages sent</returns>
    public async Task<string> AddMessagesAsync(string queueName,
      string sessionId,
      IList<string> messageBodies,
      string subject = null,
      IDictionary<string, object> applicationProperties = null,
      int retryCount = 3)
    {
      try
      {
        _logger.LogInformation("Sending {Count} messages to queue {QueueName} in batches", messageBodies.Count, queueName);

        var retryOptions = new ServiceBusRetryOptions()
        {
          MaxRetries = retryCount,
          MaxDelay = TimeSpan.FromSeconds(_appSettings.ServiceBus.MaxDelaySeconds),
          Mode = _appSettings.ServiceBus.RetryMode?.ToLowerInvariant() == "exponential"
            ? ServiceBusRetryMode.Exponential
            : ServiceBusRetryMode.Fixed
        };

        var sender = _clientManager.GetSender(queueName, null, retryOptions);

        Queue<ServiceBusMessage> messages = new Queue<ServiceBusMessage>();

        foreach (var body in messageBodies)
        {
          var message = new ServiceBusMessage(Encoding.UTF8.GetBytes(body))
          {
            SessionId = sessionId,
            Subject = subject
          };

          if (applicationProperties != null)
          {
            foreach (KeyValuePair<string, object> keyValue in applicationProperties)
            {
              message.ApplicationProperties.Add(keyValue.Key, keyValue.Value);
            }
          }

          messages.Enqueue(message);
        }

        int messageCount = messages.Count;
        int processedCount = 0;

        // while all messages are not sent to the Service Bus queue
        while (messages.Count > 0)
        {
          using ServiceBusMessageBatch messageBatch = await sender.CreateMessageBatchAsync();

          if (messageBatch.TryAddMessage(messages.Peek()))
          {
            messages.Dequeue();
            processedCount++;
          }
          else
          {
            throw new Exception($"Message {processedCount + 1} is too large and cannot be sent.");
          }

          while (messages.Count > 0 && messageBatch.TryAddMessage(messages.Peek()))
          {
            messages.Dequeue();
            processedCount++;
          }

          await sender.SendMessagesAsync(messageBatch);

          _logger.LogDebug("Processed {ProcessedCount}/{TotalCount} messages", processedCount, messageCount);
        }

        _logger.LogInformation("Successfully sent {Count} messages to queue {QueueName}", messageCount, queueName);
        return $"{messageCount} Messages sent to service bus queue {queueName}";
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to send messages to queue {QueueName}", queueName);
        throw;
      }
    }

    /// <summary>
    /// Sends a message to the specified Service Bus topic with session support
    /// </summary>
    /// <param name="topicName">Target topic name</param>
    /// <param name="sessionId">Session identifier for message ordering</param>
    /// <param name="messageBody">Message content as string</param>
    /// <param name="subject">Optional message subject/label</param>
    /// <param name="applicationProperties">Optional custom properties dictionary</param>
    /// <param name="retryCount">Maximum retry attempts (default: 3)</param>
    /// <returns>Confirmation message indicating success</returns>
    public async Task<string> AddTopicAsync(string topicName,
      string sessionId,
      string messageBody,
      string subject = null,
      IDictionary<string, object> applicationProperties = null,
      int retryCount = 3)
    {
      try
      {
        _logger.LogInformation("Sending message to topic {TopicName}, SessionId: {SessionId}", topicName, sessionId);

        var retryOptions = new ServiceBusRetryOptions()
        {
          MaxRetries = retryCount,
          MaxDelay = TimeSpan.FromSeconds(_appSettings.ServiceBus.MaxDelaySeconds),
          Mode = _appSettings.ServiceBus.RetryMode?.ToLowerInvariant() == "exponential"
            ? ServiceBusRetryMode.Exponential
            : ServiceBusRetryMode.Fixed
        };

        var sender = _clientManager.GetSender(topicName, null, retryOptions);

        var message = new ServiceBusMessage(Encoding.UTF8.GetBytes(messageBody))
        {
          SessionId = sessionId,
          Subject = subject
        };

        if (applicationProperties != null)
        {
          foreach (KeyValuePair<string, object> keyValue in applicationProperties)
          {
            message.ApplicationProperties.Add(keyValue.Key, keyValue.Value);
          }
        }

        await sender.SendMessageAsync(message);

        _logger.LogInformation("Successfully sent message to topic {TopicName}", topicName);
        return $"Message '{messageBody}' sent to service bus topic {topicName}";
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to send message to topic {TopicName}", topicName);
        throw;
      }
    }

    /// <summary>
    /// Schedules a message for future delivery to the specified Service Bus queue
    /// </summary>
    /// <param name="queueName">Target queue name</param>
    /// <param name="sessionId">Session identifier for message ordering</param>
    /// <param name="messageBody">Message content as string</param>
    /// <param name="scheduledTime">UTC time when message should be delivered</param>
    /// <param name="retryCount">Maximum retry attempts (default: 3)</param>
    /// <returns>Confirmation message indicating successful scheduling</returns>
    public async Task<string> AddScheduledMessageAsync(string queueName,
      string sessionId,
      string messageBody,
      DateTime scheduledTime,
      int retryCount = 3)
    {
      try
      {
        _logger.LogInformation("Scheduling message to queue {QueueName} for {ScheduledTime}, SessionId: {SessionId}",
          queueName, scheduledTime, sessionId);

        var retryOptions = new ServiceBusRetryOptions()
        {
          MaxRetries = retryCount,
          MaxDelay = TimeSpan.FromSeconds(_appSettings.ServiceBus.MaxDelaySeconds),
          Mode = _appSettings.ServiceBus.RetryMode?.ToLowerInvariant() == "exponential"
            ? ServiceBusRetryMode.Exponential
            : ServiceBusRetryMode.Fixed
        };

        var sender = _clientManager.GetSender(queueName, null, retryOptions);

        await sender.ScheduleMessageAsync(new ServiceBusMessage(messageBody) { SessionId = sessionId }, scheduledTime);

        _logger.LogInformation("Successfully scheduled message to queue {QueueName}", queueName);
        return $"Message '{messageBody}' sent to service bus queue {queueName}";
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to schedule message to queue {QueueName}", queueName);
        throw;
      }
    }

    /// <summary>
    /// Extracts the string payload from a Service Bus received message
    /// </summary>
    /// <param name="message">The received Service Bus message</param>
    /// <returns>UTF-8 decoded message body as string</returns>
    public string GetPayload(ServiceBusReceivedMessage message)
    {
      _logger.LogDebug("Extracting payload from Service Bus message");
      return Encoding.UTF8.GetString(message.Body);
    }
  }
}
