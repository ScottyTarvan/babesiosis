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

// ---- Payloads written by /experiments/SV-02/b/scripts/build_load.py ---------------------------

interface ReadingRow {
  measure: string;
  label: string;
  unit: string;
  reading: string;
  same_sign: boolean;
  low_inside_high_1pct: boolean | null;
  low_inside_high_5pct: boolean | null;
  separate_1pct: boolean | null;
  separate_5pct: boolean | null;
  residual_outlier_dog: string | null;
  n_low_5pct: number;
  n_high_5pct: number;
  margin: number;
  low_at_1pct: string;
  high_at_1pct: string;
  low_at_5pct: string;
  high_at_5pct: string;
}

/** `primary_result`: the reading of each health measure, with n and sources. */
interface ReactionNormPrimaryPayload {
  label: string;
  headline: string;
  status: string;
  verdict: string;
  n_dogs: number;
  n_low: number;
  n_high: number;
  n_points: number;
  independent_sources: number;
  sources: string[];
  readings: ReadingRow[];
}

interface ChartPoint {
  x: number;
  y: number;
  timepoint: string;
  parasitaemia_pct: number;
}

interface ChartDog {
  dog: string;
  dose_group: string;
  died: number | null;
  points: ChartPoint[];
  fit: { x: number; y: number }[];
}

interface ReactionNormChart {
  measure: string;
  label: string;
  unit: string;
  offset: number;
  dogs: ChartDog[];
  pooled: { x: number; y: number }[];
  pooled_slope: number | null;
  matched_loads_pct: number[];
  footnote: string;
}

/** `reaction_norms`: one chart per health measure. */
interface ReactionNormChartsPayload {
  charts: ReactionNormChart[];
}

interface DogSlopeRow {
  dog: string;
  original_id: string | null;
  dose_group: string;
  died: number | null;
  measure: string;
  measure_label: string;
  unit: string;
  n_points: number;
  slope: number | null;
  ci_low: number | null;
  ci_high: number | null;
  theil_sen: number | null;
  damage_at_1pct: number | null;
  damage_at_5pct: number | null;
  peak_parasitaemia_pct: number | null;
  peak_timepoint: string | null;
  damage_at_peak: number | null;
  mean_residual: number | null;
}

/** `dog_slopes`: per dog and measure. */
interface DogSlopesPayload {
  rows: DogSlopeRow[];
}

interface SensitivityRow {
  check: string;
  measure: string;
  measure_label: string;
  reading: string;
  primary_reading: string;
  n_dogs: number;
  slope_min: number | null;
  slope_max: number | null;
  n_negative_slopes: number;
}

/** `sensitivity`: the reading under each check. */
interface SensitivityPayload {
  rows: SensitivityRow[];
}

/** Result kinds this view renders (the page hides them from its raw-JSON list). */
export const REACTION_NORM_RESULT_KINDS = ['interpretation', 'primary_result', 'reaction_norms', 'dog_slopes', 'sensitivity'];

function num(v: number | null | undefined, digits = 2): string {
  return v === null || v === undefined ? '–' : v.toFixed(digits);
}

function signed(v: number | null | undefined, digits = 3): string {
  return v === null || v === undefined ? '–' : `${v >= 0 ? '+' : ''}${v.toFixed(digits)}`;
}

function yesNo(v: boolean | null | undefined): string {
  return v === null || v === undefined ? '–' : v ? 'yes' : 'no';
}

const DIGITS: Record<string, number> = { hct_drop: 3, lactate: 2, habitus_loss: 2 };
const LOW_TOKENS = [['--fs-color-chart-2', '#2f9e8f'], ['--fs-color-chart-5', '#5aa36b']];
const HIGH_TOKENS = [['--fs-color-chart-1', '#4b6bd6'], ['--fs-color-chart-3', '#c98a2b'], ['--fs-color-chart-4', '#c6483a']];

type GridRow = Record<string, string | number>;

/**
 * The reaction-norm view (SV-02b): the reading of each health measure (one shared norm,
 * different norms, cannot tell), one chart per measure of damage against log parasitaemia
 * for each Beagle, and the tables behind it. The explanation note is rendered by the page after this.
 */
