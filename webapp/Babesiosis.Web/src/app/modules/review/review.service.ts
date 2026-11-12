import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ServiceBase } from 'app/core/services/service-base';
import { AuthService } from 'app/core/services/auth.service';
import { ConfigurationService } from 'app/core/services/configuration.service';
import {
  GetReviewGapsCommand,
  GetReviewOverviewCommand,
  GetReviewTopicCommand,
} from 'app/modules/review/commands/review.commands';
import { ReviewGapsViewModel } from 'app/modules/review/viewmodels/review-gaps.viewmodel';
import { ReviewOverviewViewModel } from 'app/modules/review/viewmodels/review-overview.viewmodel';
import { ReviewTopicViewModel } from 'app/modules/review/viewmodels/review-topic.viewmodel';

/** The Review screens: Overview (home), topic pages and Gaps and questions. */
@Injectable({
  providedIn: 'root'
})
export class ReviewService extends ServiceBase {
  private URL: string;

  constructor(
    httpClient: HttpClient,
    authService: AuthService,
    configService: ConfigurationService) {
    super(httpClient, authService);
    this.URL = configService.coreAPI('');
  }

  /** Backend: `Babesiosis.Core.Functions.Review.GetReviewOverview`. */
  getOverview(command: GetReviewOverviewCommand = {}): Observable<ReviewOverviewViewModel> {
    return this.post<ReviewOverviewViewModel>(`${this.URL}/review-overview-get`, command);
  }

  /** Backend: `Babesiosis.Core.Functions.Review.GetReviewTopic`. */
  getTopic(command: GetReviewTopicCommand): Observable<ReviewTopicViewModel> {
    return this.post<ReviewTopicViewModel>(`${this.URL}/review-topic-get`, command);
  }

  /** Backend: `Babesiosis.Core.Functions.Review.GetReviewGaps`. */
  getGaps(command: GetReviewGapsCommand = {}): Observable<ReviewGapsViewModel> {
    return this.post<ReviewGapsViewModel>(`${this.URL}/review-gaps-get`, command);
  }
}
