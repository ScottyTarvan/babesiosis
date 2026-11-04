import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ServiceBase } from 'app/core/services/service-base';
import { AuthService } from 'app/core/services/auth.service';
import { ConfigurationService } from 'app/core/services/configuration.service';
import { GetCategoryYearCountsCommand } from 'app/modules/literature-review/commands/get-category-year-counts.command';
import { GetReviewListCommand } from 'app/modules/literature-review/commands/get-review-list.command';
import { CategoryYearCountsViewModel } from 'app/modules/literature-review/viewmodels/category-year-counts.viewmodel';
import { ReviewListViewModel } from 'app/modules/literature-review/viewmodels/review.viewmodel';
import { GetTermCountsCommand } from 'app/modules/literature-review/commands/get-term-counts.command';
import { TermCountsViewModel } from 'app/modules/literature-review/viewmodels/term-counts.viewmodel';
import { GetEvidenceProfileCommand } from 'app/modules/literature-review/commands/get-evidence-profile.command';
import { EvidenceProfileViewModel } from 'app/modules/literature-review/viewmodels/evidence-profile.viewmodel';

@Injectable({
  providedIn: 'root'
})
export class LiteratureReviewService extends ServiceBase {
  private URL: string;

  constructor(
    httpClient: HttpClient,
    authService: AuthService,
    configService: ConfigurationService) {
    super(httpClient, authService);
    this.URL = configService.coreAPI('');
  }

  /** Backend: `Babesiosis.Core.Functions.Review.GetReviewList`. */
  getReviewList(command: GetReviewListCommand = {}): Observable<ReviewListViewModel> {
    return this.post<ReviewListViewModel>(`${this.URL}/review-list-get`, command);
  }

  /** Backend: `Babesiosis.Core.Functions.Review.GetCategoryYearCounts`. */
  getCategoryYearCounts(command: GetCategoryYearCountsCommand = {}): Observable<CategoryYearCountsViewModel> {
    return this.post<CategoryYearCountsViewModel>(`${this.URL}/review-category-year-counts-get`, command);
  }

  /** Backend: `Babesiosis.Core.Functions.Review.GetTermCounts`. */
  getTermCounts(command: GetTermCountsCommand = {}): Observable<TermCountsViewModel> {
    return this.post<TermCountsViewModel>(`${this.URL}/review-term-counts-get`, command);
  }

  /** Backend: `Babesiosis.Core.Functions.Review.GetEvidenceProfile`. */
  getEvidenceProfile(command: GetEvidenceProfileCommand = {}): Observable<EvidenceProfileViewModel> {
    return this.post<EvidenceProfileViewModel>(`${this.URL}/review-evidence-profile-get`, command);
  }
}
