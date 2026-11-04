import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ServiceBase } from 'app/core/services/service-base';
import { AuthService } from 'app/core/services/auth.service';
import { ConfigurationService } from 'app/core/services/configuration.service';
import { GetArticleListCommand } from 'app/modules/reference-articles/commands/get-article-list.command';
import { ArticleListViewModel } from 'app/modules/reference-articles/viewmodels/article.viewmodel';

@Injectable({
  providedIn: 'root'
})
export class ReferenceArticlesService extends ServiceBase {
  private URL: string;

  constructor(
    httpClient: HttpClient,
    authService: AuthService,
    configService: ConfigurationService) {
    super(httpClient, authService);
    this.URL = configService.coreAPI('');
  }

  /** Backend: `Babesiosis.Core.Functions.Articles.GetArticleList`. */
  getArticleList(command: GetArticleListCommand = {}): Observable<ArticleListViewModel> {
    return this.post<ArticleListViewModel>(`${this.URL}/articles-list-get`, command);
  }
}
