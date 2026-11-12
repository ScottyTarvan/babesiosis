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

// ---- Payloads written by /experiments/SV-01/scripts/build_load.py ---------------------------

interface EffectRow {
  label: string;
  estimate: number | null;
  ci_low: number | null;
  ci_high: number | null;
  p: number | null;
  n: number;
}

/** `primary_result`: the headline effect with its interval, n and sources. */
interface DiseaseSpacePrimaryPayload {
  label: string;
  statistic: string;
  estimate: number | null;
  ci_low: number | null;
  ci_high: number | null;
  p: number | null;
  q: number | null;
  n: number;
  n_unit: string;
  independent_sources: number;
  sources: string[];
  expected_direction?: string;
  status: string;
  headline: string;
  secondary: EffectRow[];
}

interface CheckRow {
  name: string;
  detail: string;
  passed: boolean;
}

/** `checks`: construction and validity checks, one set per curve construction. */
interface DiseaseSpaceChecksPayload {
  sets: { construction: string; rows: CheckRow[] }[];
}

interface MapPoint {
  id?: string;
  dog?: string;
  day?: number | null;
  timepoint?: string;
  x: number;
  y: number;
  stage: number | null;
  distance: number | null;
  habitus?: number | null;
  post?: boolean;
  beyond_end?: boolean;
}

/** `map_plane_a` / `map_plane_b`: the Beagle course, its arms and the natural dogs in one plane. */
interface DiseaseSpaceMapPayload {
  plane: string;
  x_label: string;
  y_label: string;
  y_is_log10: boolean;
  y_offset: number;
  course: { x: number; y: number; stage: number }[];
  post_arm: { x: number; y: number; stage: number }[];
  course_time_anchored: { x: number; y: number; stage: number }[];
  beagles: MapPoint[];
  groups: { key: string; label: string; colour_by_habitus: boolean; points: MapPoint[] }[];
  spread_sd_units: number;
  within_band_distance: number;
  footnote: string;
}

interface TestRow {
  code: string;
  label: string;
  statistic: string;
  estimate: number | null;
  ci_low: number | null;
  ci_high: number | null;
  n: number;
  p: number | null;
  q: number | null;
}

/** `tests_table`: every test, one set per construction. */
interface DiseaseSpaceTestsPayload {
  family_size: number;
  correction: string;
  sets: { construction: string; rows: TestRow[] }[];
}

interface LooRow {
  left_out: string;
  spread: number | null;
  median_abs_stage_change: number | null;
  spearman_stage_vs_full: number | null;
  spearman_distance_vs_full: number | null;
  share_beyond_end: number | null;
  h1_partial_rho: number | null;
}

/** `stability_loo`: refits leaving each Beagle out. */
interface DiseaseSpaceLooPayload {
  sets: { construction: string; rows: LooRow[] }[];
}

/** `habitus_table`: where the dogs of each habitus grade lie. */
interface DiseaseSpaceHabitusPayload {
  rows: { habitus: number; n: number; median_stage: number | null; median_distance: number | null; median_hct: number | null; beyond_end: number }[];
}

interface GeometryRow {
  construction: string;
  group: string;
  label: string;
  n: number;
  share_within_band: number | null;
  within_ci_low: number | null;
  within_ci_high: number | null;
  share_beyond_end: number | null;
  beyond_ci_low: number | null;
  beyond_ci_high: number | null;
  median_stage: number | null;
  stage_q1: number | null;
  stage_q3: number | null;
  median_distance: number | null;
  median_hct: number | null;
}

/** `geometry_table`: share within the Beagle band and on an end of the course, by cohort. */
interface DiseaseSpaceGeometryPayload {
  rows: GeometryRow[];
}

/** `stage_histogram`: pseudo-stage counts in 10 bins, by group. */
interface DiseaseSpaceHistogramPayload {
  bins: number[];
  groups: { key: string; label: string; n: number; counts: number[] }[];
}

/** Result kinds this view renders (the page hides them from its raw-JSON list). */
export const DISEASE_SPACE_RESULT_KINDS = ['interpretation', 'primary_result', 'checks', 'map_plane_a', 'map_plane_b', 'tests_table',
  'stability_loo', 'habitus_table', 'geometry_table', 'stage_histogram'];

