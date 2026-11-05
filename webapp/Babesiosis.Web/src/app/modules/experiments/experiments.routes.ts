import { UrlMatchResult, UrlSegment } from '@angular/router';

/**
 * Matches `/experiments` and `/experiments/:code` with one route config, so the
 * router reuses the page component when another experiment is picked: the list
 * panel keeps its search text and scroll position instead of being rebuilt.
 */
export function experimentsUrlMatcher(segments: UrlSegment[]): UrlMatchResult | null {
  if (segments.length === 0 || segments.length > 2 || segments[0].path !== 'experiments') {
    return null;
  }
  const posParams: Record<string, UrlSegment> = {};
  if (segments[1]) posParams['code'] = segments[1];
  return { consumed: segments, posParams };
}
