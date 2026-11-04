/** Mirrors `EvidenceProfileRowViewModel`: one study type or species and its raw articles per year. */
export interface EvidenceProfileRowViewModel {
  label: string;
  total: number;
  /** Articles per year, zero-filled, lined up with `EvidenceProfileViewModel.years`. */
  counts: number[];
}

/** Mirrors `EvidenceProfileBlockViewModel`: one way of slicing the articles; each article sits in one row. */
export interface EvidenceProfileBlockViewModel {
  title: string;
  rows: EvidenceProfileRowViewModel[];
}

/**
 * Mirrors `EvidenceProfileViewModel`: canine (CB) articles per year by study type
 * and by Babesia species, on a fixed year axis.
 */
export interface EvidenceProfileViewModel {
  /** CB articles counted; every block sums to this. */
  articleCount: number;
  /** The year axis, oldest first. */
  years: number[];
  blocks: EvidenceProfileBlockViewModel[];
}
