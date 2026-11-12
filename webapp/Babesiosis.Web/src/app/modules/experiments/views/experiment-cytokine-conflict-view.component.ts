import { NgTemplateOutlet } from '@angular/common';
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

// ---- Payloads written by /experiments/SV-04/scripts/build_load.py ---------------------------

/** One effect (Cliff's delta) of group a minus group b, with its interval. */
interface EffectRow {
  label: string;
  estimate: number | null;
  ci_low: number | null;
  ci_high: number | null;
  p: number | null;
  q: number | null;
  n_a: number;
  n_b: number;
  a_label: string;
  b_label: string;
  median_a?: number | null;
  median_b?: number | null;
  mean_a?: number | null;
  mean_b?: number | null;
  hl_log2?: number | null;
  hl_low?: number | null;
  hl_high?: number | null;
  definition?: string;
}

/** `primary_result`: the headline effects (one row per file or test), the verdict and the sources. */
interface CytokinePrimaryPayload {
  label: string;
  statistic: string;
  verdict: string;
  headline: string;
  independent_sources: number;
  sources: string[];
  rows: EffectRow[];
  caveats: string[];
  ds02?: { r1: boolean; r2: boolean; r3: boolean; all: boolean; text: string };
}

/** `severity_contrasts`, `infected_vs_control`, `score_sensitivity`: groups of effects for a forest plot. */
interface EffectGroupsPayload {
  statistic: string;
  groups: { key: string; label: string; note: string; rows: EffectRow[] }[];
  footnote: string;
}

interface Ds02Dog {
  dog: string;
  dose_group: string;
  points: { day: number; value: number; log2: number }[];
}

/** `ds02_courses`: the Beagle series per analyte, with the decision rules. */
interface Ds02CoursesPayload {
  analytes: {
    analyte: string;
    label: string;
    dogs: Ds02Dog[];
    decision: Ds02Decision;
    changes: { dog: string; change: number }[];
  }[];
  treatment_after_day: number;
  footnote: string;
}

interface Ds02Decision {
  n_dogs: number;
  R1_same_direction: boolean;
  median_abs_post: number;
  median_abs_daily_pre: number;
  R2_exceeds_daily: boolean;
  mean_change_high: number | null;
  mean_change_low: number | null;
  R3_high_more_upward: boolean;
  all_rules: boolean;
}

/** `ds02_decisions`: one row per analyte. */
interface Ds02DecisionsPayload {
  rows: (Ds02Decision & { analyte: string })[];
}

/** `definition_check`: IL-8 against WBC and WBC by label (check C1). */
interface DefinitionCheckPayload {
  rows: {
    file: string; species: string; rho: number; rho_low: number; rho_high: number; rho_p: number; n: number;
    wbc_delta: number; wbc_low: number; wbc_high: number; wbc_p: number;
    wbc_median_severe: number; wbc_median_nonsevere: number; severe: string; nonsevere: string;
  }[];
  footnote: string;
}

/** `floor_sensitivity`: the contrasts with floors at half the floor. */
interface FloorSensitivityPayload {
  rows: { file: string; analyte: string; delta: number; delta_primary: number; hl_log2: number | null; hl_primary: number | null; q: number }[];
  footnote: string;
}

/** `perturbation_distribution`: count of analytes outside the control range, by severity. */
interface PerturbationPayload {
  files: {
    file: string; species: string; severe: string; nonsevere: string;
    counts_severe: number[]; counts_nonsevere: number[];
    outside_severe: Record<string, number>; outside_nonsevere: Record<string, number>;
  }[];
  footnote: string;
}

/** `balance_points`: one point per infected dog. */
interface BalancePayload {
  files: { file: string; species: string; severe: string; nonsevere: string; points: { perturbation: number; balance: number; severe: number }[] }[];
  footnote: string;
}

/** Result kinds this view renders (the page hides them from its raw-JSON list). */
export const CYTOKINE_CONFLICT_RESULT_KINDS = ['interpretation', 'primary_result', 'severity_contrasts', 'ds02_courses', 'ds02_decisions',
  'infected_vs_control', 'definition_check', 'floor_sensitivity', 'perturbation_distribution', 'balance_points', 'score_sensitivity'];

const ANALYTE_LABEL: Record<string, string> = { il2: 'IL-2', il8: 'IL-8', il10: 'IL-10', il18: 'IL-18', gmcsf: 'GM-CSF', mcp1: 'MCP-1' };

function signed(v: number | null | undefined, digits = 2): string {
  return v === null || v === undefined ? '–' : `${v >= 0 ? '+' : ''}${v.toFixed(digits)}`;
}

