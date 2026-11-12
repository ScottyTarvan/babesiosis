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

// ---- Payloads written by /experiments/SV-09/scripts/build_load.py ---------------------------

interface AxisComponent {
  component: number;
  eigenvalue: number;
  pa_95: number;
  retained: boolean;
  var_explained: number;
  boot_phi_median: number;
  boot_phi_p5: number;
  stable: boolean;
}

/** `axis_summary` (SV-09-01). */
interface AxisSummaryPayload {
  n: number;
  dataset: string;
  source: string;
  retained: number;
  components: AxisComponent[];
  caveat: string;
}

/** `scree`. */
interface ScreePayload {
  points: { component: number; eigenvalue: number; pa_95: number }[];
  caption: string;
}

/** `loadings`. */
interface LoadingsPayload {
  rows: { variable: string; pc1: number; pc2: number }[];
  caption: string;
}

/** `sensitivity`. */
interface SensitivityPayload {
  rows: { analysis: string; component: number; phi: number }[];
  raw_corr: { component: number; rho_hct: number; rho_illness_days: number }[];
  caption: string;
}

/** `habitus`. */
interface HabitusPayload {
  rows: { component: number; n: number; partial_rho: number; ci: [number, number]; p: number }[];
  caption: string;
}

interface CongruenceComponent {
  component: number;
  phi: number;
  ci: [number, number];
  perm_p: number;
  n_perms: number;
  uniform_phi: number;
  specificity_testable: boolean;
}

interface CongruenceBlock {
  key: string;
  target: string;
  target_label: string;
  species: string;
  variables: string[];
  conditioning: string;
  n_ds05: number;
  n_target: number;
  components: CongruenceComponent[];
  loadings: { variable: string; label: string; ds05: number[]; target: number[] }[];
  link: { component: number; variables: string[]; phi: number }[];
}

/** `congruence` (SV-09-02). */
interface CongruencePayload {
  blocks: CongruenceBlock[];
  caption: string;
}

/** `verdicts`. */
interface VerdictsPayload {
  rows: { component: number; block: string; R1: boolean; R2: boolean; R3: boolean; R4: boolean | null; verdict: string }[];
  rule: string;
}

interface OutcomeRow {
  key: string;
  label: string;
  file: string;
  outcome: string;
  note: string;
  delta: number;
  ci: [number, number];
  p: number;
  q?: number;
  n_pos: number;
  n_neg: number;
}

/** `axis_outcome` (SV-09-03). */
interface AxisOutcomePayload {
  rows: OutcomeRow[];
  axis_component: number;
  axis_status: string;
  adds_beyond_bands: boolean;
  caption: string;
}

/** `score_points`. */
interface ScorePointsPayload {
  points: { file: string; score: number; label: number }[];
}

/** `mcp1`. */
interface Mcp1Payload {
  rows: { file: string; n: number; rho: number; ci: [number, number]; p: number }[];
  caption: string;
}

/** Result kinds this view renders (the page hides them from its raw-JSON list). */
export const AXIS_REPLICATION_RESULT_KINDS = ['interpretation', 'axis_summary', 'scree', 'loadings', 'sensitivity', 'habitus',
  'congruence', 'verdicts', 'axis_outcome', 'score_points', 'mcp1'];

const SENS_LABEL: Record<string, string> = {
  S1_hct_only: 'S1 haematocrit only',
  S2_spec_pseudo_stage: 'S2 SV-01 pseudo-stage (failed validation)',
  S3_time_anchored_stage: 'S3 SV-01 time-anchored stage',
  S4_spearman: 'S4 rank correlations',
  S5_no_conditioning: 'S5 no conditioning',
};

const BLOCK_LABEL: Record<string, string> = {
  red_cell: 'Red cell (DS03)',
  leukocyte_platelet: 'Leukocyte and platelet (S-CB017)',
  leukocyte: 'Leukocyte (S-CB050)',
};

