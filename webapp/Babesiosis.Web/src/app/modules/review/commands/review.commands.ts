/** Mirrors `GetReviewOverviewCommand`, which has no parameters. */
export type GetReviewOverviewCommand = Record<string, never>;

/** Mirrors `GetReviewTopicCommand`. */
export interface GetReviewTopicCommand {
  /** A category code, e.g. REN. */
  code: string;
}

/** Mirrors `GetReviewGapsCommand`, which has no parameters. */
export type GetReviewGapsCommand = Record<string, never>;
