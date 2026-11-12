import { SynthesisSectionViewModel } from 'app/modules/review/viewmodels/review-shared.viewmodel';

/** Mirrors `GapRowViewModel`: a category's articles per study type. */
export interface GapRowViewModel {
  code: string;
  label: string;
  name: string;
  /** Lined up with `ReviewGapsViewModel.designs`. */
  counts: number[];
  total: number;
}

/** Mirrors `GapFigureViewModel`: one computed gap figure. */
export interface GapFigureViewModel {
  key: string;
  value: string;
  title: string;
  text: string;
}

/** Mirrors `ReviewGapsViewModel` (`review-gaps-get`). */
export interface ReviewGapsViewModel {
  designs: string[];
  /** Most articles first. */
  rows: GapRowViewModel[];
  canineArticles: number;
  figures: GapFigureViewModel[];
  /** The numbered themes of CROSS.md, as written. */
  themes: SynthesisSectionViewModel[];
  /** Q1–Q5 of QUESTIONS.md, as written. */
  questions: SynthesisSectionViewModel[];
  /** ISO date-time (UTC); null when not loaded. */
  synthesisLoadedAt: string | null;
}
