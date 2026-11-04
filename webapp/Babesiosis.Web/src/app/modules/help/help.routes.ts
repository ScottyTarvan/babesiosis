import { UrlMatchResult, UrlSegment } from '@angular/router';

/**
 * Matches `/help`, `/help/:module` and `/help/:module/:topic` (spec
 * `platform/help-support.md` §3.9) with one route config, so the router
 * reuses the page component when moving between topics — the search box
 * and tree keep their state instead of the page being rebuilt.
 */
export function helpUrlMatcher(segments: UrlSegment[]): UrlMatchResult | null {
  if (segments.length === 0 || segments.length > 3 || segments[0].path !== 'help') {
    return null;
  }
  const posParams: Record<string, UrlSegment> = {};
  if (segments[1]) posParams['module'] = segments[1];
  if (segments[2]) posParams['topic'] = segments[2];
  return { consumed: segments, posParams };
}
