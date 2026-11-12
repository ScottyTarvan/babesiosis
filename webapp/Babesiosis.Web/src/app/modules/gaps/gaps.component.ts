import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, DestroyRef, inject, OnInit, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import {
  FsBannerComponent,
  FsButtonComponent,
  FsCardComponent,
  FsEmptyStateComponent,
  FsPageHeaderComponent,
  FsSpinnerComponent,
  FsSymbolComponent,
} from '@core';
import { errorMessage } from 'app/core/http-error';
import { SynthesisTextComponent } from 'app/modules/review/components/synthesis-text/synthesis-text.component';
import { HEAT_LEGEND, heatLevel } from 'app/modules/review/review-heat';
import { ARTICLES_URL, articleFilterParams, topicUrl } from 'app/modules/review/review-links';
import { ReviewService } from 'app/modules/review/review.service';
import { ReviewGapsViewModel } from 'app/modules/review/viewmodels/review-gaps.viewmodel';

/** The category codes CROSS.md names, e.g. "ERY, END, REN and OXO". */
const CATEGORY_CODE = /\b(ERY|INF|END|COA|REN|PUL|NEU|CAR|MET|OXO|SEV)\b/g;

/**
 * The Gaps and questions screen, `/gaps`: canine articles by topic and study design with
 * empty cells outlined, four gap figures computed from the same counts, and the
 * cross-cutting themes (CROSS.md) and candidate research questions (QUESTIONS.md), each
 * expandable to its full text as written.
 */
@Component({
  selector: 'fs-gaps',
  standalone: true,
  imports: [
    DatePipe,
    RouterLink,
    FsBannerComponent,
    FsButtonComponent,
    FsCardComponent,
    FsEmptyStateComponent,
    FsPageHeaderComponent,
    FsSpinnerComponent,
    FsSymbolComponent,
    SynthesisTextComponent,
  ],
  templateUrl: './gaps.component.html',
  styleUrls: ['./gaps.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class GapsComponent implements OnInit {
  private readonly reviewService = inject(ReviewService);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly data = signal<ReviewGapsViewModel | null>(null);
  protected readonly loading = signal(false);
  protected readonly loadError = signal<string | null>(null);

  protected readonly articlesUrl = ARTICLES_URL;
  protected readonly topicUrl = topicUrl;
  protected readonly legend = HEAT_LEGEND;

  /** The matrix: each cell shaded by count, empty cells outlined, non-empty cells linking to the grid. */
  protected readonly rows = computed(() => {
    const d = this.data();
    if (!d) {
      return [];
    }
    return d.rows.map(row => ({
      ...row,
      cells: row.counts.map((count, i) => ({
        count,
        heat: heatLevel(count),
        tip: `${row.label}, ${d.designs[i].toLowerCase()}: ${count} articles`,
        params: count ? articleFilterParams({ category: row.label, studyType: d.designs[i] }) : null,
      })),
    }));
  });

  /** A one-line title for the matrix from its empty cells: the topics with neither a prognostic nor a mechanistic study. */
  protected readonly matrixTitle = computed(() => {
    const d = this.data();
    if (!d) {
      return 'Topics by study design';
    }
    const prognostic = d.designs.indexOf('Prognostic');
    const mechanistic = d.designs.indexOf('Mechanistic / experimental');
    const neither = d.rows.filter(r => r.counts[prognostic] === 0 && r.counts[mechanistic] === 0).map(r => r.label);
    if (!neither.length || prognostic < 0 || mechanistic < 0) {
      return 'Topics by study design';
    }
    const names = neither.map((label, i) => (i ? label.toLowerCase() : label));
    // Semicolons between three or more: the labels hold "and" themselves.
    const list = names.length === 1 ? names[0]
      : names.length === 2 ? `${names[0]} and ${names[1]}`
      : `${names.slice(0, -1).join('; ')}; and ${names[names.length - 1]}`;
    return `${list}: no prognostic study and no experiment`;
  });

  /** Each theme with the topic codes its text names, for the collapsed row's second line. */
  protected readonly themes = computed(() => (this.data()?.themes ?? []).map(theme => {
    const codes = [...new Set(theme.body.match(CATEGORY_CODE) ?? [])];
    return { ...theme, codes };
  }));

  ngOnInit(): void {
    this.load();
  }

  protected load(): void {
    this.loading.set(true);
    this.loadError.set(null);
    this.reviewService.getGaps()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: response => {
          this.data.set(response);
          this.loading.set(false);
        },
        error: err => {
          this.loading.set(false);
          this.loadError.set(errorMessage(err, 'The gaps and questions could not be loaded.'));
        },
      });
  }
}
