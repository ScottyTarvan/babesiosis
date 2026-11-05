import { DatePipe } from '@angular/common';
import {
  afterNextRender,
  ChangeDetectionStrategy,
  Component,
  computed,
  DestroyRef,
  ElementRef,
  inject,
  Injector,
  signal,
  viewChild,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { finalize, Subscription } from 'rxjs';
import {
  FsBadgeComponent,
  FsBannerComponent,
  FsButtonComponent,
  FsCardComponent,
  FsEmptyStateComponent,
  FsPageHeaderComponent,
  FsSegmentedControlComponent,
  FsSegmentedOption,
  FsSymbolComponent,
  FsTextareaComponent,
} from '@core';
import { errorCode, errorMessage } from 'app/core/http-error';
import { renderAgentMarkdown } from 'app/modules/ai-agent/agent-markdown';
import { AiAgentService } from 'app/modules/ai-agent/ai-agent.service';
import { AgentModelTier } from 'app/modules/ai-agent/commands/ask-article-agent.command';
import { ChatMessageViewModel } from 'app/modules/ai-agent/viewmodels/chat-message.viewmodel';

/** The server's limit (`ArticleQuestionAgent.MaxQuestionLength`). */
const MAX_QUESTION_LENGTH = 4000;

/** `AskArticleAgentController.AgentUnavailable`: AppSettings:AiAgents is off or incomplete. */
const AGENT_UNAVAILABLE = 'AI_AGENT_UNAVAILABLE';

/**
 * An interactive chat with the article agent (`articles-agent-ask`), which
 * searches the review's articles and answers with citations.
 *
 * The conversation lives on the client: each answer carries an opaque
 * `conversation` that goes back with the next question, so follow-ups keep
 * their context. "New conversation" drops it.
 */
@Component({
  selector: 'fs-ai-agent',
  standalone: true,
  imports: [
    DatePipe,
    FormsModule,
    FsBadgeComponent,
    FsBannerComponent,
    FsButtonComponent,
    FsCardComponent,
    FsEmptyStateComponent,
    FsPageHeaderComponent,
    FsSegmentedControlComponent,
    FsSymbolComponent,
    FsTextareaComponent,
  ],
  templateUrl: './ai-agent.component.html',
  styleUrls: ['./ai-agent.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AiAgentComponent {
  private readonly aiAgentService = inject(AiAgentService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly injector = inject(Injector);
  private readonly thread = viewChild.required<ElementRef<HTMLElement>>('thread');

  /** State the server needs for a follow-up; null starts a new conversation. */
  private conversation: string | null = null;
  private pending: Subscription | null = null;
  private sequence = 0;

  protected readonly maxQuestionLength = MAX_QUESTION_LENGTH;

  protected readonly tierOptions: FsSegmentedOption<AgentModelTier>[] = [
    { value: 'Low', label: 'Fast' },
    { value: 'Medium', label: 'Balanced' },
    { value: 'High', label: 'Thorough' },
  ];

  protected readonly tier = signal<AgentModelTier>('Medium');
  protected readonly messages = signal<ChatMessageViewModel[]>([]);
  protected readonly draft = signal('');
  protected readonly thinking = signal(false);
  protected readonly error = signal<string | null>(null);
  /** True when the server says the agent is switched off or not configured. */
  protected readonly unavailable = signal(false);

  protected readonly tooLong = computed(() => this.draft().length > MAX_QUESTION_LENGTH);
  protected readonly canSend = computed(
    () => !this.thinking() && !this.tooLong() && this.draft().trim().length > 0,
  );

  /** Each answer's Markdown rendered once, keyed by message id. */
  protected readonly answerHtml = computed(() => new Map(
    this.messages()
      .filter(m => m.role === 'assistant')
      .map(m => [m.id, renderAgentMarkdown(m.content, m.citations ?? [])]),
  ));

  /** Starting points that show what the agent can be asked about the articles. */
  protected readonly suggestions: readonly string[] = [
    'Which haematological changes are most often reported in Babesia rossi infections?',
    'Summarise the evidence on acute kidney injury in canine babesiosis.',
    'Which studies compare treatment protocols for Babesia gibsoni?',
    'What gaps does the literature leave on prognostic markers?',
  ];

  /** Puts a suggested question in the composer so it can be edited before sending. */
  protected useSuggestion(text: string): void {
    this.draft.set(text);
  }

  protected send(): void {
    if (!this.canSend()) {
      return;
    }

    const question = this.draft().trim();
    const asked: ChatMessageViewModel = {
      id: `user-${++this.sequence}`,
      role: 'user',
      content: question,
      createdAt: new Date().toISOString(),
    };

    this.messages.update(list => [...list, asked]);
    this.draft.set('');
    this.error.set(null);
    this.thinking.set(true);
    this.scrollToLatest();

    this.pending = this.aiAgentService.ask({ question, tier: this.tier(), conversation: this.conversation })
      .pipe(
        finalize(() => {
          this.thinking.set(false);
          this.pending = null;
        }),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: answer => {
          this.conversation = answer.conversation;
          this.unavailable.set(false);
          this.messages.update(list => [...list, { ...answer.message, model: answer.model }]);
          this.scrollToLatest();
        },
        error: err => {
          // The server never took the question into the conversation, so take it back
          // out of the thread and hand it to the composer to send again.
          this.messages.update(list => list.filter(m => m.id !== asked.id));
          if (!this.draft()) {
            this.draft.set(question);
          }
          this.unavailable.set(errorCode(err) === AGENT_UNAVAILABLE);
          this.error.set(errorMessage(err, 'The AI agent could not answer. Try again shortly.'));
        },
      });
  }

  /** Starts over: cancels a pending answer and forgets the conversation. */
  protected clear(): void {
    this.pending?.unsubscribe();
    this.conversation = null;
    this.messages.set([]);
    this.draft.set('');
    this.error.set(null);
  }

  /** The short model name, e.g. `claude-sonnet-5.5` from `anthropic/claude-sonnet-5.5`. */
  protected modelName(model: string | null | undefined): string | null {
    return model ? model.slice(model.lastIndexOf('/') + 1) : null;
  }

  /**
   * After the next render, scroll so the newest message's top is in view: a
   * question scrolls to the bottom (with the "answering" dots); a long answer
   * opens at its first line rather than its last.
   */
  private scrollToLatest(): void {
    afterNextRender(() => {
      const thread = this.thread().nativeElement;
      const items = thread.querySelectorAll<HTMLElement>('.fs-ai-agent__message');
      const latest = items[items.length - 1];
      // offsetTop is measured from the thread (position: relative); the browser clamps past the end.
      thread.scrollTo({ top: latest ? latest.offsetTop - 16 : thread.scrollHeight, behavior: 'smooth' });
    }, { injector: this.injector });
  }
}
