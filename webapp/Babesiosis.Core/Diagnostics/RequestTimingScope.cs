using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.Linq;
using System.Text;

namespace Babesiosis.Core.Diagnostics
{
  /// <summary>
  /// One request's recorded spans. Created by <see cref="RequestTimings.BeginRequest"/>;
  /// never constructed directly.
  ///
  /// <para>
  /// Spans are kept in START order rather than completion order, because that is
  /// the order the code runs in and so the order someone reading the report is
  /// trying to follow. Nesting is tracked by a depth counter, which is exact for
  /// the sequential await chains these endpoints are built from and approximate
  /// if two spans are ever run concurrently — a concurrent span would be
  /// attributed to whichever one opened first. Its own duration stays correct
  /// either way; only the indentation can mislead.
  /// </para>
  /// </summary>
  public sealed class RequestTimingScope : IDisposable
  {
    /// <summary>Header length is not free and a runaway loop should not be able to
    /// produce a megabyte of it. The log report is NOT capped — only the header.</summary>
    private const int MaxHeaderMetrics = 40;

    private readonly Stopwatch _stopwatch = Stopwatch.StartNew();
    private readonly List<Entry> _entries = new List<Entry>();
    private readonly object _gate = new object();
    private int _depth;

    internal RequestTimingScope(string name)
    {
      Name = string.IsNullOrWhiteSpace(name) ? "request" : name;
    }

    /// <summary>What was being served — the request path, as the function layer names it.</summary>
    public string Name { get; }

    /// <summary>Wall clock since the scope opened.</summary>
    public double ElapsedMs => _stopwatch.Elapsed.TotalMilliseconds;

    /// <summary>Whether anything was actually recorded. A request with no spans has
    /// nothing worth logging.</summary>
    public bool HasEntries
    {
      get { lock (_gate) { return _entries.Count > 0; } }
    }

    internal IDisposable StartSpan(string label)
    {
      Entry entry;

      lock (_gate)
      {
        entry = new Entry(label, _depth, _stopwatch.Elapsed);
        _entries.Add(entry);
        _depth++;
      }

      return new Span(this, entry);
    }

    private void EndSpan(Entry entry)
    {
      lock (_gate)
      {
        entry.Complete(_stopwatch.Elapsed);

        if (_depth > 0)
        {
          _depth--;
        }
      }
    }

    /// <summary>
    /// The breakdown as a block of text, one span per line, indented by depth.
    ///
    /// <para>
    /// The trailing "unaccounted" figure sums only the TOP-LEVEL spans against the
    /// total — nested spans are inside their parents, so adding every entry would
    /// count the same milliseconds several times over. What is left is the work
    /// nobody instrumented: JSON, JWT, the worker's own dispatch and serialization.
    /// A large remainder means the next span belongs somewhere this file does not
    /// yet reach, which is a finding in itself.
    /// </para>
    /// </summary>
    public string Format()
    {
      List<Entry> entries;

      lock (_gate)
      {
        entries = _entries.ToList();
      }

      var total = ElapsedMs;
      var topLevel = entries.Where(e => e.Depth == 0).Sum(e => e.DurationMs);
      var builder = new StringBuilder();

      builder.Append(Name)
        .Append("  total ").Append(Round(total)).Append("ms")
        .Append("  (measured ").Append(Round(topLevel))
        .Append("ms, unaccounted ").Append(Round(Math.Max(0, total - topLevel))).Append("ms)");

      foreach (var entry in entries)
      {
        builder.AppendLine()
          .Append("  ")
          .Append(Round(entry.DurationMs).PadLeft(8))
          .Append("ms  ")
          .Append(new string(' ', entry.Depth * 2))
          .Append(entry.Label);

        if (!entry.Completed)
        {
          // An open span at flush time is a span whose `using` never ran — an
          // early return or a throw. Say so rather than print a plausible zero.
          builder.Append("  (did not complete)");
        }
      }

      return builder.ToString();
    }

    /// <summary>
    /// The same breakdown as a <c>Server-Timing</c> header value, so the browser's
    /// network panel renders it per request with no client code at all.
    ///
    /// <para>
    /// Metric names are positional (<c>s0</c>, <c>s1</c>, …) rather than derived
    /// from the label: the grammar allows only a token there, labels carry dots
    /// and would need escaping anyway, and duplicates — the same span recorded
    /// three times, which is precisely what we are hunting — must stay distinct.
    /// The readable label travels in <c>desc</c>, which is a quoted string and can
    /// hold it as-is.
    /// </para>
    /// </summary>
    public string ToServerTiming()
    {
      List<Entry> entries;

      lock (_gate)
      {
        entries = _entries.Take(MaxHeaderMetrics).ToList();
      }

      var metrics = new List<string>(entries.Count + 1)
      {
        "total;dur=" + Round(ElapsedMs)
      };

      for (var i = 0; i < entries.Count; i++)
      {
        metrics.Add(string.Concat(
          "s", i.ToString(CultureInfo.InvariantCulture),
          ";dur=", Round(entries[i].DurationMs),
          ";desc=\"", Describe(entries[i]), "\""));
      }

      return string.Join(", ", metrics);
    }

    public void Dispose()
    {
      _stopwatch.Stop();
      RequestTimings.Close(this);
    }

    /// <summary>Depth is carried in the description because the header has nowhere
    /// else to put it, and a flat list of repeated labels is unreadable without it.</summary>
    private static string Describe(Entry entry)
    {
      var label = entry.Label.Replace('"', '\'');

      return entry.Depth == 0 ? label : new string('>', entry.Depth) + " " + label;
    }

    private static string Round(double milliseconds)
    {
      return milliseconds.ToString("0.#", CultureInfo.InvariantCulture);
    }

    private sealed class Entry
    {
      private readonly TimeSpan _start;
      private TimeSpan? _end;

      internal Entry(string label, int depth, TimeSpan start)
      {
        Label = string.IsNullOrWhiteSpace(label) ? "(unnamed)" : label;
        Depth = depth;
        _start = start;
      }

      internal string Label { get; }
      internal int Depth { get; }
      internal bool Completed => _end.HasValue;
      internal double DurationMs => ((_end ?? _start) - _start).TotalMilliseconds;

      internal void Complete(TimeSpan end)
      {
        _end ??= end;
      }
    }

    private sealed class Span : IDisposable
    {
      private readonly RequestTimingScope _scope;
      private readonly Entry _entry;
      private bool _disposed;

      internal Span(RequestTimingScope scope, Entry entry)
      {
        _scope = scope;
        _entry = entry;
      }

      public void Dispose()
      {
        if (_disposed)
        {
          return;
        }

        _disposed = true;
        _scope.EndSpan(_entry);
      }
    }
  }
}