function num(v: number | null | undefined, digits = 2): string {
  return v === null || v === undefined ? '–' : v.toFixed(digits);
}

function signed(v: number | null | undefined, digits = 2): string {
  return v === null || v === undefined ? '–' : `${v >= 0 ? '+' : ''}${v.toFixed(digits)}`;
}

function pText(p: number | null | undefined): string {
  return p === null || p === undefined ? '–' : p < 0.001 ? '< 0.001' : p.toFixed(3);
}

function pct(v: number | null | undefined): string {
  return v === null || v === undefined ? '–' : `${Math.round(100 * v)}%`;
}

/** Habitus grades of DS05 (4 bright to 0 collapsed), from bright to dull. */
const HABITUS_SERIES = [
  { label: 'Habitus 4 (bright)', match: (h: number) => h === 4, token: '--fs-color-chart-2', fallback: '#2f9e8f' },
  { label: 'Habitus 3 (mildly depressed)', match: (h: number) => h === 3, token: '--fs-color-chart-1', fallback: '#4b6bd6' },
  { label: 'Habitus 2 (depressed)', match: (h: number) => h === 2, token: '--fs-color-chart-3', fallback: '#c98a2b' },
  { label: 'Habitus 1 or collapsed', match: (h: number) => h <= 1, token: '--fs-color-chart-4', fallback: '#c6483a' },
];

const GROUP_TOKENS = ['--fs-color-chart-1', '--fs-color-chart-3', '--fs-color-chart-2', '--fs-color-chart-5', '--fs-color-chart-6'];

/**
 * The disease-space view (SV-01): the primary effect with its interval, the construction and
 * validity checks, the map of haematocrit against reticulocytes (or band neutrophils) with the
 * Beagle reference course and the natural dogs, and the tables behind it. The explanation note
 * is rendered by the page after this.
 */
