import { parseUtcDate } from 'app/core/types/utc-date';

/**
 * The rule every wire timestamp in the app now goes through. Written as
 * assertions about the *instant* — `toISOString()` — rather than about rendered
 * text, because the bug this function exists for produced a `Date` holding the
 * wrong instant while every formatter was working correctly.
 *
 * Timezone-independent by construction: nothing here asserts a local rendering,
 * so the suite gives the same answer on a CI box in UTC as on a developer's in
 * SAST. That matters — the fault it guards against is invisible at UTC+00:00.
 */
describe('parseUtcDate', () => {

  /**
   * The core case. `DATETIME2` carries no offset, so the wire value arrives
   * unzoned; read as local it would be wrong by the reader's offset, which is
   * exactly what made the deployment log appear to show UTC.
   */
  it('reads an unzoned wire timestamp as UTC', () => {
    expect(parseUtcDate('2026-08-28T05:48:21')?.toISOString())
      .toBe('2026-08-28T05:48:21.000Z');
  });

  /** `DATETIME2`'s seven fractional digits are what the wire actually carries. */
  it('accepts sub-second precision', () => {
    expect(parseUtcDate('2026-08-28T05:48:21.1234567')?.toISOString())
      .toBe('2026-08-28T05:48:21.123Z');
  });

  /** Minutes-only is a legal unzoned form and must pin the same way. */
  it('accepts a minute-precision timestamp', () => {
    expect(parseUtcDate('2026-08-28T05:48')?.toISOString())
      .toBe('2026-08-28T05:48:00.000Z');
  });

  /**
   * Idempotence is what lets this land alongside the endpoints already emitting
   * `Z` — the entity-group reads, which were patched server-side — and what will
   * let the backend be corrected later without double-shifting anything.
   */
  it('leaves an already-zoned value alone', () => {
    expect(parseUtcDate('2026-08-28T05:48:21Z')?.toISOString())
      .toBe('2026-08-28T05:48:21.000Z');
    expect(parseUtcDate('2026-08-28T05:48:21+02:00')?.toISOString())
      .toBe('2026-08-28T03:48:21.000Z');
  });

  /**
   * A calendar date is not an instant. ECMAScript already reads the date-only
   * form as UTC, and appending `Z` to it would rely on lenient parsing that not
   * every engine accepts — so effective dates and the like must pass untouched.
   */
  it('leaves a date-only value untouched', () => {
    expect(parseUtcDate('2026-08-28')?.toISOString())
      .toBe('2026-08-28T00:00:00.000Z');
  });

  /**
   * The C# members are frequently non-nullable, so "never happened" arrives as
   * MinValue. Rendering that as "01 Jan 1" reads as data rather than absence.
   */
  it('treats DateTime.MinValue as absent', () => {
    expect(parseUtcDate('0001-01-01T00:00:00')).toBeNull();
  });

  it('returns null for absent or unparseable input', () => {
    expect(parseUtcDate(null)).toBeNull();
    expect(parseUtcDate(undefined)).toBeNull();
    expect(parseUtcDate('')).toBeNull();
    expect(parseUtcDate('not-a-date')).toBeNull();
    expect(parseUtcDate(new Date('nonsense'))).toBeNull();
  });

  /** Grids hand `datetime` columns a parsed `Date` but a raw string from a cell
   *  template, so one function has to serve both. */
  it('passes an already-parsed Date through', () => {
    const date = new Date('2026-08-28T05:48:21Z');
    expect(parseUtcDate(date)).toBe(date);
  });
});
