using Azure.Messaging.ServiceBus;
using Babesiosis.Core.Api.Teams.Permissions.Controllers;
using Babesiosis.Core.Permissions;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using System.Text;
using System.Text.Json;

namespace Babesiosis.Core.Functions.Teams.Permissions
{
  /// <summary>
  /// Drains the permissions-cache retry queue. Each message names one user whose
  /// invalidation tombstone could not be written when their grants changed (see
  /// <c>UserPermissionsCacheService.ClearUserPermissionsFromCacheAsync</c>).
  ///
  /// The handler rethrows on failure on purpose: with <c>autoCompleteMessages</c> on, an
  /// exception abandons the message, Service Bus redelivers it with the queue's backoff,
  /// and after the queue's max delivery count it lands in the dead-letter queue — the
  /// place an operator looks when a revoke never took. A message with no usable body is
  /// logged and completed, since redelivering it can never help.
  /// </summary>
  public class PermissionsCacheRetryQueue : ServiceBusFunctionBase
    {
      public const string NAME = "permissions-cache-retry-queue";
    private const string QUEUE_NAME = "%AppSettings:Queues:PermissionsCacheRetry%";
    private readonly PermissionsCacheRetryController _controller;

    public PermissionsCacheRetryQueue(ILogger<PermissionsCacheRetryQueue> logger,
      PermissionsCacheRetryController controller)
      : base(logger)
    {
      _controller = controller;
    }

    [Function(NAME)]
    public async Task Run(
      [ServiceBusTrigger(QUEUE_NAME, IsSessionsEnabled = false)] ServiceBusReceivedMessage message)
    {
      if (message.Body == null)
      {
        Logger.LogError("Permissions cache retry: message {MessageId} has no body; discarding.", message.MessageId);
        return;
      }

      string messageBody = Encoding.UTF8.GetString(message.Body);
      PermissionsCacheRetryMessage retry;

      try
      {
        retry = JsonSerializer.Deserialize<PermissionsCacheRetryMessage>(messageBody);
      }
      catch (JsonException ex)
      {
        Logger.LogError(ex, "Permissions cache retry: message {MessageId} is not a PermissionsCacheRetryMessage; discarding. Body: {Body}",
          message.MessageId, messageBody);
        return;
      }

      try
      {
        Logger.LogInformation("Permissions cache retry: invalidating user {UserId} (delivery {DeliveryCount}).",
          retry?.UserId, message.DeliveryCount);

        await _controller.HandleCommand(retry);
      }
      catch (Exception ex)
      {
        Logger.LogError(ex, "Permissions cache retry: invalidation for user {UserId} failed on delivery {DeliveryCount}; abandoning for redelivery.",
          retry?.UserId, message.DeliveryCount);
        throw;
      }
    }
  }
}
