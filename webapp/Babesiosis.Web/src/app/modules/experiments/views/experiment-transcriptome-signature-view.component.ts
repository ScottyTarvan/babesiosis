import { ChangeDetectionStrategy, Component, computed, DestroyRef, inject, input, OnInit, signal } from '@angular/core';
import {
  FsBadgeComponent,
  FsCardComponent,
  FsChartComponent,
  fsChartCssColor,
  FsChartOptions,
  FsDataGridComponent,
  FsGridColumn,
  fsObserveTheme,
} from '@core';
import { ExperimentDetailViewModel, parsePayload } from 'app/modules/experiments/viewmodels/experiment.viewmodel';

// ---- Payloads written by /experiments/SV-08/scripts/build_load.py ---------------------------

interface SetVerdict {
  signature_appears: boolean;
  before_deterioration_working: boolean;
  before_deterioration_alternative: boolean;
  earlier_at_high_dose: boolean;
}

interface SetSummary {
  set: string;
  label: string;
  in_family: boolean;
  n_dogs: number;
  n_genes: number;
  n_genes_fixed: number;
  positive: number;
  sign_test_p: number | null;
  beyond_rise: number;
  beyond_fall: number;
  median_delta: number | null;
  s1_positive: number;
  s1_beyond_rise: number;
  s2_positive: number;
  s3_positive: number;
  s4_positive_all_loo: number;
  verdict: SetVerdict | null;
}

interface DogDelta {
  dog: string;
  label: string;
  dose: string;
  set: string;
  last_pre_day: number;
  score_d0: number | null;
  score_last: number | null;
  delta: number | null;
  bg_percentile: number | null;
  bg_lo95: number | null;
  bg_hi95: number | null;
  beyond: string;
}

/** `primary_result`: per set sign counts and the per-dog deltas. */
interface SignaturePrimaryPayload {
  label: string;
  n_dogs: number;
  n_low: number;
  n_high: number;
  n_samples: number;
  n_genes_matrix: number;
  independent_sources: number;
  sources: string[];
  sets: SetSummary[];
  dogs: DogDelta[];
  note: string;
}

interface TrajPoint {
  day: number;
  score: number | null;
  delta: number | null;
  bg_percentile: number | null;
  post_treatment: boolean;
  parasitaemia_working: number | null;
  parasitaemia_alt: number | null;
  library_size: number | null;
}

interface TrajDog {
  dog: string;
  label: string;
  dose: string;
  points: TrajPoint[];
}

interface TrajSet {
  set: string;
  label: string;
  n_genes: number;
  low_0_d0: number | null;
  dogs: TrajDog[];
}

/** `score_trajectories`: one entry per set. */
interface TrajectoriesPayload {
  sets: TrajSet[];
}

interface TimingRow {
  mapping: string;
  dog: string;
  dose: string;
  ds02_dog: string;
  ds02_original_id: string | null;
  set: string;
  set_label: string;
  first_risen_day: number | null;
  deterioration_day: number | null;
  habitus_baseline: number | null;
  risen_before_deterioration: boolean;
}

interface TimingPayload {
  rows: TimingRow[];
  verdict: Record<string, SetVerdict>;
}

interface CheckRow {
  mapping: string;
  set: string;
  set_label: string;
  variable: string;
  dog: string;
  n_points: number | null;
  rho: number | null;
}

interface SensRow {
  dog: string;
  label: string;
  set: string;
  set_label: string;
  delta: number | null;
  s1_delta_d3: number | null;
  s1_bg_percentile: number | null;
  s2_delta_log2_uq: number | null;
  s3_delta: number | null;
  s4_min: number | null;
  s4_max: number | null;
}

interface GeneRow {
  set: string;
  set_label: string;
  gene: string;
  mapped: boolean;
  row_id: string | null;
  how: string | null;
  reason: string | null;
}

interface LibRow {
  sample: string;
  dog: string;
  day: number;
  library_size: number | null;
  alas2_percentile: number | null;
}

interface RowsPayload<T> {
  rows: T[];
}

