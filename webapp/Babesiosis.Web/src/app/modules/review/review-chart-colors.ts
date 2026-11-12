import { fsChartCssColor, fsChartIntentColor } from '@core';

/** Blends two `#RRGGBB` colours: `weight` 0 gives `a`, 1 gives `b`. Falls back to `a` on any other format. */
export function mixHex(a: string, b: string, weight: number): string {
  const parse = (hex: string) => /^#[0-9a-f]{6}$/i.test(hex)
    ? [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16))
    : null;
  const from = parse(a);
  const to = parse(b);
  if (!from || !to) {
    return a;
  }
  return '#' + from
    .map((c, i) => Math.round(c + (to[i] - c) * weight).toString(16).padStart(2, '0'))
    .join('');
}

/**
 * The year chart's two colours: the theme's primary for full years and a lighter
 * blend of it into the card surface for the partial first and last years. Read
 * again whenever the theme flips.
 */
export function fullAndPartialYearColors(): [string, string] {
  const primary = fsChartIntentColor('primary');
  const surface = fsChartCssColor('--fs-color-surface', '#ffffff');
  return [primary, mixHex(primary, surface, 0.55)];
}
