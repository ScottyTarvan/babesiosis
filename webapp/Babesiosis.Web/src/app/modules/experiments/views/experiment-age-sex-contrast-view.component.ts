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

// ---- Payloads written by /experiments/SV-05/scripts/build_load.py ---------------------------

/** One contrast: young (first group) minus or over adult (second group), with its interval. */
interface ContrastRow {
  id: string;
  test: string;
  label: string;
  dataset: string;
  source: string;
  measure: string;
  effect_label: string;
  /** `diff`: null value 0, linear axis. `ratio`: null value 1, log axis. */
  scale: 'diff' | 'ratio';
  null_value: number;
  estimate: number | null;
  ci_low: number | null;
  ci_high: number | null;
  n_young: number | null;
  n_adult: number | null;
  value_label: string;
  young_value: number | null;
  adult_value: number | null;
  events_young?: number | null;
  events_adult?: number | null;
  cliff: number | null;
  cliff_low: number | null;
  cliff_high: number | null;
  p: number | null;
  q: number | null;
  digits: number;
  note: string;
  group_labels?: string[] | null;
}

interface ContrastGroupsPayload {
  groups: { key: string; label: string; note: string; rows: ContrastRow[] }[];
  footnote: string;
}

/** `primary_result`. */
interface AgePrimaryPayload {
  label: string;
  statistic: string;
  verdict: string;
  signals?: { anaemia: boolean; inflammatory: boolean; risk: boolean; against: string[] };
  independent_sources: number;
  sources: string[];
  rows: ContrastRow[];
  headline: string;
  caveats: string[];
}

/** `strata`: death by age group inside each sex. */
interface StrataPayload {
  rows: { stratum: string; deaths_young: number; n_young: number; deaths_adult: number; n_adult: number;
    or: number | null; or_low: number | null; or_high: number | null; p: number | null }[];
  sex_contrast: { deaths_male: number; n_male: number; deaths_female: number; n_female: number;
    or: number | null; or_low: number | null; or_high: number | null; p: number | null };
  footnote: string;
}

/** `age_bands`: deaths by age band. */
interface AgeBandsPayload {
  rows: { band: string; n: number; died: number; share: number | null }[];
  footnote: string;
}

interface ProfilePoint { band: string; n: number; median: number | null; q1: number | null; q3: number | null }

/** `age_profile`: median per age band, per source. */
interface AgeProfilePayload {
  bands: string[];
  measures: { key: string; label: string; series: { key: string; label: string; dataset: string; points: ProfilePoint[] }[] }[];
  footnote: string;
}

/** `control_check`: haematocrit of healthy controls by age. */
interface ControlCheckPayload {
  n_young: number;
  n_adult: number;
  young_values: number[];
  median_adult: number | null;
  range_adult: number[] | null;
  footnote: string;
}

interface Summary { n: number; median: number | null; min: number | null; max: number | null }

/** `neuter_description`: neutered against intact adult dogs in DS05. */
interface NeuterPayload {
  n_neutered: number;
  n_neutered_young: number;
  sex_neutered: { male: number; female: number };
  rows: { variable: string; neutered: Summary; intact_adult: Summary }[];
  footnote: string;
}

/** Result kinds this view renders (the page hides them from its raw-JSON list). */
export const AGE_SEX_CONTRAST_RESULT_KINDS = ['interpretation', 'primary_result', 'contrasts', 'strata', 'age_bands',
  'secondary', 'sensitivity', 'control_check', 'age_profile', 'neuter_description'];

function fixed(v: number | null | undefined, digits = 2): string {
  return v === null || v === undefined ? '–' : v.toFixed(digits);
}

function signed(v: number | null | undefined, digits = 2): string {
  return v === null || v === undefined ? '–' : `${v > 0 ? '+' : ''}${v.toFixed(digits)}`;
}

function pText(p: number | null | undefined): string {
  return p === null || p === undefined ? '–' : p < 0.001 ? '< 0.001' : p.toFixed(3);
}

function pct(v: number | null | undefined): string {
  return v === null || v === undefined ? '–' : `${Math.round(100 * v)}%`;
}

/** A contrast row as shown: text cells and the coordinates of its own mini interval plot. */
interface ViewRow {
  id: string;
  label: string;
  source: string;
  n: string;
  values: string;
  effect: string;
  cliff: string;
  p: string;
  q: string;
  note: string;
  excludesNull: boolean;
  x: number;
  x1: number;
  x2: number;
  /** Label of the axis end (the half-width of the row's own scale). */
  span: string;
}

