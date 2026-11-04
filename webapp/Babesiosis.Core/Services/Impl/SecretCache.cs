using System;
using System.Collections.Concurrent;

namespace Babesiosis.Core.Services.Impl
{
  /// <summary>
  /// An in-process, time-limited cache of secret values, keyed by vault and name.
  /// <para>
  /// Every linked-service connection string and every distribution-channel configuration is a
  /// Key Vault secret, and before this cache each read of one paid for a vault round trip — twice
  /// per manage-grid edit, once per lookup list, once per report query. Values change rarely
  /// (an operator editing a linked service) and every writer in the codebase goes through
  /// <see cref="IKeyVaultService"/>, so a short TTL plus removal on write keeps the host that
  /// made a change exact and bounds staleness elsewhere to the TTL.
  /// </para>
  /// <para>
  /// Thread-safe. The clock is injectable so expiry can be tested without waiting.
  /// </para>
  /// </summary>
  internal sealed class SecretCache
  {
    private readonly ConcurrentDictionary<string, Entry> _entries = new ConcurrentDictionary<string, Entry>();
    private readonly TimeSpan _timeToLive;
    private readonly Func<DateTimeOffset> _now;

    public SecretCache(TimeSpan timeToLive, Func<DateTimeOffset> now = null)
    {
      _timeToLive = timeToLive;
      _now = now ?? (() => DateTimeOffset.UtcNow);
    }

    /// <summary>The cached value, unless it is absent or has expired. An expired entry is dropped.</summary>
    public bool TryGet(string vault, string name, out string value)
    {
      var key = KeyFor(vault, name);

      if (_entries.TryGetValue(key, out var entry))
      {
        if (entry.ExpiresOn > _now())
        {
          value = entry.Value;
          return true;
        }

        _entries.TryRemove(key, out _);
      }

      value = null;
      return false;
    }

    public void Set(string vault, string name, string value)
    {
      _entries[KeyFor(vault, name)] = new Entry(value, _now() + _timeToLive);
    }

    public void Remove(string vault, string name)
    {
      _entries.TryRemove(KeyFor(vault, name), out _);
    }

    public void Clear()
    {
      _entries.Clear();
    }

    private static string KeyFor(string vault, string name)
    {
      return $"{vault}|{name}";
    }

    private readonly struct Entry
    {
      public Entry(string value, DateTimeOffset expiresOn)
      {
        Value = value;
        ExpiresOn = expiresOn;
      }

      public string Value { get; }
      public DateTimeOffset ExpiresOn { get; }
    }
  }
}
