import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, DestroyRef, inject, OnInit, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { catchError, EMPTY, Subject, switchMap, tap } from 'rxjs';
import {
  FsBadgeComponent,
  FsBannerComponent,
  FsButtonComponent,
  FsCardComponent,
  FsDefinitionItem,
  FsDefinitionListComponent,
  FsEmptyStateComponent,
  FsPageHeaderComponent,
  FsSpinnerComponent,
  FsSymbolComponent,
  FsTextInputComponent,
} from '@core';
import { errorMessage } from 'app/core/http-error';
import { ExperimentsService } from 'app/modules/experiments/experiments.service';
import {
  ExperimentDetailViewModel,
  ExperimentListItemViewModel,
  InterpretationPayload,
  methodLabel,
  parseJson,
  parsePayload,
} from 'app/modules/experiments/viewmodels/experiment.viewmodel';
import { ExperimentPairwiseViewComponent } from 'app/modules/experiments/views/experiment-pairwise-view.component';

/** The runs over one dataset, the unit the left-hand panel groups by. */
interface ExperimentGroup {
  datasetCode: string;
  datasetTitle: string;
  articleCode: string | null;
  items: ExperimentListItemViewModel[];
}

/** Result kinds the page renders itself; anything else goes to the generic payload view. */
const HANDLED_RESULT_KINDS = new Set(['interpretation', 'spearman_matrix', 'variable_clusters', 'top_associations', 'run_notes']);

/**
 * The Experiments screen: every analysis run over the downloaded datasets in a
 * searchable panel on the left, grouped by dataset; the selected run on the right
 * as its visualisation, then the script's explanation and interpretation, then the
 * dataset and run details. The selection is the URL (`/experiments/:code`), so a run
 * can be linked to.
 */