interface ViewGroup { key: string; label: string; note: string; rows: ViewRow[] }

const MINI = { width: 240, height: 24 };

/** Each row has its own axis, centred on its null value (0, or 1 on a log scale). */
function toViewRow(r: ContrastRow): ViewRow {
  const ratio = r.scale === 'ratio';
  const t = (v: number | null) => (v === null ? null : ratio ? Math.log(Math.max(v, 1e-6)) : v - r.null_value);
  const est = t(r.estimate);
  const lo = t(r.ci_low);
  const hi = t(r.ci_high);
  const half = Math.max(Math.abs(lo ?? 0), Math.abs(hi ?? 0), Math.abs(est ?? 0), 1e-9) * 1.15;
  const x = (v: number | null) => MINI.width / 2 + ((v ?? 0) / half) * (MINI.width / 2 - 6);
  const labels = r.group_labels ?? ['young', 'adult'];
  const isShare = r.value_label.startsWith('share');
  const vals = r.young_value === null && r.adult_value === null
    ? '–'
    : isShare
      ? `${pct(r.young_value)}${r.events_young !== undefined && r.events_young !== null ? ` (${r.events_young}/${r.n_young})` : ''} vs `
        + `${pct(r.adult_value)}${r.events_adult !== undefined && r.events_adult !== null ? ` (${r.events_adult}/${r.n_adult})` : ''}`
      : `${fixed(r.young_value, r.digits)} vs ${fixed(r.adult_value, r.digits)}`;
  const d = ratio ? 2 : r.digits;
  const fmt = ratio ? fixed : signed;
  return {
    id: r.id,
    label: r.label,
    source: `${r.dataset} · ${r.source}`,
    n: r.n_adult === null || r.n_adult === undefined ? `${r.n_young ?? '–'}` : `${r.n_young} ${labels[0]} vs ${r.n_adult} ${labels[1]}`,
    values: vals === '–' ? '–' : `${r.value_label}: ${vals}`,
    effect: `${r.effect_label} ${fmt(r.estimate, d)} (${fmt(r.ci_low, d)} to ${fmt(r.ci_high, d)})`,
    cliff: r.cliff === null ? '–' : `${signed(r.cliff)} (${signed(r.cliff_low)} to ${signed(r.cliff_high)})`,
    p: pText(r.p),
    q: pText(r.q),
    note: r.note ?? '',
    excludesNull: r.ci_low !== null && r.ci_high !== null && (r.ci_low > r.null_value || r.ci_high < r.null_value),
    x: x(est),
    x1: x(lo),
    x2: x(hi),
    span: ratio ? `×${Math.exp(half).toFixed(1)}` : signed(half, r.digits),
  };
}

function toGroups(p: ContrastGroupsPayload | null): ViewGroup[] {
  return (p?.groups ?? []).map(g => ({ key: g.key, label: g.label, note: g.note, rows: g.rows.map(toViewRow) }));
}

/**
 * The age-and-sex contrast view (SV-05): the primary contrast with its interval, every contrast
 * young minus adult inside each source with its own interval plot, sex strata, deaths by age band,
 * the medians by age band side by side per source, and the neuter description. The explanation
 * note is rendered by the page after this.
 */
