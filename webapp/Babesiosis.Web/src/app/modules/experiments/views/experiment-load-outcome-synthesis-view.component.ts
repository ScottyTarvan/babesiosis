import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';
import { FsCardComponent, FsDataGridComponent, FsGridColumn, FsGridPager } from '@core';
import { ExperimentDetailViewModel, parsePayload } from 'app/modules/experiments/viewmodels/experiment.viewmodel';

// ---- Payloads written by /experiments/SV-02/a/scripts/build_load.py -------------------------

export interface LoadCell {
  species_group: string;
  outcome_class: string;
  units: number;
  unit_ids: string[];
  definitions: number;
  units_with_g: number;
  pooled: boolean;
  reason: string;
}

export interface LoadCellsPayload {
  cells: LoadCell[];
  pooled: { species_group: string; outcome_class: string; mu: number; lo: number; hi: number; tau2: number; k: number }[];
  counts: Record<string, number | string[]>;
  primary: {
    unit: string; article: string; species_group: string; outcome_class: string; effect_type: string;
    effect: number; ci_lo: number; ci_hi: number; n_severe: number; n_comparison: number; detectable: number | null; doi: string | null;
  };
  load_units: number;
  species_groups: string[];
}

export interface UnitEffect {
  unit: string;
  article: string;
  species_group: string;
  outcome_class: string;
  definition: string;
  effect_type: string;
  effect: number;
  ci_lo: number | null;
  ci_hi: number | null;
  n: number | null;
  basis: string;
  assumed_n: boolean;
}

export interface LoadOutcomeRow {
  unit: string;
  article: string;
  species_group: string;
  outcome_class: string;
  definition: string;
  euthanasia_included: string;
  load_method: string;
  sample_timing: string;
  direction: string;
  significant: string;
  n_total: number | null;
  n_severe: number | null;
  n_comparison: number | null;
  severe_value: string;
  comparison_value: string;
  summary_type: string;
  p_value: string;
  effect_type: string | null;
  effect: number | null;
  ci_lo: number | null;
  ci_hi: number | null;
  detectable: number | null;
  effect_basis: string;
  doi: string | null;
}

export interface LowLoadItem {
  kind: string;
  unit: string;
  article: string;
  species: string;
  design: string;
  n_dogs: number | null;
  source_level: string;
  statement: string;
  doi: string | null;
}

export interface DamageUnit {
  unit: string;
  article: string;
  species_group: string;
  definition: string;
  rows: number;
  worse_with_load: number;
  better_with_load: number;
  no_difference: number;
  doi: string | null;
}

export interface DamageRow {
  unit: string;
  article: string;
  marker: string;
  n_high: number | null;
  n_low: number | null;
  high_value: string;
  low_value: string;
  direction: string;
  effect_type: string | null;
  effect: number | null;
  ci_lo: number | null;
  ci_hi: number | null;
  flag: string | null;
}

export interface SensitivityRow {
  check: string;
  unit: string;
  article: string;
  species_group: string;
  effect_type: string;
  effect: number | null;
  ci_lo: number | null;
  ci_hi: number | null;
  note: string;
}

/** One line of the forest plot. */
interface ForestLine {
  key: string;
  label: string;
  sub: string;
  y: number;
  cx: number;
  x1: number;
  x2: number;
  value: string;
  dashed: boolean;
}

interface ForestPanel {
  title: string;
  axis: string;
  ticks: { x: number; label: string }[];
  zero: number;
  lines: ForestLine[];
  height: number;
}

const PANEL_LEFT = 250;
const PANEL_WIDTH = 300;
const ROW_H = 34;

function fmt(x: number | null | undefined, digits = 2): string {
  return x === null || x === undefined ? '–' : x.toFixed(digits);
}

const TYPE_LABEL: Record<string, string> = {
  hedges_g_log_load: 'Hedges g, log load',
  rho: 'Spearman rho, load',
  r: 'Pearson r, load',
  rho_antibody: 'Spearman rho, antibody level',
  odds_ratio_smear_positive: 'Odds ratio, smear positive',
};

/**
 * The view for SV-02a: parasite load against outcome, synthesised from the published contrasts that SV-G2 extracted.
 * The pooling cells first (none reached the rule), then a forest plot of every unit with computable numbers,
 * the direction table, the list of discordant results (severe disease at low load), and damage by load group.
 */
