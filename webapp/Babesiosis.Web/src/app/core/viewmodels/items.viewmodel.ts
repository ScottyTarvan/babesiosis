import { PagedResult } from "app/core/viewmodels/paged-result";
import { ViewModel } from "app/core/viewmodels/viewmodel";
import { UserStatsViewModel } from "@core/viewmodels/user-stats.viewmodel";

export class ItemsViewModel<T> extends ViewModel {

  public page: PagedResult<T>;
  public stats?: UserStatsViewModel;

  constructor(obj?: ItemsViewModel<T> | Partial<ItemsViewModel<T>>) {
    super(obj);
    if (obj) {
      this.page = new PagedResult<T>(obj.page);
      this.stats = obj.stats ? new UserStatsViewModel(obj.stats) : undefined;
    }
  }
}
