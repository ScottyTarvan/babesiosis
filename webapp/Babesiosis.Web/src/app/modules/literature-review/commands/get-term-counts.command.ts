/** Mirrors `GetTermCountsCommand`. Filters arrive with the dashboard's filter bar. */
export interface GetTermCountsCommand {
  /** How many terms to return, highest article count first. The backend defaults to 20. */
  top?: number;
}