function num(v: number | null | undefined, digits = 1): string {
  return v === null || v === undefined ? '–' : v.toFixed(digits);
}

function pText(p: number | null | undefined): string {
  return p === null || p === undefined ? '–' : p < 0.001 ? '< 0.001' : p.toFixed(3);
}

/** A row of the forest plot, in SVG coordinates. */
interface ForestRow {
  id: string;
  label: string;
  y: number;
  x: number;
  x1: number;
  x2: number;
  excludesZero: boolean;
  estimate: string;
  interval: string;
  n: string;
  medians: string;
  p: string;
  q: string;
  hl: string;
}

interface ForestGroup {
  key: string;
  label: string;
  note: string;
  height: number;
  rows: ForestRow[];
}

const FOREST = { left: 0, right: 420, rowHeight: 26, top: 22 };

function forestX(v: number): number {
  const clamped = Math.max(-1, Math.min(1, v));
  return FOREST.left + (clamped + 1) / 2 * (FOREST.right - FOREST.left);
}

function toForest(payload: EffectGroupsPayload | null): ForestGroup[] {
  return (payload?.groups ?? []).map(g => ({
    key: g.key,
    label: g.label,
    note: g.note,
    height: FOREST.top + g.rows.length * FOREST.rowHeight + 8,
    rows: g.rows.map((r, i) => ({
      id: `${g.key}-${i}`,
      label: r.label,
      y: FOREST.top + i * FOREST.rowHeight + FOREST.rowHeight / 2,
      x: forestX(r.estimate ?? 0),
      x1: forestX(r.ci_low ?? 0),
      x2: forestX(r.ci_high ?? 0),
      excludesZero: (r.ci_low ?? 0) > 0 || (r.ci_high ?? 0) < 0,
      estimate: signed(r.estimate),
      interval: `${signed(r.ci_low)} to ${signed(r.ci_high)}`,
      n: `${r.n_a} vs ${r.n_b}`,
      medians: r.median_a !== undefined && r.median_a !== null ? `${num(r.median_a)} vs ${num(r.median_b)}` : '–',
      p: pText(r.p),
      q: r.q === null || r.q === undefined ? '–' : pText(r.q),
      hl: r.hl_log2 !== undefined && r.hl_log2 !== null ? `${signed(r.hl_log2)} (${signed(r.hl_low)} to ${signed(r.hl_high)})` : '–',
    })),
  }));
}

/**
 * The cytokine-conflict view (SV-04): the IL-8 contrast inside each file with its interval, forest
 * plots of the six shared analytes, the Beagle courses around treatment with the decision rules,
 * and (for the size-and-balance experiment) the perturbation count and balance index. The
 * explanation note is rendered by the page after this.
 */
