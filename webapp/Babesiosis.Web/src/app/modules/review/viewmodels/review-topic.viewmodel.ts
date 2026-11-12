import {
  BreakdownRowViewModel,
  PeriodViewModel,
  SynthesisSectionViewModel,
  TopicRowViewModel,
} from 'app/modules/review/viewmodels/review-shared.viewmodel';

/** Mirrors `TopicArticleViewModel`: one article in a topic's list. */
export interface TopicArticleViewModel {
  code: string;
  year: number | null;
  title: string;
  studyType: string;
  infectedDogs: number | null;
  controls: number | null;
  species: string;
  finding: string | null;
  abstractOnly: boolean;
  highConfidence: boolean;
  /** Publisher, PubMed or a landing page; null when none is known. */
  sourceUrl: string | null;
}

/** Mirrors `TopicLinkViewModel`: one entry of the topic switcher. */
export interface TopicLinkViewModel {
  code: string;
  label: string;
  name: string;
  articles: number;
}

/** Mirrors `ReviewTopicViewModel` (`review-topic-get`). */
export interface ReviewTopicViewModel {
  topic: TopicRowViewModel;
  canineArticles: number;
  periods: PeriodViewModel[];
  designs: BreakdownRowViewModel[];
  /** The synthesis as written, in reading order; empty when it is not loaded. */
  synthesis: SynthesisSectionViewModel[];
  /** ISO date-time (UTC) of the synthesis load; null when it is not loaded. */
  synthesisLoadedAt: string | null;
  /** Newest first. */
  articles: TopicArticleViewModel[];
  topics: TopicLinkViewModel[];
}
