using Babesiosis.Core.Assertions;
using Babesiosis.Core.Permissions;
using Babesiosis.Core.Services;
using System;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Teams.Permissions.Controllers
{
  /// <summary>
  /// Handles one <see cref="PermissionsCacheRetryMessage"/> from the permissions-cache
  /// retry queue: either a user whose cache invalidation could not be written when their
  /// grants changed, or a deleted user whose record is due for removal. There is no
  /// user-facing request behind either — the SQL change already committed — so the only
  /// job is to land the change in the shared cache.
  ///
  /// Failure is allowed to propagate. The queue function rethrows it, Service Bus
  /// redelivers the message, and after the queue's delivery limit it dead-letters, which
  /// is the signal an operator sees. Swallowing here would turn a retry queue into a
  /// black hole.
  /// </summary>
  public class PermissionsCacheRetryController
  {
    private readonly IUserPermissionsCacheService _userPermissionsCacheService;

    public PermissionsCacheRetryController(IUserPermissionsCacheService userPermissionsCacheService)
    {
      _userPermissionsCacheService = userPermissionsCacheService;
    }

    public async Task HandleCommand(PermissionsCacheRetryMessage message)
    {
      Assertion.IsNotNull(message, "Permissions cache retry message is required");
      Assertion.True(message.UserId != Guid.Empty, "Permissions cache retry message must name a user");

      switch (message.Action)
      {
        case PermissionsCacheRetryAction.Invalidate:
          await _userPermissionsCacheService.RetryClearUserPermissionsFromCacheAsync(message.UserId);
          break;

        case PermissionsCacheRetryAction.Remove:
          await _userPermissionsCacheService.RemoveUserPermissionsFromCacheAsync(message.UserId);
          break;

        default:
          // Throws; the queue function rethrows, so the message dead-letters once the
          // delivery limit is reached. An unknown action can never succeed on redelivery,
          // and the dead-letter queue is where an operator will see it.
          Assertion.True(false, $"Unknown permissions cache retry action {message.Action}");
          break;
      }
    }
  }
}
