import { ChangeDetectionStrategy, Component, computed, DestroyRef, inject, OnInit, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import {
  FsBannerComponent,
  FsButtonComponent,
  FsCardComponent,
  FsChartBarComponent,
  fsChartCssColor,
  fsChartGreys,
  fsChartIntentColor,
  FsChartLineComponent,
  FsEmptyStateComponent,
  fsObserveTheme,
  FsPageHeaderComponent,
  FsSparklineComponent,
  FsSpinnerComponent,
} from '@core';
import { errorMessage } from 'app/core/http-error';
import { ChartLabelTitlesDirective } from 'app/modules/literature-review/directives/chart-label-titles.directive';
import { ChartNoWheelZoomDirective } from 'app/modules/literature-review/directives/chart-no-wheel-zoom.directive';
import { EqualRowHeightsDirective } from 'app/modules/literature-review/directives/equal-row-heights.directive';
import { LiteratureReviewService } from 'app/modules/literature-review/literature-review.service';
import { EvidenceProfileViewModel } from 'app/modules/literature-review/viewmodels/evidence-profile.viewmodel';
import { TermCountsViewModel } from 'app/modules/literature-review/viewmodels/term-counts.viewmodel';

/** Blends two `#RRGGBB` colours: `weight` 0 gives `a`, 1 gives `b`. Falls back to `a` on any other format. */
function mixHex(a: string, b: string, weight: number): string {
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

/** Trailing rolling mean: each point averages itself and up to `window - 1` points before it. */
function rollingMean(values: number[], window: number): number[] {
  return values.map((_, i) => {
    const slice = values.slice(Math.max(0, i - window + 1), i + 1);
    return slice.reduce((sum, v) => sum + v, 0) / slice.length;
  });
}

/** Years summed for the evidence profile's "Share" column: the last five on the axis (2022 to 2026). */
const EVIDENCE_SHARE_YEARS = 5;

/** The Literature Review dashboard: article counts by category, year and term, and the evidence profile. */
@Component({
  selector: 'fs-literature-review',
  standalone: true,
  imports: [
    FsBannerComponent,
    FsButtonComponent,
    FsCardComponent,
    FsChartBarComponent,
    FsChartLineComponent,
    FsEmptyStateComponent,
    FsPageHeaderComponent,
    FsSparklineComponent,
    FsSpinnerComponent,
    ChartLabelTitlesDirective,
    ChartNoWheelZoomDirective,
    EqualRowHeightsDirective,
  ],
  templateUrl: './literature-review.component.html',
  styleUrls: ['./literature-review.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LiteratureReviewComponent implements OnInit {
  private readonly literatureReviewService = inject(LiteratureReviewService);
  private readonly destroyRef = inject(DestroyRef);

  /** Article counts per category (by code, in SortOrder), one count per year of `categoryYears`. */
  protected readonly categoryYearRows = signal<{ code: string; counts: number[] }[]>([]);
  /** Category code to label, the series title in the stacked bar chart's tooltip. */
  protected readonly categoryLabels = signal<Record<string, string>>({});
  /** Category code to full name, the hover title on both category charts' legends. */
  protected readonly categoryNames = signal<Record<string, string>>({});
  /** Publication years, the x-axis of the stacked bar and the trend line chart. */
  protected readonly categoryYears = signal<string[]>([]);
  /**
   * One series per category, shared by the stacked bar and the trend lines.
   * Named by code to keep the legend short; the legend hover and the bar
   * tooltip give the full name.
   */
  protected readonly categoryYearSeries = computed(() => this.categoryYearRows().map(row => ({
    name: row.code,
    data: row.counts,
  })));
  /** Bumped when the theme flips, so the category colours re-read their tokens. */
  private readonly themeChanges = signal(0);
  /**
   * One `--fs-color-category-N` hue per category, by position: the categories
   * come back in SortOrder, every one of them, so a category keeps its colour.
   * Past the last token a category goes grey rather than repeating a hue.
   */
  protected readonly categoryYearColors = computed(() => {
    this.themeChanges();
    const fallback = fsChartGreys().muted;
    return this.categoryYearRows().map((_, i) => fsChartCssColor(`--fs-color-category-${i + 1}`, fallback));
  });
  protected readonly categoryYearTooltip = computed(() => {
    const labels = this.categoryLabels();
    return { y: { title: { formatter: (code: string) => `${labels[code] ?? code}:` } } };
  });
  protected readonly categoryYearLoading = signal(false);
  protected readonly categoryYearError = signal<string | null>(null);

  /**
   * Top clinical syndromes and signs by canine article count, highest first, from the
   * curated UMLS terms (hidden and merged in core/data/terms/term_display.csv).
   */
  protected readonly termCounts = signal<TermCountsViewModel>({ articleCount: 0, abstractOnlyCount: 0, terms: [] });
  protected readonly termNames = computed(() => this.termCounts().terms.map(t => t.name));
  /** Two stacked series: studied (dark) and mentioned only (light). */
  protected readonly termSeries = computed(() => {
    const terms = this.termCounts().terms;
    return [
      { name: 'Studied', data: terms.map(t => t.studied) },
      { name: 'Mentioned only', data: terms.map(t => t.mentionedOnly) },
    ];
  });
  /**
   * Primary for studied, muted grey for mentioned only; re-read when the theme flips.
   * The theme's muted grey is darker than primary, so it is blended halfway into the
   * surface colour to keep the studied segment the stronger of the two.
   */
  protected readonly termColors = computed(() => {
    this.themeChanges();
    const surface = fsChartCssColor('--fs-color-surface', '#ffffff');
    return [fsChartIntentColor('primary'), mixHex(fsChartGreys().muted, surface, 0.5)];
  });
  protected readonly termSubtitle = computed(() => {
    const { terms, articleCount, abstractOnlyCount } = this.termCounts();
    if (!terms.length) {
      return 'Studied and mentioned only';
    }
    return `Top ${terms.length} · studied (coloured) and mentioned only (grey) · `
      + `${abstractOnlyCount} of ${articleCount} articles abstract-only`;
  });
  protected readonly termLoading = signal(false);
  protected readonly termError = signal<string | null>(null);

  /**
   * Canine articles per year by study type and by Babesia species. The server sends raw
   * counts; each row here carries its 3-year rolling mean (the sparkline) and the share
   * of its articles published in the last five years.
   */
  protected readonly evidenceProfile = signal<EvidenceProfileViewModel>({ articleCount: 0, years: [], blocks: [] });
  protected readonly evidenceYears = computed(() => this.evidenceProfile().years.map(String));
  protected readonly evidenceBlocks = computed(() => this.evidenceProfile().blocks.map((block, i) => ({
    title: block.title,
    // One colour per block, not per row.
    intent: i === 0 ? 'primary' as const : 'success' as const,
    rows: block.rows.map(row => {
      const recent = row.counts.slice(-EVIDENCE_SHARE_YEARS).reduce((sum, v) => sum + v, 0);
      return {
        label: row.label,
        total: row.total,
        trend: rollingMean(row.counts, 3),
        share: row.total ? Math.round(100 * recent / row.total) : 0,
      };
    }),
  })));
  protected readonly evidenceSubtitle = computed(() =>
    'Articles per year, 3-year rolling average · '
    + `${this.evidenceProfile().articleCount} canine articles · 2006 is a partial year`);
  protected readonly evidenceLoading = signal(false);
  protected readonly evidenceError = signal<string | null>(null);

  /** True while any part of the dashboard is still loading. */
  protected readonly refreshing = computed(() =>
    this.categoryYearLoading() || this.termLoading()
    || this.evidenceLoading());

  ngOnInit(): void {
    this.destroyRef.onDestroy(fsObserveTheme(() => this.themeChanges.update(n => n + 1)));
    this.refresh();
  }

  /** Reloads every chart on the dashboard. */
  protected refresh(): void {
    this.loadCategoryYearCounts();
    this.loadTermCounts();
    this.loadEvidenceProfile();
  }

  protected loadCategoryYearCounts(): void {
    this.categoryYearLoading.set(true);
    this.categoryYearError.set(null);
    this.literatureReviewService.getCategoryYearCounts()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: response => {
          const years = response.years ?? [];
          const categories = response.categories ?? [];
          this.categoryYears.set(years.map(String));
          this.categoryYearRows.set(categories.map(category => ({
            code: category.code,
            counts: years.map((_, i) => category.counts[i] ?? 0),
          })));
          // A category with no label falls back to its full name.
          this.categoryLabels.set(Object.fromEntries(
            categories.map(category => [category.code, category.label || category.name])));
          this.categoryNames.set(Object.fromEntries(
            categories.map(category => [category.code, category.name])));
          this.categoryYearLoading.set(false);
        },
        error: err => {
          this.categoryYearLoading.set(false);
          this.categoryYearError.set(errorMessage(err, 'The category counts could not be loaded.'));
        },
      });
  }

  protected loadTermCounts(): void {
    this.termLoading.set(true);
    this.termError.set(null);
    this.literatureReviewService.getTermCounts()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: response => {
          this.termCounts.set({
            articleCount: response.articleCount ?? 0,
            abstractOnlyCount: response.abstractOnlyCount ?? 0,
            terms: response.terms ?? [],
          });
          this.termLoading.set(false);
        },
        error: err => {
          this.termLoading.set(false);
          this.termError.set(errorMessage(err, 'The syndrome and sign counts could not be loaded.'));
        },
      });
  }

  protected loadEvidenceProfile(): void {
    this.evidenceLoading.set(true);
    this.evidenceError.set(null);
    this.literatureReviewService.getEvidenceProfile()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: response => {
          const years = response.years ?? [];
          this.evidenceProfile.set({
            articleCount: response.articleCount ?? 0,
            years,
            blocks: (response.blocks ?? []).map(block => ({
              title: block.title,
              rows: (block.rows ?? []).map(row => ({
                label: row.label,
                total: row.total ?? 0,
                counts: years.map((_, i) => row.counts?.[i] ?? 0),
              })),
            })),
          });
          this.evidenceLoading.set(false);
        },
        error: err => {
          this.evidenceLoading.set(false);
          this.evidenceError.set(errorMessage(err, 'The evidence profile could not be loaded.'));
        },
      });
  }
}
