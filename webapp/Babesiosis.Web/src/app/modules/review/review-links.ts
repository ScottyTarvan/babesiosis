import { Params } from '@angular/router';

/** The Articles grid. */
export const ARTICLES_URL = '/reference-articles';

/**
 * The Articles grid's query parameters, each presetting one column's filter
 * (`ReferenceArticlesComponent` reads them on load). Values are the labels the
 * server produces, so a preset always matches a row label exactly.
 */
export interface ArticleFilterParams {
  /** Primary category label, e.g. "Kidney". */
  category?: string;
  /** One of `STUDY_TYPES`. */
  studyType?: string;
  /** One of `SPECIES_GROUPS`. */
  species?: string;
  /** Tidied study country, e.g. "India". */
  country?: string;
  /** Article code, e.g. CB001. */
  code?: string;
}

/** The query parameter names, in the order the grid applies them. */
export const ARTICLE_FILTER_KEYS: readonly (keyof ArticleFilterParams)[] = ['code', 'category', 'studyType', 'species', 'country'];

/** Query params for a grid link; empty values are dropped. */
export function articleFilterParams(filter: ArticleFilterParams): Params {
  return Object.fromEntries(Object.entries(filter).filter(([, v]) => !!v));
}

/** The in-app link for one article: the grid filtered to its code. */
export function articleUrl(code: string): string {
  return `${ARTICLES_URL}?code=${encodeURIComponent(code)}`;
}

/** A topic page. */
export function topicUrl(code: string): string {
  return `/topics/${encodeURIComponent(code)}`;
}
