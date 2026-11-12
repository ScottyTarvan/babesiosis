import { ChangeDetectionStrategy, Component, computed, DestroyRef, inject, OnInit, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import {
  FsBannerComponent,
  FsButtonComponent,
  FsCardComponent,
  FsChartBarComponent,
  FsEmptyStateComponent,
  fsObserveTheme,
  FsPageHeaderComponent,
  FsSpinnerComponent,
  FsStatCardComponent,
} from '@core';
import { errorMessage } from 'app/core/http-error';
import { BreakdownBarsComponent } from 'app/modules/review/components/breakdown-bars/breakdown-bars.component';
import { fullAndPartialYearColors } from 'app/modules/review/review-chart-colors';
import { heatLevel, PERIOD_THRESHOLDS } from 'app/modules/review/review-heat';
import { ARTICLES_URL, articleFilterParams, topicUrl } from 'app/modules/review/review-links';
import { ReviewService } from 'app/modules/review/review.service';
import { ReviewOverviewViewModel } from 'app/modules/review/viewmodels/review-overview.viewmodel';

/** Percentage, rounded; 0 when the base is 0. */
function percent(part: number, whole: number): number {
  return whole ? Math.round(100 * part / whole) : 0;
}

/**
 * The landing page: a newcomer's overview of 20 years of canine babesiosis research.
 * Canine (CB) articles only. Every figure comes from `review-overview-get`, which counts
 * them from the database; nothing here is a fixed number.
 */
@Component({
  selector: 'fs-home',
  standalone: true,
  imports: [
    RouterLink,
    FsBannerComponent,
    FsButtonComponent,
    FsCardComponent,
    FsChartBarComponent,
    FsEmptyStateComponent,
    FsPageHeaderComponent,
    FsSpinnerComponent,
    FsStatCardComponent,
    BreakdownBarsComponent,
  ],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HomeComponent implements OnInit {
  private readonly reviewService = inject(ReviewService);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly overview = signal<ReviewOverviewViewModel | null>(null);
  protected readonly loading = signal(false);
  protected readonly loadError = signal<string | null>(null);
  /** Bumped when the theme flips, so the chart colours re-read their tokens. */
  private readonly themeChanges = signal(0);

  protected readonly articlesUrl = ARTICLES_URL;
  protected readonly topicUrl = topicUrl;

  protected readonly summary = computed(() => this.overview()?.summary ?? null);

  protected readonly tiles = computed(() => {
    const s = this.summary();
    if (!s) {
      return [];
    }
    return [
      {
        label: 'Canine articles', value: s.canineArticles,
        note: `${s.primaryStudies + s.caseReports} primary studies and case reports, ${s.reviews} reviews`,
      },
      {
        label: 'Independent sources', value: s.independentSources,
        note: `${s.cohorts} cohorts published ${s.cohortArticles} of the articles`,
      },
      {
        label: 'Read in full text', value: s.fullText,
        note: `${s.abstractOnly} (${percent(s.abstractOnly, s.canineArticles)}%) were appraised from the abstract only`,
      },
      {
        label: 'High-confidence topic labels', value: s.highConfidence,
        note: `${s.lowConfidence} low-confidence, ${s.fallbackLabels} from a fallback label`,
      },
      {
        label: 'Median infected dogs', value: s.medianInfectedDogs ?? '–',
        note: `per primary study that states a number (${s.primaryStudiesWithSize} of ${s.primaryStudies})`,
      },
    ];
  });

  protected readonly caveats = computed(() => {
    const s = this.summary();
    if (!s) {
      return [];
    }
    const notHigh = s.lowConfidence + s.fallbackLabels;
    return [
      {
        title: 'Articles are not independent.',
        text: `${s.cohorts} cohorts published ${s.cohortArticles} of the ${s.canineArticles} articles, `
          + `so ${s.canineArticles} articles are ${s.independentSources} independent sources. Both counts are shown.`,
      },
      {
        title: 'Topics are assigned automatically.',
        text: `No person has reviewed the topic, design or species labels; ${notHigh} topic labels are not high-confidence.`,
      },
      {
        title: `${percent(s.abstractOnly, s.canineArticles)}% were read as abstracts only.`,
        text: `${s.abstractOnly} of ${s.canineArticles} articles; `
          + 'details such as country and sample size are often missing for them.',
      },
      {
        title: 'Only canine articles are counted.',
        text: 'Human comparator papers are not loaded into the app'
          + (s.backgroundArticles ? `, and ${s.backgroundArticles} background papers are kept apart.` : '.'),
      },
    ];
  });

  /** The year chart: full years and the partial first and last years as two stacked series. */
  protected readonly yearCategories = computed(() => (this.overview()?.years ?? []).map(y => String(y.year)));
  protected readonly yearSeries = computed(() => {
    const years = this.overview()?.years ?? [];
    return [
      { name: 'Full year', data: years.map(y => (y.partial ? 0 : y.articles)) },
      { name: 'Partial year', data: years.map(y => (y.partial ? y.articles : 0)) },
    ];
  });
  protected readonly yearColors = computed(() => {
    this.themeChanges();
    return fullAndPartialYearColors();
  });
  protected readonly yearSubtitle = computed(() => {
    const o = this.overview();
    if (!o) {
      return '';
    }
    const bands = o.periods.map(p => {
      const n = o.years.filter(y => y.year >= p.fromYear && y.year <= p.toYear).reduce((sum, y) => sum + y.articles, 0);
      return `${n} in ${p.label}`;
    });
    const partial = o.years.filter(y => y.partial).map(y => y.year).join(' and ');
    return `Canine articles per publication year: ${bands.join(', ')}. `
      + `${partial} are partial years (the window starts and ends 23 October).`;
  });

  /** The topics table: bars scaled to the largest topic, period cells shaded by count. */
  protected readonly topicRows = computed(() => {
    const o = this.overview();
    if (!o) {
      return [];
    }
    const max = Math.max(1, ...o.topics.map(t => t.articles));
    return o.topics.map(t => ({
      ...t,
      width: `${Math.max(1, Math.round(100 * t.articles / max))}%`,
      notHighWidth: `${percent(t.notHighConfidence, t.articles)}%`,
      abstractShare: percent(t.abstractOnly, t.articles),
      gridParams: articleFilterParams({ category: t.label }),
      cells: t.periodCounts.map((count, i) => ({
        count,
        heat: heatLevel(count, PERIOD_THRESHOLDS),
        tip: `${t.label}, ${o.periods[i]?.label}: ${count} articles`,
      })),
    }));
  });
  protected readonly weakestTopic = computed(() => {
    const rows = this.overview()?.topics.filter(t => t.articles > 0) ?? [];
    return rows.reduce<(typeof rows)[number] | null>((worst, t) =>
      !worst || t.notHighConfidence / t.articles > worst.notHighConfidence / worst.articles ? t : worst, null);
  });
  protected readonly lastPeriod = computed(() => {
    const periods = this.overview()?.periods ?? [];
    return periods[periods.length - 1] ?? null;
  });

  protected readonly countrySubtitle = computed(() => {
    const s = this.summary();
    return s
      ? `Canine articles by study country (${s.countries} countries after tidying ${s.countrySpellings} spellings), with the leading species.`
      : '';
  });
  protected readonly sizeSubtitle = computed(() => {
    const s = this.summary();
    return s
      ? `Infected dogs per primary study (${s.primaryStudies} studies). The median is ${s.medianInfectedDogs ?? '–'}.`
      : '';
  });
  protected readonly sizeFootnote = computed(() => {
    const o = this.overview();
    if (!o) {
      return '';
    }
    const small = o.sampleSizes.filter(r => r.label === '1–9' || r.label === '10–19').reduce((sum, r) => sum + r.articles, 0);
    const s = o.summary;
    return `${small} of the ${s.primaryStudiesWithSize} primary studies with a stated size have fewer than 20 infected dogs. `
      + `${s.primaryStudiesWithControls} primary studies report a control group.`;
  });
  /**
   * Why the "not identified" row is large: how many of it were appraised from the abstract
   * only, and that a smear alone does not identify the species.
   */
  protected readonly speciesFootnote = computed(() => {
    const row = this.overview()?.species.find(r => r.isUnknown);
    if (!row) {
      return '';
    }
    const abstractOnly = row.abstractOnly ?? 0;
    return `"${row.label}": ${abstractOnly} of these ${row.articles} articles were read as abstracts only, `
      + 'and a diagnosis from a blood smear alone does not give the species. Reviews that name no single species '
      + 'are counted as Multiple species.';
  });

  ngOnInit(): void {
    this.destroyRef.onDestroy(fsObserveTheme(() => this.themeChanges.update(n => n + 1)));
    this.load();
  }

  protected load(): void {
    this.loading.set(true);
    this.loadError.set(null);
    this.reviewService.getOverview()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: response => {
          this.overview.set(response);
          this.loading.set(false);
        },
        error: err => {
          this.loading.set(false);
          this.loadError.set(errorMessage(err, 'The overview could not be loaded.'));
        },
      });
  }
}
