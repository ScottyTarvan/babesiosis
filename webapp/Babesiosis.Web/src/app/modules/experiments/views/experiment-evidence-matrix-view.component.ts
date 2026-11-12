import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';
import { FsCardComponent, FsDataGridComponent, FsGridColumn, FsGridPager } from '@core';
import { ExperimentDetailViewModel, parsePayload } from 'app/modules/experiments/viewmodels/experiment.viewmodel';

// ---- Payloads written by /experiments/SV-03/scripts/build_load.py ---------------------------

/** The result kinds this view draws (both SV-03 experiments). */
export const EVIDENCE_MATRIX_RESULT_KINDS: readonly string[] = [
  'matrix_summary', 'evidence_matrix', 'evidence_matrix_collapsed', 'pooling', 'named_conflicts', 'sensitivity',
  'selective_reporting', 'definition_summary', 'definition_components', 'definition_outcome_classes', 'circularity',
  'definition_map',
];

export interface MatrixCell {
  marker: string;
  marker_class: string;
  outcome_class?: string;
  species_group: string;
  units: number;
  tested_units: number;
  H: number;
  L: number;
  N: number;
  X: number;
  U: number;
  D: number;
  consistent: boolean;
  consistent_direction: string | null;
  circular: boolean;
  circular_units: number;
  presumed_species_units: string | null;
  multivariable_units: number;
  unit_calls: string | null;
  S1_tested_units?: number;
  S1_H?: number;
  S1_L?: number;
  S1_consistent?: boolean;
  S4_consistent?: boolean;
  S1_onderstepoort_collapse?: string | null;
  S4_no_circular_units?: string | null;
}

export interface MatrixSummaryPayload {
  tiles: {
    rows: number; articles: number; units: number; markers: number; cells: number; cells_ge2_tested: number;
    cells_ge3_tested: number; largest_cell: number; pooled: number; consistent: number; collapsed_cells_ge3: number;
    collapsed_consistent_ge3_noncircular: number; collapsed_consistent_ge3_noncircular_s1: number;
    opposite_cells: number; within_unit_conflicts: number; species_units: Record<string, number>;
    share_not_significant: number;
  };
  consistent_cells: MatrixCell[];
  collapsed_consistent: MatrixCell[];
  note: string;
}

export interface PooledRow {
  marker: string; outcome_class: string; species_group: string; effect: string; k_units: number;
  estimate: number; ci_low: number; ci_high: number; units: string;
}

export interface PoolingPayload {
  pooled: PooledRow[];
  near_misses: { marker: string; outcome_class: string; species_group: string; effect: string; k_units: number; units: string }[];
  poolable_if_collapsed: { marker: string; species_group: string; effect: string; k_units: number }[];
  usable_rows: number;
}

export interface ConflictRow {
  conflict: string; markers: string; tested_or_flagged_units: number; descriptive_only_units: number;
  H: number; L: number; N: number; X: number; U: number; species_groups: string; verdict: string; pattern: string;
}

export interface ConflictUnit {
  conflict: string; unit: string; articles: string; marker: string; species_group: string; outcome_class: string;
  family: string; call: string; row_calls: string; timing: string; setting: string; circular: boolean;
}

export interface SensitivityRow {
  set: string; cells: number; cells_ge2_tested: number; cells_ge3_tested: number; consistent: number;
  consistent_noncircular: number; consistent_ge3: number; consistent_ge3_noncircular: number;
  cells_with_opposite_significant: number;
}

export interface SelectiveRow {
  id: string; independent_unit: string; rows: number; tested_rows: number; significant_rows: number;
  not_significant_rows: number; share_not_significant: number | null; descriptive_rows: number;
}

export interface SelectivePayload {
  summary: {
    articles_with_tested_rows: number; median_share_not_significant: number; q1: number; q3: number;
    articles_with_no_not_significant_row: number; those_articles: string[]; overall_share_not_significant: number;
  };
  rows: SelectiveRow[];
}