@Component({
  selector: 'fs-experiment-cytokine-conflict-view',
  standalone: true,
  imports: [NgTemplateOutlet, FsBadgeComponent, FsCardComponent, FsChartComponent, FsDataGridComponent],
  templateUrl: './experiment-cytokine-conflict-view.component.html',
  styleUrls: ['./experiment-cytokine-conflict-view.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExperimentCytokineConflictViewComponent implements OnInit {
  private readonly destroyRef = inject(DestroyRef);

  readonly detail = input.required<ExperimentDetailViewModel>();

  /** Bumped when the theme flips, so chart colours re-read their tokens. */
  private readonly themeChanges = signal(0);

  protected readonly forestWidth = FOREST.right;
  protected readonly forestTicks = [-1, -0.5, 0, 0.5, 1].map(v => ({ v, x: forestX(v), label: v === 0 ? '0' : signed(v, 1) }));

  private find<T>(kind: string): T | null {
    return parsePayload<T>(this.detail().results.find(r => r.kind === kind));
  }

  protected readonly primary = computed(() => this.find<CytokinePrimaryPayload>('primary_result'));
  protected readonly contrasts = computed(() => toForest(this.find<EffectGroupsPayload>('severity_contrasts')));
  protected readonly contrastsPayload = computed(() => this.find<EffectGroupsPayload>('severity_contrasts'));
  protected readonly infected = computed(() => toForest(this.find<EffectGroupsPayload>('infected_vs_control')));
  protected readonly infectedPayload = computed(() => this.find<EffectGroupsPayload>('infected_vs_control'));
  protected readonly scoreSens = computed(() => toForest(this.find<EffectGroupsPayload>('score_sensitivity')));
  protected readonly scoreSensPayload = computed(() => this.find<EffectGroupsPayload>('score_sensitivity'));
  protected readonly ds02 = computed(() => this.find<Ds02CoursesPayload>('ds02_courses'));
  protected readonly ds02Decisions = computed(() => this.find<Ds02DecisionsPayload>('ds02_decisions'));
  protected readonly definition = computed(() => this.find<DefinitionCheckPayload>('definition_check'));
  protected readonly floors = computed(() => this.find<FloorSensitivityPayload>('floor_sensitivity'));
  protected readonly perturbation = computed(() => this.find<PerturbationPayload>('perturbation_distribution'));
  protected readonly balance = computed(() => this.find<BalancePayload>('balance_points'));

  protected readonly verdictIntent = computed(() => {
    const v = this.primary()?.verdict ?? '';
    return v === 'conflict confirmed' ? 'danger' as const : v === 'no conflict' || v === 'neither' ? 'info' as const : 'warning' as const;
  });

  protected readonly primaryRows = computed(() => (this.primary()?.rows ?? []).map(r => ({
    label: r.label,
    estimate: signed(r.estimate),
    interval: `${signed(r.ci_low)} to ${signed(r.ci_high)}`,
    n: `${r.n_a} ${r.a_label} vs ${r.n_b} ${r.b_label}`,
    centre: r.median_a !== undefined && r.median_a !== null
      ? `medians ${num(r.median_a, 0)} vs ${num(r.median_b, 0)} pg/mL`
      : r.mean_a !== undefined && r.mean_a !== null ? `means ${num(r.mean_a, 2)} vs ${num(r.mean_b, 2)}` : '',
    p: pText(r.p),
    q: r.q === null || r.q === undefined ? '–' : pText(r.q),
    definition: r.definition ?? '',
    excludesZero: (r.ci_low ?? 0) > 0 || (r.ci_high ?? 0) < 0,
  })));

  protected readonly forestColumns: FsGridColumn<ForestRow>[] = [
    { dataField: 'label', caption: 'Analyte or score', minWidth: 200 },
    { dataField: 'estimate', caption: "Cliff's delta", width: 110, alignment: 'right' },
    { dataField: 'interval', caption: '95% CI', width: 140, alignment: 'right' },
    { dataField: 'n', caption: 'n', width: 90, alignment: 'right' },
    { dataField: 'medians', caption: 'Medians', width: 150, alignment: 'right' },
    { dataField: 'hl', caption: 'HL log2 shift (95% CI)', width: 200, alignment: 'right' },
    { dataField: 'p', caption: 'p', width: 80, alignment: 'right' },
    { dataField: 'q', caption: 'BH q', width: 80, alignment: 'right' },
  ];

  // ---- DS02 courses ----------------------------------------------------------------------

  protected readonly selectedAnalyte = signal('il8');
  protected readonly ds02Analytes = computed(() => (this.ds02()?.analytes ?? []).map(a => ({ key: a.analyte, label: a.label })));
  protected readonly ds02Selected = computed(() => this.ds02()?.analytes.find(a => a.analyte === this.selectedAnalyte()) ?? null);

  protected readonly ds02Options = computed<FsChartOptions>(() => {
    this.themeChanges();
    const d = this.ds02();
    const a = this.ds02Selected();
    if (!d || !a) {
      return {};
    }
    const soft = fsChartCssColor('--fs-color-ink-soft', '#6b6862');
    const high = ['--fs-color-chart-5', '--fs-color-chart-4', '--fs-color-chart-6'];
    const low = ['--fs-color-chart-3', '--fs-color-chart-2'];
    let hi = 0;
    let lo = 0;
    const colors = a.dogs.map(dog => dog.dose_group === 'high'
      ? fsChartCssColor(high[hi++ % high.length], '#c6483a')
      : fsChartCssColor(low[lo++ % low.length], '#4b6bd6'));
    const raw = (v: number) => {
      const x = Math.pow(2, v) - 1;
      return x >= 10 ? x.toFixed(0) : x.toFixed(1);
    };
    return {
      chart: { type: 'line', toolbar: { show: false }, animations: { enabled: false }, zoom: { enabled: false } },
      series: a.dogs.map(dog => ({
        name: `${dog.dog} (${dog.dose_group} dose)`,
        data: dog.points.map(p => ({ x: p.day, y: p.log2 })),
      })),
      colors,
      stroke: { width: 2, curve: 'straight' },
      markers: { size: 4, strokeWidth: 0 },
      dataLabels: { enabled: false },
      xaxis: {
        type: 'numeric', min: -1, max: 8, tickAmount: 9,
        title: { text: 'Day after inoculation', style: { color: soft } },
        labels: { formatter: (v: string) => Number(v).toFixed(0) },
      },
      yaxis: {
        title: { text: `${a.label} (pg/mL, log scale)`, style: { color: soft } },
        labels: { formatter: raw },
        tickAmount: 6,
      },
      annotations: {
        xaxis: [{
          x: d.treatment_after_day + 0.5,
          borderColor: soft,
          strokeDashArray: 4,
          label: { text: 'Treatment (after the day-4 sample)', orientation: 'horizontal', style: { color: soft, background: 'transparent' } },
        }],
      },
      legend: { position: 'bottom' },
      tooltip: { shared: false, intersect: true, y: { formatter: (v: number) => `${raw(v)} pg/mL` } },
    };
  });

  protected readonly ds02DecisionRows = computed(() => (this.ds02Decisions()?.rows ?? []).map(r => ({
    analyte: r.analyte,
    r1: r.R1_same_direction ? 'Yes' : 'No',
    r2: `${r.median_abs_post.toFixed(2)} vs ${r.median_abs_daily_pre.toFixed(2)} · ${r.R2_exceeds_daily ? 'Yes' : 'No'}`,
    r3: `${signed(r.mean_change_high)} vs ${signed(r.mean_change_low)} · ${r.R3_high_more_upward ? 'Yes' : 'No'}`,
    all: r.all_rules ? 'All met' : 'Not met',
    n: r.n_dogs,
  })));
  protected readonly ds02DecisionColumns: FsGridColumn<Record<string, string | number>>[] = [
    { dataField: 'analyte', caption: 'Analyte', width: 100 },
    { dataField: 'r1', caption: 'R1 same direction', width: 140 },
    { dataField: 'r2', caption: 'R2 median |Δ| post vs daily (log2)', minWidth: 230 },
    { dataField: 'r3', caption: 'R3 mean Δ high vs low dose', minWidth: 210 },
    { dataField: 'all', caption: 'Rules', width: 100 },
    { dataField: 'n', caption: 'Dogs', width: 70, alignment: 'right' },
  ];

  protected readonly definitionRows = computed(() => (this.definition()?.rows ?? []).map(r => ({
    file: `${r.file} (${r.species})`,
    rho: `${signed(r.rho)} (${signed(r.rho_low)} to ${signed(r.rho_high)})`,
    rhoP: pText(r.rho_p),
    n: r.n,
    wbc: `${signed(r.wbc_delta)} (${signed(r.wbc_low)} to ${signed(r.wbc_high)})`,
    wbcMedians: `${num(r.wbc_median_severe, 1)} ${r.severe} vs ${num(r.wbc_median_nonsevere, 1)} ${r.nonsevere}`,
    wbcP: pText(r.wbc_p),
  })));
  protected readonly definitionColumns: FsGridColumn<Record<string, string | number>>[] = [
    { dataField: 'file', caption: 'File', width: 170 },
    { dataField: 'rho', caption: 'IL-8 with WBC, rho (95% CI)', width: 210, alignment: 'right' },
    { dataField: 'rhoP', caption: 'p', width: 80, alignment: 'right' },
    { dataField: 'n', caption: 'Dogs', width: 70, alignment: 'right' },
    { dataField: 'wbc', caption: "WBC by label, Cliff's delta (95% CI)", width: 250, alignment: 'right' },
    { dataField: 'wbcMedians', caption: 'WBC medians (10^9/L)', minWidth: 230 },
    { dataField: 'wbcP', caption: 'p', width: 80, alignment: 'right' },
  ];

  protected readonly floorRows = computed(() => (this.floors()?.rows ?? []).map((r, i) => ({
    id: i,
    file: r.file,
    analyte: r.analyte,
    delta: `${signed(r.delta)} (primary ${signed(r.delta_primary)})`,
    hl: `${signed(r.hl_log2)} (primary ${signed(r.hl_primary)})`,
    q: pText(r.q),
  })));
  protected readonly floorColumns: FsGridColumn<Record<string, string | number>>[] = [
    { dataField: 'file', caption: 'File', width: 110 },
    { dataField: 'analyte', caption: 'Analyte', width: 100 },
    { dataField: 'delta', caption: "Cliff's delta, half floor", width: 220, alignment: 'right' },
    { dataField: 'hl', caption: 'HL log2 shift, half floor', width: 220, alignment: 'right' },
    { dataField: 'q', caption: 'BH q', width: 80, alignment: 'right' },
  ];

  // ---- Experiment 2 charts ----------------------------------------------------------------

  protected readonly perturbationCharts = computed(() => {
    this.themeChanges();
    const soft = fsChartCssColor('--fs-color-ink-soft', '#6b6862');
    return (this.perturbation()?.files ?? []).map(f => {
      const ns = f.counts_severe.reduce((a, b) => a + b, 0);
      const nn = f.counts_nonsevere.reduce((a, b) => a + b, 0);
      const share = (c: number, n: number) => (n ? Math.round(1000 * c / n) / 10 : 0);
      const options: FsChartOptions = {
        chart: { type: 'bar', toolbar: { show: false }, animations: { enabled: false } },
        series: [
          { name: `${f.severe} (n ${ns})`, data: f.counts_severe.map(c => share(c, ns)) },
          { name: `${f.nonsevere} (n ${nn})`, data: f.counts_nonsevere.map(c => share(c, nn)) },
        ],
        colors: [fsChartCssColor('--fs-color-chart-5', '#ff4c51'), fsChartCssColor('--fs-color-chart-3', '#00bad1')],
        plotOptions: { bar: { columnWidth: '70%' } },
        dataLabels: { enabled: false },
        xaxis: { categories: ['0', '1', '2', '3', '4', '5', '6'], title: { text: 'Analytes outside the control range (of 6)', style: { color: soft } } },
        yaxis: { title: { text: '% of dogs', style: { color: soft } }, labels: { formatter: (v: number) => `${Math.round(v)}%` } },
        legend: { position: 'bottom' },
        tooltip: { y: { formatter: (v: number) => `${v}%` } },
      };
      const outside = Object.keys(ANALYTE_LABEL).map(k => ({
        analyte: ANALYTE_LABEL[k],
        severe: `${f.outside_severe[k] ?? 0} of ${ns}`,
        nonsevere: `${f.outside_nonsevere[k] ?? 0} of ${nn}`,
      }));
      const columns: FsGridColumn<Record<string, string>>[] = [
        { dataField: 'analyte', caption: 'Analyte', width: 100 },
        { dataField: 'severe', caption: `Outside, ${f.severe}`, minWidth: 130, alignment: 'right' },
        { dataField: 'nonsevere', caption: `Outside, ${f.nonsevere}`, minWidth: 130, alignment: 'right' },
      ];
      return { file: f.file, title: `${f.file} · ${f.species}`, options, outside, columns };
    });
  });
  protected readonly balanceCharts = computed(() => {
    this.themeChanges();
    const soft = fsChartCssColor('--fs-color-ink-soft', '#6b6862');
    return (this.balance()?.files ?? []).map(f => {
      // A small fixed horizontal offset per dog, so dogs with the same count do not hide each other.
      const jitter = (i: number) => ((i * 37) % 11 - 5) * 0.04;
      const sev = f.points.filter(p => p.severe === 1);
      const non = f.points.filter(p => p.severe === 0);
      const options: FsChartOptions = {
        chart: { type: 'scatter', toolbar: { show: false }, animations: { enabled: false }, zoom: { enabled: false } },
        series: [
          { name: `${f.severe} (n ${sev.length})`, data: sev.map((p, i) => ({ x: p.perturbation + jitter(i), y: Math.round(p.balance * 10) / 10 })) },
          { name: `${f.nonsevere} (n ${non.length})`, data: non.map((p, i) => ({ x: p.perturbation + jitter(i + 3), y: Math.round(p.balance * 10) / 10 })) },
        ],
        colors: [fsChartCssColor('--fs-color-chart-5', '#ff4c51'), fsChartCssColor('--fs-color-chart-3', '#00bad1')],
        markers: { size: 5, strokeWidth: 0 },
        dataLabels: { enabled: false },
        xaxis: {
          type: 'numeric', min: -0.5, max: 6.5, tickAmount: 7,
          title: { text: 'Perturbation count (analytes outside the control range)', style: { color: soft } },
          labels: { formatter: (v: string) => Number(v).toFixed(0) },
        },
        yaxis: { min: -100, max: 100, tickAmount: 4, title: { text: 'Balance: MCP-1 minus IL-8 percentile', style: { color: soft } } },
        legend: { position: 'bottom' },
        tooltip: { x: { formatter: (v: number) => `count ${Math.round(v)}` } },
      };
      return { file: f.file, title: `${f.file} · ${f.species}`, options };
    });
  });

  ngOnInit(): void {
    this.destroyRef.onDestroy(fsObserveTheme(() => this.themeChanges.update(n => n + 1)));
  }

  protected selectAnalyte(key: string): void {
    this.selectedAnalyte.set(key);
  }
}
