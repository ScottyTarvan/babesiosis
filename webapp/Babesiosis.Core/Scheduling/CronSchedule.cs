using System;
using System.Collections.Generic;
using Cronos;

namespace Babesiosis.Core.Scheduling
{
  /// <summary>
  /// Parses, validates and evaluates the 5-field cron expressions a Timer activator runs on.
  /// Every schedule is fixed to SAST - there is deliberately no time-zone picker and no raw-cron
  /// mode - and the sweep itself only ticks every <see cref="SweepIntervalMinutes"/> minutes, so
  /// <see cref="Validate"/> rejects a minute field that could ever ask for anything finer.
  /// </summary>
  public static class CronSchedule
  {
    /// <summary>
    /// How often <c>event-trigger-timer-sweep</c> ticks, and so the only minute grid a schedule
    /// may use. The sweep's TimerTrigger attribute needs a literal, so it repeats this value; the
    /// web designer mirrors it as <c>SWEEP_INTERVAL_MINUTES</c>. Change all three together.
    /// </summary>
    public const int SweepIntervalMinutes = 30;

    /// <summary>
    /// Africa/Johannesburg, falling back to the Windows id when the IANA id is not registered on
    /// the host. South Africa has never observed daylight saving, so this is a fixed UTC+2 offset
    /// - there is no ambiguous/invalid wall-clock handling to do here, unlike a DST zone.
    /// </summary>
    public static TimeZoneInfo SastTimeZone { get; } = ResolveSastTimeZone();

    private static TimeZoneInfo ResolveSastTimeZone()
    {
      try
      {
        return TimeZoneInfo.FindSystemTimeZoneById("Africa/Johannesburg");
      }
      catch (Exception error) when (error is TimeZoneNotFoundException || error is InvalidTimeZoneException)
      {
        return TimeZoneInfo.FindSystemTimeZoneById("South Africa Standard Time");
      }
    }

    /// <summary>
    /// True when <paramref name="expression"/> is a parseable 5-field (standard) cron expression
    /// whose minute field only ever produces minutes on the <see cref="SweepIntervalMinutes"/>
    /// grid. False with a human-readable
    /// reason in <paramref name="error"/> otherwise.
    /// </summary>
    public const int MaxLength = 100;

    public static bool Validate(string expression, out string error)
    {
      if (string.IsNullOrWhiteSpace(expression))
      {
        error = "A cron expression is required.";
        return false;
      }

      // meta.EventTrigger.CronExpression is VARCHAR(100) - fail here, not as a SQL truncation 500.
      if (expression.Length > MaxLength)
      {
        error = $"A cron expression cannot be longer than {MaxLength} characters.";
        return false;
      }

      try
      {
        CronExpression.Parse(expression, CronFormat.Standard);
      }
      catch (CronFormatException ex)
      {
        error = ex.Message;
        return false;
      }

      // Parse above already enforces 5 whitespace-separated fields for CronFormat.Standard, except
      // for the macro forms ("@daily" etc.) it also accepts - reject those explicitly rather than
      // read a macro token as a minute field below.
      var fields = expression.Split((char[])null, StringSplitOptions.RemoveEmptyEntries);
      if (fields.Length != 5)
      {
        error = "A cron expression must have exactly 5 fields (minute hour day month day-of-week).";
        return false;
      }

      return ValidateMinuteField(fields[0], out error);
    }

    /// <summary>The next SAST occurrence strictly after <paramref name="afterUtc"/>, as UTC.</summary>
    public static DateTime? Next(string expression, DateTime afterUtc)
    {
      var cron = CronExpression.Parse(expression, CronFormat.Standard);
      var next = cron.GetNextOccurrence(AsUtc(afterUtc), SastTimeZone);
      return next.HasValue ? DateTime.SpecifyKind(next.Value, DateTimeKind.Utc) : null;
    }

    /// <summary>
    /// The most recent SAST occurrence at or before <paramref name="atUtc"/> (inclusive). This is
    /// the slot an outage-recovery tick should treat as "the one that is due now" - unlike the
    /// row's stale <c>NextRunUtc</c>, which after a multi-day outage is still the FIRST slot that
    /// was ever missed. Falls back to <paramref name="atUtc"/> itself only when the expression can
    /// never produce an occurrence at or before it, which does not happen for a schedule already
    /// known to be due.
    /// </summary>
    public static DateTime Previous(string expression, DateTime atUtc)
    {
      var cron = CronExpression.Parse(expression, CronFormat.Standard);
      var at = AsUtc(atUtc);
      var previous = cron.GetPreviousOccurrence(at, SastTimeZone, inclusive: true);
      return previous.HasValue ? DateTime.SpecifyKind(previous.Value, DateTimeKind.Utc) : at;
    }