export interface DefinitionSummaryPayload {
  circularity: {
    tested_rows: number; tested_rows_marker_in_definition: number; share_rows: number; units_tested: number;
    units_with_marker_in_definition: number; share_units: number; share_significant_circular: number;
    share_significant_noncircular: number; definitions: number; definition_units: number;
    euthanasia_in_mortality: Record<string, number>; component_count_median: number;
  };
  species_units: Record<string, number>;
}

export interface ComponentRow {
  component?: string;
  outcome_class?: string;
  units_all: number;
  share_of_units?: number;
  [species: string]: string | number | undefined;
}

export interface DefinitionRow {
  id: string; independent_unit: string; species_group: string; setting: string; sample_timing: string;
  outcome_class: string; severity_label: string; components: string; euthanasia_included: string;
  n_rows: number; n_tested_rows: number; n_tested_rows_marker_in_definition: number; markers_in_definition: string | null;
}

/** One stacked bar: units by call for one cell. */
interface Bar {
  key: string;
  label: string;
  sub: string;
  y: number;
  segs: { x: number; w: number; cls: string; n: number }[];
  tag: string;
}

const SPECIES = ['B. rossi', 'B. canis', 'B. gibsoni', 'B. vogeli', 'mixed/unspecified'];
const BAR_LEFT = 260;
const UNIT_W = 34;
const BAR_H = 16;
const ROW_H = 30;

function pct(x: number | null | undefined, digits = 0): string {
  return x === null || x === undefined ? '–' : `${(x * 100).toFixed(digits)}%`;
}

/**
 * The view for SV-03 (method evidence_matrix). Experiment 1: the marker-evidence matrix (primary result first:
 * cells, pooling, consistency), the post-hoc collapsed matrix drawn as stacked bars of independent units by call,
 * pooling, named conflicts, sensitivity and the selective-reporting check. Experiment 2: the definition map.
 * Each card shows only when its payload is present.
 */
