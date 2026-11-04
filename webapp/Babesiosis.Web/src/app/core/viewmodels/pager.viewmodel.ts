/**
 * PagerViewModel — mirrors the backend `Babesiosis.Core.ViewModels.PagerViewModel`
 * that every `teams-*` list endpoint returns alongside its item collection.
 *
 * Distinct from {@link PagingViewModel}, which is the newer `PagedResult<T>.paging`
 * shape used by the short-named endpoints. Where a component needs a total row
 * count for server-side paging, read `recordCount`.
 */
export class PagerViewModel {
  /** First record number on the page, as in `{1}`-10 of 100. */
  start = 0;
  /** Last record number on the page, as in 1-`{10}` of 100. */
  end = 0;
  /** Current page, 1-based. */
  page = 0;
  /** Configured page size. */
  pageSize = 0;
  /** Total number of pages. */
  pageCount = 0;
  /** Actual number of records in this page. */
  pageRecordCount = 0;
  /** Total number of records in the whole dataset. */
  recordCount = 0;

  constructor(pager?: PagerViewModel | Partial<PagerViewModel>) {
    if (pager) {
      this.start = pager.start ?? 0;
      this.end = pager.end ?? 0;
      this.page = pager.page ?? 0;
      this.pageSize = pager.pageSize ?? 0;
      this.pageCount = pager.pageCount ?? 0;
      this.pageRecordCount = pager.pageRecordCount ?? 0;
      this.recordCount = pager.recordCount ?? 0;
    }
  }
}
