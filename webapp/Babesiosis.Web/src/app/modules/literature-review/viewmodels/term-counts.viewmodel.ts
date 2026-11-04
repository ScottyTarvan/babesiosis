/** Mirrors `TermCountsRowViewModel`: one curated term and its article counts. */
export interface TermCountsRowViewModel {
  /** Display name; merged UMLS concepts count once under it. */
  name: string;
  /** Articles that studied the term (title, results, case or conclusion; the abstract for abstract-only articles). */
  studied: number;
  /** Articles that only mention it elsewhere. */
  mentionedOnly: number;
  total: number;
}

/**
 * Mirrors `TermCountsViewModel`: article counts per clinical syndrome or sign,
 * canine (CB) articles only, highest total first.
 */
export interface TermCountsViewModel {
  /** CB articles with at least one term. */
  articleCount: number;
  /** Of those, the articles whose terms come from the abstract alone. */
  abstractOnlyCount: number;
  terms: TermCountsRowViewModel[];
}
