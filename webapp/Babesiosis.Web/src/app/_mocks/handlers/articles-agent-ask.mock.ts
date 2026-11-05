import { HttpErrorResponse } from '@angular/common/http';
import { delay, of, throwError } from 'rxjs';
import { MockRegistration } from 'app/_mocks/mock-handler';
import { AskArticleAgentCommand } from 'app/modules/ai-agent/commands/ask-article-agent.command';
import { ArticleAgentAnswerViewModel } from 'app/modules/ai-agent/viewmodels/article-agent-answer.viewmodel';

const models: Record<string, string> = {
  Low: 'anthropic/claude-haiku-5.5',
  Medium: 'anthropic/claude-sonnet-5.5',
  High: 'anthropic/claude-opus-5.5',
  Max: 'anthropic/claude-opus-5.5',
};

/**
 * Mirrors `AskArticleAgentController`: a 400 for an empty question, otherwise
 * one canned answer in the real shape (Markdown with [CODE] citations, resolved
 * citations, and a `conversation` that counts the turns). Ask a question
 * containing "unavailable" to see the 503 the server returns when
 * AppSettings:AiAgents is off. Answers and articles are illustrative, not real.
 */
export const articlesAgentAskMock: MockRegistration<AskArticleAgentCommand, ArticleAgentAnswerViewModel> = {
  route: 'articles-agent-ask',
  handler: (command) => {
    const question = command?.question?.trim() ?? '';
    if (!question) {
      return throwError(() => new HttpErrorResponse({
        status: 400, error: { message: 'The AI agent could not answer', detail: 'A question is required.' },
      }));
    }
    if (/unavailable/i.test(question)) {
      return throwError(() => new HttpErrorResponse({
        status: 503,
        error: {
          code: 'AI_AGENT_UNAVAILABLE', message: 'The AI agent could not answer',
          detail: 'AppSettings:AiAgents:Enabled is false.',
        },
      }));
    }

    const turn = Number(command.conversation ?? '0') + 1;
    const model = models[command.tier ?? 'Medium'] ?? models['Medium'];

    return of<ArticleAgentAnswerViewModel>({
      message: {
        id: `mock-answer-${turn}`,
        role: 'assistant',
        createdAt: new Date().toISOString(),
        content: [
          turn > 1 ? `Following on from your earlier question (turn ${turn}):` : '## Summary',
          '',
          'Acute kidney injury is reported mainly in **Babesia rossi** infections [CB024 Results], '
          + 'where azotaemia at admission was linked to *higher mortality* [CB024, CB040].',
          '',
          '- Urinary markers such as `uNGAL` rose before serum creatinine [CB124].',
          '- Most studies were small and single-centre [CB040].',
          '',
          '| Marker | Articles |',
          '|---|---|',
          '| uNGAL | [CB124] |',
          '| Proteinuria | [CB024] |',
        ].join('\n'),
        citations: [
          {
            articleId: 24, code: 'CB024', title: 'Glomerular and tubular kidney damage markers in canine babesiosis',
            year: 2018, sourceUrl: 'https://doi.org/10.1000/example.cb024', hasFullText: true, sectionsRead: ['Results'],
          },
          {
            articleId: 40, code: 'CB040', title: 'Clinical and pathological description of 320 cases of naturally acquired babesiosis',
            year: 2019, sourceUrl: null, hasFullText: false, sectionsRead: [],
          },
          {
            articleId: 124, code: 'CB124', title: 'Diagnostic efficacy of urinary neutrophil gelatinase-associated lipocalin',
            year: 2024, sourceUrl: 'https://pubmed.ncbi.nlm.nih.gov/30000124/', hasFullText: false, sectionsRead: [],
          },
        ],
      },
      conversation: String(turn),
      model,
      inputTokens: 5120,
      outputTokens: 310,
    }).pipe(delay(1200));
  },
};
