/** Who wrote a message in the AI agent conversation. */
export type ChatRole = 'user' | 'assistant';

/**
 * An article the agent cited, shown as a link under the answer.
 * Mirrors `ArticleAgentCitationViewModel`.
 */
export interface ChatCitationViewModel {
  articleId: number;
  /** The review code, e.g. `CB040`. */
  code: string;
  title: string;
  year?: number | null;
  /** Where to open the article; null when no link is known. */
  sourceUrl?: string | null;
  /** Whether the paper's own full text is in the database. */
  hasFullText?: boolean;
  /** Sections of the paper's own text the agent read (methods, results, ...). Empty when it used the review's record only. */
  sectionsRead?: string[];
}

/**
 * An experiment the agent cited, shown as a link to the Experiments screen.
 * Mirrors `ArticleAgentExperimentViewModel`.
 */
export interface ChatExperimentViewModel {
  /** The experiment code, e.g. `SV-05-01-age-death`: the screen shows it at `/experiments/<code>`. */
  code: string;
  /** The short form an answer may use instead, e.g. `SV-05-01`. */
  shortCode?: string | null;
  name: string;
  method?: string | null;
}

/**
 * A page of the clinical manual the agent cited, shown as a link to the Clinical screen.
 * Mirrors `ArticleAgentClinicalPageViewModel`.
 */
export interface ChatClinicalPageViewModel {
  /** The page ID, e.g. `SY05` or `TX00`: the screen shows it at `/clinical/<id>`. */
  id: string;
  title: string;
  /** The page's group on the Clinical screen's rail, e.g. `Organs`. */
  group?: string | null;
}

/**
 * One message in the AI agent conversation. Mirrors `ArticleAgentMessageViewModel`,
 * so an answer from the server can be appended to the thread as is.
 */
export interface ChatMessageViewModel {
  id: string;
  role: ChatRole;
  /**
   * Plain text for the user's questions. For answers, Markdown that cites its sources in
   * square brackets: articles ([CB024]), experiments ([SV-05-01-age-death]) and clinical
   * manual pages ([SY05]).
   */
  content: string;
  /** ISO 8601 timestamp. */
  createdAt: string;
  /** The articles the answer cites, in order of first citation. */
  citations?: ChatCitationViewModel[];
  /** The experiments the answer cites, in order of first citation. */
  experiments?: ChatExperimentViewModel[];
  /** The clinical manual pages the answer cites, in order of first citation. */
  clinicalPages?: ChatClinicalPageViewModel[];
  /** The OpenRouter model that answered (client-side only, copied from the answer envelope). */
  model?: string | null;
}
