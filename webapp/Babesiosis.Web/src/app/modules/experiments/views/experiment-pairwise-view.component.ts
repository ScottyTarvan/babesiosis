import { ChangeDetectionStrategy, Component, computed, DestroyRef, inject, input, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import {
  FsBadgeComponent,
  FsCardComponent,
  FsChartComponent,
  fsChartCssColor,
  FsChartOptions,
  FsCheckboxComponent,
  FsDataGridComponent,
  FsGridColumn,
  FsGridPager,
  fsObserveTheme,
  FsTextInputComponent,
} from '@core';
import {
  ESTIMATE_SYMBOLS,
  ExperimentAssociationViewModel,
  ExperimentDetailViewModel,
  parsePayload,
  SpearmanMatrixPayload,
  TEST_LABELS,
  VariableClustersPayload,
} from 'app/modules/experiments/viewmodels/experiment.viewmodel';

/** One association as the findings grid shows it: display strings precomputed, sort keys numeric. */
interface AssociationRow extends ExperimentAssociationViewModel {
  id: string;
  testLabel: string;
  estimateText: string;
  absEstimate: number;
  pAdjustedText: string;
  domainA: string;
  domainB: string;
  crossDomain: boolean;
}

/** Blends two `#RRGGBB` colours: `weight` 0 gives `a`, 1 gives `b`. */
function mixHex(a: string, b: string, weight: number): string {
  const parse = (hex: string) => /^#[0-9a-f]{6}$/i.test(hex) ? [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16)) : null;
  const from = parse(a);
  const to = parse(b);
  if (!from || !to) {
    return a;
  }
  return '#' + from.map((c, i) => Math.round(c + (to[i] - c) * weight).toString(16).padStart(2, '0')).join('');
}

/** Diverging poles for the correlation matrix: a cool and a warm hue, with a neutral grey midpoint. */
const NEGATIVE_POLE = '#3366b0';
const POSITIVE_POLE = '#c6483a';

function formatP(p: number | null): string {
  if (p === null || p === undefined) {
    return '–';
  }
  return p < 0.001 ? '< 0.001' : p.toFixed(3);
}

/**
 * The pairwise-association view: the Spearman matrix of the numeric variables as a
 * diverging heatmap, the blocks of variables that move together, and the findings
 * table with its filters. The explanation note is rendered by the page after this.
 */
@Component({
  selector: 'fs-experiment-pairwise-view',
  standalone: true,
  imports: [
    FormsModule,
    FsBadgeComponent,
    FsCardComponent,
    FsChartComponent,
    FsCheckboxComponent,
    FsDataGridComponent,
    FsTextInputComponent,
  ],
  templateUrl: './experiment-pairwise-view.component.html',
  styleUrls: ['./experiment-pairwise-view.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExperimentPairwiseViewComponent implements OnInit {
  private readonly destroyRef = inject(DestroyRef);

  readonly detail = input.required<ExperimentDetailViewModel>();

  /** Bumped when the theme flips, so the heatmap's neutral and gap colours re-read their tokens. */
  private readonly themeChanges = signal(0);

  protected readonly significantOnly = signal(true);
  protected readonly hideTrivial = signal(true);
  protected readonly crossDomainOnly = signal(false);
  protected readonly search = signal('');

  /** Variable code to its dictionary entry. */
  private readonly variables = computed(() => new Map(this.detail().variables.map(v => [v.code, v])));

  protected readonly matrix = computed(() =>
    parsePayload<SpearmanMatrixPayload>(this.detail().results.find(r => r.kind === 'spearman_matrix')));
  protected readonly clusters = computed(() =>
    parsePayload<VariableClustersPayload>(this.detail().results.find(r => r.kind === 'variable_clusters')));

  protected readonly matrixNames = computed(() => (this.matrix()?.variables ?? []).map(code => this.nameOf(code)));
  /** Rows of about 22px each, plus room for the rotated column labels. */
  protected readonly heatmapHeight = computed(() => Math.max(320, 24 * (this.matrix()?.variables.length ?? 0) + 150));

  /**
   * Apex heatmap over the Spearman matrix. Series are reversed because Apex draws the
   * first series at the bottom, and the matrix should read top-down in the same order
   * as the columns read left-right. A 2px gap in the surface colour separates cells.
   */
  protected readonly heatmapOptions = computed<FsChartOptions>(() => {
    this.themeChanges();
    const matrix = this.matrix();
    if (!matrix) {
      return {};
    }
    const names = this.matrixNames();
    const neutral = fsChartCssColor('--fs-color-fill-subtle', '#f0efec');
    const surface = fsChartCssColor('--fs-color-surface', '#ffffff');
    const ranges = [
      { from: -1.001, to: -0.6, color: NEGATIVE_POLE, name: 'rho ≤ −0.6' },
      { from: -0.6, to: -0.3, color: mixHex(NEGATIVE_POLE, neutral, 0.4), name: '−0.6 to −0.3' },
      { from: -0.3, to: -0.1, color: mixHex(NEGATIVE_POLE, neutral, 0.72), name: '−0.3 to −0.1' },
      { from: -0.1, to: 0.1, color: neutral, name: 'about 0' },
      { from: 0.1, to: 0.3, color: mixHex(POSITIVE_POLE, neutral, 0.72), name: '0.1 to 0.3' },
      { from: 0.3, to: 0.6, color: mixHex(POSITIVE_POLE, neutral, 0.4), name: '0.3 to 0.6' },
      { from: 0.6, to: 1.001, color: POSITIVE_POLE, name: 'rho ≥ 0.6' },
    ];
    const series = matrix.variables.map((_, i) => ({
      name: names[i],
      data: matrix.variables.map((__, j) => ({ x: names[j], y: matrix.rho[i][j] ?? 0 })),
    })).reverse();
    const n = matrix.n;
    const rowCount = matrix.variables.length;
    return {
      chart: { type: 'heatmap', toolbar: { show: false }, animations: { enabled: false } },
      series,
      plotOptions: { heatmap: { radius: 2, enableShades: false, colorScale: { ranges } } },
      dataLabels: { enabled: false },
      stroke: { width: 2, colors: [surface] },
      xaxis: { labels: { rotate: -55, rotateAlways: true, trim: true, maxHeight: 140, style: { fontSize: '11px' } } },
      yaxis: { labels: { maxWidth: 190, style: { fontSize: '11px' } } },
      legend: { show: true, position: 'bottom' },
      tooltip: {
        custom: ({ seriesIndex, dataPointIndex }: { seriesIndex: number; dataPointIndex: number }) => {
          const i = rowCount - 1 - seriesIndex;
          const j = dataPointIndex;
          const rho = matrix.rho[i]?.[j];
          const pairs = n?.[i]?.[j];
          const value = rho === null || rho === undefined ? 'not tested' : `rho ${rho >= 0 ? '+' : ''}${rho.toFixed(2)}`;
          return `<div class="fs-experiment-pairwise__tip"><strong>${names[i]}</strong> × <strong>${names[j]}</strong>`
            + `<br>${value}${pairs ? ` · n = ${pairs}` : ''}</div>`;
        },
      },
    };
  });

  /** Clusters with member names, strongest first; singletons listed after. */
  protected readonly clusterRows = computed(() => (this.clusters()?.clusters ?? []).map(c => ({
    members: c.members.map(m => this.nameOf(m)),
    strength: c.mean_abs_rho,
  })));
  protected readonly singletonNames = computed(() => (this.clusters()?.singletons ?? []).map(s => this.nameOf(s)));

  /** Every association row the server sent, with display fields. */
  private readonly rows = computed<AssociationRow[]>(() => this.detail().associations.map(a => {
    const domainA = this.variables().get(a.variableA)?.domain ?? '';
    const domainB = this.variables().get(a.variableB)?.domain ?? '';
    const symbol = ESTIMATE_SYMBOLS[a.estimateLabel ?? ''] ?? a.estimateLabel ?? '';
    return {
      ...a,
      id: `${a.variableA}|${a.variableB}`,
      testLabel: TEST_LABELS[a.test] ?? a.test,
      estimateText: a.estimate === null ? '–' : `${symbol} ${a.estimate >= 0 && a.estimateLabel === 'rho' ? '+' : ''}${a.estimate.toFixed(2)}`,
      absEstimate: Math.abs(a.estimate ?? 0),
      pAdjustedText: formatP(a.pAdjusted),
      domainA,
      domainB,
      crossDomain: !!domainA && !!domainB && domainA !== domainB,
    };
  }));

  protected readonly filteredRows = computed(() => {
    const term = this.search().trim().toLowerCase();
    return this.rows().filter(r =>
      (!this.significantOnly() || r.significant)
      && (!this.hideTrivial() || !r.trivial)
      && (!this.crossDomainOnly() || r.crossDomain)
      && (!term || r.variableAName.toLowerCase().includes(term) || r.variableBName.toLowerCase().includes(term)
        || r.domainA.includes(term) || r.domainB.includes(term) || r.testLabel.toLowerCase().includes(term)));
  });

  protected readonly columns: FsGridColumn<AssociationRow>[] = [
    { dataField: 'variableAName', caption: 'Variable A', minWidth: 160 },
    { dataField: 'variableBName', caption: 'Variable B', minWidth: 160 },
    { dataField: 'testLabel', caption: 'Test', width: 130 },
    { dataField: 'estimateText', caption: 'Effect', width: 150, calculateSortValue: 'absEstimate' },
    { dataField: 'n', caption: 'n', width: 70, alignment: 'right' },
    { dataField: 'pAdjustedText', caption: 'Adjusted p', width: 110, alignment: 'right', calculateSortValue: 'pAdjusted', sortOrder: 'asc', sortIndex: 0 },
    { dataField: 'direction', caption: 'Direction', minWidth: 200 },
  ];
  protected readonly pager: FsGridPager = { visible: true, showPageSizeSelector: true, allowedPageSizes: [25, 50, 100], showInfo: true };
  protected readonly pageSize = 25;

  ngOnInit(): void {
    this.destroyRef.onDestroy(fsObserveTheme(() => this.themeChanges.update(n => n + 1)));
  }

  private nameOf(code: string): string {
    return this.variables().get(code)?.name ?? code;
  }
}