/** Result kinds this view renders (the page hides them from its raw-JSON list). */
export const TRANSCRIPTOME_SIGNATURE_RESULT_KINDS = ['interpretation', 'primary_result', 'score_trajectories', 'timing',
  'construct_checks', 'sensitivity', 'gene_mapping', 'library_sizes'];

function signed(v: number | null | undefined, digits = 3): string {
  return v === null || v === undefined ? '–' : `${v >= 0 ? '+' : ''}${v.toFixed(digits)}`;
}

function num(v: number | null | undefined, digits = 2): string {
  return v === null || v === undefined ? '–' : v.toFixed(digits);
}

function yesNo(v: boolean | null | undefined): string {
  return v === null || v === undefined ? '–' : v ? 'yes' : 'no';
}

const DOG_TOKENS: Record<string, [string, string]> = {
  low_1: ['--fs-color-chart-2', '#2f9e8f'],
  low_2: ['--fs-color-chart-5', '#5aa36b'],
  high_1: ['--fs-color-chart-1', '#4b6bd6'],
  high_2: ['--fs-color-chart-3', '#c98a2b'],
  high_3: ['--fs-color-chart-4', '#c6483a'],
};
const SET_TOKENS: Record<string, [string, string]> = {
  neutrophil_granule: ['--fs-color-chart-1', '#4b6bd6'],
  type1_interferon: ['--fs-color-chart-4', '#c6483a'],
  erythroid_control: ['--fs-color-chart-6', '#8a8580'],
};

type GridRow = Record<string, string | number>;

/**
 * The transcriptome-signature view (SV-08): per-dog change of the neutrophil granule, type 1 interferon and
 * erythroid set scores in the DS06 Beagles, against a composition background; score by day and by
 * parasitaemia; timing against clinical deterioration; construct checks and the gene mapping.
 */
