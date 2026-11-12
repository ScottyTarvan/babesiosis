import { UrlMatchResult, UrlSegment } from '@angular/router';

/**
 * Matches `/clinical` and `/clinical/:id` with one route config, so the router
 * reuses the page component when another page of the manual is picked: the rail
 * keeps its filter text and scroll position instead of being rebuilt.
 */
export function clinicalUrlMatcher(segments: UrlSegment[]): UrlMatchResult | null {
  if (segments.length === 0 || segments.length > 2 || segments[0].path !== 'clinical') {
    return null;
  }
  const posParams: Record<string, UrlSegment> = {};
  if (segments[1]) posParams['id'] = segments[1];
  return { consumed: segments, posParams };
}
