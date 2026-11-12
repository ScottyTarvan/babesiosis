import { PagedResult } from 'app/core/viewmodels/paged-result';

/** How much of `pubDate` is known: year, month or day. */
export type ArticleDatePrecision = 'Y' | 'M' | 'D';

/**
 * The study-type labels `ArticleClassification` assigns on the server, in display
 * order. Reviews and case reports come from the inclusion type, the rest from the
 * evidence-type text; both are agent extractions, not human review.
 */
export const STUDY_TYPES = [
  'Descriptive', 'Associational', 'Mechanistic / experimental', 'Prognostic', 'Case reports', 'Reviews',
] as const;
export type ArticleStudyType = (typeof STUDY_TYPES)[number];

/**
 * The Babesia species labels `ArticleClassification` assigns on the server, in display
 * order: one named species, Multiple species (two or more named), Other named species
 * (vulpes, microti-like, conradae, negevi, Rangelia vitalii and similar) or Not identified in
 * text read (the text appraised names no species; reviews with no single species are Multiple species).
 */
export const SPECIES_GROUPS = [
  'B. canis', 'B. gibsoni', 'B. rossi', 'B. vogeli', 'Multiple species', 'Other named species', 'Not identified in text read',
] as const;
export type ArticleSpecies = (typeof SPECIES_GROUPS)[number];

/** Mirrors `ArticleViewModel`: one row of the Articles list. */
export interface ArticleViewModel {
  id: number;
  /** Review code, e.g. CB001. */
  code: string;
  /** ISO date (yyyy-MM-dd), the first day of the known period. */
  pubDate: string | null;
  pubDatePrecision: ArticleDatePrecision;
  /** The primary category's name; null when the article has none. */
  categoryName: string | null;
  /** The primary category's code, e.g. REN; null when the article has none. */
  categoryCode: string | null;
  /** The primary category's short label, e.g. Kidney; null when the article has none. */
  categoryLabel: string | null;
  /** Study type as the Evidence profile card classifies it; see `STUDY_TYPES`. */
  studyType: ArticleStudyType;
  /** Babesia species as the Evidence profile card classifies it; see `SPECIES_GROUPS`. */
  species: ArticleSpecies;
  /** The study country, tidied; null when none is stated. */
  country: string | null;
  journal: string | null;
  title: string;
  /** The article's one-sentence finding. */
  summary: string | null;
  /** Bare DOI, e.g. `10.1186/s13071-017-2106-8`; null when the article has none. */
  doi: string | null;
  /** PubMed identifier; null when the article is not in PubMed. */
  pmid: string | null;
  /**
   * Where the article opens outside this application: the publisher via the
   * DOI, else PubMed, else a recorded landing page. Null when no source is
   * known, and the title is then plain text.
   */
  sourceUrl: string | null;
}

/** The `{ page, permissions }` envelope `articles-list-get` answers with. */
export interface ArticleListViewModel {
  page: PagedResult<ArticleViewModel>;
  permissions: Record<string, boolean>;
}