@Component({
  selector: 'fs-experiment-transcriptome-signature-view',
  standalone: true,
  imports: [FsBadgeComponent, FsCardComponent, FsChartComponent, FsDataGridComponent],
  templateUrl: './experiment-transcriptome-signature-view.component.html',
  styleUrls: ['./experiment-transcriptome-signature-view.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExperimentTranscriptomeSignatureViewComponent implements OnInit {
  private readonly destroyRef = inject(DestroyRef);

  readonly detail = input.required<ExperimentDetailViewModel>();

  private readonly themeChanges = signal(0);

  private find<T>(kind: string): T | null {
    return parsePayload<T>(this.detail().results.find(r => r.kind === kind));
  }

  protected readonly primary = computed(() => this.find<SignaturePrimaryPayload>('primary_result'));
  protected readonly trajectories = computed(() => this.find<TrajectoriesPayload>('score_trajectories'));
  protected readonly timing = computed(() => this.find<TimingPayload>('timing'));
  protected readonly checks = computed(() => this.find<RowsPayload<CheckRow>>('construct_checks'));
  protected readonly sensitivity = computed(() => this.find<RowsPayload<SensRow>>('sensitivity'));
  protected readonly genes = computed(() => this.find<RowsPayload<GeneRow>>('gene_mapping'));
  protected readonly libs = computed(() => this.find<RowsPayload<LibRow>>('library_sizes'));

  protected intent(s: SetSummary): 'success' | 'danger' | 'warning' | 'info' {
    if (!s.in_family) {
      return 'info';
    }
    return s.verdict?.signature_appears ? 'success' : 'warning';
  }

  protected readonly deltaRows = computed<GridRow[]>(() => (this.primary()?.dogs ?? []).map((d, i) => ({
    id: i,
    dog: d.label,
    set: this.setLabel(d.set),
    days: `D0 → D${d.last_pre_day}`,
    d0: num(d.score_d0, 3),
    last: num(d.score_last, 3),
    delta: signed(d.delta),
    bg: `${signed(d.bg_lo95)} to ${signed(d.bg_hi95)}`,
    pct: num(d.bg_percentile, 3),
    beyond: d.beyond === 'rise' ? 'rise' : d.beyond === 'fall' ? 'fall' : 'no',
  })));
  protected readonly deltaColumns: FsGridColumn<GridRow>[] = [
    { dataField: 'dog', caption: 'Dog', width: 210 },
    { dataField: 'set', caption: 'Set', minWidth: 200 },
    { dataField: 'days', caption: 'Change', width: 100 },
    { dataField: 'd0', caption: 'Score D0', width: 90, alignment: 'right' },
    { dataField: 'last', caption: 'Score last', width: 90, alignment: 'right' },
    { dataField: 'delta', caption: 'Delta', width: 90, alignment: 'right' },
    { dataField: 'bg', caption: 'Random-set delta, 95% range', width: 200, alignment: 'right' },
    { dataField: 'pct', caption: 'Background percentile', width: 160, alignment: 'right' },
    { dataField: 'beyond', caption: 'Beyond background', width: 140 },
  ];

  protected readonly timingRows = computed<GridRow[]>(() => (this.timing()?.rows ?? [])
    .filter(t => t.set !== 'erythroid_control')
    .map((t, i) => ({
      id: i,
      mapping: t.mapping,
      dog: t.dog,
      ds02: `${t.ds02_dog}${t.ds02_original_id ? ` (${t.ds02_original_id})` : ''}`,
      set: t.set_label,
      risen: t.first_risen_day === null ? 'never' : `day ${t.first_risen_day}`,
      det: t.deterioration_day === null ? 'never' : `day ${t.deterioration_day}`,
      before: yesNo(t.risen_before_deterioration),
    })));
  protected readonly timingColumns: FsGridColumn<GridRow>[] = [
    { dataField: 'mapping', caption: 'Mapping', width: 110 },
    { dataField: 'dog', caption: 'DS06 dog', width: 90 },
    { dataField: 'ds02', caption: 'DS02 dog', width: 160 },
    { dataField: 'set', caption: 'Set', minWidth: 170 },
    { dataField: 'risen', caption: 'First risen (≥ 0.975)', width: 150 },
    { dataField: 'det', caption: 'Habitus fell', width: 110 },
    { dataField: 'before', caption: 'Risen before', width: 110 },
  ];

  protected readonly verdictRows = computed(() => {
    const v = this.timing()?.verdict ?? {};
    return Object.keys(v).map(k => ({ set: this.setLabel(k), ...v[k] }));
  });

  protected readonly checkRows = computed<GridRow[]>(() => (this.checks()?.rows ?? []).map((c, i) => ({
    id: i,
    mapping: c.mapping,
    pair: `${c.set_label} with ${c.variable}`,
    dog: c.dog,
    n: c.n_points ?? '–',
    rho: signed(c.rho, 2),
  })));
  protected readonly checkColumns: FsGridColumn<GridRow>[] = [
    { dataField: 'mapping', caption: 'Mapping', width: 110 },
    { dataField: 'pair', caption: 'Score with DS02 measure', minWidth: 300 },
    { dataField: 'dog', caption: 'Dog', width: 140 },
    { dataField: 'n', caption: 'Points (dogs for median)', width: 170, alignment: 'right' },
    { dataField: 'rho', caption: 'Spearman rho', width: 120, alignment: 'right' },
  ];

  protected readonly sensRows = computed<GridRow[]>(() => (this.sensitivity()?.rows ?? []).map((s, i) => ({
    id: i,
    dog: s.dog,
    set: s.set_label,
    delta: signed(s.delta),
    s1: `${signed(s.s1_delta_d3)} (${num(s.s1_bg_percentile, 2)})`,
    s2: signed(s.s2_delta_log2_uq, 2),
    s3: signed(s.s3_delta),
    s4: `${signed(s.s4_min)} to ${signed(s.s4_max)}`,
  })));
  protected readonly sensColumns: FsGridColumn<GridRow>[] = [
    { dataField: 'dog', caption: 'Dog', width: 90 },
    { dataField: 'set', caption: 'Set', minWidth: 200 },
    { dataField: 'delta', caption: 'Primary delta', width: 110, alignment: 'right' },
    { dataField: 's1', caption: 'S1 D0 → D3 (percentile)', width: 180, alignment: 'right' },
    { dataField: 's2', caption: 'S2 log2 UQ-CPM', width: 130, alignment: 'right' },
    { dataField: 's3', caption: 'S3 no reticulocyte genes', width: 180, alignment: 'right' },
    { dataField: 's4', caption: 'S4 leave one gene out', width: 180, alignment: 'right' },
  ];

  protected readonly geneRows = computed<GridRow[]>(() => (this.genes()?.rows ?? []).map((g, i) => ({
    id: i,
    set: g.set_label,
    gene: g.gene,
    mapped: g.mapped ? 'mapped' : 'not mapped',
    row: g.row_id ?? '–',
    how: g.mapped ? (g.how ?? '') : (g.reason ?? ''),
  })));
  protected readonly geneColumns: FsGridColumn<GridRow>[] = [
    { dataField: 'set', caption: 'Set', width: 220 },
    { dataField: 'gene', caption: 'Gene', width: 90 },
    { dataField: 'mapped', caption: 'Status', width: 100 },
    { dataField: 'row', caption: 'DS06 row', width: 220 },
    { dataField: 'how', caption: 'How, or why not', minWidth: 300 },
  ];

  protected readonly unmappedCount = computed(() => (this.genes()?.rows ?? []).filter(g => !g.mapped).length);

  protected readonly deltaChart = computed(() => this.deltaOptions());
  protected readonly dayCharts = computed(() => (this.trajectories()?.sets ?? []).map(s => ({ set: s, options: this.dayOptions(s) })));
  protected readonly loadCharts = computed(() => (this.trajectories()?.sets ?? [])
    .filter(s => s.set !== 'erythroid_control').map(s => ({ set: s, options: this.loadOptions(s) })));
  protected readonly libChart = computed(() => this.libOptions());

  ngOnInit(): void {
    this.destroyRef.onDestroy(fsObserveTheme(() => this.themeChanges.update(n => n + 1)));
  }

  private setLabel(key: string): string {
    return this.primary()?.sets.find(s => s.set === key)?.label ?? key;
  }

  private axisColours() {
    return { soft: fsChartCssColor('--fs-color-ink-soft', '#6b6862'), ink: fsChartCssColor('--fs-color-ink', '#2b2a27') };
  }

  private deltaOptions(): FsChartOptions | null {
    this.themeChanges();
    const p = this.primary();
    if (!p) {
      return null;
    }
    const { soft } = this.axisColours();
    const dogs = Array.from(new Set(p.dogs.map(d => d.dog)));
    const labels = dogs.map(d => p.dogs.find(x => x.dog === d)?.label ?? d);
    const series = p.sets.map(s => ({
      name: s.label,
      data: dogs.map(d => p.dogs.find(x => x.dog === d && x.set === s.set)?.delta ?? null),
    }));
    return {
      chart: { type: 'bar', toolbar: { show: false }, animations: { enabled: false } },
      series,
      colors: p.sets.map(s => fsChartCssColor(SET_TOKENS[s.set]?.[0] ?? '--fs-color-chart-1', SET_TOKENS[s.set]?.[1] ?? '#4b6bd6')),
      plotOptions: { bar: { horizontal: false, columnWidth: '60%' } },
      dataLabels: { enabled: false },
      xaxis: { categories: labels, labels: { style: { colors: soft } } },
      yaxis: {
        title: { text: 'Change in score, D0 → last pre-treatment', style: { color: soft } },
        labels: { formatter: (v: number) => signed(v, 2) },
      },
      annotations: { yaxis: [{ y: 0, borderColor: soft }] },
      legend: { position: 'bottom', horizontalAlign: 'left' },
      tooltip: { y: { formatter: (v: number) => signed(v) } },
    };
  }

  private dayOptions(s: TrajSet): FsChartOptions {
    this.themeChanges();
    const { soft } = this.axisColours();
    const series = s.dogs.map(d => ({
      name: d.label,
      type: 'line',
      data: d.points.filter(p => p.score !== null).map(p => ({ x: p.day, y: p.score as number })),
    }));
    const colours = s.dogs.map(d => fsChartCssColor(DOG_TOKENS[d.dog]?.[0] ?? '--fs-color-chart-1', DOG_TOKENS[d.dog]?.[1] ?? '#4b6bd6'));
    const annotations: object[] = [{
      x: 4.5, borderColor: soft, strokeDashArray: 4,
      label: { text: 'treatment (about day 4); later days post-treatment', style: { color: soft, background: 'transparent' }, borderWidth: 0 },
    }];
    return {
      chart: { type: 'line', toolbar: { show: false }, animations: { enabled: false }, zoom: { enabled: false } },
      series,
      colors: colours,
      stroke: { width: 2, curve: 'straight' },
      markers: { size: 5, strokeWidth: 0 },
      dataLabels: { enabled: false },
      annotations: {
        xaxis: annotations,
        yaxis: s.low_0_d0 === null ? [] : [{
          y: s.low_0_d0, borderColor: soft, strokeDashArray: 2,
          label: { text: 'low_0 (D0 only)', style: { color: soft, background: 'transparent' }, borderWidth: 0 },
        }],
      },
      xaxis: { type: 'numeric', min: 0, max: 8, tickAmount: 8, title: { text: 'Day after inoculation', style: { color: soft } } },
      yaxis: { title: { text: 'Set score (mean rank percentile)', style: { color: soft } }, labels: { formatter: (v: number) => num(v, 2) } },
      legend: { position: 'bottom', horizontalAlign: 'left' },
      tooltip: { shared: false, intersect: true, y: { formatter: (v: number) => num(v, 3) } },
    };
  }

  private loadOptions(s: TrajSet): FsChartOptions {
    this.themeChanges();
    const { soft } = this.axisColours();
    const offset = 0.01;
    const series = s.dogs.map(d => ({
      name: d.label,
      type: 'line',
      data: d.points
        .filter(p => !p.post_treatment && p.score !== null)
        .map(p => ({ x: Math.log10((p.day === 0 ? 0 : (p.parasitaemia_working ?? 0)) + offset), y: p.score as number })),
    }));
    const colours = s.dogs.map(d => fsChartCssColor(DOG_TOKENS[d.dog]?.[0] ?? '--fs-color-chart-1', DOG_TOKENS[d.dog]?.[1] ?? '#4b6bd6'));
    const xLabel = (v: number) => {
      const raw = Math.pow(10, v) - offset;
      return raw < 0.005 ? '0' : raw >= 10 ? raw.toFixed(0) : raw >= 1 ? raw.toFixed(1) : raw.toFixed(2);
    };
    return {
      chart: { type: 'line', toolbar: { show: false }, animations: { enabled: false }, zoom: { enabled: false } },
      series,
      colors: colours,
      stroke: { width: 2, curve: 'straight' },
      markers: { size: 5, strokeWidth: 0 },
      dataLabels: { enabled: false },
      xaxis: {
        type: 'numeric', min: -2.1, max: 2, tickAmount: 8,
        title: { text: 'Parasitaemia, % (log scale; working mapping)', style: { color: soft } },
        labels: { formatter: (v: string) => xLabel(Number(v)) },
      },
      yaxis: { title: { text: 'Set score', style: { color: soft } }, labels: { formatter: (v: number) => num(v, 2) } },
      legend: { position: 'bottom', horizontalAlign: 'left' },
      tooltip: { shared: false, intersect: true, y: { formatter: (v: number) => num(v, 3) } },
    };
  }

  private libOptions(): FsChartOptions | null {
    this.themeChanges();
    const rows = this.libs()?.rows ?? [];
    if (!rows.length) {
      return null;
    }
    const { soft } = this.axisColours();
    return {
      chart: { type: 'bar', toolbar: { show: false }, animations: { enabled: false } },
      series: [{ name: 'Library size (million counts)', data: rows.map(r => (r.library_size ?? 0) / 1e6) }],
      colors: [fsChartCssColor('--fs-color-chart-1', '#4b6bd6')],
      dataLabels: { enabled: false },
      xaxis: { categories: rows.map(r => r.sample), labels: { rotate: -60, style: { colors: soft, fontSize: '10px' } } },
      yaxis: { title: { text: 'Million counts', style: { color: soft } }, labels: { formatter: (v: number) => num(v, 0) } },
      tooltip: {
        y: {
          formatter: (v: number, o: { dataPointIndex: number }) =>
            `${num(v, 1)} M · ALAS2 percentile ${num(rows[o.dataPointIndex]?.alas2_percentile, 3)}`,
        },
      },
      legend: { show: false },
    };
  }
}
