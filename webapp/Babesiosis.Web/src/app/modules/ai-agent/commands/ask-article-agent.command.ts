/** The configured OpenRouter model tiers (`AppSettings:AiAgents:Models`). */
export type AgentModelTier = 'Low' | 'Medium' | 'High' | 'Max';

/** Mirrors `AskArticleAgentCommand`: one question to the article agent. */
export interface AskArticleAgentCommand {
  /** The question, at most 4,000 characters. */
  question: string;
  /** Defaults to Medium on the server. */
  tier?: AgentModelTier;
  /** The previous answer's `conversation`, to ask a follow-up. Omit to start a new conversation. */
  conversation?: string | null;
}
