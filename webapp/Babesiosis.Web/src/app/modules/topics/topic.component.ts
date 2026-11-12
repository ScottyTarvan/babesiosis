import { DatePipe } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  computed,
  DestroyRef,
  inject,
  OnInit,
  signal,
  TemplateRef,
  viewChild,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { catchError, EMPTY, map, Subject, switchMap, tap } from 'rxjs';
import {
  FsBannerComponent,
  FsButtonComponent,
  FsCardComponent,
  FsDataGridComponent,
  FsEmptyStateComponent,
  FsGridCellContext,
  FsGridColumn,
  FsPageHeaderComponent,
  FsSpinnerComponent,
  FsStatCardComponent,
  FsSymbolComponent,
} from '@core';
import { errorMessage } from 'app/core/http-error';
import { BreakdownBarsComponent } from 'app/modules/review/components/breakdown-bars/breakdown-bars.component';
import { SynthesisTextComponent } from 'app/modules/review/components/synthesis-text/synthesis-text.component';
import { heatLevel, PERIOD_THRESHOLDS } from 'app/modules/review/review-heat';
import { ARTICLES_URL, articleFilterParams, topicUrl } from 'app/modules/review/review-links';
import { ReviewService } from 'app/modules/review/review.service';
import { ReviewTopicViewModel, TopicArticleViewModel } from 'app/modules/review/viewmodels/review-topic.viewmodel';

type ArticleCell = TemplateRef<FsGridCellContext<TopicArticleViewModel>>;

/** The synthesis section shown as the page's lead question rather than in the body. */
const QUESTION_KEY = 'question-this-direction-asks';

function percent(part: number, whole: number): number {
  return whole ? Math.round(100 * part / whole) : 0;
}

/**
 * One topic (category) page, `/topics/:code`: the topic's live figures, its study designs
 * and periods, its narrative synthesis as written (core/search/synthesis/<CODE>.md, loaded
 * by the console's --synthesis-only mode) and its canine articles. Figures come from
 * `review-topic-get`; the synthesis text is shown unedited.
 */
@Component({
  selector: 'fs-topic',
  standalone: true,
  imports: [
    DatePipe,
    RouterLink,
    FsBannerComponent,
    FsButtonComponent,
    FsCardComponent,
    FsDataGridComponent,
    FsEmptyStateComponent,
    FsPageHeaderComponent,
    FsSpinnerComponent,
    FsStatCardComponent,
    FsSymbolComponent,
    BreakdownBarsComponent,
    SynthesisTextComponent,
  ],
  templateUrl: './topic.component.html',
  styleUrls: ['./topic.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TopicComponent implements OnInit {
  private readonly reviewService = inject(ReviewService);
  private readonly route = inject(ActivatedRoute);
  private readonly destroyRef = inject(DestroyRef);

  private readonly titleCell = viewChild.required<ArticleCell>('titleCell');
  private readonly wrapCell = viewChild.required<ArticleCell>('wrapCell');
  private readonly dogsCell = viewChild.required<ArticleCell>('dogsCell');

  /** Each load request; switchMap drops a response a newer topic has overtaken. */
  private readonly loads = new Subject<string>();

  protected readonly code = signal('');
  protected readonly data = signal<ReviewTopicViewModel | null>(null);
  protected readonly loading = signal(false);
  protected readonly loadError = signal<string | null>(null);

  protected readonly articlesUrl = ARTICLES_URL;
  protected readonly topicUrl = topicUrl;

  protected readonly topic = computed(() => this.data()?.topic ?? null);
  protected readonly question = computed(() => this.data()?.synthesis.find(s => s.key === QUESTION_KEY) ?? null);
  protected readonly sections = computed(() => this.data()?.synthesis.filter(s => s.key !== QUESTION_KEY) ?? []);
  protected readonly gridParams = computed(() => articleFilterParams({ category: this.topic()?.label }));

  protected readonly tiles = computed(() => {
    const d = this.data();
    const t = d?.topic;
    if (!d || !t) {
      return [];
    }
    return [
      {
        label: `Articles with ${t.label.toLowerCase()} as main topic`, value: t.articles,
        note: `${percent(t.articles, d.canineArticles)}% of the ${d.canineArticles} canine articles`,
      },
      {
        label: 'Independent sources', value: t.independentSources,
        note: t.cohorts ? `${t.cohortArticles} articles share ${t.cohorts} cohorts` : 'no article shares a cohort',
      },
      { label: 'Other articles that touch it', value: t.secondaryTags, note: `${t.label} as a secondary topic` },
      { label: 'Abstract-only', value: t.abstractOnly, note: `of ${t.articles}; ${t.articles - t.abstractOnly} read in full text` },
      { label: 'Label not high-confidence', value: t.notHighConfidence, note: `of ${t.articles}; assigned automatically` },
    ];
  });

  protected readonly periods = computed(() => {
    const d = this.data();
    if (!d) {
      return [];
    }
    return d.periods.map((p, i) => {
      const count = d.topic.periodCounts[i] ?? 0;
      return { label: p.label, count, heat: heatLevel(count, PERIOD_THRESHOLDS) };
    });
  });

  protected readonly designSubtitle = computed(() => {
    const d = this.data();
    if (!d) {
      return '';
    }
    const none = d.designs.filter(r => !r.articles).map(r => r.label.toLowerCase());
    return `${d.topic.articles} articles` + (none.length ? `; none ${none.join(', ')}.` : '.');
  });

  protected readonly columns = computed<FsGridColumn<TopicArticleViewModel>[]>(() => [
    { dataField: 'code', caption: 'ID', width: 84 },
    { dataField: 'year', caption: 'Year', dataType: 'number', width: 76, sortOrder: 'desc', sortIndex: 0 },
    { dataField: 'title', caption: 'Article', minWidth: 220, cellTemplate: this.titleCell() },
    { dataField: 'studyType', caption: 'Design', width: 150 },
    { dataField: 'infectedDogs', caption: 'Infected dogs', dataType: 'number', width: 120, cellTemplate: this.dogsCell() },
    { dataField: 'species', caption: 'Species', width: 140 },
    { dataField: 'finding', caption: 'Finding in one sentence', minWidth: 260, cellTemplate: this.wrapCell() },
  ]);

  ngOnInit(): void {
    this.loads.pipe(
      tap(() => {
        this.loading.set(true);
        this.loadError.set(null);
      }),
      switchMap(code => this.reviewService.getTopic({ code }).pipe(
        catchError(err => {
          this.loading.set(false);
          this.data.set(null);
          this.loadError.set(errorMessage(err, `The topic ${code} could not be loaded.`));
          return EMPTY;
        }),
      )),
      takeUntilDestroyed(this.destroyRef),
    ).subscribe(response => {
      this.data.set(response);
      this.loading.set(false);
    });

    this.route.paramMap.pipe(
      map(params => (params.get('code') ?? '').toUpperCase()),
      takeUntilDestroyed(this.destroyRef),
    ).subscribe(code => {
      this.code.set(code);
      this.loads.next(code);
    });
  }

  protected reload(): void {
    this.loads.next(this.code());
  }
}
