import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ServiceBase } from 'app/core/services/service-base';
import { AuthService } from 'app/core/services/auth.service';
import { ConfigurationService } from 'app/core/services/configuration.service';
import { GetExperimentDetailCommand } from 'app/modules/experiments/commands/get-experiment-detail.command';
import { GetExperimentListCommand } from 'app/modules/experiments/commands/get-experiment-list.command';
import {
  ExperimentDetailViewModel,
  ExperimentListViewModel,
} from 'app/modules/experiments/viewmodels/experiment.viewmodel';

@Injectable({
  providedIn: 'root'
})
export class ExperimentsService extends ServiceBase {
  private URL: string;

  constructor(
    httpClient: HttpClient,
    authService: AuthService,
    configService: ConfigurationService) {
    super(httpClient, authService);
    this.URL = configService.coreAPI('');
  }

  /** Backend: `Babesiosis.Core.Functions.Experiments.GetExperimentList`. */
  getExperimentList(command: GetExperimentListCommand = {}): Observable<ExperimentListViewModel> {
    return this.post<ExperimentListViewModel>(`${this.URL}/experiments-list-get`, command);
  }

  /** Backend: `Babesiosis.Core.Functions.Experiments.GetExperimentDetail`. */
  getExperimentDetail(command: GetExperimentDetailCommand): Observable<ExperimentDetailViewModel> {
    return this.post<ExperimentDetailViewModel>(`${this.URL}/experiments-detail-get`, command);
  }
}
