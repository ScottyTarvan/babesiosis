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

/** The result kinds that this view draws (SV-07, method `linkage_audit`). */
export const LINKAGE_AUDIT_RESULT_KINDS: readonly string[] = [
  'primary_result', 'ds04_join', 'ds03_signalment', 'ds07_numbering', 'ds06_mapping', 'source_proposal', 'linkage_table',
];

type Certainty = 'confirmed by values' | 'probable' | 'unverified';

interface FilePairRow {
  file_a: string;
  file_b: string;
  shared_dogs: string;
  certainty: string;
  found_by: string;
  consequence: string;
}

interface PrimaryPayload {
  link_counts: Record<Certainty, number>;
  n_links: number;
  file_pairs: FilePairRow[];
  headline: { label: string; value: number; of: number | null; note?: string }[];
}

interface Ds04Row {
  row: number;
  ds04_case: string | number;
  group: string;
  wbc: number;
  seg: number;
  band: number;
  s050_exact: string | number | null;
  s050_near_5pct: string | number | null;
  nearest_case: number;
  nearest_max_reldiff: number;
  nearest_outcome: string;
  signalment_agrees: boolean | null;
}

interface Ds04Payload {
  rows: Ds04Row[];
  p_three_matches: number;
  icterus_agree: number;
  icterus_n: number;
  icterus_p_fixed: number;
  orders_agree: boolean;
}

interface RateRow {
  ds03_block: string;
  against: string;
  pairs: number;
  candidate_pairs: number;
  per_1000: number;
  expected_at_baseline: number;
  ratio_to_baseline: number;
  p_poisson: number;
}

interface OrderRow {
  ds03_block: string;
  unique_pairs: number;
  order_inversions: number;
  kendall_tau: number | null;
}

interface Ds03Payload {
  rates: RateRow[];
  summary: { ds03_block: string; n_complete: number; with_s050_candidate: number; with_unique_s050_candidate: number; with_ds05_candidate: number | null }[];
  order_check: OrderRow[];
  unique_pairs: { ds03_block: string; ds03_id: string; ds03_number: number; s050_case: number }[];
  baseline_rate_per_1000: number;
  value_check: { ds04_case: string | number; ds03_id: string; ds04_hct: number; ds03_hct: number; ds04_retic_pct: number; ds03_retic_pct: number }[];
}

interface Ds07Payload {
  hypergeometric: { universe: string; expected_in_complicated: number; p_ge_observed_complicated: number; expected_in_any_infected: number; p_ge_observed_any: number }[];
  consistency: { ds04_case: number; ds07_group: string; sex: string; neuter: string | null; age_months: number; timing: string; s050_case: number | null; contradiction: string | null }[];
  in_complicated: number[];
  in_uncomplicated: number[];
}

interface Ds06Payload {
  scores: { test: string; assignment: string; days: string; lymph: number; neut: number; mono: number; mean: number; best: boolean; wins: number }[];
  positive_control_pass: boolean;
  markers_absent: Record<string, string[]>;
}

interface LinkRow {
  dataset_a: string;
  id_a: string;
  dataset_b: string;
  id_b: string;
  basis: string;
  fields_matched: string;
  certainty: Certainty;
}

const BLOCK_TOKENS: Record<string, [string, string]> = {
  'cohort 1': ['--fs-color-chart-1', '#4b6bd6'],
  'cohort 2': ['--fs-color-chart-3', '#2f9f7a'],
  controls: ['--fs-color-chart-4', '#c6483a'],
};

function fmtP(p: number | null | undefined): string {
  if (p === null || p === undefined) {
    return '–';
  }
  return p < 0.001 ? p.toExponential(1) : p.toFixed(3);
}

/**
 * The linkage-audit view (SV-07): which files share dogs. The file-pair table first, then the evidence for each pair:
 * DS04 against S-CB050 by values, DS03 against S-CB050 by signalment with a chance baseline and the study-number order,
 * DS07 numbering, DS06 names, the proposed independent_source changes and every link row.
 */
