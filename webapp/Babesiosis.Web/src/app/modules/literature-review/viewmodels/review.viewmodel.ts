import { PagedResult } from 'app/core/viewmodels/paged-result';

/** Mirrors `ReviewViewModel`: one row of the Review list. */
export interface ReviewViewModel {
  instanceId: string;
  title: string;
  status: string;
  /** ISO 8601, UTC. */
  updatedDate: string;
}

/** The `{ page, permissions }` envelope `review-list-get` answers with. */
export interface ReviewListViewModel {
  page: PagedResult<ReviewViewModel>;
  permissions: Record<string, boolean>;
}