@Component({
  selector: 'fs-experiment-load-outcome-synthesis-view',
  standalone: true,
  imports: [FsCardComponent, FsDataGridComponent],
  templateUrl: './experiment-load-outcome-synthesis-view.component.html',
  styleUrls: ['./experiment-load-outcome-synthesis-view.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExperimentLoadOutcomeSynthesisViewComponent {
  readonly detail = input.required<ExperimentDetailViewModel>();

  protected readonly panelLeft = PANEL_LEFT;
  protected readonly panelWidth = PANEL_WIDTH;
  protected readonly svgWidth = PANEL_LEFT + PANEL_WIDTH + 250;

  private result<T>(kind: string): T | null {
    return parsePayload<T>(this.detail().results.find(r => r.kind === kind));
  }

  protected readonly cells = computed(() => this.result<LoadCellsPayload>('load_cells'));
  protected readonly effects = computed(() => this.result<{ rows: UnitEffect[] }>('unit_effects')?.rows ?? null);
  protected readonly table = computed(() => this.result<{ rows: LoadOutcomeRow[] }>('load_by_outcome')?.rows ?? null);
  protected readonly lowLoad = computed(() =>
    this.result<{ rows: LowLoadItem[]; note_hits: number; note_hits_included: number }>('low_load_list'));
  protected readonly damage = computed(() => this.result<{ units: DamageUnit[]; rows: DamageRow[] }>('damage_by_load_group'));
  protected readonly sensitivity = computed(() => this.result<{ rows: SensitivityRow[] }>('sensitivity')?.rows ?? null);

  protected readonly count = (key: string): string => {
    const v = this.cells()?.counts?.[key];
    return Array.isArray(v) ? v.join(', ') : v === undefined ? '–' : String(v);
  };
  protected readonly fmt = fmt;

  private panel(title: string, axis: string, rows: UnitEffect[], min: number, max: number, zero: number,
                ticks: number[], toX: (v: number) => number = v => v): ForestPanel {
    const scale = (v: number) => PANEL_LEFT + ((toX(v) - toX(min)) / (toX(max) - toX(min))) * PANEL_WIDTH;
    const clamp = (v: number) => Math.min(Math.max(v, min), max);
    const lines = rows.map((r, i) => ({
      key: `${r.unit}-${r.effect_type}-${r.assumed_n}`,
      label: `${r.article} · ${r.species_group}`,
      sub: `${TYPE_LABEL[r.effect_type] ?? r.effect_type} · ${r.definition}`.slice(0, 60),
      y: 30 + i * ROW_H,
      cx: scale(clamp(r.effect)),
      x1: scale(clamp(r.ci_lo ?? r.effect)),
      x2: scale(clamp(r.ci_hi ?? r.effect)),
      value: `${fmt(r.effect)} (${fmt(r.ci_lo)} to ${fmt(r.ci_hi)})${r.n ? ', n ' + r.n : ''}${r.assumed_n ? ' · n split assumed' : ''}`,
      dashed: r.assumed_n,
    }));
    return {
      title, axis, zero: scale(zero), lines, height: 30 + rows.length * ROW_H + 30,
      ticks: ticks.map(t => ({ x: scale(t), label: String(t) })),
    };
  }

  protected readonly forest = computed<ForestPanel[]>(() => {
    const e = this.effects() ?? [];
    const g = e.filter(r => r.effect_type === 'hedges_g_log_load');
    const rho = e.filter(r => r.effect_type === 'rho' || r.effect_type === 'r' || r.effect_type === 'rho_antibody');
    const or = e.filter(r => r.effect_type === 'odds_ratio_smear_positive');
    const panels: ForestPanel[] = [];
    if (g.length) {
      panels.push(this.panel('Standardised difference in log load, severe minus comparison', 'Hedges g (below 0: lower load in the severe group)',
        g, -2, 2, 0, [-2, -1, 0, 1, 2]));
    }
    if (rho.length) {
      panels.push(this.panel('Correlation with a continuous severity measure', 'Correlation coefficient', rho, -1, 1, 0, [-1, -0.5, 0, 0.5, 1]));
    }
    if (or.length) {
      panels.push(this.panel('Detectable load (smear positive), complicated vs uncomplicated', 'Odds ratio (log scale)',
        or, 0.1, 10, 1, [0.1, 0.3, 1, 3, 10], v => Math.log10(v)));
    }
    return panels;
  });

  protected readonly cellColumns: FsGridColumn<LoadCell>[] = [
    { dataField: 'species_group', caption: 'Species', width: 120 },
    { dataField: 'outcome_class', caption: 'Outcome class', width: 160 },
    { dataField: 'units', caption: 'Units', width: 70, alignment: 'right' },
    { dataField: 'unit_ids', caption: 'Unit IDs', width: 130, calculateCellValue: (r: LoadCell) => r.unit_ids.join(', ') },
    { dataField: 'definitions', caption: 'Definitions', width: 100, alignment: 'right' },
    { dataField: 'units_with_g', caption: 'With g', width: 75, alignment: 'right' },
    { dataField: 'pooled', caption: 'Pooled', width: 80, calculateCellValue: (r: LoadCell) => (r.pooled ? 'yes' : 'no') },
    { dataField: 'reason', caption: 'Why', minWidth: 260 },
  ];

  protected readonly tableColumns: FsGridColumn<LoadOutcomeRow>[] = [
    { dataField: 'article', caption: 'Article', width: 80 },
    { dataField: 'unit', caption: 'Unit', width: 70 },
    { dataField: 'species_group', caption: 'Species', width: 105 },
    { dataField: 'definition', caption: 'Outcome definition', minWidth: 220 },
    { dataField: 'n_total', caption: 'n', width: 60, alignment: 'right' },
    { dataField: 'severe_value', caption: 'Severe', width: 130 },
    { dataField: 'comparison_value', caption: 'Comparison', width: 150 },
    { dataField: 'direction', caption: 'Direction', width: 150 },
    { dataField: 'significant', caption: 'Significant', width: 100 },
    { dataField: 'load_method', caption: 'Load method', width: 150 },
    { dataField: 'sample_timing', caption: 'Sample timing', width: 130 },
    { dataField: 'effect', caption: 'Effect (95% CI)', width: 170,
      calculateCellValue: (r: LoadOutcomeRow) => r.effect === null ? '–' : `${fmt(r.effect)} (${fmt(r.ci_lo)} to ${fmt(r.ci_hi)})` },
    { dataField: 'detectable', caption: 'Detectable at 80%', width: 135, alignment: 'right',
      calculateCellValue: (r: LoadOutcomeRow) => fmt(r.detectable) },
    { dataField: 'euthanasia_included', caption: 'Euthanasia in death', width: 140 },
  ];

  protected readonly lowColumns: FsGridColumn<LowLoadItem>[] = [
    { dataField: 'kind', caption: 'Kind', width: 210 },
    { dataField: 'article', caption: 'Article', width: 80 },
    { dataField: 'species', caption: 'Species', width: 150 },
    { dataField: 'design', caption: 'Design or definition', minWidth: 200 },
    { dataField: 'n_dogs', caption: 'Dogs', width: 70, alignment: 'right' },
    { dataField: 'source_level', caption: 'Source', width: 150 },
    { dataField: 'statement', caption: 'Result (paraphrased)', minWidth: 320 },
    { dataField: 'doi', caption: 'DOI', width: 260 },
  ];

  protected readonly damageUnitColumns: FsGridColumn<DamageUnit>[] = [
    { dataField: 'article', caption: 'Article', width: 80 },
    { dataField: 'unit', caption: 'Unit', width: 70 },
    { dataField: 'species_group', caption: 'Species', width: 110 },
    { dataField: 'definition', caption: 'Load groups', minWidth: 220 },
    { dataField: 'rows', caption: 'Markers', width: 80, alignment: 'right' },
    { dataField: 'worse_with_load', caption: 'Worse at high load', width: 140, alignment: 'right' },
    { dataField: 'better_with_load', caption: 'Better at high load', width: 140, alignment: 'right' },
    { dataField: 'no_difference', caption: 'No difference', width: 110, alignment: 'right' },
  ];

  protected readonly damageColumns: FsGridColumn<DamageRow>[] = [
    { dataField: 'article', caption: 'Article', width: 80 },
    { dataField: 'marker', caption: 'Marker', minWidth: 170 },
    { dataField: 'high_value', caption: 'High load', width: 120 },
    { dataField: 'low_value', caption: 'Low load', width: 120 },
    { dataField: 'direction', caption: 'Direction', width: 150 },
    { dataField: 'effect', caption: 'Effect (95% CI)', width: 190,
      calculateCellValue: (r: DamageRow) => r.effect === null ? '–'
        : `${r.effect_type === 'hedges_g' ? 'g' : r.effect_type ?? ''} ${fmt(r.effect)}${r.ci_lo !== null ? ` (${fmt(r.ci_lo)} to ${fmt(r.ci_hi)})` : ''}` },
    { dataField: 'flag', caption: 'Flag', minWidth: 200 },
  ];

  protected readonly sensitivityColumns: FsGridColumn<SensitivityRow>[] = [
    { dataField: 'check', caption: 'Check', width: 230 },
    { dataField: 'article', caption: 'Article', width: 80 },
    { dataField: 'species_group', caption: 'Species', width: 110 },
    { dataField: 'effect_type', caption: 'Effect', width: 150 },
    { dataField: 'effect', caption: 'Value (95% CI)', width: 170,
      calculateCellValue: (r: SensitivityRow) => r.effect === null ? '–'
        : `${fmt(r.effect)}${r.ci_lo !== null ? ` (${fmt(r.ci_lo)} to ${fmt(r.ci_hi)})` : ''}` },
    { dataField: 'note', caption: 'Note', minWidth: 300 },
  ];

  protected readonly pager: FsGridPager = { visible: true, showPageSizeSelector: true, allowedPageSizes: [10, 30, 100], showInfo: true };
}