@Component({
  selector: 'fs-experiment-linkage-audit-view',
  standalone: true,
  imports: [FsBadgeComponent, FsCardComponent, FsChartComponent, FsDataGridComponent],
  templateUrl: './experiment-linkage-audit-view.component.html',
  styleUrls: ['./experiment-linkage-audit-view.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExperimentLinkageAuditViewComponent implements OnInit {
  private readonly destroyRef = inject(DestroyRef);

  readonly detail = input.required<ExperimentDetailViewModel>();

  private readonly themeChanges = signal(0);

  private payload<T>(kind: string) {
    return computed(() => parsePayload<T>(this.detail().results.find(r => r.kind === kind)));
  }

  protected readonly primary = this.payload<PrimaryPayload>('primary_result');
  protected readonly ds04 = this.payload<Ds04Payload>('ds04_join');
  protected readonly ds03 = this.payload<Ds03Payload>('ds03_signalment');
  protected readonly ds07 = this.payload<Ds07Payload>('ds07_numbering');
  protected readonly ds06 = this.payload<Ds06Payload>('ds06_mapping');
  protected readonly proposal = this.payload<{ rows: Record<string, string>[] }>('source_proposal');
  protected readonly linkTable = this.payload<{ rows: LinkRow[] }>('linkage_table');

  protected readonly pager: FsGridPager = { visible: true, showPageSizeSelector: true, allowedPageSizes: [10, 25, 50], showInfo: true };

  protected readonly filePairColumns: FsGridColumn<FilePairRow>[] = [
    { dataField: 'file_a', caption: 'File', width: 170 },
    { dataField: 'file_b', caption: 'Shares dogs with', width: 170 },
    { dataField: 'shared_dogs', caption: 'Dogs', minWidth: 180 },
    { dataField: 'certainty', caption: 'Certainty', width: 190 },
    { dataField: 'consequence', caption: 'Evidence and consequence', minWidth: 320 },
    { dataField: 'found_by', caption: 'Found by', width: 140 },
  ];

  protected readonly ds04Rows = computed(() => (this.ds04()?.rows ?? []).map(r => ({
    ...r,
    countsText: `${r.wbc} / ${r.seg} / ${r.band}`,
    matchText: r.s050_exact !== null && r.s050_exact !== '' ? `case ${r.s050_exact}` : 'none',
    nearestText: `case ${r.nearest_case} (${(100 * r.nearest_max_reldiff).toFixed(1)}%, ${r.nearest_outcome})`,
    signalText: r.signalment_agrees === null ? '–' : (r.signalment_agrees ? 'equal' : 'differs'),
  })));
  protected readonly ds04Columns: FsGridColumn<Record<string, unknown>>[] = [
    { dataField: 'row', caption: 'Row', width: 60, alignment: 'right' },
    { dataField: 'ds04_case', caption: 'DS04 case (by order)', width: 150 },
    { dataField: 'group', caption: 'Group', width: 80 },
    { dataField: 'countsText', caption: 'WBC / seg / band (10^9/L)', minWidth: 190 },
    { dataField: 'matchText', caption: 'S-CB050 within rounding', width: 170 },
    { dataField: 'signalText', caption: 'Age, weight, sex', width: 130 },
    { dataField: 'nearestText', caption: 'Nearest S-CB050 row (largest difference)', minWidth: 260 },
  ];

  protected readonly rateRows = computed(() => (this.ds03()?.rates ?? []).map(r => ({
    ...r, pText: fmtP(r.p_poisson), id: `${r.ds03_block}|${r.against}`,
  })));
  protected readonly rateColumns: FsGridColumn<Record<string, unknown>>[] = [
    { dataField: 'ds03_block', caption: 'File block', width: 150 },
    { dataField: 'against', caption: 'Against', width: 160 },
    { dataField: 'pairs', caption: 'Pairs compared', width: 120, alignment: 'right' },
    { dataField: 'candidate_pairs', caption: 'Twin pairs', width: 100, alignment: 'right' },
    { dataField: 'per_1000', caption: 'Per 1,000 pairs', width: 120, alignment: 'right' },
    { dataField: 'expected_at_baseline', caption: 'Expected at chance', width: 140, alignment: 'right' },
    { dataField: 'ratio_to_baseline', caption: 'Times chance', width: 110, alignment: 'right' },
    { dataField: 'pText', caption: 'p (Poisson)', width: 110, alignment: 'right' },
  ];

  protected readonly rateChart = computed<FsChartOptions>(() => {
    this.themeChanges();
    const rows = this.ds03()?.rates ?? [];
    if (!rows.length) {
      return {};
    }
    const soft = fsChartCssColor('--fs-color-ink-soft', '#6b6862');
    return {
      chart: { type: 'bar', toolbar: { show: false }, animations: { enabled: false } },
      series: [{ name: 'Twin pairs per 1,000 pairs', data: rows.map(r => r.per_1000) }],
      colors: rows.map(r => r.against.includes('DS05')
        ? fsChartCssColor('--fs-color-ink-soft', '#6b6862')
        : fsChartCssColor('--fs-color-chart-1', '#4b6bd6')),
      plotOptions: { bar: { horizontal: true, distributed: true, barHeight: '65%' } },
      dataLabels: { enabled: true, formatter: (v: number) => v.toFixed(1), style: { fontSize: '11px' } },
      legend: { show: false },
      xaxis: {
        categories: rows.map(r => `${r.ds03_block} vs ${r.against}`),
        title: { text: 'Age-weight-sex twin pairs per 1,000 pairs compared', style: { color: soft } },
      },
      yaxis: { labels: { maxWidth: 260, style: { fontSize: '11px' } } },
      tooltip: { y: { formatter: (v: number) => `${v.toFixed(2)} per 1,000` } },
    };
  });

  protected readonly orderChart = computed<FsChartOptions>(() => {
    this.themeChanges();
    const pairs = this.ds03()?.unique_pairs ?? [];
    if (!pairs.length) {
      return {};
    }
    const soft = fsChartCssColor('--fs-color-ink-soft', '#6b6862');
    const blocks = ['cohort 1', 'cohort 2', 'controls'];
    const prefix: Record<string, string> = { 'cohort 1': 'BC', 'cohort 2': 'BLSC', controls: 'CON' };
    return {
      chart: { type: 'scatter', toolbar: { show: false }, animations: { enabled: false }, zoom: { enabled: false } },
      series: blocks.map(b => {
        const pts = pairs.filter(p => p.ds03_block === b);
        return { name: `DS03 ${b} (${prefix[b]} numbers, n ${pts.length})`, data: pts.map(p => ({ x: p.ds03_number, y: p.s050_case })) };
      }),
      colors: blocks.map(b => fsChartCssColor(BLOCK_TOKENS[b][0], BLOCK_TOKENS[b][1])),
      markers: { size: 4, strokeWidth: 0 },
      dataLabels: { enabled: false },
      xaxis: {
        type: 'numeric', tickAmount: 10,
        title: { text: 'DS03 study number (digits of BC / BLSC / CON)', style: { color: soft } },
        labels: { formatter: (v: string) => Number(v).toFixed(0) },
      },
      yaxis: { title: { text: 'S-CB050 case number of the unique twin', style: { color: soft } }, labels: { formatter: (v: number) => v.toFixed(0) } },
      legend: { position: 'bottom' },
      tooltip: { x: { formatter: (v: number) => `DS03 number ${v}` }, y: { formatter: (v: number) => `S-CB050 case ${v}` } },
    };
  });

  protected readonly hypRows = computed(() => (this.ds07()?.hypergeometric ?? []).map(r => ({
    ...r, pc: fmtP(r.p_ge_observed_complicated), pa: fmtP(r.p_ge_observed_any),
  })));
  protected readonly hypColumns: FsGridColumn<Record<string, unknown>>[] = [
    { dataField: 'universe', caption: 'Number range assumed', width: 160 },
    { dataField: 'expected_in_complicated', caption: 'Expected in complicated', width: 170, alignment: 'right' },
    { dataField: 'pc', caption: 'p (6 or more of 7)', width: 140, alignment: 'right' },
    { dataField: 'expected_in_any_infected', caption: 'Expected in any infected list', width: 200, alignment: 'right' },
    { dataField: 'pa', caption: 'p (7 of 7)', width: 120, alignment: 'right' },
  ];
  protected readonly consColumns: FsGridColumn<Record<string, unknown>>[] = [
    { dataField: 'ds04_case', caption: 'Number', width: 80, alignment: 'right' },
    { dataField: 'ds07_group', caption: 'DS07 group', width: 130 },
    { dataField: 'timing', caption: 'DS04 death', width: 130 },
    { dataField: 'sex', caption: 'Sex', width: 80 },
    { dataField: 'neuter', caption: 'Neuter', width: 90 },
    { dataField: 'age_months', caption: 'Age (months)', width: 110, alignment: 'right' },
    { dataField: 's050_case', caption: 'S-CB050 case', width: 110, alignment: 'right' },
    { dataField: 'contradiction', caption: 'Contradiction with CB112', minWidth: 280 },
  ];

  protected readonly ds06Rows = computed(() => (this.ds06()?.scores ?? []).map((r, i) => ({ ...r, id: i, bestText: r.best ? 'best' : '' })));
  protected readonly ds06Columns: FsGridColumn<Record<string, unknown>>[] = [
    { dataField: 'test', caption: 'Test', minWidth: 220 },
    { dataField: 'assignment', caption: 'Assignment', minWidth: 260 },
    { dataField: 'lymph', caption: 'rho lymph', width: 90, alignment: 'right' },
    { dataField: 'neut', caption: 'rho neut', width: 90, alignment: 'right' },
    { dataField: 'mono', caption: 'rho mono', width: 90, alignment: 'right' },
    { dataField: 'mean', caption: 'Mean', width: 80, alignment: 'right' },
    { dataField: 'bestText', caption: '', width: 60 },
  ];
  protected readonly absentMarkers = computed(() => {
    const a = this.ds06()?.markers_absent ?? {};
    return Object.values(a).flat().join(', ');
  });

  protected readonly proposalColumns: FsGridColumn<Record<string, string>>[] = [
    { dataField: 'dataset', caption: 'Dataset', minWidth: 220 },
    { dataField: 'current', caption: 'Now', width: 90 },
    { dataField: 'proposed', caption: 'Proposed', width: 220 },
    { dataField: 'reason', caption: 'Reason', minWidth: 320 },
  ];

  protected readonly certaintyFilter = signal<Certainty | 'all'>('all');
  protected readonly linkRows = computed(() => {
    const f = this.certaintyFilter();
    return (this.linkTable()?.rows ?? []).map((r, i) => ({ ...r, id: i })).filter(r => f === 'all' || r.certainty === f);
  });
  protected readonly linkColumns: FsGridColumn<Record<string, unknown>>[] = [
    { dataField: 'dataset_a', caption: 'File A', width: 170 },
    { dataField: 'id_a', caption: 'ID A', width: 160 },
    { dataField: 'dataset_b', caption: 'File B', width: 150 },
    { dataField: 'id_b', caption: 'ID B', width: 130 },
    { dataField: 'certainty', caption: 'Certainty', width: 160 },
    { dataField: 'fields_matched', caption: 'Fields', minWidth: 200 },
    { dataField: 'basis', caption: 'Basis', minWidth: 360 },
  ];
  protected readonly certainties: (Certainty | 'all')[] = ['all', 'confirmed by values', 'probable', 'unverified'];

  protected intent(c: string): 'success' | 'warning' | 'secondary' {
    return c.startsWith('confirmed') ? 'success' : (c.startsWith('probable') ? 'warning' : 'secondary');
  }

  protected fmtP(p: number | null | undefined): string {
    return fmtP(p);
  }

  ngOnInit(): void {
    this.destroyRef.onDestroy(fsObserveTheme(() => this.themeChanges.update(n => n + 1)));
  }
}
