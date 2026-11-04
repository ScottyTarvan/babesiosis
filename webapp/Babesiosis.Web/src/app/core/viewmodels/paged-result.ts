import { PagingViewModel } from "app/core/viewmodels/paging.viewmodel";

export class PagedResult<T> {
  items: T[];
  paging: PagingViewModel;

  constructor(obj?: PagedResult<T> | Partial<PagedResult<T>>) {
    if (obj) {
      this.items = obj.items ?? [];
      this.paging = new PagingViewModel(obj.paging);
    }
  }
}
