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
import { catchError, EMPTY, Subject, switchMap, tap } from 'rxjs';
import {
  FsBannerComponent,
  FsButtonComponent,
  FsCardComponent,
  FsDataGridComponent,
  FsGridCellContext,
  FsGridColumn,
  FsGridFilterExpression,
  FsGridFilterOperation,
  FsGridFilterRow,
  FsGridPager,
  FsGridRemoteLoadEvent,
  FsGridRemoteLoadOptions,
  FsPageHeaderComponent,
  FsSymbolComponent,
} from '@core';
import { errorMessage } from 'app/core/http-error';
import { ReferenceArticlesService } from 'app/modules/reference-articles/reference-articles.service';
import {
  ArticleDatePrecision,
  ArticleViewModel,
  SPECIES_GROUPS,
  STUDY_TYPES,
} from 'app/modules/reference-articles/viewmodels/article.viewmodel';

type ArticleCell = TemplateRef<FsGridCellContext<ArticleViewModel>>;

/**
 * Every article loaded to the database, the source set for analysis.
 * Filtered, sorted and paged server-side by `articles-list-get`, 500 rows a page.
 */
@Component({
  selector: 'fs-reference-articles',
  standalone: true,
  imports: [
    DatePipe,
    FsBannerComponent,
    FsButtonComponent,
    FsCardComponent,
    FsDataGridComponent,
    FsPageHeaderComponent,
    FsSymbolComponent,
  ],
  templateUrl: './reference-articles.component.html',
  styleUrls: ['./reference-articles.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ReferenceArticlesComponent implements OnInit {
  private readonly referenceArticlesService = inject(ReferenceArticlesService);
  private readonly destroyRef = inject(DestroyRef);

  private readonly pubDateCell = viewChild.required<ArticleCell>('pubDateCell');
  private readonly categoryCell = viewChild.required<ArticleCell>('categoryCell');
  private readonly titleCell = viewChild.required<ArticleCell>('titleCell');
  private readonly wrapCell = viewChild.required<ArticleCell>('wrapCell');

  /** Each grid query; switchMap drops a response a newer query has overtaken. */
  private readonly loads = new Subject<FsGridRemoteLoadOptions>();
  private lastLoad: FsGridRemoteLoadOptions | null = null;

  protected readonly pageSize = 500;
  protected readonly pager: FsGridPager = {
    visible: true,
    showPageSizeSelector: true,
    allowedPageSizes: [100, 250, 500],
    showNavigationButtons: true,
    showInfo: true,
  };
  protected readonly filterRow: FsGridFilterRow = { visible: true, showOperationChooser: true };

  protected readonly rows = signal<ArticleViewModel[]>([]);
  protected readonly totalCount = signal(0);
  protected readonly loading = signal(false);
  protected readonly loadError = signal<string | null>(null);

  protected readonly columns = computed<FsGridColumn<ArticleViewModel>[]>(() => [
    {
      dataField: 'pubDate', caption: 'Publish date', dataType: 'date', width: 170,
      sortOrder: 'desc', sortIndex: 0,
      cellTemplate: this.pubDateCell(), calculateFilterExpression: pubDateFilter,
    },
    { dataField: 'categoryName', caption: 'Category', width: 260, cellTemplate: this.categoryCell() },
    // The two labels the Evidence profile card counts, filtered from a fixed list
    // rather than typed, so a filter always names a label the server produces.
    {
      dataField: 'studyType', caption: 'Study type', width: 190,
      lookup: { dataSource: STUDY_TYPES, allowClearing: true },
      filterOperations: ['=', '<>'], selectedFilterOperation: '=',
    },
    {
      dataField: 'species', caption: 'Babesia species', width: 170,
      lookup: { dataSource: SPECIES_GROUPS, allowClearing: true },
      filterOperations: ['=', '<>'], selectedFilterOperation: '=',
    },
    { dataField: 'journal', caption: 'Journal', width: 220, cellTemplate: this.wrapCell() },
    { dataField: 'title', caption: 'Title', cellTemplate: this.titleCell() },
    { dataField: 'summary', caption: 'Summary', cellTemplate: this.wrapCell() },
  ]);

  ngOnInit(): void {
    this.loads.pipe(
      tap(() => {
        this.loading.set(true);
        this.loadError.set(null);
      }),
      switchMap(options => this.referenceArticlesService.getArticleList({ loadOptions: options }).pipe(
        catchError(err => {
          this.loading.set(false);
          this.loadError.set(errorMessage(err, 'The articles could not be loaded.'));
          return EMPTY;
        }),
      )),
      takeUntilDestroyed(this.destroyRef),
    ).subscribe(response => {
      this.rows.set(response.page?.items ?? []);
      this.totalCount.set(response.page?.paging?.totalCount ?? 0);
      this.loading.set(false);
    });
  }

  /** The grid never fetches: it hands over skip, take, sort and filter, and waits for `[data]`. */
  protected onRemoteLoad(event: FsGridRemoteLoadEvent): void {
    this.lastLoad = event.options;
    this.loads.next(event.options);
  }

  /**
   * Refresh and Retry: re-run the grid's last query, so the current page, sort
   * and filters are kept.
   */
  protected reload(): void {
    if (this.lastLoad) {
      this.loads.next(this.lastLoad);
    }
  }

  /** A year-only date reads "2019", a month-only one "Mar 2019", never a made-up day. */
  protected dateFormat(precision: ArticleDatePrecision): string {
    switch (precision) {
      case 'Y': return 'y';
      case 'M': return 'MMM y';
      default: return 'd MMM y';
    }
  }
}

/**
 * The filter row hands date values over as local-midnight `Date`s, which JSON
 * would send as the UTC instant: a day early east of Greenwich. Send the
 * calendar date instead.
 */
function toCalendarDate(value: unknown): unknown {
  if (!(value instanceof Date)) {
    return value;
  }
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${value.getFullYear()}-${pad(value.getMonth() + 1)}-${pad(value.getDate())}`;
}

/**
 * The publish-date filter as the server reads it: calendar dates, and
 * `between` spelt out as `>=` / `<=`, which the server has no operator for.
 */
function pubDateFilter(value: unknown, operation: FsGridFilterOperation | string | null): FsGridFilterExpression {
  if (operation === 'between') {
    const [start, end] = (Array.isArray(value) ? value : []).map(toCalendarDate);
    const parts: FsGridFilterExpression[] = [];
    if (start != null) parts.push(['pubDate', '>=', start]);
    if (end != null) parts.push(['pubDate', '<=', end]);
    return parts.length === 1 ? parts[0] : [parts[0], 'and', parts[1]];
  }
  return ['pubDate', (operation ?? '=') as FsGridFilterOperation, toCalendarDate(value)];
}