@Component({
  selector: 'fs-experiment-disease-space-map-view',
  standalone: true,
  imports: [FsBadgeComponent, FsCardComponent, FsChartComponent, FsDataGridComponent],
  templateUrl: './experiment-disease-space-map-view.component.html',
  styleUrls: ['./experiment-disease-space-map-view.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExperimentDiseaseSpaceMapViewComponent implements OnInit {
  private readonly destroyRef = inject(DestroyRef);

  readonly detail = input.required<ExperimentDetailViewModel>();

  /** Bumped when the theme flips, so chart colours re-read their tokens. */
  private readonly themeChanges = signal(0);

  private find<T>(kind: string): T | null {
    return parsePayload<T>(this.detail().results.find(r => r.kind === kind));
  }

  protected readonly primary = computed(() => this.find<DiseaseSpacePrimaryPayload>('primary_result'));
  protected readonly checks = computed(() => this.find<DiseaseSpaceChecksPayload>('checks'));
  protected readonly mapA = computed(() => this.find<DiseaseSpaceMapPayload>('map_plane_a'));
  protected readonly mapB = computed(() => this.find<DiseaseSpaceMapPayload>('map_plane_b'));
  protected readonly tests = computed(() => this.find<DiseaseSpaceTestsPayload>('tests_table'));
  protected readonly loo = computed(() => this.find<DiseaseSpaceLooPayload>('stability_loo'));
  protected readonly habitus = computed(() => this.find<DiseaseSpaceHabitusPayload>('habitus_table'));
  protected readonly geometry = computed(() => this.find<DiseaseSpaceGeometryPayload>('geometry_table'));
  protected readonly histogram = computed(() => this.find<DiseaseSpaceHistogramPayload>('stage_histogram'));

  protected readonly primaryIsProportion = computed(() => this.primary()?.statistic === 'proportion');
  protected readonly primaryEstimate = computed(() => {
    const p = this.primary();
    if (!p) {
      return '–';
    }
    return this.primaryIsProportion() ? pct(p.estimate) : signed(p.estimate);
  });
  protected readonly primaryInterval = computed(() => {
    const p = this.primary();
    if (!p) {
      return '–';
    }
    return this.primaryIsProportion() ? `${pct(p.ci_low)} to ${pct(p.ci_high)}` : `${signed(p.ci_low)} to ${signed(p.ci_high)}`;
  });
  protected readonly primaryP = computed(() => pText(this.primary()?.p));
  protected readonly primaryQ = computed(() => pText(this.primary()?.q));

  protected readonly secondaryRows = computed(() => {
    const prop = this.primaryIsProportion();
    return (this.primary()?.secondary ?? []).map((r, i) => ({
      id: i,
      label: r.label,
      estimate: prop ? pct(r.estimate) : signed(r.estimate),
      interval: prop ? `${pct(r.ci_low)} to ${pct(r.ci_high)}` : `${signed(r.ci_low)} to ${signed(r.ci_high)}`,
      p: pText(r.p),
      n: r.n,
    }));
  });
  protected readonly secondaryColumns: FsGridColumn<{ id: number; label: string; estimate: string; interval: string; p: string; n: number }>[] = [
    { dataField: 'label', caption: 'Also', minWidth: 260 },
    { dataField: 'estimate', caption: 'Estimate', width: 100, alignment: 'right' },
    { dataField: 'interval', caption: '95% CI', width: 150, alignment: 'right' },
    { dataField: 'p', caption: 'p', width: 90, alignment: 'right' },
    { dataField: 'n', caption: 'n', width: 70, alignment: 'right' },
  ];

  protected readonly mapAOptions = computed(() => this.mapOptions(this.mapA()));
  protected readonly mapBOptions = computed(() => this.mapOptions(this.mapB()));

  protected readonly testSets = computed(() => (this.tests()?.sets ?? []).map(set => ({
    construction: set.construction,
    rows: set.rows.map(r => ({
      code: r.code,
      label: r.label,
      estimate: `${r.statistic} ${signed(r.estimate)}`,
      interval: `${signed(r.ci_low)} to ${signed(r.ci_high)}`,
      n: r.n,
      p: pText(r.p),
      q: r.q === null ? '–' : pText(r.q),
      pSort: r.p ?? 1,
    })),
  })));
  protected readonly testColumns: FsGridColumn<{ code: string; label: string; estimate: string; interval: string; n: number; p: string; q: string; pSort: number }>[] = [
    { dataField: 'code', caption: 'Test', width: 70 },
    { dataField: 'label', caption: 'What', minWidth: 260 },
    { dataField: 'estimate', caption: 'Estimate', width: 160 },
    { dataField: 'interval', caption: '95% CI', width: 140, alignment: 'right' },
    { dataField: 'n', caption: 'n', width: 60, alignment: 'right' },
    { dataField: 'p', caption: 'p', width: 80, alignment: 'right', calculateSortValue: 'pSort' },
    { dataField: 'q', caption: 'BH q', width: 80, alignment: 'right' },
  ];

  protected readonly looSets = computed(() => (this.loo()?.sets ?? []).map(set => ({
    construction: set.construction,
    rows: set.rows.map(r => ({
      left_out: r.left_out,
      spread: num(r.spread),
      stageChange: num(r.median_abs_stage_change),
      stageRank: signed(r.spearman_stage_vs_full),
      distanceRank: signed(r.spearman_distance_vs_full),
      beyond: pct(r.share_beyond_end),
      h1: signed(r.h1_partial_rho),
    })),
  })));
  protected readonly looColumns: FsGridColumn<Record<string, string>>[] = [
    { dataField: 'left_out', caption: 'Beagle left out', width: 130 },
    { dataField: 'spread', caption: 'Spread', width: 80, alignment: 'right' },
    { dataField: 'stageChange', caption: 'Median |Δ stage|', width: 130, alignment: 'right' },
    { dataField: 'stageRank', caption: 'Stage rank agreement', width: 160, alignment: 'right' },
    { dataField: 'distanceRank', caption: 'Distance rank agreement', width: 170, alignment: 'right' },
    { dataField: 'beyond', caption: 'On an end', width: 90, alignment: 'right' },
    { dataField: 'h1', caption: 'H1 partial rho', width: 120, alignment: 'right' },
  ];

  protected readonly habitusRows = computed(() => (this.habitus()?.rows ?? []).map(r => ({
    habitus: r.habitus === 0 ? '0 (collapsed)' : String(r.habitus),
    n: r.n,
    stage: num(r.median_stage),
    distance: num(r.median_distance),
    hct: num(r.median_hct),
    beyond: `${r.beyond_end} of ${r.n}`,
  })));
  protected readonly habitusColumns: FsGridColumn<Record<string, string | number>>[] = [
    { dataField: 'habitus', caption: 'Habitus grade', width: 130 },
    { dataField: 'n', caption: 'Dogs', width: 70, alignment: 'right' },
    { dataField: 'hct', caption: 'Median haematocrit', width: 150, alignment: 'right' },
    { dataField: 'stage', caption: 'Median pseudo-stage', width: 160, alignment: 'right' },
    { dataField: 'distance', caption: 'Median distance', width: 140, alignment: 'right' },
    { dataField: 'beyond', caption: 'On an end of the course', minWidth: 170, alignment: 'right' },
  ];

  protected readonly geometryRows = computed(() => (this.geometry()?.rows ?? []).map((r, i) => ({
    id: i,
    construction: r.construction,
    label: r.label,
    n: r.n,
    within: `${pct(r.share_within_band)} (${pct(r.within_ci_low)} to ${pct(r.within_ci_high)})`,
    beyond: `${pct(r.share_beyond_end)} (${pct(r.beyond_ci_low)} to ${pct(r.beyond_ci_high)})`,
    stage: `${num(r.median_stage)} (${num(r.stage_q1)} to ${num(r.stage_q3)})`,
    distance: num(r.median_distance),
    hct: num(r.median_hct),
  })));
  protected readonly geometryColumns: FsGridColumn<Record<string, string | number>>[] = [
    { dataField: 'construction', caption: 'Course', width: 210 },
    { dataField: 'label', caption: 'Group', minWidth: 240 },
    { dataField: 'n', caption: 'Dogs', width: 70, alignment: 'right' },
    { dataField: 'within', caption: 'Within the band (95% CI)', width: 190, alignment: 'right' },
    { dataField: 'beyond', caption: 'On an end (95% CI)', width: 170, alignment: 'right' },
    { dataField: 'stage', caption: 'Median stage (IQR)', width: 170, alignment: 'right' },
    { dataField: 'distance', caption: 'Median distance', width: 130, alignment: 'right' },
    { dataField: 'hct', caption: 'Median haematocrit', width: 150, alignment: 'right' },
  ];

  protected readonly histogramOptions = computed<FsChartOptions>(() => {
    this.themeChanges();
    const h = this.histogram();
    if (!h) {
      return {};
    }
    const labels = h.bins.slice(0, -1).map((b, i) => `${b.toFixed(1)}–${h.bins[i + 1].toFixed(1)}`);
    const ink = fsChartCssColor('--fs-color-ink-soft', '#6b6862');
    return {
      chart: { type: 'bar', toolbar: { show: false }, animations: { enabled: false } },
      series: h.groups.map(g => ({ name: `${g.label} (n ${g.n})`, data: g.counts.map(c => g.n ? Math.round(1000 * c / g.n) / 10 : 0) })),
      colors: h.groups.map((_, i) => fsChartCssColor(GROUP_TOKENS[i % GROUP_TOKENS.length], '#4b6bd6')),
      plotOptions: { bar: { columnWidth: '75%' } },
      dataLabels: { enabled: false },
      xaxis: { categories: labels, title: { text: 'Pseudo-stage (0 early end, 1 late end of the Beagle course)', style: { color: ink } } },
      yaxis: { title: { text: '% of dogs', style: { color: ink } }, labels: { formatter: (v: number) => `${Math.round(v)}%` } },
      legend: { position: 'bottom' },
      tooltip: { y: { formatter: (v: number) => `${v}%` } },
    };
  });

  ngOnInit(): void {
    this.destroyRef.onDestroy(fsObserveTheme(() => this.themeChanges.update(n => n + 1)));
  }

  /**
   * One Apex chart with scatter series (natural dogs, Beagle samples) and line series (the
   * reference course, the time-anchored course and the post-treatment arm). The y axis holds
   * log10 values; its labels show them back on the original scale.
   */
  private mapOptions(m: DiseaseSpaceMapPayload | null): FsChartOptions {
    this.themeChanges();
    if (!m) {
      return {};
    }
    const ink = fsChartCssColor('--fs-color-ink', '#2b2a27');
    const soft = fsChartCssColor('--fs-color-ink-soft', '#6b6862');
    type Series = { name: string; type: string; data: { x: number; y: number; meta?: string }[] };
    const series: Series[] = [];
    const colors: string[] = [];
    const widths: number[] = [];
    const dashes: number[] = [];
    const markers: number[] = [];
    const add = (s: Series, colour: string, width: number, dash: number, marker: number) => {
      series.push(s);
      colors.push(colour);
      widths.push(width);
      dashes.push(dash);
      markers.push(marker);
    };
    const meta = (p: MapPoint) => `${p.id ?? p.dog ?? ''}${p.day !== undefined && p.day !== null ? ` · day ${p.day}` : ''}`
      + ` · stage ${num(p.stage)} · distance ${num(p.distance)}${p.habitus !== undefined && p.habitus !== null ? ` · habitus ${p.habitus}` : ''}`;
    m.groups.forEach((g, gi) => {
      if (g.colour_by_habitus) {
        HABITUS_SERIES.forEach(h => {
          const pts = g.points.filter(p => p.habitus !== null && p.habitus !== undefined && h.match(p.habitus));
          if (pts.length) {
            add({ name: `${h.label} (n ${pts.length})`, type: 'scatter', data: pts.map(p => ({ x: p.x, y: p.y, meta: meta(p) })) },
              fsChartCssColor(h.token, h.fallback), 0, 0, 4);
          }
        });
      } else {
        add({ name: `${g.label} (n ${g.points.length})`, type: 'scatter', data: g.points.map(p => ({ x: p.x, y: p.y, meta: meta(p) })) },
          fsChartCssColor(GROUP_TOKENS[gi % GROUP_TOKENS.length], '#4b6bd6'), 0, 0, 4);
      }
    });
    const pre = m.beagles.filter(b => !b.post);
    const post = m.beagles.filter(b => b.post);
    add({ name: `Beagles before treatment (${pre.length} samples)`, type: 'scatter', data: pre.map(p => ({ x: p.x, y: p.y, meta: meta(p) })) }, ink, 0, 0, 6);
    add({ name: `Beagles after treatment (${post.length} samples)`, type: 'scatter', data: post.map(p => ({ x: p.x, y: p.y, meta: meta(p) })) }, soft, 0, 0, 5);
    add({ name: 'Reference course (spec construction)', type: 'line', data: m.course.map(p => ({ x: p.x, y: p.y, meta: `stage ${num(p.stage)}` })) }, ink, 3, 0, 0);
    if (m.course_time_anchored?.length) {
      add({ name: 'Time-anchored course (deviation D1)', type: 'line', data: m.course_time_anchored.map(p => ({ x: p.x, y: p.y, meta: `stage ${num(p.stage)}` })) }, ink, 2, 6, 0);
    }
    if (m.post_arm?.length) {
      add({ name: 'Post-treatment arm', type: 'line', data: m.post_arm.map(p => ({ x: p.x, y: p.y, meta: `stage ${num(p.stage)}` })) }, soft, 2, 2, 0);
    }
    const offset = m.y_offset ?? 0;
    const yLabel = (v: number) => {
      if (!m.y_is_log10) {
        return num(v);
      }
      const raw = Math.pow(10, v) - offset;
      return raw >= 100 ? raw.toFixed(0) : raw >= 10 ? raw.toFixed(0) : raw >= 1 ? raw.toFixed(1) : raw.toFixed(2);
    };
    return {
      chart: { type: 'line', toolbar: { show: false }, animations: { enabled: false }, zoom: { enabled: false } },
      series,
      colors,
      stroke: { width: widths, dashArray: dashes, curve: 'straight' },
      markers: { size: markers, strokeWidth: 0, hover: { sizeOffset: 2 } },
      fill: { type: 'solid', opacity: 1 },
      dataLabels: { enabled: false },
      xaxis: {
        type: 'numeric', min: 0, max: 0.7, tickAmount: 7,
        title: { text: m.x_label, style: { color: soft } },
        labels: { formatter: (v: string) => Number(v).toFixed(2) },
      },
      yaxis: {
        title: { text: m.y_is_log10 ? m.y_label.replace('log10 ', '') + ' (log scale)' : m.y_label, style: { color: soft } },
        labels: { formatter: yLabel },
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
          return `<div class="fs-experiment-disease-space__tip"><strong>${s.name}</strong><br>`
            + `haematocrit ${p.x.toFixed(2)} · ${m.y_label.split(' (')[0].replace('log10 ', '')} ${yLabel(p.y)}<br>${p.meta ?? ''}</div>`;
        },
      },
    };
  }
}
