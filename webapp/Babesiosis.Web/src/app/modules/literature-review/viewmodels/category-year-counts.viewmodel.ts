/** Mirrors `CategoryYearCountsRowViewModel`: one category row of the matrix. */
export interface CategoryYearCountsRowViewModel {
  code: string;
  name: string;
  /** Short display name, e.g. "Renal". Null when the category has none. */
  label: string | null;
  /** One count per entry of `CategoryYearCountsViewModel.years`, in the same order. */
  counts: number[];
}

/**
 * Mirrors `CategoryYearCountsViewModel`: article counts per primary category
 * per publication year. `years` runs from the earliest to the latest with no gaps.
 */
export interface CategoryYearCountsViewModel {
  years: number[];
  categories: CategoryYearCountsRowViewModel[];
}