@Component({
  selector: 'fs-experiment-reaction-norm-view',
  standalone: true,
  imports: [FsBadgeComponent, FsCardComponent, FsChartComponent, FsDataGridComponent],
  templateUrl: './experiment-reaction-norm-view.component.html',
  styleUrls: ['./experiment-reaction-norm-view.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExperimentReactionNormViewComponent implements OnInit {
  private readonly destroyRef = inject(DestroyRef);

  readonly detail = input.required<ExperimentDetailViewModel>();

  private readonly themeChanges = signal(0);

  private find<T>(kind: string): T | null {
    return parsePayload<T>(this.detail().results.find(r => r.kind === kind));
  }

  protected readonly primary = computed(() => this.find<ReactionNormPrimaryPayload>('primary_result'));
  protected readonly charts = computed(() => this.find<ReactionNormChartsPayload>('reaction_norms'));
  protected readonly slopes = computed(() => this.find<DogSlopesPayload>('dog_slopes'));
  protected readonly sensitivity = computed(() => this.find<SensitivityPayload>('sensitivity'));

  protected intent(reading: string): 'success' | 'danger' | 'warning' {
    return reading === 'one shared norm' ? 'success' : reading === 'different norms' ? 'danger' : 'warning';
  }

  protected readonly readingRows = computed<GridRow[]>(() => (this.primary()?.readings ?? []).map(r => ({
    measure: `${r.label} (${r.unit})`,
    reading: r.reading,
    low5: r.low_at_5pct,
    high5: r.high_at_5pct,
    low1: r.low_at_1pct,
    high1: r.high_at_1pct,
    sign: yesNo(r.same_sign),
    inside: yesNo(r.low_inside_high_5pct),
    separate: `${yesNo(r.separate_1pct)} / ${yesNo(r.separate_5pct)}`,
    outlier: r.residual_outlier_dog ?? 'none',
    margin: r.margin,
  })));
  protected readonly readingColumns: FsGridColumn<GridRow>[] = [
    { dataField: 'measure', caption: 'Health measure', minWidth: 220 },
    { dataField: 'reading', caption: 'Reading', width: 140 },
    { dataField: 'low5', caption: 'Low dose at 5%', width: 120, alignment: 'right' },
    { dataField: 'high5', caption: 'High dose at 5%', width: 130, alignment: 'right' },
    { dataField: 'low1', caption: 'Low dose at 1%', width: 120, alignment: 'right' },
    { dataField: 'high1', caption: 'High dose at 1%', width: 130, alignment: 'right' },
    { dataField: 'sign', caption: 'Slopes share a sign', width: 140 },
    { dataField: 'inside', caption: 'Low inside high at 5%', width: 160 },
    { dataField: 'separate', caption: 'Separated 1% / 5%', width: 140 },
    { dataField: 'outlier', caption: 'Residual outlier', width: 130 },
    { dataField: 'margin', caption: 'Margin', width: 80, alignment: 'right' },
  ];

  protected readonly slopeRows = computed<GridRow[]>(() => (this.slopes()?.rows ?? []).map((r, i) => {
    const d = DIGITS[r.measure] ?? 2;
    return {
      id: i,
      dog: `${r.dog}${r.died ? ' · died day 4' : ''}`,
      dose: r.dose_group,
      measure: `${r.measure_label} (${r.unit})`,
      n: r.n_points,
      slope: signed(r.slope),
      interval: r.ci_low === null ? '–' : `${signed(r.ci_low)} to ${signed(r.ci_high)}`,
      theil: signed(r.theil_sen),
      at1: num(r.damage_at_1pct, d),
      at5: num(r.damage_at_5pct, d),
      peak: r.peak_parasitaemia_pct === null ? '–' : `${num(r.peak_parasitaemia_pct, r.peak_parasitaemia_pct < 10 ? 2 : 1)}% (${r.peak_timepoint})`,
      atPeak: num(r.damage_at_peak, d),
      resid: signed(r.mean_residual, d),
    };
  }));
  protected readonly slopeColumns: FsGridColumn<GridRow>[] = [
    { dataField: 'dog', caption: 'Dog', width: 190 },
    { dataField: 'dose', caption: 'Dose', width: 70 },
    { dataField: 'measure', caption: 'Measure', minWidth: 220 },
    { dataField: 'n', caption: 'Points', width: 70, alignment: 'right' },
    { dataField: 'slope', caption: 'OLS slope per log10', width: 140, alignment: 'right' },
    { dataField: 'interval', caption: '95% CI', width: 170, alignment: 'right' },
    { dataField: 'theil', caption: 'Theil-Sen', width: 100, alignment: 'right' },
    { dataField: 'at1', caption: 'At 1%', width: 80, alignment: 'right' },
    { dataField: 'at5', caption: 'At 5%', width: 80, alignment: 'right' },
    { dataField: 'peak', caption: 'Peak load', width: 140, alignment: 'right' },
    { dataField: 'atPeak', caption: 'At peak', width: 80, alignment: 'right' },
    { dataField: 'resid', caption: 'Mean residual', width: 110, alignment: 'right' },
  ];

  protected readonly sensitivityRows = computed<GridRow[]>(() => (this.sensitivity()?.rows ?? []).map((r, i) => ({
    id: i,
    check: r.check.replace(/_/g, ' '),
    measure: r.measure_label,
    reading: r.reading,
    same: r.reading === r.primary_reading ? 'same' : `changed (primary: ${r.primary_reading})`,
    slopes: `${signed(r.slope_min)} to ${signed(r.slope_max)}`,
    negative: `${r.n_negative_slopes} of ${r.n_dogs}`,
  })));
  protected readonly sensitivityColumns: FsGridColumn<GridRow>[] = [
    { dataField: 'check', caption: 'Check', width: 190 },
    { dataField: 'measure', caption: 'Measure', minWidth: 200 },
    { dataField: 'reading', caption: 'Reading', width: 140 },
    { dataField: 'same', caption: 'Against primary', width: 230 },
    { dataField: 'slopes', caption: 'Slope range', width: 170, alignment: 'right' },
    { dataField: 'negative', caption: 'Negative slopes', width: 120, alignment: 'right' },
  ];

  protected readonly chartOptions = computed(() => (this.charts()?.charts ?? []).map(c => ({ chart: c, options: this.options(c) })));

  ngOnInit(): void {
    this.destroyRef.onDestroy(fsObserveTheme(() => this.themeChanges.update(n => n + 1)));
  }

  private options(c: ReactionNormChart): FsChartOptions {
    this.themeChanges();
    const soft = fsChartCssColor('--fs-color-ink-soft', '#6b6862');
    const ink = fsChartCssColor('--fs-color-ink', '#2b2a27');
    type Series = { name: string; type: string; data: { x: number; y: number; meta?: string }[] };
    const series: Series[] = [];
    const colors: string[] = [];
    const widths: number[] = [];
    const dashes: number[] = [];
    const markers: number[] = [];
    let li = 0;
    let hi = 0;
    const d = DIGITS[c.measure] ?? 2;
    c.dogs.forEach(dog => {
      const tok = dog.dose_group === 'low' ? LOW_TOKENS[li++ % LOW_TOKENS.length] : HIGH_TOKENS[hi++ % HIGH_TOKENS.length];
      const colour = fsChartCssColor(tok[0], tok[1]);
      const name = `${dog.dog} · ${dog.dose_group} dose${dog.died ? ' · died' : ''}`;
      series.push({ name, type: 'scatter', data: dog.points.map(p => ({ x: p.x, y: p.y, meta: `${p.timepoint} · parasitaemia ${p.parasitaemia_pct}%` })) });
      colors.push(colour); widths.push(0); dashes.push(0); markers.push(dog.died ? 8 : 6);
      if (dog.fit.length) {
        series.push({ name: `${dog.dog} fit`, type: 'line', data: dog.fit });
        colors.push(colour); widths.push(2); dashes.push(0); markers.push(0);
      }
    });
    if (c.pooled.length) {
      series.push({ name: 'Pooled fit (ignores repeated measures)', type: 'line', data: c.pooled });
      colors.push(ink); widths.push(2); dashes.push(6); markers.push(0);
    }
    const offset = c.offset;
    const xLabel = (v: number) => {
      const raw = Math.pow(10, v) - offset;
      return raw < 0.005 ? '0' : raw >= 10 ? raw.toFixed(0) : raw >= 1 ? raw.toFixed(1) : raw.toFixed(2);
    };
    const annotations = c.matched_loads_pct.map(t => ({
      x: Math.log10(t + offset),
      borderColor: soft,
      strokeDashArray: 3,
      label: { text: `${t}%`, style: { color: soft, background: 'transparent' }, borderWidth: 0 },
    }));
    return {
      chart: { type: 'line', toolbar: { show: false }, animations: { enabled: false }, zoom: { enabled: false } },
      series,
      colors,
      stroke: { width: widths, dashArray: dashes, curve: 'straight' },
      markers: { size: markers, strokeWidth: 0, hover: { sizeOffset: 2 } },
      fill: { type: 'solid', opacity: 1 },
      dataLabels: { enabled: false },
      annotations: { xaxis: annotations },
      xaxis: {
        type: 'numeric', min: -2.1, max: 2, tickAmount: 8,
        title: { text: 'Parasitaemia, % (log scale)', style: { color: soft } },
        labels: { formatter: (v: string) => xLabel(Number(v)) },
      },
      yaxis: {
        title: { text: `${c.label} (${c.unit})`, style: { color: soft } },
        labels: { formatter: (v: number) => num(v, d) },
        tickAmount: 6,
      },
      legend: { position: 'bottom', horizontalAlign: 'left' },
      tooltip: {
        shared: false, intersect: true,
        custom: ({ seriesIndex, dataPointIndex }: { seriesIndex: number; dataPointIndex: number }) => {
          const s = series[seriesIndex];
          const p = s?.data[dataPointIndex];
          if (!p) {
            return '';
          }
          return `<div class="fs-experiment-reaction-norm__tip"><strong>${s.name}</strong><br>`
            + `${c.label} ${num(p.y, d)} ${c.unit}${p.meta ? `<br>${p.meta}` : ''}</div>`;
        },
      },
    };
  }
}
