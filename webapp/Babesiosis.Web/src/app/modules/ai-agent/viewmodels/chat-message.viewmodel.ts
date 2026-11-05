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
 * One message in the AI agent conversation. Mirrors `ArticleAgentMessageViewModel`,
 * so an answer from the server can be appended to the thread as is.
 */
export interface ChatMessageViewModel {
  id: string;
  role: ChatRole;
  /** Plain text for the user's questions; Markdown, citing codes like [CB024], for answers. */
  content: string;
  /** ISO 8601 timestamp. */
  createdAt: string;
  /** The articles the answer cites, in order of first citation. */
  citations?: ChatCitationViewModel[];
  /** The OpenRouter model that answered (client-side only, copied from the answer envelope). */
  model?: string | null;
}
