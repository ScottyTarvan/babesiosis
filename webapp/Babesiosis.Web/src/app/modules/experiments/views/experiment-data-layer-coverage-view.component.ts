import { ChangeDetectionStrategy, Component, computed, DestroyRef, inject, input, OnInit, signal } from '@angular/core';
import {
  FsBadgeComponent,
  FsCardComponent,
  FsChartComponent,
  fsChartCssColor,
  FsChartOptions,
  FsDataGridComponent,
  FsGridColumn,
  FsGridPager,
  fsObserveTheme,
} from '@core';
import { ExperimentDetailViewModel, parsePayload } from 'app/modules/experiments/viewmodels/experiment.viewmodel';

/** One dataset row of the `dataset_summary` payload (SV-G1). */
interface DataLayerDatasetRow {
  dataset: string;
  independent_source: string;
  species: string;
  dogs: number;
  infected: number;
  control: number;
  comparator: number;
  records: number;
  timepoints: string[];
  variables: number;
  harmonised_variables: number;
  missing_pct: number | null;
  censored_cells: number;
  outcomes: { name: string; dogs_with_value: number }[];
  checks_passed: number;
  checks_total: number;
  flags: number;
}

interface DataLayerSummaryPayload {
  rows: DataLayerDatasetRow[];
  dog_records: number;
  distinct_dogs_after_links: number;
  independent_sources: string[];
  feature_records: number;
  checks_total: number;
  checks_passed: number;
}

/** Share of dogs with a value, by harmonised name (rows) and dataset (columns). Null: the dataset lacks the variable. */
interface CoverageMatrixPayload {
  datasets: string[];
  names: string[];
  share: (number | null)[][];
}

interface DataCheckRow {
  dataset: string;
  check: string;
  observed: string;
  expected: string;
  source: string;
  pass: boolean;
}

interface CleaningFlagRow {
  dataset: string;
  note: string;
}

interface DatasetLinksPayload {
  rows: { a: string; b: string; what: string }[];
  scb050_scb517_comparison: unknown;
}

interface DatasetGridRow extends DataLayerDatasetRow {
  groupsText: string;
  timepointsText: string;
  outcomesText: string;
  checksText: string;
  missingText: string;
}

interface CheckGridRow extends DataCheckRow {
  id: number;
  passText: string;
}

/** Heat steps for coverage: from a pale tint to the full primary hue. */
const COVERAGE_POLE = '#2f6f9f';

function mixHex(a: string, b: string, weight: number): string {
  const parse = (hex: string) => /^#[0-9a-f]{6}$/i.test(hex) ? [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16)) : null;
  const from = parse(a);
  const to = parse(b);
  if (!from || !to) {
    return a;
  }
  return '#' + from.map((c, i) => Math.round(c + (to[i] - c) * weight).toString(16).padStart(2, '0')).join('');
}

/**
 * The data-layer view (SV-G1): what the shared tidy files hold. Totals first, then the dataset table,
 * the coverage heatmap of the harmonised variables, the checks, the flagged values and the files that share dogs.
 */