    /// <summary>
    /// The next <paramref name="count"/> SAST occurrences strictly after <paramref name="afterUtc"/>,
    /// as UTC - the schedule designer's "next 5 runs" preview. Shorter than <paramref name="count"/>
    /// only if the expression can never fire again, which a validated standard expression never does.
    /// </summary>
    public static IReadOnlyList<DateTime> NextMany(string expression, DateTime afterUtc, int count)
    {
      var results = new List<DateTime>(Math.Max(count, 0));
      if (count <= 0) return results;

      var cron = CronExpression.Parse(expression, CronFormat.Standard);
      var cursor = AsUtc(afterUtc);

      for (var i = 0; i < count; i++)
      {
        var next = cron.GetNextOccurrence(cursor, SastTimeZone);
        if (!next.HasValue) break;

        cursor = DateTime.SpecifyKind(next.Value, DateTimeKind.Utc);
        results.Add(cursor);
      }

      return results;
    }

    /// <summary>
    /// Cronos insists on Kind == Utc and throws otherwise. EF Core hands back Unspecified for
    /// every datetime2 column, so that Kind is trusted as UTC rather than rejected; a Local value
    /// (a test literal, a debugger watch) is converted properly instead of being reinterpreted.
    /// </summary>
    private static DateTime AsUtc(DateTime value)
    {
      if (value.Kind == DateTimeKind.Local) return value.ToUniversalTime();
      return DateTime.SpecifyKind(value, DateTimeKind.Utc);
    }

    /// <summary>
    /// Accepts N, a comma list, a range, and */S or a-b/S, provided every minute the field could
    /// ever produce is on the <see cref="SweepIntervalMinutes"/> grid; rejects a bare '*' outright. This is deliberately simpler
    /// than a general cron-field parser - it only has to recognise the shapes CronSchedule.Validate
    /// itself, and the designer's presets, can ever produce.
    /// </summary>
    private static bool ValidateMinuteField(string minuteField, out string error)
    {
      error = null;
      const int grid = SweepIntervalMinutes;

      foreach (var raw in minuteField.Split(','))
      {
        var token = raw.Trim();
        if (token.Length == 0)
        {
          error = "The minute field has an empty entry.";
          return false;
        }

        if (token == "*")
        {
          error = $"The minute field cannot be '*' - the sweep only runs every {grid} minutes, so pick a step or specific minutes.";
          return false;
        }

        var rangePart = token;
        int? step = null;
        var slash = token.IndexOf('/');
        if (slash >= 0)
        {
          rangePart = token.Substring(0, slash);
          if (!int.TryParse(token.Substring(slash + 1), out var parsedStep) || parsedStep <= 0)
          {
            error = $"'{token}' is not a valid minute step.";
            return false;
          }
          step = parsedStep;
        }

        if (rangePart == "*")
        {
          if (step is null || step.Value % grid != 0)
          {
            error = $"'{token}' must step by a multiple of {grid} minutes.";
            return false;
          }
          continue;
        }

        var dash = rangePart.IndexOf('-');
        if (dash >= 0)
        {
          if (!int.TryParse(rangePart.Substring(0, dash), out var start) ||
              !int.TryParse(rangePart.Substring(dash + 1), out var end) ||
              start < 0 || end > 59 || start > end)
          {
            error = $"'{token}' is not a valid minute range.";
            return false;
          }

          if (step.HasValue)
          {
            // The sequence is start, start + step, start + 2*step, ... - every term stays a
            // multiple of the grid iff both the start and the step already are, regardless of end.
            if (start % grid != 0 || step.Value % grid != 0)
            {
              error = $"'{token}' must start on and step by a multiple of {grid} minutes.";
              return false;
            }
          }
          else
          {
            // No step: every integer in the range fires, so every one of them has to qualify.
            for (var minute = start; minute <= end; minute++)
            {
              if (minute % grid != 0)
              {
                error = $"'{token}' includes minute {minute}, which is not a multiple of {grid}.";
                return false;
              }
            }
          }
          continue;
        }

        if (!int.TryParse(rangePart, out var value) || value < 0 || value > 59)
        {
          error = $"'{token}' is not a valid minute value.";
          return false;
        }

        if (value % grid != 0)
        {
          error = $"'{token}' is not a multiple of {grid} minutes.";
          return false;
        }

        if (step.HasValue && step.Value % grid != 0)
        {
          error = $"'{token}' must step by a multiple of {grid} minutes.";
          return false;
        }
      }

      return true;
    }
  }
}
