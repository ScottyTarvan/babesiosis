using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Threading;

namespace Babesiosis.Core.Diagnostics
{
  /// <summary>
  /// Ambient per-request timing. A scope is opened once by the function layer
  /// (<c>HttpFunctionBase</c>); everything below it — services, controllers, the
  /// SQL store — records named spans against that scope without knowing it
  /// exists and without taking a dependency on it through DI.
  ///
  /// <para>
  /// <b>Off unless asked for.</b> <see cref="Enabled"/> reads the
  /// <c>DM_REQUEST_TIMINGS</c> environment variable ONCE at type-init. When it
  /// is off no scope is ever opened, so every <see cref="Time"/> call is a null
  /// check and a shared no-op instance: no allocation, no stopwatch, nothing to
  /// flush. That is what makes it safe to leave the call sites in place
  /// permanently rather than deleting them after each investigation.
  /// </para>
  ///
  /// <para>
  /// <b>Why ambient and not injected.</b> The interesting call sites sit behind
  /// static provider factories (<c>UserPermissionItemsServiceProvider</c>) and
  /// static helpers (<c>ManageSystemDatasets</c>, <c>SqlManageDataStore</c>),
  /// none of which can be handed a scoped service without changing every
  /// signature between the function and the store. An <see cref="AsyncLocal{T}"/>
  /// flows there by itself, and flows per invocation: the isolated worker gives
  /// each request its own execution context, so two concurrent requests cannot
  /// see each other's spans.
  /// </para>
  /// </summary>
  public static class RequestTimings
  {
    /// <summary>Set to <c>1</c> or <c>true</c> to record. Locally that belongs in
    /// the Functions host's <c>local.settings.json</c> under <c>Values</c>.</summary>
    public const string EnvironmentVariable = "DM_REQUEST_TIMINGS";

    /// <summary>The response header the breakdown is echoed on, so the browser's
    /// network panel shows it without anyone reading a log.</summary>
    public const string HeaderName = "Server-Timing";

    private static readonly AsyncLocal<RequestTimingScope> _current = new AsyncLocal<RequestTimingScope>();

    static RequestTimings()
    {
      var flag = Environment.GetEnvironmentVariable(EnvironmentVariable);

      Enabled = string.Equals(flag, "1", StringComparison.Ordinal)
        || string.Equals(flag, "true", StringComparison.OrdinalIgnoreCase);

      // Announced once per process, and ONLY when on, so that silence has a
      // single meaning: the variable did not reach this process. Without it,
      // "no timings in the console" is ambiguous between the flag being unset,
      // the host running a stale build, and nothing having been instrumented on
      // the path under test — which cost an investigation the first time.
      if (Enabled)
      {
        Console.WriteLine($"[timings] enabled ({EnvironmentVariable}={flag})");
      }
    }

    /// <summary>Whether anything is recorded at all. Evaluated once per process.</summary>
    public static bool Enabled { get; }

    /// <summary>The open scope, or null when there is none (disabled, or a code
    /// path that no request opened — a queue trigger, a background job, a test).</summary>
    public static RequestTimingScope Current => _current.Value;

    /// <summary>
    /// Opens the request scope. Dispose closes it; read the breakdown off the
    /// returned scope BEFORE disposing, which is what the function layer does in
    /// its <c>finally</c>.
    /// </summary>
    public static RequestTimingScope BeginRequest(string name)
    {
      if (!Enabled)
      {
        return null;
      }

      var scope = new RequestTimingScope(name);
      _current.Value = scope;

      return scope;
    }

    /// <summary>
    /// Times a named region. Always safe to call: with no open scope it returns a
    /// shared no-op, so call sites need no guard of their own.
    /// </summary>
    public static IDisposable Time(string label)
    {
      var scope = _current.Value;

      return scope == null ? NoOpSpan.Instance : scope.StartSpan(label);
    }

    internal static void Close(RequestTimingScope scope)
    {
      if (ReferenceEquals(_current.Value, scope))
      {
        _current.Value = null;
      }
    }

    private sealed class NoOpSpan : IDisposable
    {
      internal static readonly NoOpSpan Instance = new NoOpSpan();

      private NoOpSpan() { }

      public void Dispose() { }
    }
  }
}