@Component({
  selector: 'fs-experiment-evidence-matrix-view',
  standalone: true,
  imports: [FsCardComponent, FsDataGridComponent],
  templateUrl: './experiment-evidence-matrix-view.component.html',
  styleUrls: ['./experiment-evidence-matrix-view.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExperimentEvidenceMatrixViewComponent {
  readonly detail = input.required<ExperimentDetailViewModel>();

  private result<T>(kind: string): T | null {
    return parsePayload<T>(this.detail().results.find(r => r.kind === kind));
  }

  protected readonly pct = pct;
  protected readonly species = SPECIES;
  protected readonly barLeft = BAR_LEFT;

  protected readonly summary = computed(() => this.result<MatrixSummaryPayload>('matrix_summary'));
  protected readonly matrix = computed(() => this.result<{ rows: MatrixCell[]; all_cells: number }>('evidence_matrix'));
  protected readonly collapsed = computed(() => this.result<{ rows: MatrixCell[] }>('evidence_matrix_collapsed')?.rows ?? null);
  protected readonly pooling = computed(() => this.result<PoolingPayload>('pooling'));
  protected readonly conflicts = computed(() => this.result<{ rows: ConflictRow[]; units: ConflictUnit[] }>('named_conflicts'));
  protected readonly sensitivity = computed(() => this.result<{ rows: SensitivityRow[] }>('sensitivity')?.rows ?? null);
  protected readonly selective = computed(() => this.result<SelectivePayload>('selective_reporting'));

  protected readonly defSummary = computed(() => this.result<DefinitionSummaryPayload>('definition_summary'));
  protected readonly components = computed(() => this.result<{ rows: ComponentRow[] }>('definition_components')?.rows ?? null);
  protected readonly outcomeClasses = computed(() => this.result<{ rows: ComponentRow[] }>('definition_outcome_classes')?.rows ?? null);
  protected readonly circularity = computed(() =>
    this.result<{ rows: { marker: string; reason: string; tested_rows: number }[] }>('circularity')?.rows ?? null);
  protected readonly definitions = computed(() => this.result<{ rows: DefinitionRow[] }>('definition_map')?.rows ?? null);

  protected readonly isMatrix = computed(() => this.summary() !== null || this.matrix() !== null);
  protected readonly isDefinitionMap = computed(() => this.defSummary() !== null || this.components() !== null);

  protected readonly speciesUnits = computed(() => {
    const su = this.summary()?.tiles.species_units ?? this.defSummary()?.species_units ?? {};
    return SPECIES.filter(s => su[s]).map(s => `${s} ${su[s]}`).join(' · ');
  });

  /** Stacked bars of the collapsed matrix: cells with 3 or more tested units. */
  protected readonly bars = computed(() => {
    const rows = (this.collapsed() ?? []).filter(r => r.tested_units >= 3);
    const bars: Bar[] = rows.map((r, i) => {
      const parts: [string, number][] = [['h', r.H], ['l', r.L], ['n', r.N], ['x', r.X]];
      let x = BAR_LEFT;
      const segs = parts.filter(([, n]) => n > 0).map(([cls, n]) => {
        const s = { x, w: n * UNIT_W, cls, n };
        x += n * UNIT_W;
        return s;
      });
      const tags = [r.consistent ? `consistent ${r.consistent_direction}` : '', r.circular ? 'circular' : '',
        r.S1_tested_units !== undefined ? `S1: ${r.S1_H ?? 0}H/${r.S1_L ?? 0}L of ${r.S1_tested_units}` : '',
        r.presumed_species_units ? `presumed species: ${r.presumed_species_units}` : ''].filter(t => t);
      return {
        key: `${r.marker}-${r.species_group}`,
        label: r.marker.length > 34 ? r.marker.slice(0, 33) + '…' : r.marker,
        sub: r.species_group,
        y: 24 + i * ROW_H,
        segs,
        tag: tags.join(' · '),
      };
    });
    const maxUnits = Math.max(4, ...rows.map(r => r.H + r.L + r.N + r.X));
    return {
      bars,
      height: 24 + bars.length * ROW_H + 30,
      width: BAR_LEFT + maxUnits * UNIT_W + 330,
      ticks: Array.from({ length: maxUnits + 1 }, (_, k) => ({ x: BAR_LEFT + k * UNIT_W, label: String(k) })),
      tagX: BAR_LEFT + maxUnits * UNIT_W + 10,
      barH: BAR_H,
    };
  });

  /** Component x species heat table. */
  protected readonly heat = computed(() => {
    const rows = this.components() ?? [];
    const max = Math.max(1, ...rows.flatMap(r => SPECIES.map(s => Number(r[s] ?? 0))));
    return rows.map(r => ({
      name: String(r.component ?? r.outcome_class ?? ''),
      all: r.units_all,
      share: r.share_of_units ?? null,
      cells: SPECIES.map(s => {
        const n = Number(r[s] ?? 0);
        return { n, alpha: n === 0 ? 0 : 0.15 + 0.85 * (n / max) };
      }),
    }));
  });

  protected readonly cellColumns: FsGridColumn<MatrixCell>[] = [
    { dataField: 'marker', caption: 'Marker', minWidth: 190 },
    { dataField: 'outcome_class', caption: 'Outcome class', width: 150 },
    { dataField: 'species_group', caption: 'Species', width: 120 },
    { dataField: 'tested_units', caption: 'Tested units', width: 95, alignment: 'right' },
    { dataField: 'H', caption: 'Higher', width: 70, alignment: 'right' },
    { dataField: 'L', caption: 'Lower', width: 70, alignment: 'right' },
    { dataField: 'N', caption: 'Not sig.', width: 75, alignment: 'right' },
    { dataField: 'X', caption: 'Both in unit', width: 95, alignment: 'right' },
    { dataField: 'D', caption: 'Descriptive', width: 90, alignment: 'right' },
    { dataField: 'consistent', caption: 'Consistent', width: 95,
      calculateCellValue: (r: MatrixCell) => (r.consistent ? r.consistent_direction ?? 'yes' : '') },
    { dataField: 'circular', caption: 'Marker in definition', width: 140,
      calculateCellValue: (r: MatrixCell) => (r.circular ? `yes (${r.circular_units})` : '') },
    { dataField: 'unit_calls', caption: 'Unit calls', minWidth: 220 },
  ];

  protected readonly collapsedColumns: FsGridColumn<MatrixCell>[] = [
    { dataField: 'marker', caption: 'Marker', minWidth: 190 },
    { dataField: 'species_group', caption: 'Species', width: 120 },
    { dataField: 'tested_units', caption: 'Tested units', width: 95, alignment: 'right' },
    { dataField: 'H', caption: 'Higher', width: 70, alignment: 'right' },
    { dataField: 'L', caption: 'Lower', width: 70, alignment: 'right' },
    { dataField: 'N', caption: 'Not sig.', width: 75, alignment: 'right' },
    { dataField: 'X', caption: 'Both in unit', width: 95, alignment: 'right' },
    { dataField: 'consistent', caption: 'Consistent', width: 95,
      calculateCellValue: (r: MatrixCell) => (r.consistent ? r.consistent_direction ?? 'yes' : '') },
    { dataField: 'circular', caption: 'Marker in definition', width: 140,
      calculateCellValue: (r: MatrixCell) => (r.circular ? `yes (${r.circular_units})` : '') },
    { dataField: 'S1_consistent', caption: 'Onderstepoort once', width: 140,
      calculateCellValue: (r: MatrixCell) => `${r.S1_H ?? 0}H/${r.S1_L ?? 0}L of ${r.S1_tested_units ?? 0}${r.S1_consistent ? ', consistent' : ''}` },
    { dataField: 'unit_calls', caption: 'Unit calls', minWidth: 260 },
  ];

  protected readonly nearColumns: FsGridColumn<PoolingPayload['near_misses'][number]>[] = [
    { dataField: 'marker', caption: 'Marker', minWidth: 190 },
    { dataField: 'outcome_class', caption: 'Outcome class', width: 150 },
    { dataField: 'species_group', caption: 'Species', width: 120 },
    { dataField: 'effect', caption: 'Effect', width: 150 },
    { dataField: 'k_units', caption: 'Units', width: 70, alignment: 'right' },
    { dataField: 'units', caption: 'Unit IDs', minWidth: 140 },
  ];

  protected readonly poolableColumns: FsGridColumn<PoolingPayload['poolable_if_collapsed'][number]>[] = [
    { dataField: 'marker', caption: 'Marker', minWidth: 190 },
    { dataField: 'species_group', caption: 'Species', width: 120 },
    { dataField: 'effect', caption: 'Effect', width: 150 },
    { dataField: 'k_units', caption: 'Units with a usable summary', width: 200, alignment: 'right' },
  ];

  protected readonly conflictColumns: FsGridColumn<ConflictRow>[] = [
    { dataField: 'conflict', caption: 'Named conflict', width: 190 },
    { dataField: 'tested_or_flagged_units', caption: 'Units tested', width: 100, alignment: 'right' },
    { dataField: 'H', caption: 'Higher', width: 70, alignment: 'right' },
    { dataField: 'L', caption: 'Lower', width: 70, alignment: 'right' },
    { dataField: 'N', caption: 'Not sig.', width: 75, alignment: 'right' },
    { dataField: 'U', caption: 'Unclear', width: 75, alignment: 'right' },
    { dataField: 'species_groups', caption: 'Species', width: 200 },
    { dataField: 'verdict', caption: 'Verdict', minWidth: 230 },
  ];

  protected readonly conflictUnitColumns: FsGridColumn<ConflictUnit>[] = [
    { dataField: 'conflict', caption: 'Conflict', width: 160 },
    { dataField: 'unit', caption: 'Unit', width: 70 },
    { dataField: 'articles', caption: 'Articles', width: 90 },
    { dataField: 'marker', caption: 'Marker', width: 170 },
    { dataField: 'species_group', caption: 'Species', width: 120 },
    { dataField: 'outcome_class', caption: 'Outcome class', width: 150 },
    { dataField: 'call', caption: 'Unit call', width: 80 },
    { dataField: 'row_calls', caption: 'Row calls', width: 90 },
    { dataField: 'timing', caption: 'Timing', width: 130 },
    { dataField: 'setting', caption: 'Setting', width: 150 },
  ];

  protected readonly sensitivityColumns: FsGridColumn<SensitivityRow>[] = [
    { dataField: 'set', caption: 'Set', minWidth: 300 },
    { dataField: 'cells_ge2_tested', caption: 'Cells ≥ 2 units', width: 115, alignment: 'right' },
    { dataField: 'cells_ge3_tested', caption: 'Cells ≥ 3 units', width: 115, alignment: 'right' },
    { dataField: 'consistent', caption: 'Consistent', width: 95, alignment: 'right' },
    { dataField: 'consistent_ge3_noncircular', caption: 'Consistent, ≥ 3 agreeing, not circular', width: 230, alignment: 'right' },
    { dataField: 'cells_with_opposite_significant', caption: 'Opposite directions', width: 140, alignment: 'right' },
  ];

  protected readonly selectiveColumns: FsGridColumn<SelectiveRow>[] = [
    { dataField: 'id', caption: 'Article', width: 80 },
    { dataField: 'independent_unit', caption: 'Unit', width: 70 },
    { dataField: 'rows', caption: 'Rows', width: 70, alignment: 'right' },
    { dataField: 'tested_rows', caption: 'Tested', width: 75, alignment: 'right' },
    { dataField: 'significant_rows', caption: 'Significant', width: 95, alignment: 'right' },
    { dataField: 'not_significant_rows', caption: 'Not sig.', width: 80, alignment: 'right' },
    { dataField: 'share_not_significant', caption: 'Share not sig.', width: 110, alignment: 'right',
      calculateCellValue: (r: SelectiveRow) => pct(r.share_not_significant) },
    { dataField: 'descriptive_rows', caption: 'Descriptive', width: 95, alignment: 'right' },
  ];

  protected readonly circColumns: FsGridColumn<{ marker: string; reason: string; tested_rows: number }>[] = [
    { dataField: 'marker', caption: 'Marker', minWidth: 190 },
    { dataField: 'reason', caption: 'Why it is in the definition', minWidth: 230 },
    { dataField: 'tested_rows', caption: 'Tested rows', width: 100, alignment: 'right' },
  ];

  protected readonly ocColumns: FsGridColumn<ComponentRow>[] = [
    { dataField: 'outcome_class', caption: 'Outcome class', minWidth: 170 },
    { dataField: 'units_all', caption: 'Units', width: 70, alignment: 'right' },
    ...SPECIES.map(s => ({ dataField: s, caption: s, width: 110, alignment: 'right' as const })),
  ];

  protected readonly defColumns: FsGridColumn<DefinitionRow>[] = [
    { dataField: 'id', caption: 'Article', width: 80 },
    { dataField: 'independent_unit', caption: 'Unit', width: 70 },
    { dataField: 'species_group', caption: 'Species', width: 120 },
    { dataField: 'setting', caption: 'Setting', width: 140 },
    { dataField: 'outcome_class', caption: 'Outcome class', width: 150 },
    { dataField: 'severity_label', caption: 'Severity groups', minWidth: 220 },
    { dataField: 'components', caption: 'Components', minWidth: 200 },
    { dataField: 'euthanasia_included', caption: 'Euthanasia', width: 100 },
    { dataField: 'n_tested_rows', caption: 'Tested rows', width: 95, alignment: 'right' },
    { dataField: 'markers_in_definition', caption: 'Markers in own definition', minWidth: 180 },
  ];

  protected readonly pager: FsGridPager = { visible: true, showPageSizeSelector: true, allowedPageSizes: [10, 30, 100], showInfo: true };
}