@Component({
  selector: 'fs-experiments',
  standalone: true,
  imports: [
    DatePipe,
    FormsModule,
    FsBadgeComponent,
    FsBannerComponent,
    FsButtonComponent,
    FsCardComponent,
    FsDefinitionListComponent,
    FsEmptyStateComponent,
    FsPageHeaderComponent,
    FsSpinnerComponent,
    FsSymbolComponent,
    FsTextInputComponent,
    ExperimentPairwiseViewComponent,
  ],
  templateUrl: './experiments.component.html',
  styleUrls: ['./experiments.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExperimentsComponent implements OnInit {
  private readonly experimentsService = inject(ExperimentsService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly destroyRef = inject(DestroyRef);

  /** Each detail request; switchMap drops a response an newer selection has overtaken. */
  private readonly detailRequests = new Subject<string>();

  protected readonly items = signal<ExperimentListItemViewModel[]>([]);
  protected readonly listLoading = signal(false);
  protected readonly listError = signal<string | null>(null);
  protected readonly search = signal('');

  protected readonly selectedCode = signal<string | null>(null);
  protected readonly detail = signal<ExperimentDetailViewModel | null>(null);
  protected readonly detailLoading = signal(false);
  protected readonly detailError = signal<string | null>(null);

  /** The panel's rows after the search box, grouped by dataset in list order. */
  protected readonly groups = computed<ExperimentGroup[]>(() => {
    const term = this.search().trim().toLowerCase();
    const groups = new Map<string, ExperimentGroup>();
    for (const item of this.items()) {
      if (term && !this.matches(item, term)) {
        continue;
      }
      const key = item.datasetCode ?? '';
      let group = groups.get(key);
      if (!group) {
        group = {
          datasetCode: item.datasetCode ?? 'No dataset',
          datasetTitle: item.datasetTitle ?? '',
          articleCode: item.articleCode,
          items: [],
        };
        groups.set(key, group);
      }
      group.items.push(item);
    }
    return [...groups.values()];
  });
  protected readonly filteredCount = computed(() => this.groups().reduce((n, g) => n + g.items.length, 0));

  /** The script's note, rendered after the visualisation. */
  protected readonly interpretation = computed(() =>
    parsePayload<InterpretationPayload>(this.detail()?.results.find(r => r.kind === 'interpretation')));
  /** Payloads no view renders, shown as formatted JSON so a new method is visible before it has a view. */
  protected readonly unhandledResults = computed(() => {
    const d = this.detail();
    if (!d) {
      return [];
    }
    const handled = d.method === 'pairwise_association' ? HANDLED_RESULT_KINDS : new Set(['interpretation']);
    return d.results
      .filter(r => !handled.has(r.kind))
      .map(r => ({ kind: r.kind, title: r.title ?? r.kind, text: this.prettyJson(r.payload) }));
  });
  protected readonly datasetNotes = computed(() => parseJson<string[]>(this.detail()?.dataset?.notes, []));
  protected readonly parameters = computed<FsDefinitionItem[]>(() => {
    const params = parseJson<Record<string, unknown>>(this.detail()?.parameters, {});
    return Object.entries(params)
      .filter(([, v]) => !(Array.isArray(v) && v.length === 0))
      .map(([k, v]) => ({ term: k.replace(/_/g, ' '), value: Array.isArray(v) ? v.join(', ') : String(v) }));
  });
  protected readonly datasetItems = computed<FsDefinitionItem[]>(() => {
    const d = this.detail();
    const ds = d?.dataset;
    if (!d || !ds) {
      return [];
    }
    return [
      { term: 'Dataset', value: `${ds.code} · ${ds.title}` },
      { term: 'Subjects', value: ds.subjectCount },
      { term: 'Species', value: ds.species },
      { term: 'Repository', value: ds.repository, hint: ds.sourceRecord ?? undefined },
      { term: 'Licence', value: ds.licence },
      { term: 'Independent source', value: ds.independentSource },
      { term: 'Script', value: d.script, hint: d.scriptVersion ? `version ${d.scriptVersion}` : undefined },
    ].filter(item => item.value !== null && item.value !== undefined && item.value !== '');
  });

  protected readonly methodLabel = methodLabel;

  ngOnInit(): void {
    this.detailRequests.pipe(
      tap(() => {
        this.detailLoading.set(true);
        this.detailError.set(null);
      }),
      switchMap(code => this.experimentsService.getExperimentDetail({ code }).pipe(
        catchError(err => {
          this.detailLoading.set(false);
          this.detail.set(null);
          this.detailError.set(errorMessage(err, 'The experiment could not be loaded.'));
          return EMPTY;
        }),
      )),
      takeUntilDestroyed(this.destroyRef),
    ).subscribe(detail => {
      this.detail.set(detail);
      this.detailLoading.set(false);
    });

    // The route is the selection. The matcher reuses this component across codes.
    this.route.paramMap
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(params => {
        const code = params.get('code');
        this.selectedCode.set(code);
        if (code) {
          this.detailRequests.next(code);
        } else {
          this.detail.set(null);
          this.selectFirst();
        }
      });

    this.loadList();
  }

  protected loadList(): void {
    this.listLoading.set(true);
    this.listError.set(null);
    this.experimentsService.getExperimentList()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: response => {
          this.items.set(response.items ?? []);
          this.listLoading.set(false);
          this.selectFirst();
        },
        error: err => {
          this.listLoading.set(false);
          this.listError.set(errorMessage(err, 'The experiments could not be loaded.'));
        },
      });
  }

  /** Refresh: the list and, when one is selected, the open experiment. */
  protected refresh(): void {
    this.loadList();
    const code = this.selectedCode();
    if (code) {
      this.detailRequests.next(code);
    }
  }

  protected select(code: string): void {
    if (code !== this.selectedCode()) {
      this.router.navigate(['/experiments', code]);
    }
  }

  protected retryDetail(): void {
    const code = this.selectedCode();
    if (code) {
      this.detailRequests.next(code);
    }
  }

  /** With nothing selected, open the newest run so the page never shows an empty right-hand side. */
  private selectFirst(): void {
    const first = this.items()[0];
    if (!this.selectedCode() && first) {
      this.router.navigate(['/experiments', first.code], { replaceUrl: true });
    }
  }

  private matches(item: ExperimentListItemViewModel, term: string): boolean {
    return [item.name, item.code, item.method, methodLabel(item.method), item.datasetCode, item.datasetTitle,
      item.articleCode, item.articleTitle, item.summary]
      .some(v => (v ?? '').toLowerCase().includes(term));
  }

  private prettyJson(text: string): string {
    try {
      return JSON.stringify(JSON.parse(text), null, 2);
    } catch {
      return text;
    }
  }
}
