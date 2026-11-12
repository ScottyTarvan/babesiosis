/** Mirrors `PeriodViewModel`: one period band of the topics table, e.g. 2006–10. */
export interface PeriodViewModel {
  label: string;
  fromYear: number;
  toYear: number;
}

/**
 * Mirrors `TopicRowViewModel`: one category's figures, the overview's topics-table row and
 * the topic page's tiles. Canine (CB) articles whose primary category this is.
 */
export interface TopicRowViewModel {
  code: string;
  /** Short plain-language name, e.g. "Kidney". */
  label: string;
  /** Formal category name, shown on hover. */
  name: string;
  articles: number;
  /** Articles with no cohort plus distinct cohorts. */
  independentSources: number;
  cohortArticles: number;
  cohorts: number;
  /** Canine articles that carry this category as a secondary tag. */
  secondaryTags: number;
  /** Articles per period band, in the order of the response's `periods`. */
  periodCounts: number[];
  /** Articles whose category label is low-confidence or a fallback. */
  notHighConfidence: number;
  abstractOnly: number;
}

/** Mirrors `BreakdownRowViewModel`: one bar of a breakdown card. */
export interface BreakdownRowViewModel {
  label: string;
  /** The value the Articles grid filters on for this row; null when it cannot. */
  filterValue: string | null;
  articles: number;
  independentSources: number | null;
  /** Articles published 2022–26 (species card). */
  recentArticles: number | null;
  /** Articles appraised from the abstract only (species card). */
  abstractOnly?: number | null;
  note: string | null;
  /** A "not stated" / "not reported" row, drawn in grey. */
  isUnknown: boolean;
}

/** Mirrors `SynthesisSectionViewModel`: one headed section of a synthesis, as written (Markdown). */
export interface SynthesisSectionViewModel {
  key: string;
  heading: string;
  body: string;
}
