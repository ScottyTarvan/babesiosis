// Builds the server `LoadOptions` (skip / take / sort / filter) wire payload
// from `<fs-data-table>` state, for grids that filter/sort/page server-side.
//
// The filter array follows the load-options grammar the backend understands
// (binary `[selector, op, value]`, group `[expr, "and"|"or", expr]`); the
// backend translates it to a query (see Babesiosis.Core.Search.DynamicLinqFilter).

import { LoadOptions } from 'app/core/commands/search.command';
import {
  FsColumnFilter,
  FsFilters,
  FsPageState,
  FsSortState,
  FsTableColumn,
} from '@fundstream-ai/gnome-ui';

export interface BuildLoadOptionsOptions<T = unknown> {
  /** Columns for the grid — used to resolve each active filter's type. */
  columns: FsTableColumn<T>[];
  /**
   * Optional overrides mapping a grid column key to its backing entity
   * selector for server-side filter/sort (e.g. `{ clientName: 'Client.Name' }`).
   * Keys not present here are sent unchanged.
   */
  selectorMap?: Record<string, string>;
}

type FilterClause = unknown[];

/**
 * Converts the current table filter/sort/page state into a `LoadOptions`
 * payload. Active column filters are combined with `"and"`. Returns a payload
 * with `requireTotalCount` so the grid can show the server total.
 */
export function buildLoadOptions<T>(
  filters: FsFilters,
  sort: FsSortState | null,
  page: FsPageState,
  options: BuildLoadOptionsOptions<T>,
): LoadOptions {
  const selectorFor = (key: string): string => options.selectorMap?.[key] ?? key;
  const filterFor = (key: string): FsColumnFilter | undefined =>
    options.columns.find(c => c.key === key)?.filter;

  const clauses: FilterClause[] = [];
  for (const key of Object.keys(filters)) {
    const columnFilter = filterFor(key);
    if (!columnFilter) continue;
    const clause = toClause(selectorFor(key), columnFilter, filters[key]);
    if (clause) clauses.push(clause);
  }

  const result: LoadOptions = {
    skip: page.pageIndex * page.pageSize,
    take: page.pageSize,
    requireTotalCount: true,
  };

  const filter = combineWithAnd(clauses);
  if (filter) result.filter = filter;
  if (sort) result.sort = [{ selector: selectorFor(sort.key), desc: sort.direction === 'desc' }];

  return result;
}

function toClause(selector: string, filter: FsColumnFilter, value: unknown): FilterClause | null {
  switch (filter.type) {
    case 'search': {
      const text = typeof value === 'string' ? value.trim() : '';
      return text ? [selector, 'contains', text] : null;
    }
    case 'single-select':
      return value === null || value === undefined || value === '' ? null : [selector, '=', value];
    case 'multi-select': {
      const values = Array.isArray(value) ? value : [];
      if (values.length === 0) return null;
      if (values.length === 1) return [selector, '=', values[0]];
      // [[sel, '=', v1], 'or', [sel, '=', v2], ...]
      const parts: unknown[] = [];
      values.forEach((v, index) => {
        if (index > 0) parts.push('or');
        parts.push([selector, '=', v]);
      });
      return parts;
    }
    case 'date-range': {
      const range = (value ?? {}) as { from?: string | null; to?: string | null };
      const parts: unknown[] = [];
      if (range.from) parts.push([selector, '>=', range.from]);
      if (range.to) {
        if (parts.length > 0) parts.push('and');
        parts.push([selector, '<=', endOfDayIso(range.to)]);
      }
      if (parts.length === 0) return null;
      return parts.length === 1 ? (parts[0] as FilterClause) : parts;
    }
  }
}

function combineWithAnd(clauses: FilterClause[]): unknown[] | null {
  if (clauses.length === 0) return null;
  if (clauses.length === 1) return clauses[0];
  const combined: unknown[] = [];
  clauses.forEach((clause, index) => {
    if (index > 0) combined.push('and');
    combined.push(clause);
  });
  return combined;
}

/**
 * Inclusive end-of-day so a `to` bound includes the whole day, matching the
 * client-side `filterDateRange` helper's behaviour.
 */
function endOfDayIso(date: string): string {
  const parsed = new Date(date);
  if (isNaN(parsed.getTime())) return date;
  parsed.setHours(23, 59, 59, 999);
  return parsed.toISOString();
}
