import {
  BreakdownRowViewModel,
  PeriodViewModel,
  TopicRowViewModel,
} from 'app/modules/review/viewmodels/review-shared.viewmodel';

/** Mirrors `ReviewSummaryViewModel`: the headline tiles and the caveats box. */
export interface ReviewSummaryViewModel {
  canineArticles: number;
  primaryStudies: number;
  caseReports: number;
  reviews: number;
  independentSources: number;
  cohorts: number;
  cohortArticles: number;
  fullText: number;
  abstractOnly: number;
  highConfidence: number;
  lowConfidence: number;
  fallbackLabels: number;
  uncategorised: number;
  medianInfectedDogs: number | null;
  primaryStudiesWithSize: number;
  primaryStudiesWithControls: number;
  backgroundArticles: number;
  countries: number;
  countrySpellings: number;
  firstYear: number;
  lastYear: number;
}

/** Mirrors `YearCountViewModel`: canine articles published in one year. */
export interface YearCountViewModel {
  year: number;
  articles: number;
  independentSources: number;
  /** The window starts and ends 23 October, so the first and last years are partial. */
  partial: boolean;
}

/** Mirrors `ReviewOverviewViewModel` (`review-overview-get`). */
export interface ReviewOverviewViewModel {
  summary: ReviewSummaryViewModel;
  years: YearCountViewModel[];
  periods: PeriodViewModel[];
  /** One row per category, most articles first. */
  topics: TopicRowViewModel[];
  designs: BreakdownRowViewModel[];
  species: BreakdownRowViewModel[];
  /** The top ten countries, then "Not stated". */
  countries: BreakdownRowViewModel[];
  /** Infected dogs per primary study, in bands, then "Not reported". */
  sampleSizes: BreakdownRowViewModel[];
}
