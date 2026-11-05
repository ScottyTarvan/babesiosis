import { ChatMessageViewModel } from 'app/modules/ai-agent/viewmodels/chat-message.viewmodel';

/** Mirrors `ArticleAgentAnswerViewModel`: one answer from `articles-agent-ask`. */
export interface ArticleAgentAnswerViewModel {
  message: ChatMessageViewModel;
  /** Opaque state to send back as `conversation` with the next question. */
  conversation: string;
  /** The OpenRouter model id that answered. */
  model: string;
  inputTokens?: number | null;
  outputTokens?: number | null;
}
