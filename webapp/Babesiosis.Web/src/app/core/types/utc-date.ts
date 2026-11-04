/**
 * The one place a wire timestamp becomes a `Date`.
 *
 * **The problem this exists for.** The backing columns are `DATETIME2`, which
 * stores no offset, so EF materialises every value with
 * `DateTimeKind.Unspecified` however it was written. The serializer then emits
 * it with no designator — `"2026-08-28T05:48:21"` — and ECMAScript reads a
 * date-time with no designator as LOCAL time. A value stored as `UtcNow`
 * therefore lands in the browser as an instant that is wrong by exactly the
 * reader's offset, with nothing on the wire to reveal it.
 *
 * On SAST (+02:00) the resulting `Date` sits two hours early, so `getHours()`
 * prints back the UTC clock reading — which is how this surfaced: every
 * timestamp on the deployment log appeared to have skipped the conversion to
 * local time. It had not. It was never parsed as UTC in the first place.
 *
 * It is worse than a display fault, because the mis-parsed `Date` is a real
 * instant that is simply wrong: anything comparing it against `Date.now()` —
 * the deployment summary's Elapsed, the health dashboard's "12 minutes ago" —
 * is off by the offset too, and no amount of formatting recovers that.
 *
 * Fixing it at the parse boundary rather than at each render is what makes
 * every downstream use correct at once: grid sorting, `format:` callbacks,
 * duration arithmetic and CSV export all read the same corrected instant.
 */

/**
 * A full date-time with **no** zone designator — the shape that needs pinning.
 *
 * Deliberately anchored at both ends. A value already carrying `Z` or a numeric
 * offset must be left alone (pinning it twice would shift it), and a date-only
 * `"2026-08-28"` must be left alone too: ECMAScript already reads the date-only
 * form as UTC, and appending `Z` to it relies on lenient non-standard parsing
 * that only some engines accept.
 *
 * The optional fractional part covers `DATETIME2`'s seven digits, which is what
 * the wire actually carries.
 */
const UNZONED_DATE_TIME = /^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?$/;

/**
 * A wire timestamp as the UTC instant it actually is, or `null`.
 *
 * `null` — never a fallback date — for absent, unparseable, and
 * `DateTime.MinValue` input. The C# members are frequently non-nullable, so
 * "never happened" arrives as `0001-01-01`, and rendering that as a real date
 * ("01 Jan 1") reads as data rather than as the absence it is.
 *
 * Accepts an already-parsed `Date` so the callers that sit behind a grid — which
 * hands `date`/`datetime` columns a parsed value but a raw string from a cell
 * template — can route both through one function.
 */
export function parseUtcDate(value: unknown): Date | null {
  if (!value) return null;

  const date = value instanceof Date
    ? value
    : typeof value === 'string'
      ? new Date(UNZONED_DATE_TIME.test(value) ? `${value}Z` : value)
      : null;

  if (!date || Number.isNaN(date.getTime())) return null;

  // `DateTime.MinValue`. Compared in UTC because that is now what it was parsed
  // as; a local-time comparison would land in year 0 for positive offsets.
  return date.getUTCFullYear() <= 1 ? null : date;
}