@Component({
  selector: 'fs-experiment-data-layer-coverage-view',
  standalone: true,
  imports: [FsBadgeComponent, FsCardComponent, FsChartComponent, FsDataGridComponent],
  templateUrl: './experiment-data-layer-coverage-view.component.html',
  styleUrls: ['./experiment-data-layer-coverage-view.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExperimentDataLayerCoverageViewComponent implements OnInit {
  private readonly destroyRef = inject(DestroyRef);

  readonly detail = input.required<ExperimentDetailViewModel>();

  private readonly themeChanges = signal(0);

  protected readonly summary = computed(() =>
    parsePayload<DataLayerSummaryPayload>(this.detail().results.find(r => r.kind === 'dataset_summary')));
  protected readonly coverage = computed(() =>
    parsePayload<CoverageMatrixPayload>(this.detail().results.find(r => r.kind === 'coverage_matrix')));
  protected readonly checks = computed(() =>
    parsePayload<{ rows: DataCheckRow[] }>(this.detail().results.find(r => r.kind === 'data_checks')));
  protected readonly flags = computed(() =>
    parsePayload<{ rows: CleaningFlagRow[] }>(this.detail().results.find(r => r.kind === 'cleaning_flags')));
  protected readonly links = computed(() =>
    parsePayload<DatasetLinksPayload>(this.detail().results.find(r => r.kind === 'dataset_links')));

  protected readonly comparisonText = computed(() => {
    const c = this.links()?.scb050_scb517_comparison;
    return c ? JSON.stringify(c, null, 1) : null;
  });

  protected readonly datasetRows = computed<DatasetGridRow[]>(() => (this.summary()?.rows ?? []).map(r => ({
    ...r,
    groupsText: [
      r.infected ? `${r.infected} infected` : '',
      r.control ? `${r.control} control` : '',
      r.comparator ? `${r.comparator} comparator` : '',
    ].filter(Boolean).join(' · '),
    timepointsText: r.timepoints.length > 3 ? `${r.timepoints.length} timepoints` : r.timepoints.join(', '),
    outcomesText: r.outcomes.length ? r.outcomes.map(o => `${o.name} (${o.dogs_with_value})`).join(', ') : 'none',
    checksText: `${r.checks_passed} / ${r.checks_total}`,
    missingText: r.missing_pct === null ? '–' : `${r.missing_pct.toFixed(1)}%`,
  })));

  protected readonly datasetColumns: FsGridColumn<DatasetGridRow>[] = [
    { dataField: 'dataset', caption: 'Dataset', width: 100 },
    { dataField: 'independent_source', caption: 'Source', width: 80 },
    { dataField: 'species', caption: 'Species', width: 90 },
    { dataField: 'dogs', caption: 'Dogs', width: 70, alignment: 'right' },
    { dataField: 'groupsText', caption: 'Groups', minWidth: 180 },
    { dataField: 'records', caption: 'Records', width: 80, alignment: 'right' },
    { dataField: 'timepointsText', caption: 'Timepoints', minWidth: 120 },
    { dataField: 'variables', caption: 'Variables', width: 90, alignment: 'right' },
    { dataField: 'harmonised_variables', caption: 'Harmonised', width: 100, alignment: 'right' },
    { dataField: 'missingText', caption: 'Cells missing', width: 110, alignment: 'right', calculateSortValue: 'missing_pct' },
    { dataField: 'outcomesText', caption: 'Outcomes file (dogs)', minWidth: 200 },
    { dataField: 'checksText', caption: 'Checks', width: 80, alignment: 'right' },
    { dataField: 'flags', caption: 'Flags', width: 70, alignment: 'right' },
  ];

  protected readonly checkRows = computed<CheckGridRow[]>(() => (this.checks()?.rows ?? []).map((r, i) => ({
    ...r, id: i, passText: r.pass ? 'passed' : 'FAILED',
  })));
  protected readonly failedChecks = computed(() => this.checkRows().filter(r => !r.pass).length);
  protected readonly checkColumns: FsGridColumn<CheckGridRow>[] = [
    { dataField: 'dataset', caption: 'Dataset', width: 100 },
    { dataField: 'check', caption: 'Check', minWidth: 260 },
    { dataField: 'observed', caption: 'Observed', minWidth: 120 },
    { dataField: 'expected', caption: 'Expected', minWidth: 120 },
    { dataField: 'passText', caption: 'Result', width: 90 },
    { dataField: 'source', caption: 'Source of the expected value', minWidth: 240 },
  ];
  protected readonly pager: FsGridPager = { visible: true, showPageSizeSelector: true, allowedPageSizes: [10, 25, 50], showInfo: true };

  /** Harmonised names that at least one dataset has, in the dictionary order. */
  private readonly coveredRows = computed(() => {
    const m = this.coverage();
    if (!m) {
      return [];
    }
    return m.names.map((name, i) => ({ name, share: m.share[i] })).filter(r => r.share.some(v => v !== null));
  });
  protected readonly heatmapHeight = computed(() => Math.max(320, 22 * this.coveredRows().length + 110));

  protected readonly heatmapOptions = computed<FsChartOptions>(() => {
    this.themeChanges();
    const m = this.coverage();
    const rows = this.coveredRows();
    if (!m || !rows.length) {
      return {};
    }
    const empty = fsChartCssColor('--fs-color-fill-subtle', '#f0efec');
    const surface = fsChartCssColor('--fs-color-surface', '#ffffff');
    const ranges = [
      { from: -1.5, to: -0.5, color: empty, name: 'not in the file' },
      { from: -0.5, to: 0.25, color: mixHex(empty, COVERAGE_POLE, 0.2), name: 'under 25% of dogs' },
      { from: 0.25, to: 0.75, color: mixHex(empty, COVERAGE_POLE, 0.5), name: '25 to 75%' },
      { from: 0.75, to: 0.95, color: mixHex(empty, COVERAGE_POLE, 0.75), name: '75 to 95%' },
      { from: 0.95, to: 1.01, color: COVERAGE_POLE, name: '95% or more' },
    ];
    // Apex draws the first series at the bottom: reverse so the list reads top-down.
    const series = rows.map(r => ({
      name: r.name,
      data: m.datasets.map((ds, j) => ({ x: ds, y: r.share[j] === null ? -1 : r.share[j] })),
    })).reverse();
    return {
      chart: { type: 'heatmap', toolbar: { show: false }, animations: { enabled: false } },
      series,
      plotOptions: { heatmap: { radius: 2, enableShades: false, colorScale: { ranges } } },
      dataLabels: { enabled: false },
      stroke: { width: 2, colors: [surface] },
      xaxis: { position: 'top', labels: { style: { fontSize: '11px' } } },
      yaxis: { labels: { maxWidth: 140, style: { fontSize: '11px' } } },
      legend: { show: true, position: 'bottom' },
      tooltip: {
        custom: ({ seriesIndex, dataPointIndex }: { seriesIndex: number; dataPointIndex: number }) => {
          const row = rows[rows.length - 1 - seriesIndex];
          const v = row?.share[dataPointIndex];
          const text = v === null || v === undefined ? 'not in the file' : `${(v * 100).toFixed(0)}% of dogs have a value`;
          return `<div class="fs-experiment-data-layer__tip"><strong>${row?.name}</strong> · ${m.datasets[dataPointIndex]}<br>${text}</div>`;
        },
      },
    };
  });

  ngOnInit(): void {
    this.destroyRef.onDestroy(fsObserveTheme(() => this.themeChanges.update(n => n + 1)));
  }
}
