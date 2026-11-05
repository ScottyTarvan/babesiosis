import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ServiceBase } from 'app/core/services/service-base';
import { AuthService } from 'app/core/services/auth.service';
import { ConfigurationService } from 'app/core/services/configuration.service';
import { AskArticleAgentCommand } from 'app/modules/ai-agent/commands/ask-article-agent.command';
import { ArticleAgentAnswerViewModel } from 'app/modules/ai-agent/viewmodels/article-agent-answer.viewmodel';

@Injectable({
  providedIn: 'root'
})
export class AiAgentService extends ServiceBase {
  private URL: string;

  constructor(
    httpClient: HttpClient,
    authService: AuthService,
    configService: ConfigurationService) {
    super(httpClient, authService);
    this.URL = configService.coreAPI('');
  }

  /**
   * Backend: `Babesiosis.Core.Functions.Articles.AskArticleAgent`.
   * Never retried: every call costs OpenRouter credit.
   */
  ask(command: AskArticleAgentCommand): Observable<ArticleAgentAnswerViewModel> {
    return this.post<ArticleAgentAnswerViewModel>(`${this.URL}/articles-agent-ask`, command);
  }
}
