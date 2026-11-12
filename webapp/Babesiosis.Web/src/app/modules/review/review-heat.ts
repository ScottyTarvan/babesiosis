/**
 * Heat shading for count cells (topics table periods, the gaps matrix), on the
 * app's own primary colour so it follows the theme.
 *
 * Levels 0..5: 0 is an empty cell (no fill; the gaps matrix outlines it), 1..5
 * step the primary colour's alpha. The level comes from fixed thresholds, so the
 * same count gets the same shade on every screen. SCSS reads the level from a
 * `data-heat` attribute (see `review-heat.scss`).
 */
export type HeatLevel = 0 | 1 | 2 | 3 | 4 | 5;

/** Upper bounds of levels 1..4 for the gaps matrix (counts 0 to about 50); above the last is level 5. */
export const MATRIX_THRESHOLDS: readonly number[] = [2, 5, 12, 24];
/** Upper bounds for the topics table's period cells (five- and six-year bands, counts up to about 50). */
export const PERIOD_THRESHOLDS: readonly number[] = [5, 10, 20, 30];

export function heatLevel(count: number, thresholds: readonly number[] = MATRIX_THRESHOLDS): HeatLevel {
  if (!count) {
    return 0;
  }
  const index = thresholds.findIndex(max => count <= max);
  return (index === -1 ? 5 : index + 1) as HeatLevel;
}

/** The legend's steps, lightest first. */
export const HEAT_LEGEND: readonly HeatLevel[] = [1, 2, 3, 4, 5];
