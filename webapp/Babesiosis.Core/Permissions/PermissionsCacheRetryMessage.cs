using System;

namespace Babesiosis.Core.Permissions
{
  /// <summary>What the queue function must do for the user a message names.</summary>
  public enum PermissionsCacheRetryAction
  {
    /// <summary>
    /// Write the invalidation tombstone that could not be written when the user's
    /// grants changed. Retried until it lands or the message dead-letters.
    /// </summary>
    Invalidate = 0,

    /// <summary>
    /// Delete the user's blob outright. Scheduled an hour after a user is deleted, once
    /// no reload that read SQL before the delete can still be in flight, so the record
    /// of a user who no longer exists does not wait for the storage lifecycle rule.
    /// </summary>
    Remove = 1
  }

  /// <summary>
  /// Body of a message on the <c>AppSettings:Queues:PermissionsCacheRetry</c> queue: one
  /// user and one <see cref="PermissionsCacheRetryAction"/>. Sent by
  /// <c>UserPermissionsCacheService</c>, consumed by the <c>permissions-cache-retry-queue</c>
  /// function, which dispatches to <c>IUserPermissionsCacheService</c>. Serialised with
  /// System.Text.Json on both sides; <see cref="Action"/> defaults to Invalidate so a
  /// message written before the field existed still means what it meant.
  /// </summary>
  public class PermissionsCacheRetryMessage
  {
    /// <summary>Service Bus subject stamped on every message of this shape.</summary>
    public const string SUBJECT = "PermissionsCacheRetry";

    public Guid UserId { get; set; }

    public PermissionsCacheRetryAction Action { get; set; } = PermissionsCacheRetryAction.Invalidate;
  }
}
