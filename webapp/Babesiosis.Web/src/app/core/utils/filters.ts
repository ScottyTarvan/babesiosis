// Shared filter helpers for fs-data-table.
//
// Used by features to apply filter state to row arrays. Each helper takes a
// row array, the filter value, and the row field to compare against, and
// returns the filtered array.
//
// The methodology's Section 11 "filter contract" requires that the column
// key (used to declare the column and store the filter value) appears
// exactly once at the call site. These helpers help enforce that by taking
// the row field as a parameter — features pass `filters[column.key]` and
// the row field separately, so a typo can be caught at the call site.

/** Case-insensitive substring search across one or more row fields. */
export function filterSearch<T>(
  rows: T[],
  value: string | null | undefined,
  fields: (keyof T)[],
): T[] {
  const trimmed = (value ?? '').trim().toLowerCase();
  if (!trimmed) return rows;
  return rows.filter(row =>
    fields.some(field => {
      const fieldValue = row[field];
      if (fieldValue == null) return false;
      return String(fieldValue).toLowerCase().includes(trimmed);
    }),
  );
}

/** Row passes when row[field] is one of the values. Empty values → no filter. */
export function filterMultiValues<T, V>(
  rows: T[],
  values: V[] | null | undefined,
  field: keyof T,
): T[] {
  if (!values || values.length === 0) return rows;
  const set = new Set(values);
  return rows.filter(row => set.has(row[field] as unknown as V));
}

/** Row passes when row[field] equals the value. null/undefined → no filter. */
export function filterSingleValue<T, V>(
  rows: T[],
  value: V | null | undefined,
  field: keyof T,
): T[] {
  if (value === null || value === undefined) return rows;
  return rows.filter(row => row[field] === (value as unknown));
}

export interface FilterDateRange {
  from?: string | null;
  to?: string | null;
}

/**
 * Filter rows whose date field falls within the range (inclusive).
 * Accepts ISO yyyy-mm-dd or anything Date.parse can read on both the row field
 * and the range bounds. Empty range → no filter.
 */
export function filterDateRange<T>(
  rows: T[],
  range: FilterDateRange | null | undefined,
  field: keyof T,
): T[] {
  if (!range || (!range.from && !range.to)) return rows;
  const fromTs = range.from ? Date.parse(range.from) : Number.NEGATIVE_INFINITY;
  const toTs = range.to ? Date.parse(range.to) : Number.POSITIVE_INFINITY;
  // toTs is the *start* of the to date; we want to include the whole day,
  // so push it to the end of the day.
  const toEndTs = range.to ? toTs + 24 * 60 * 60 * 1000 - 1 : toTs;
  return rows.filter(row => {
    const v = row[field];
    if (v == null) return false;
    const ts = typeof v === 'number' ? v : Date.parse(String(v));
    if (isNaN(ts)) return false;
    return ts >= fromTs && ts <= toEndTs;
  });
}