@Component({
  selector: 'fs-experiment-age-sex-contrast-view',
  standalone: true,
  imports: [NgTemplateOutlet, FsBadgeComponent, FsCardComponent, FsChartComponent, FsDataGridComponent],
  templateUrl: './experiment-age-sex-contrast-view.component.html',
  styleUrls: ['./experiment-age-sex-contrast-view.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExperimentAgeSexContrastViewComponent implements OnInit {
  private readonly destroyRef = inject(DestroyRef);

  readonly detail = input.required<ExperimentDetailViewModel>();

  private readonly themeChanges = signal(0);

  protected readonly mini = MINI;

  private find<T>(kind: string): T | null {
    return parsePayload<T>(this.detail().results.find(r => r.kind === kind));
  }

  protected readonly primary = computed(() => this.find<AgePrimaryPayload>('primary_result'));
  protected readonly primaryRows = computed(() => (this.primary()?.rows ?? []).map(toViewRow));
  protected readonly contrastsPayload = computed(() => this.find<ContrastGroupsPayload>('contrasts'));
  protected readonly contrasts = computed(() => toGroups(this.contrastsPayload()));
  protected readonly secondaryPayload = computed(() => this.find<ContrastGroupsPayload>('secondary'));
  protected readonly secondary = computed(() => toGroups(this.secondaryPayload()));
  protected readonly sensitivityPayload = computed(() => this.find<ContrastGroupsPayload>('sensitivity'));
  protected readonly sensitivity = computed(() => toGroups(this.sensitivityPayload()));
  protected readonly strata = computed(() => this.find<StrataPayload>('strata'));
  protected readonly bands = computed(() => this.find<AgeBandsPayload>('age_bands'));
  protected readonly profile = computed(() => this.find<AgeProfilePayload>('age_profile'));
  protected readonly control = computed(() => this.find<ControlCheckPayload>('control_check'));
  protected readonly neuter = computed(() => this.find<NeuterPayload>('neuter_description'));

  protected readonly verdictIntent = computed(() => {
    const v = this.primary()?.verdict ?? '';
    return v === 'Supported' ? 'success' as const : v === 'Partly supported' ? 'warning' as const : 'info' as const;
  });

  protected readonly rowColumns: FsGridColumn<ViewRow>[] = [
    { dataField: 'label', caption: 'Contrast', minWidth: 220 },
    { dataField: 'source', caption: 'Source', width: 140 },
    { dataField: 'n', caption: 'n', width: 170 },
    { dataField: 'values', caption: 'Young vs adult', minWidth: 200 },
    { dataField: 'effect', caption: 'Effect (95% CI)', minWidth: 260 },
    { dataField: 'cliff', caption: "Cliff's delta (95% CI)", width: 190, alignment: 'right' },
    { dataField: 'p', caption: 'p', width: 80, alignment: 'right' },
    { dataField: 'q', caption: 'BH q', width: 80, alignment: 'right' },
  ];

  protected readonly strataRows = computed(() => (this.strata()?.rows ?? []).map(r => ({
    stratum: r.stratum,
    young: `${r.deaths_young} of ${r.n_young} (${pct(r.n_young ? r.deaths_young / r.n_young : null)})`,
    adult: `${r.deaths_adult} of ${r.n_adult} (${pct(r.n_adult ? r.deaths_adult / r.n_adult : null)})`,
    or: `${fixed(r.or)} (${fixed(r.or_low)} to ${fixed(r.or_high)})`,
    p: pText(r.p),
  })));
  protected readonly strataColumns: FsGridColumn<Record<string, string>>[] = [
    { dataField: 'stratum', caption: 'Sex', width: 100 },
    { dataField: 'young', caption: 'Died, under 12 months', minWidth: 170 },
    { dataField: 'adult', caption: 'Died, 12 months or more', minWidth: 170 },
    { dataField: 'or', caption: 'Odds ratio young/adult (95% CI)', minWidth: 220, alignment: 'right' },
    { dataField: 'p', caption: 'Fisher p', width: 90, alignment: 'right' },
  ];
  protected readonly sexText = computed(() => {
    const s = this.strata()?.sex_contrast;
    return s
      ? `Death by sex (secondary): ${s.deaths_male} of ${s.n_male} males and ${s.deaths_female} of ${s.n_female} females died; `
        + `odds ratio male/female ${fixed(s.or)} (${fixed(s.or_low)} to ${fixed(s.or_high)}), p ${pText(s.p)}.`
      : '';
  });

  protected readonly bandOptions = computed<FsChartOptions>(() => {
    this.themeChanges();
    const b = this.bands();
    if (!b) {
      return {};
    }
    const soft = fsChartCssColor('--fs-color-ink-soft', '#6b6862');
    return {
      chart: { type: 'bar', toolbar: { show: false }, animations: { enabled: false } },
      series: [{ name: 'Share died', data: b.rows.map(r => (r.share === null ? 0 : Math.round(1000 * r.share) / 10)) }],
      colors: [fsChartCssColor('--fs-color-chart-1', '#4b6bd6')],
      plotOptions: { bar: { columnWidth: '55%' } },
      dataLabels: {
        enabled: true,
        formatter: (_v: number, o: { dataPointIndex: number }) => `${b.rows[o.dataPointIndex].died}/${b.rows[o.dataPointIndex].n}`,
        style: { colors: [soft] },
        offsetY: -18,
      },
      xaxis: { categories: b.rows.map(r => r.band), title: { text: 'Age band (months)', style: { color: soft } } },
      yaxis: { title: { text: 'Died (%)', style: { color: soft } }, min: 0, labels: { formatter: (v: number) => v.toFixed(0) } },
      tooltip: { y: { formatter: (v: number) => `${v.toFixed(1)}%` } },
    };
  });

  protected readonly selectedMeasure = signal('hct');
  protected readonly profileMeasures = computed(() => (this.profile()?.measures ?? []).map(m => ({ key: m.key, label: m.label })));
  protected readonly profileSelected = computed(() =>
    this.profile()?.measures.find(m => m.key === this.selectedMeasure()) ?? this.profile()?.measures[0] ?? null);

  protected readonly profileOptions = computed<FsChartOptions>(() => {
    this.themeChanges();
    const p = this.profile();
    const m = this.profileSelected();
    if (!p || !m) {
      return {};
    }
    const soft = fsChartCssColor('--fs-color-ink-soft', '#6b6862');
    const palette = ['--fs-color-chart-1', '--fs-color-chart-5', '--fs-color-chart-3'];
    return {
      chart: { type: 'line', toolbar: { show: false }, animations: { enabled: false }, zoom: { enabled: false } },
      series: m.series.map(s => ({ name: s.label, data: s.points.map(pt => pt.median) })),
      colors: m.series.map((_, i) => fsChartCssColor(palette[i % palette.length], '#4b6bd6')),
      stroke: { width: 2, curve: 'straight' },
      markers: { size: 5, strokeWidth: 0 },
      dataLabels: { enabled: false },
      xaxis: { categories: p.bands, title: { text: 'Age band (months)', style: { color: soft } } },
      yaxis: { title: { text: `Median ${m.label}`, style: { color: soft } }, labels: { formatter: (v: number) => (v === null ? '' : v.toFixed(2)) } },
      legend: { position: 'bottom' },
      tooltip: {
        shared: false, intersect: true,
        y: {
          formatter: (v: number, o: { seriesIndex: number; dataPointIndex: number }) => {
            const pt = m.series[o.seriesIndex]?.points[o.dataPointIndex];
            return pt ? `${fixed(v)} (IQR ${fixed(pt.q1)} to ${fixed(pt.q3)}, n ${pt.n})` : fixed(v);
          },
        },
      },
    };
  });

  protected readonly profileRows = computed(() => {
    const m = this.profileSelected();
    const p = this.profile();
    if (!m || !p) {
      return [];
    }
    return p.bands.map((b, i) => {
      const row: Record<string, string> = { band: b };
      m.series.forEach(s => {
        const pt = s.points[i];
        row[s.key] = pt && pt.n ? `${fixed(pt.median)} (${fixed(pt.q1)}–${fixed(pt.q3)}), n ${pt.n}` : '–';
      });
      return row;
    });
  });
  protected readonly profileColumns = computed<FsGridColumn<Record<string, string>>[]>(() => [
    { dataField: 'band', caption: 'Age (months)', width: 110 },
    ...(this.profileSelected()?.series ?? []).map(s => ({ dataField: s.key, caption: `${s.label}: median (IQR)`, minWidth: 220 })),
  ]);

  protected readonly controlText = computed(() => {
    const c = this.control();
    return c
      ? `${c.n_young} control dogs under 12 months: haematocrit ${c.young_values.map(v => fixed(v)).join(' and ')} L/L. `
        + `${c.n_adult} adult controls: median ${fixed(c.median_adult)} (range ${fixed(c.range_adult?.[0])} to ${fixed(c.range_adult?.[1])}).`
      : '';
  });

  protected readonly neuterRows = computed(() => (this.neuter()?.rows ?? []).map(r => ({
    variable: r.variable,
    neutered: `${fixed(r.neutered.median)} (${fixed(r.neutered.min)}–${fixed(r.neutered.max)}), n ${r.neutered.n}`,
    intact: `${fixed(r.intact_adult.median)} (${fixed(r.intact_adult.min)}–${fixed(r.intact_adult.max)}), n ${r.intact_adult.n}`,
  })));
  protected readonly neuterColumns: FsGridColumn<Record<string, string>>[] = [
    { dataField: 'variable', caption: 'Variable', minWidth: 200 },
    { dataField: 'neutered', caption: 'Neutered: median (range)', minWidth: 200 },
    { dataField: 'intact', caption: 'Intact adults: median (range)', minWidth: 200 },
  ];

  ngOnInit(): void {
    this.destroyRef.onDestroy(fsObserveTheme(() => this.themeChanges.update(n => n + 1)));
  }

  protected selectMeasure(key: string): void {
    this.selectedMeasure.set(key);
  }
}
