export class PagingViewModel {
  totalCount: number;
  pageIndex: number;
  pageSize: number;
  totalPages: number;
  hasPreviousPage: boolean;
  hasNextPage: boolean;

  constructor(obj?: PagingViewModel | Partial<PagingViewModel>) {
    if (obj) {
      this.totalCount = obj.totalCount ?? 0;
      this.pageIndex = obj.pageIndex ?? 0;
      this.pageSize = obj.pageSize ?? 0;
      this.totalPages = obj.totalPages ?? 0;
      this.hasPreviousPage = obj.hasPreviousPage ?? false;
      this.hasNextPage = obj.hasNextPage ?? false;
    }
  }
}
