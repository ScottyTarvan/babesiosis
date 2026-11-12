import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ARTICLES_URL, ArticleFilterParams, articleFilterParams } from 'app/modules/review/review-links';
import { BreakdownRowViewModel } from 'app/modules/review/viewmodels/review-shared.viewmodel';

/** What the column beside each bar shows. */
export type BreakdownAside = 'none' | 'recent' | 'note';

/**
 * A breakdown card's bars: one row per label, bar length relative to the largest row,
 * the article count, optionally the independent sources in brackets, and an aside
 * (recent share or a note). A "not stated" row is grey. When `filterKey` is set, a
 * row with a filter value links to the Articles grid filtered to it.
 */
@Component({
  selector: 'fs-breakdown-bars',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './breakdown-bars.component.html',
  styleUrls: ['./breakdown-bars.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BreakdownBarsComponent {
  readonly rows = input.required<readonly BreakdownRowViewModel[]>();
  /** The grid filter a row label sets; null for rows the grid cannot filter on. */
  readonly filterKey = input<keyof ArticleFilterParams | null>(null);
  /** Filters added to every row link, e.g. the topic on a topic page. */
  readonly baseFilter = input<ArticleFilterParams>({});
  readonly showIndependent = input(false);
  readonly aside = input<BreakdownAside>('none');
  /** Noun after the count in each row's tooltip. */
  readonly unit = input('articles');

  protected readonly articlesUrl = ARTICLES_URL;

  protected readonly view = computed(() => {
    const rows = this.rows();
    const max = Math.max(1, ...rows.map(r => r.articles));
    const key = this.filterKey();
    const base = this.baseFilter();
    const unit = this.unit();
    return rows.map(row => {
      const recentShare = row.recentArticles != null && row.articles
        ? Math.round(100 * row.recentArticles / row.articles) : null;
      return {
        ...row,
        width: `${Math.max(row.articles ? 1 : 0, Math.round(100 * row.articles / max))}%`,
        recentShare,
        queryParams: key && row.filterValue ? articleFilterParams({ ...base, [key]: row.filterValue }) : null,
        tip: `${row.label}: ${row.articles} ${unit}`
          + (row.independentSources != null ? `, ${row.independentSources} independent sources` : '')
          + (row.recentArticles != null ? `, ${row.recentArticles} published 2022–26` : ''),
      };
    });
  });
}
