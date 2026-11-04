using Babesiosis.Core.Configurations;
using Babesiosis.Core.Data;
using Babesiosis.Core.Models.Domain;
using Babesiosis.Core.Permissions;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Abstractions;
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace Babesiosis.Core.Services.Impl
{
  /// <summary>
  /// The shared cache: Blob Storage (container
  /// <c>AppSettings.Containers.PermissionsCache</c>, key
  /// <c>permissions:user:{userId}</c>) holds the record for every function-app
  /// instance to read, with a per-instance L1 in front of it so a hot path does
  /// not hit blob storage on every request.
  /// <para>
  /// An L1 entry is trusted without any blob call until <see cref="L1Ttl"/>
  /// after it was last verified; past that, a single <c>GetBlobETagAsync</c>
  /// HEAD call re-verifies it — an unchanged ETag just bumps the verified time,
  /// a changed one triggers a re-download, and a missing/errored check falls
  /// back to a full SQL reload. Independently of L1, a record older than
  /// <c>MaxEntryAge</c> (24h, from the base class) is always reloaded from SQL,
  /// whichever path found it.
  /// </para>
  /// <para>
  /// Every SQL reload writes the blob back conditionally — <c>If-Match</c> the
  /// exact ETag it was reloading over, or a create-only write when it was
  /// reloading because the blob was confirmed missing — via
  /// <see cref="IBlobStorageService.UpdateBlobIfUnchangedAsync"/>. A SQL read
  /// racing an invalidation (<see cref="ClearUserPermissionsFromCacheAsync"/>)
  /// can otherwise write stale data back over a fresh one; losing the
  /// conditional write instead discards the stale read and re-derives the
  /// entry from whatever the concurrent writer left. Every L1 write is
  /// similarly a compare-and-swap against the tuple observed when the call
  /// started, so a Clear that lands mid-flight is never silently overwritten.
  /// </para>
  /// </summary>
  internal class UserPermissionsCacheService : UserPermissionsCacheServiceBase
  {
    private readonly IAppSettings _appSettings;
    private readonly IBlobStorageService _blobStorageService;
    private readonly IServiceBusService _serviceBusService;
    private readonly ILogger _logger;

    private static readonly TimeSpan L1Ttl = TimeSpan.FromMinutes(5);

    /// <summary>
    /// How long after a user is deleted their blob is removed. Removal is deferred so a
    /// reload that read SQL just before the delete committed cannot land a live record
    /// after the blob is gone — the tombstone written at delete time covers the interval,
    /// and by the time this fires nothing that old can still be in flight.
    /// </summary>
    private static readonly TimeSpan RemovalDelay = TimeSpan.FromHours(1);

    private readonly ConcurrentDictionary<Guid, (UserPermissionsCacheEntry Entry, string ETag, DateTimeOffset VerifiedAtUtc)> _l1 = new();

    public UserPermissionsCacheService(IAppSettings appSettings,
      IBlobStorageService blobStorageService,
      IDbContextService dbContextService,
      IPermissionsConfigService permissionsConfigService,
      TimeProvider timeProvider = null,
      ILogger logger = null,
      IServiceBusService serviceBusService = null)
      : base(dbContextService, permissionsConfigService, timeProvider ?? TimeProvider.System)
    {
      _appSettings = appSettings;
      _blobStorageService = blobStorageService;
      _serviceBusService = serviceBusService;
      _logger = logger ?? NullLogger.Instance;
    }

    public override async Task<HashSet<Guid>> GetUserPermissionsFromCacheAsync(Guid userId)
    {
      UserPermissionsCacheEntry entry = await GetEntryAsync(userId);
      return Resolve(entry);
    }

    private async Task<UserPermissionsCacheEntry> GetEntryAsync(Guid userId)
    {
      bool hasL1 = _l1.TryGetValue(userId, out var l1);
      (UserPermissionsCacheEntry Entry, string ETag, DateTimeOffset VerifiedAtUtc)? preceding = hasL1 ? l1 : null;

      if (hasL1)
      {
        if (IsStale(l1.Entry))
        {
          return await ReloadFromDbAsync(userId, l1.ETag, preceding);
        }

        if (Clock.GetUtcNow() - l1.VerifiedAtUtc < L1Ttl)
        {
          return l1.Entry;
        }

        string cacheKey = GetCacheKey(userId);
        string currentETag = null;

        try
        {
          currentETag = await _blobStorageService.GetBlobETagAsync(
            _appSettings.Containers.PermissionsCache, cacheKey);
        }
        catch (Exception ex)
        {
          _logger.LogWarning(ex, "Permissions cache: failed to verify blob ETag for user {UserId}.", userId);
          return await ReloadFromDbAsync(userId, l1.ETag, preceding);
        }

        if (currentETag == null)
        {
          // Blob missing: something deleted it outside of the normal invalidation path (which
          // always leaves a tombstone rather than deleting), or it genuinely never existed.
          return await ReloadFromDbAsync(userId, null, preceding);
        }

        if (currentETag == l1.ETag)
        {
          // Compare-and-swap against the exact tuple this call started with: if a concurrent
          // Clear (and possibly a reload right behind it) already replaced or removed the L1
          // entry, this must not overwrite that fresher state with the one this call read.
          var refreshed = (l1.Entry, l1.ETag, Clock.GetUtcNow());
          _l1.TryUpdate(userId, refreshed, l1);
          return l1.Entry;
        }

        // ETag changed since it was last verified: fall through and re-download below.
      }

      return await DownloadOrReloadAsync(userId, preceding);
    }

    private async Task<UserPermissionsCacheEntry> DownloadOrReloadAsync(Guid userId,
      (UserPermissionsCacheEntry Entry, string ETag, DateTimeOffset VerifiedAtUtc)? preceding)
    {
      string cacheKey = GetCacheKey(userId);
      string downloadedETag = null;
      bool downloaded = false;

      try
      {
        var (content, etag) = await _blobStorageService.DownloadBlobWithETagAsync(
          _appSettings.Containers.PermissionsCache, cacheKey);

        if (content == null)
        {
          return await ReloadFromDbAsync(userId, null, preceding);
        }

        downloadedETag = etag;
        downloaded = true;

        UserPermissionsCacheEntry entry;

        using (content)
        {
          entry = JsonSerializer.Deserialize<UserPermissionsCacheEntry>(content)
            ?? throw new InvalidOperationException("Cached permissions blob deserialized to null.");
        }

        if (IsStale(entry))
        {
          return await ReloadFromDbAsync(userId, etag, preceding);
        }

        SetL1(userId, (entry, etag, Clock.GetUtcNow()), preceding);
        return entry;
      }
      catch (Exception ex)
      {
        // Covers a missing/unreachable blob and a blob that fails to deserialize into the
        // current record shape — for example a legacy blob holding a bare GUID array.
        _logger.LogWarning(ex, "Permissions cache: failed to read blob for user {UserId}; reloading from SQL.", userId);

        if (downloaded)
        {
          // We know exactly what is there (it simply did not deserialize): overwrite it
          // conditionally on that exact ETag rather than risk clobbering a concurrent writer.
          return await ReloadFromDbAsync(userId, downloadedETag, preceding);
        }

        // The download itself failed: there is no confirmed blob state to condition on. Fall
        // back to a best-effort unconditional write rather than loop on a precondition that
        // cannot be known.
        return await ReloadFromDbUnconditionallyAsync(userId);
      }
    }

    /// <summary>
    /// Reloads the user's record from SQL and writes it back only if the blob still matches
    /// what this call last observed — <paramref name="expectedETag"/> null means "must still be
    /// missing" (a create-only write), otherwise "must still have exactly this ETag". Losing
    /// that race means a concurrent writer — almost always an invalidation — changed the blob
    /// between the SQL read and this write, so the record just loaded may already be stale: it
    /// is discarded in favour of re-deriving the entry from scratch.
    /// </summary>
    private async Task<UserPermissionsCacheEntry> ReloadFromDbAsync(Guid userId, string expectedETag,
      (UserPermissionsCacheEntry Entry, string ETag, DateTimeOffset VerifiedAtUtc)? preceding)
    {
      UserPermissionsCacheEntry entry = await LoadEntryFromDbAsync(userId);

      string cacheKey = GetCacheKey(userId);
      string json = JsonSerializer.Serialize(entry);
      byte[] bytes = Encoding.UTF8.GetBytes(json);

      BlobConditionalWriteResult result;

      using (MemoryStream stream = new MemoryStream(bytes))
      {
        try
        {
          result = await _blobStorageService.UpdateBlobIfUnchangedAsync(
            _appSettings.Containers.PermissionsCache, cacheKey, stream, expectedETag);
        }
        catch (Exception ex)
        {
          _logger.LogWarning(ex, "Permissions cache: failed to write blob for user {UserId}.", userId);
          _l1.TryRemove(userId, out _);
          return entry;
        }
      }

      if (!result.Success)
      {
        return await GetEntryAsync(userId);
      }

      SetL1(userId, (entry, result.Blob.ETag, Clock.GetUtcNow()), preceding);
      return entry;
    }

    /// <summary>
    /// The last-resort reload used only when the blob's current state truly cannot be
    /// determined (the download attempt itself failed). Always overwrites — there is nothing
    /// to condition the write on — and is also what the base class's explicit
    /// <see cref="RefreshUserPermissionsCacheAsync"/> uses.
    /// </summary>
    private async Task<UserPermissionsCacheEntry> ReloadFromDbUnconditionallyAsync(Guid userId)
    {
      UserPermissionsCacheEntry entry = await LoadEntryFromDbAsync(userId);
      await SaveEntryAsync(userId, entry);
      return entry;
    }

    /// <summary>
    /// Writes <paramref name="value"/> to L1 as a compare-and-swap against
    /// <paramref name="preceding"/> — the tuple (or absence of one) observed when the enclosing
    /// call started — rather than an unconditional indexer assignment, so a Clear that removed
    /// or replaced the entry mid-flight is never overwritten by a call that started before it.
    /// </summary>
    private void SetL1(Guid userId,
      (UserPermissionsCacheEntry Entry, string ETag, DateTimeOffset VerifiedAtUtc) value,
      (UserPermissionsCacheEntry Entry, string ETag, DateTimeOffset VerifiedAtUtc)? preceding)
    {
      if (preceding.HasValue)
      {
        _l1.TryUpdate(userId, value, preceding.Value);
      }
      else
      {
        _l1.TryAdd(userId, value);
      }
    }

    protected override async Task SaveEntryAsync(Guid userId, UserPermissionsCacheEntry entry)
    {
      string cacheKey = GetCacheKey(userId);
      string json = JsonSerializer.Serialize(entry);
      byte[] bytes = Encoding.UTF8.GetBytes(json);

      using MemoryStream stream = new MemoryStream(bytes);

      try
      {
        var blob = await _blobStorageService.UpdateBlobAsync(
          _appSettings.Containers.PermissionsCache,
          cacheKey,
          stream);

        _l1[userId] = (entry, blob.ETag, Clock.GetUtcNow());
      }
      catch (Exception ex)
      {
        // If the cache write fails, drop any stale L1 entry to force a rebuild next read.
        _logger.LogWarning(ex, "Permissions cache: failed to write blob for user {UserId}.", userId);
        _l1.TryRemove(userId, out _);
      }
    }

    public override async Task ClearUserPermissionsFromCacheAsync(Guid userId)
    {
      _l1.TryRemove(userId, out _);

      try
      {
        await WriteTombstoneAsync(userId);
      }
      catch (Exception ex)
      {
        // The user's stale record is still trusted by every instance until the 24h max age,
        // which is too long for a revoke to wait on a transient storage fault. Hand the
        // invalidation to the retry queue, where Service Bus redelivers it until it lands or
        // is dead-lettered for a human to see. The caller is never failed: the grant change
        // itself has already committed to SQL.
        _logger.LogWarning(ex, "Permissions cache: failed to write invalidation tombstone for user {UserId}; enqueuing a retry.", userId);
        await EnqueueRetryAsync(userId);
      }
    }

    public override async Task RetryClearUserPermissionsFromCacheAsync(Guid userId)
    {
      _l1.TryRemove(userId, out _);

      // Deliberately no catch: the queue trigger relies on the exception to abandon the
      // message so Service Bus redelivers it.
      await WriteTombstoneAsync(userId);
    }

    public override async Task RetireUserPermissionsFromCacheAsync(Guid userId)
    {
      // Revoke first, exactly as a grant change would; this also covers the deferred
      // removal failing outright, since a tombstone ages out at MaxEntryAge anyway.
      await ClearUserPermissionsFromCacheAsync(userId);

      string queueName = _appSettings.Queues?.PermissionsCacheRetry;

      if (_serviceBusService == null || string.IsNullOrWhiteSpace(queueName))
      {
        // No queue to defer through. Delete now and accept the narrow race the delay
        // exists to close; the storage lifecycle rule is the backstop either way.
        try
        {
          await RemoveUserPermissionsFromCacheAsync(userId);
        }
        catch (Exception ex)
        {
          _logger.LogWarning(ex, "Permissions cache: immediate removal for deleted user {UserId} failed; the lifecycle rule will collect it.", userId);
        }

        return;
      }

      try
      {
        var message = new PermissionsCacheRetryMessage { UserId = userId, Action = PermissionsCacheRetryAction.Remove };
        string body = JsonSerializer.Serialize(message);
        DateTime scheduledFor = Clock.GetUtcNow().Add(RemovalDelay).UtcDateTime;

        await _serviceBusService.AddScheduledMessageAsync(queueName, sessionId: null, body, scheduledFor);
      }
      catch (Exception ex)
      {
        _logger.LogWarning(ex, "Permissions cache: failed to schedule removal for deleted user {UserId}; the lifecycle rule will collect it.", userId);
      }
    }

    public override async Task RemoveUserPermissionsFromCacheAsync(Guid userId)
    {
      _l1.TryRemove(userId, out _);

      // Deliberately no catch, for the same reason as the retry path.
      await _blobStorageService.DeleteBlobAsync(_appSettings.Containers.PermissionsCache, GetCacheKey(userId));
    }

    /// <summary>
    /// Overwrites the user's blob with fresh, always-stale content. Throws on failure.
    /// </summary>
    private async Task WriteTombstoneAsync(Guid userId)
    {
      string cacheKey = GetCacheKey(userId);
      UserPermissionsCacheEntry tombstone = CreateTombstone();
      string json = JsonSerializer.Serialize(tombstone);
      byte[] bytes = Encoding.UTF8.GetBytes(json);

      using MemoryStream stream = new MemoryStream(bytes);

      // A tombstone, not a delete: deleting the blob makes "missing" indistinguishable from
      // "never cached", so a reload already in flight — which may have observed the blob
      // missing before this ran — could still satisfy its own create-only write afterwards
      // and resurrect the pre-invalidation record. Writing fresh, always-stale content
      // instead gives every invalidation a distinct blob version no in-flight reader could
      // already hold, so a racing reload either loses its conditional write and retries, or
      // downloads this record and reloads because it reads as stale.
      await _blobStorageService.UpdateBlobAsync(_appSettings.Containers.PermissionsCache, cacheKey, stream);
    }

    private async Task EnqueueRetryAsync(Guid userId)
    {
      string queueName = _appSettings.Queues?.PermissionsCacheRetry;

      if (_serviceBusService == null || string.IsNullOrWhiteSpace(queueName))
      {
        // No queue wired (debugger / tests / a host without the setting): the 24h max age
        // remains the only backstop, which is worth an error rather than a warning.
        _logger.LogError("Permissions cache: no retry queue configured; user {UserId} keeps a stale record until it ages out.", userId);
        return;
      }

      try
      {
        var message = new PermissionsCacheRetryMessage { UserId = userId };
        string body = JsonSerializer.Serialize(message);

        await _serviceBusService.AddMessageAsync(queueName, sessionId: null, body,
          subject: PermissionsCacheRetryMessage.SUBJECT);
      }
      catch (Exception ex)
      {
        // Two independent services down at once. Nothing else to fall back to.
        _logger.LogError(ex, "Permissions cache: failed to enqueue invalidation retry for user {UserId}.", userId);
      }
    }

    private static UserPermissionsCacheEntry CreateTombstone()
    {
      return new UserPermissionsCacheEntry
      {
        Exists = false,
        RefreshedAtUtc = DateTimeOffset.MinValue,
        // Every invalidation must produce a distinct blob version, even two tombstones written
        // back-to-back for the same user, or a reload racing this one could satisfy an
        // If-Match against content that merely happens to be byte-identical to what it last saw.
        GrantedIds = new HashSet<Guid> { Guid.NewGuid() }
      };
    }
  }
}
