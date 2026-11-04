import { MockRegistration } from 'app/_mocks/mock-handler';
import { GetReviewListCommand } from 'app/modules/literature-review/commands/get-review-list.command';
import { ReviewListViewModel, ReviewViewModel } from 'app/modules/literature-review/viewmodels/review.viewmodel';

/**
 * Mirrors `GetReviewListController`, which returns the same three placeholder
 * rows until phase two gives Review real data.
 */
const DAY = 24 * 60 * 60 * 1000;
const iso = (offsetDays: number) => new Date(Date.now() + offsetDays * DAY).toISOString();

const reviews: ReviewViewModel[] = [
  { instanceId: '3f6d2a10-7c1e-4b8a-9d2f-1a2b3c4d5e01', title: 'Sample review 1', status: 'Open', updatedDate: iso(-1) },
  { instanceId: '3f6d2a10-7c1e-4b8a-9d2f-1a2b3c4d5e02', title: 'Sample review 2', status: 'In progress', updatedDate: iso(-3) },
  { instanceId: '3f6d2a10-7c1e-4b8a-9d2f-1a2b3c4d5e03', title: 'Sample review 3', status: 'Closed', updatedDate: iso(-7) },
];

export const reviewListGetMock: MockRegistration<GetReviewListCommand, ReviewListViewModel> = {
  route: 'review-list-get',
  handler: () => ({
    page: {
      items: reviews,
      paging: {
        totalCount: reviews.length,
        pageIndex: 0,
        pageSize: reviews.length,
        totalPages: 1,
        hasPreviousPage: false,
        hasNextPage: false,
      },
    },
    permissions: {},
  }),
};
