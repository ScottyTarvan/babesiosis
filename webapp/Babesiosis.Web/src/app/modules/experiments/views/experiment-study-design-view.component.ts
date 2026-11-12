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

/** The result kinds that this view draws (SV-10, method `study_design`). */
export const STUDY_DESIGN_RESULT_KINDS: readonly string[] = ['primary_result', 'sample_size', 'memo_sections'];

interface Recommendation {
  design: string;
  scenario: string;
  n_total: number;
  n_cases: number | null;
  n_controls: number | null;
  cohort_needed: number | null;
  detects: string;
  basis: string;
}

interface Assumption {
  label: string;
  value: string;
  source: string;
}

interface GapRow {
  package: string;
  gap: string;
  answer: string;
}

interface PrimaryPayload {
  memo_title: string;
  question: string;
  recommendation: Recommendation;
  assumptions: Assumption[];
  gaps: GapRow[];
  caveat: string;
}

interface PowerRow {
  scenario: string;
  design: string;
  exposure_freq_controls: number | null;
  exposure_freq_cases: number | null;
  odds_ratio: number | null;
  alpha: number;
  power: number;
  r2_covariates: number | null;
  controls_per_case: number | null;
  n_cases: number;
  n_controls: number;
  n_total: number;
  cohort_needed: number | null;
  cohort_basis: string | null;
  note: string;
  recommended?: boolean;
}

interface SampleSizePayload {
  rows: PowerRow[];
  calibration: { cohort_framing_detectable_or: number; sv05_reported: string; case_control_framing_detectable_or_above: number };
  death_proportion: number;
  severe_proportion: number;
  complicated_proportion: number;
}

type MemoBlock =
  | { type: 'p'; text: string }
  | { type: 'h3'; text: string }
  | { type: 'ul'; items: string[] }
  | { type: 'table'; header: string[]; rows: string[][] };

interface MemoPayload {
  title: string;
  file: string;
  words: number;
  sections: { heading: string; blocks: MemoBlock[] }[];
}

/**
 * The study-design view (SV-10): one design memo per experiment. The recommended design and its sample size first, then the
 * gaps of the finished packages that it answers, the sample-size scenarios (chart and table), and the memo itself.
 * No data are analysed: every number is a planning assumption or a power calculation.
 */
@Component({
  selector: 'fs-experiment-study-design-view',
  standalone: true,
  imports: [FsBadgeComponent, FsCardComponent, FsChartComponent, FsDataGridComponent],
  templateUrl: './experiment-study-design-view.component.html',
  styleUrls: ['./experiment-study-design-view.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExperimentStudyDesignViewComponent implements OnInit {
  private readonly destroyRef = inject(DestroyRef);

  readonly detail = input.required<ExperimentDetailViewModel>();

  private readonly themeChanges = signal(0);

  private payload<T>(kind: string) {
    return computed(() => parsePayload<T>(this.detail().results.find(r => r.kind === kind)));
  }

  protected readonly primary = this.payload<PrimaryPayload>('primary_result');
  protected readonly sizes = this.payload<SampleSizePayload>('sample_size');
  protected readonly memo = this.payload<MemoPayload>('memo_sections');


  protected readonly gapRows = computed(() => (this.primary()?.gaps ?? []).map((g, i) => ({ ...g, id: i })));

  protected readonly sizeRows = computed(() => (this.sizes()?.rows ?? []).map((r, i) => ({
    ...r,
    id: i,
    orText: r.odds_ratio === null ? '–' : String(r.odds_ratio),
    alphaText: r.alpha < 0.001 ? r.alpha.toExponential(1) : String(r.alpha),
    freqText: r.exposure_freq_controls === null ? '–'
      : `${r.exposure_freq_controls}${r.exposure_freq_cases === null ? '' : ` → ${r.exposure_freq_cases}`}`,
    cohortText: this.cohortText(r),
    recText: r.recommended ? 'recommended' : '',
  })));

  protected readonly sizeColumns: FsGridColumn<Record<string, unknown>>[] = [
    { dataField: 'recText', caption: '', width: 110 },
    { dataField: 'design', caption: 'Design', minWidth: 220 },
    { dataField: 'scenario', caption: 'Scenario', minWidth: 300 },
    { dataField: 'freqText', caption: 'Exposure: mild → severe', width: 160 },
    { dataField: 'orText', caption: 'OR', width: 70, alignment: 'right' },
    { dataField: 'alphaText', caption: 'Alpha', width: 90, alignment: 'right' },
    { dataField: 'n_cases', caption: 'Severe (cases)', width: 110, alignment: 'right' },
    { dataField: 'n_controls', caption: 'Mild (controls)', width: 110, alignment: 'right' },
    { dataField: 'n_total', caption: 'Total', width: 80, alignment: 'right' },
    { dataField: 'cohortText', caption: 'Cohort to enrol', width: 230 },
    { dataField: 'note', caption: 'Note', minWidth: 260 },
  ];

  protected readonly sizeChart = computed<FsChartOptions>(() => {
    this.themeChanges();
    const rows = this.sizes()?.rows ?? [];
    if (!rows.length) {
      return {};
    }
    const soft = fsChartCssColor('--fs-color-ink-soft', '#6b6862');
    const base = fsChartCssColor('--fs-color-ink-soft', '#8a877f');
    const rec = fsChartCssColor('--fs-color-chart-1', '#4b6bd6');
    return {
      chart: { type: 'bar', toolbar: { show: false }, animations: { enabled: false } },
      series: [{ name: 'Dogs to genotype or analyse', data: rows.map(r => r.n_total) }],
      colors: rows.map(r => (r.recommended ? rec : base)),
      plotOptions: { bar: { horizontal: true, distributed: true, barHeight: '70%' } },
      dataLabels: { enabled: true, formatter: (v: number) => v.toLocaleString(), style: { fontSize: '10px' } },
      legend: { show: false },
      xaxis: {
        categories: rows.map(r => r.scenario),
        title: { text: 'Dogs needed (severe + mild), 80% power', style: { color: soft } },
        labels: { formatter: (v: string) => Number(v).toLocaleString() },
      },
      yaxis: { labels: { maxWidth: 380, style: { fontSize: '10px' } } },
      tooltip: { y: { formatter: (v: number) => `${v.toLocaleString()} dogs` } },
    };
  });

  protected readonly chartHeight = computed(() => Math.max(260, 22 * (this.sizes()?.rows.length ?? 0) + 80));

  protected cohortText(r: PowerRow): string {
    return r.cohort_needed === null ? '–' : `${r.cohort_needed.toLocaleString()} (${r.cohort_basis ?? ''})`;
  }

  protected pct(v: number | null | undefined): string {
    return v === null || v === undefined ? '–' : String(Math.round(v * 100));
  }

  protected tableKey(i: number): string {
    return `t${i}`;
  }

  ngOnInit(): void {
    this.destroyRef.onDestroy(fsObserveTheme(() => this.themeChanges.update(n => n + 1)));
  }
}