function signed(v: number | null | undefined, digits = 2): string {
  return v === null || v === undefined ? '–' : `${v >= 0 ? '+' : ''}${v.toFixed(digits)}`;
}

function pText(p: number | null | undefined): string {
  return p === null || p === undefined ? '–' : p < 0.001 ? '< 0.001' : p.toFixed(3);
}

function interval(c: [number, number] | undefined): string {
  return c ? `${signed(c[0])} to ${signed(c[1])}` : '–';
}

const FOREST = { width: 420, rowHeight: 26, top: 22 };

function forestX(v: number): number {
  const c = Math.max(-1, Math.min(1, v));
  return (c + 1) / 2 * FOREST.width;
}

/**
 * The axis-replication view (SV-09): residual axes of DS05 after anaemia and illness duration,
 * their congruence with shared variable blocks in other files, and the axis score against death
 * (S-CB050) and complicated disease (S-CB017). The explanation note is rendered by the page after this.
 */
@Component({
  selector: 'fs-experiment-axis-replication-view',
  standalone: true,
  imports: [FsBadgeComponent, FsCardComponent, FsChartComponent, FsDataGridComponent],
  templateUrl: './experiment-axis-replication-view.component.html',
  styleUrls: ['./experiment-axis-replication-view.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExperimentAxisReplicationViewComponent implements OnInit {
  private readonly destroyRef = inject(DestroyRef);

  readonly detail = input.required<ExperimentDetailViewModel>();

  private readonly themeChanges = signal(0);

  private find<T>(kind: string): T | null {
    return parsePayload<T>(this.detail().results.find(r => r.kind === kind));
  }

  protected readonly hasAny = computed(() => !!(this.summary() || this.congruence() || this.outcome()));

  // ---- Experiment 1 ------------------------------------------------------------------------

  protected readonly summary = computed(() => this.find<AxisSummaryPayload>('axis_summary'));
  protected readonly scree = computed(() => this.find<ScreePayload>('scree'));
  protected readonly loadings = computed(() => this.find<LoadingsPayload>('loadings'));
  protected readonly sensitivity = computed(() => this.find<SensitivityPayload>('sensitivity'));
  protected readonly habitus = computed(() => this.find<HabitusPayload>('habitus'));

  protected readonly componentCards = computed(() => (this.summary()?.components ?? []).filter(c => c.retained).map(c => ({
    title: `Axis ${c.component}`,
    eigen: c.eigenvalue.toFixed(2),
    pa: c.pa_95.toFixed(2),
    share: `${Math.round(c.var_explained * 100)}%`,
    phi: `${c.boot_phi_median.toFixed(2)} (5th pct ${c.boot_phi_p5.toFixed(2)})`,
    stable: c.stable,
    habitus: this.habitus()?.rows.find(h => h.component === c.component) ?? null,
  })));

  protected habitusText(h: { partial_rho: number; ci: [number, number]; p: number; n: number } | null): string {
    return h ? `${signed(h.partial_rho)} (${interval(h.ci)}), p ${pText(h.p)}, n ${h.n}` : '–';
  }

  protected readonly screeOptions = computed<FsChartOptions>(() => {
    this.themeChanges();
    const s = this.scree();
    if (!s) {
      return {};
    }
    const soft = fsChartCssColor('--fs-color-ink-soft', '#6b6862');
    return {
      chart: { type: 'line', toolbar: { show: false }, animations: { enabled: false }, zoom: { enabled: false } },
      series: [
        { name: 'Observed eigenvalue', type: 'column', data: s.points.map(p => p.eigenvalue) },
        { name: 'Parallel analysis, 95th percentile', type: 'line', data: s.points.map(p => p.pa_95) },
      ],
      colors: [fsChartCssColor('--fs-color-chart-1', '#4b6bd6'), fsChartCssColor('--fs-color-chart-5', '#c6483a')],
      stroke: { width: [0, 2] },
      markers: { size: [0, 4] },
      dataLabels: { enabled: false },
      xaxis: { categories: s.points.map(p => `${p.component}`), title: { text: 'Component', style: { color: soft } } },
      yaxis: { title: { text: 'Eigenvalue', style: { color: soft } }, labels: { formatter: (v: number) => v.toFixed(1) } },
      legend: { position: 'bottom' },
    };
  });

  protected readonly loadingOptions = computed<FsChartOptions>(() => {
    this.themeChanges();
    const l = this.loadings();
    if (!l) {
      return {};
    }
    const soft = fsChartCssColor('--fs-color-ink-soft', '#6b6862');
    return {
      chart: { type: 'bar', toolbar: { show: false }, animations: { enabled: false } },
      series: [
        { name: 'Axis 1', data: l.rows.map(r => r.pc1) },
        { name: 'Axis 2', data: l.rows.map(r => r.pc2) },
      ],
      colors: [fsChartCssColor('--fs-color-chart-1', '#4b6bd6'), fsChartCssColor('--fs-color-chart-4', '#e0a030')],
      plotOptions: { bar: { horizontal: true, barHeight: '70%' } },
      dataLabels: { enabled: false },
      xaxis: { categories: l.rows.map(r => r.variable), min: -1, max: 1, tickAmount: 4,
        title: { text: 'Loading (correlation with the axis score)', style: { color: soft } },
        labels: { formatter: (v: string) => Number(v).toFixed(1) } },
      legend: { position: 'bottom' },
      tooltip: { y: { formatter: (v: number) => signed(v) } },
    };
  });

  protected readonly sensRows = computed(() => (this.sensitivity()?.rows ?? []).map((r, i) => ({
    id: i, analysis: SENS_LABEL[r.analysis] ?? r.analysis, component: `Axis ${r.component}`, phi: r.phi.toFixed(3),
  })));
  protected readonly sensColumns: FsGridColumn<Record<string, string | number>>[] = [
    { dataField: 'analysis', caption: 'Analysis', minWidth: 260 },
    { dataField: 'component', caption: 'Axis', width: 90 },
    { dataField: 'phi', caption: 'Tucker phi with primary', width: 180, alignment: 'right' },
  ];

  // ---- Experiment 2 ------------------------------------------------------------------------

  protected readonly congruence = computed(() => this.find<CongruencePayload>('congruence'));
  protected readonly verdicts = computed(() => this.find<VerdictsPayload>('verdicts'));

  protected readonly blockCards = computed(() => {
    this.themeChanges();
    const soft = fsChartCssColor('--fs-color-ink-soft', '#6b6862');
    return (this.congruence()?.blocks ?? []).map(b => {
      const options: FsChartOptions = {
        chart: { type: 'bar', toolbar: { show: false }, animations: { enabled: false } },
        series: [
          { name: 'DS05', data: b.loadings.map(l => l.ds05[0]) },
          { name: b.target, data: b.loadings.map(l => l.target[0]) },
        ],
        colors: [fsChartCssColor('--fs-color-chart-1', '#4b6bd6'), fsChartCssColor('--fs-color-chart-3', '#00bad1')],
        plotOptions: { bar: { horizontal: true, barHeight: '70%' } },
        dataLabels: { enabled: false },
        xaxis: { categories: b.loadings.map(l => l.label), min: -1, max: 1, tickAmount: 4,
          title: { text: 'Component 1 loading', style: { color: soft } },
          labels: { formatter: (v: string) => Number(v).toFixed(1) } },
        legend: { position: 'bottom' },
        tooltip: { y: { formatter: (v: number) => signed(v) } },
      };
      return {
        key: b.key,
        title: `${b.target_label} · ${b.species}`,
        subtitle: `${b.variables.length} shared variables · DS05 n ${b.n_ds05}, target n ${b.n_target} · conditioning: ${b.conditioning}`,
        comps: b.components.map(c => ({
          label: `Component ${c.component}`,
          phi: c.phi.toFixed(3),
          ci: `${c.ci[0].toFixed(2)} to ${c.ci[1].toFixed(2)}`,
          uniform: c.uniform_phi.toFixed(2),
          perm: c.specificity_testable ? `${pText(c.perm_p)} (${c.n_perms} orderings)` : `not testable (minimum 1/${c.n_perms})`,
          specific: c.specificity_testable && c.perm_p <= 0.05 && c.phi > c.uniform_phi,
          testable: c.specificity_testable,
        })),
        link: b.link.map(l => `axis ${l.component}: ${signed(l.phi)}`).join(' · '),
        linkVars: b.link[0]?.variables.join(', ') ?? '',
        options,
      };
    });
  });

  protected readonly verdictRows = computed(() => (this.verdicts()?.rows ?? []).map((v, i) => ({
    id: i,
    axis: `Axis ${v.component}`,
    block: BLOCK_LABEL[v.block] ?? v.block,
    r1: v.R1 ? 'Yes' : 'No',
    r2: v.R2 ? 'Yes' : 'No',
    r3: v.R3 ? 'Yes' : 'No',
    r4: v.R4 === null ? 'Not testable' : v.R4 ? 'Yes' : 'No',
    verdict: v.verdict,
  })));
  protected readonly verdictColumns: FsGridColumn<Record<string, string | number>>[] = [
    { dataField: 'axis', caption: 'DS05 axis', width: 100 },
    { dataField: 'block', caption: 'Block', minWidth: 170 },
    { dataField: 'r1', caption: 'R1 stable', width: 90 },
    { dataField: 'r2', caption: 'R2 maps', width: 90 },
    { dataField: 'r3', caption: 'R3 phi ≥ 0.85', width: 120 },
    { dataField: 'r4', caption: 'R4 specific', width: 120 },
    { dataField: 'verdict', caption: 'Verdict', minWidth: 200 },
  ];
  protected readonly nReplicated = computed(() => (this.verdicts()?.rows ?? []).filter(v => v.verdict === 'replicated').length);

  // ---- Experiment 3 ------------------------------------------------------------------------

  protected readonly outcome = computed(() => this.find<AxisOutcomePayload>('axis_outcome'));
  protected readonly points = computed(() => this.find<ScorePointsPayload>('score_points'));
  protected readonly mcp1 = computed(() => this.find<Mcp1Payload>('mcp1'));

  protected readonly forestWidth = FOREST.width;
  protected readonly forestTicks = [-1, -0.5, 0, 0.5, 1].map(v => ({ v, x: forestX(v), label: v === 0 ? '0' : signed(v, 1) }));

  protected readonly headline = computed(() => {
    const o = this.outcome();
    if (!o) {
      return [];
    }
    return o.rows.filter(r => r.key === 's050_died' || r.key === 's017_complicated' || r.key === 's050_bands_only' || r.key === 's050_axis_given_bands')
      .map(r => ({
        label: `${r.file} · ${r.label}`,
        delta: signed(r.delta),
        ci: interval(r.ci),
        n: `${r.n_pos} ${r.outcome} vs ${r.n_neg}`,
        p: `${pText(r.p)}${r.q !== undefined && r.q !== null ? ' · q ' + pText(r.q) : ''}`,
        excludes: r.ci[0] > 0 || r.ci[1] < 0,
      }));
  });

  protected readonly forest = computed(() => {
    const rows = this.outcome()?.rows ?? [];
    return {
      height: FOREST.top + rows.length * FOREST.rowHeight + 8,
      rows: rows.map((r, i) => ({
        id: r.key + i,
        label: `${r.file} · ${r.label}`,
        y: FOREST.top + i * FOREST.rowHeight + FOREST.rowHeight / 2,
        x: forestX(r.delta),
        x1: forestX(r.ci[0]),
        x2: forestX(r.ci[1]),
        strong: r.ci[0] > 0 || r.ci[1] < 0,
        estimate: signed(r.delta),
        interval: interval(r.ci),
      })),
    };
  });

  protected readonly outcomeRows = computed(() => (this.outcome()?.rows ?? []).map((r, i) => ({
    id: i, analysis: r.label, file: r.file, n: `${r.n_pos} vs ${r.n_neg}`, delta: signed(r.delta), ci: interval(r.ci),
    p: pText(r.p), q: r.q === undefined || r.q === null ? '–' : pText(r.q), note: r.note,
  })));
  protected readonly outcomeColumns: FsGridColumn<Record<string, string | number>>[] = [
    { dataField: 'analysis', caption: 'Analysis', minWidth: 240 },
    { dataField: 'file', caption: 'File', width: 90 },
    { dataField: 'n', caption: 'n (label 1 vs 0)', width: 120, alignment: 'right' },
    { dataField: 'delta', caption: "Cliff's delta", width: 100, alignment: 'right' },
    { dataField: 'ci', caption: '95% CI', width: 130, alignment: 'right' },
    { dataField: 'p', caption: 'p', width: 80, alignment: 'right' },
    { dataField: 'q', caption: 'BH q', width: 80, alignment: 'right' },
    { dataField: 'note', caption: 'Note', minWidth: 200 },
  ];

  protected readonly stripCharts = computed(() => {
    this.themeChanges();
    const soft = fsChartCssColor('--fs-color-ink-soft', '#6b6862');
    const pts = this.points()?.points ?? [];
    const files: { file: string; pos: string; neg: string }[] = [
      { file: 'S-CB050', pos: 'Died', neg: 'Survived' },
      { file: 'S-CB017', pos: 'Complicated', neg: 'Uncomplicated' },
    ];
    return files.filter(f => pts.some(p => p.file === f.file)).map(f => {
      const jitter = (i: number) => ((i * 37) % 11 - 5) * 0.03;
      const sel = pts.filter(p => p.file === f.file);
      const pos = sel.filter(p => p.label === 1);
      const neg = sel.filter(p => p.label === 0);
      const options: FsChartOptions = {
        chart: { type: 'scatter', toolbar: { show: false }, animations: { enabled: false }, zoom: { enabled: false } },
        series: [
          { name: `${f.neg} (n ${neg.length})`, data: neg.map((p, i) => ({ x: 0 + jitter(i), y: p.score })) },
          { name: `${f.pos} (n ${pos.length})`, data: pos.map((p, i) => ({ x: 1 + jitter(i + 3), y: p.score })) },
        ],
        colors: [fsChartCssColor('--fs-color-chart-3', '#00bad1'), fsChartCssColor('--fs-color-chart-5', '#ff4c51')],
        markers: { size: 5, strokeWidth: 0 },
        dataLabels: { enabled: false },
        xaxis: { type: 'numeric', min: -0.6, max: 1.6, tickAmount: 1,
          labels: { formatter: (v: string) => (Math.round(Number(v)) === 1 ? f.pos : Math.round(Number(v)) === 0 ? f.neg : '') } },
        yaxis: { title: { text: 'Axis score (SD units)', style: { color: soft } }, labels: { formatter: (v: number) => v.toFixed(1) } },
        legend: { position: 'bottom' },
        tooltip: { x: { show: false }, y: { formatter: (v: number) => v.toFixed(2) } },
      };
      return { file: f.file, options };
    });
  });

  protected readonly mcpRows = computed(() => (this.mcp1()?.rows ?? []).map(r => ({
    file: r.file, n: r.n, rho: signed(r.rho), ci: interval(r.ci), p: pText(r.p),
  })));
  protected readonly mcpColumns: FsGridColumn<Record<string, string | number>>[] = [
    { dataField: 'file', caption: 'File', minWidth: 160 },
    { dataField: 'n', caption: 'Dogs', width: 80, alignment: 'right' },
    { dataField: 'rho', caption: 'Spearman rho', width: 120, alignment: 'right' },
    { dataField: 'ci', caption: '95% CI', width: 140, alignment: 'right' },
    { dataField: 'p', caption: 'p', width: 80, alignment: 'right' },
  ];

  ngOnInit(): void {
    this.destroyRef.onDestroy(fsObserveTheme(() => this.themeChanges.update(n => n + 1)));
  }
}
