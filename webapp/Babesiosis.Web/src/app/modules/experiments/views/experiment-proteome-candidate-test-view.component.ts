import { ChangeDetectionStrategy, Component, computed, input, signal } from '@angular/core';
import { FsBadgeComponent, FsCardComponent, FsDataGridComponent, FsGridColumn } from '@core';
import { ExperimentDetailViewModel, parsePayload } from 'app/modules/experiments/viewmodels/experiment.viewmodel';

// ---- Payloads written by /experiments/SV-06/b/scripts/build_load.py ---------------------------

/** One candidate protein: complicated against uncomplicated, plex-stratified. */
interface CandidateRow {
  key: string;
  protein: string;
  accession: string;
  mechanism: string;
  role: 'mechanism' | 'positive_control' | 'secondary';
  expected_direction: string;
  coverage_rule: string;
  n_comp: number;
  n_unc: number;
  n_ctrl: number;
  plexes_observed: string[];
  tested: boolean;
  median_comp?: number | null;
  median_unc?: number | null;
  median_ctrl?: number | null;
  delta?: number | null;
  delta_lo?: number | null;
  delta_hi?: number | null;
  hl_log2?: number | null;
  hl_lo?: number | null;
  hl_hi?: number | null;
  hl_sd_units?: number | null;
  p_stratified?: number | null;
  q_bh?: number | null;
  presence_fisher_p?: number | null;
  detectable_sd_a05?: number | null;
  detectable_sd_a005?: number | null;
}

/** `primary_result`. */
interface PrimaryPayload {
  label: string;
  verdict: string;
  statistic: string;
  dataset: string;
  independent_sources: number;
  sources: string[];
  n_comp: number;
  n_unc: number;
  n_ctrl: number;
  family_size: number;
  n_tested: number;
  n_q05: number;
  n_p05: number;
  positive_controls_consistent: boolean;
  positive_controls: { protein: string; delta: number; delta_lo: number; delta_hi: number; p: number; q: number }[];
  best: CandidateRow;
  best_mechanism: CandidateRow;
  headline: string;
  caveats: string[];
}

/** `candidate_tests` and `secondary`. */
interface RowsPayload {
  rows: CandidateRow[];
  footnote: string;
}

/** `dog_values`. */
interface DogValuesPayload {
  proteins: { key: string; label: string; in_family: boolean;
    points: { dog_id: string; plex: string; group: 'complicated' | 'uncomplicated' | 'control'; value: number | null }[] }[];
  footnote: string;
}

/** `sensitivity`. */
interface SensitivityPayload {
  rows: {
    key: string; protein: string; tested: boolean; in_family?: boolean;
    delta?: number; p_stratified?: number; delta_unstratified?: number; p_unstratified?: number;
    lopo_min?: number; lopo_max?: number; lopo_sign_change?: boolean;
    delta_infected_vs_control?: number | null; p_infected_vs_control?: number | null;
    rho_with_hbb?: number | null; n_rho?: number;
  }[];
  footnote: string;
}

/** `master_check`. */
interface MasterCheckPayload {
  rows: { candidate: string; named_accessions: string[]; named_status: string[]; quantity_accession: string;
    quantity_description: string; quantity_gene: string; coverage_pct: string; unique_peptides: number; psms: number;
    same_abundances_as_named: boolean; check: string; in_family: boolean }[];
  footnote: string;
}

/** `plex_layout`. */
interface PlexPayload {
  rows: { plex: string; complicated: number; uncomplicated: number; control: number }[];
  footnote: string;
}

/** Result kinds this view renders (the page hides them from its raw-JSON list). */
export const PROTEOME_CANDIDATE_TEST_RESULT_KINDS = ['interpretation', 'primary_result', 'candidate_tests', 'dog_values',
  'sensitivity', 'secondary', 'master_check', 'plex_layout'];

function signed(v: number | null | undefined, digits = 2): string {
  return v === null || v === undefined ? '–' : `${v > 0 ? '+' : ''}${v.toFixed(digits)}`;
}

function fixed(v: number | null | undefined, digits = 2): string {
  return v === null || v === undefined ? '–' : v.toFixed(digits);
}

function pText(p: number | null | undefined): string {
  return p === null || p === undefined ? '–' : p < 0.001 ? '< 0.001' : p.toFixed(3);
}

const ROLE_LABEL: Record<string, string> = {
  mechanism: 'Mechanism candidate',
  positive_control: 'Positive control (CB112)',
  secondary: 'Secondary, outside the family',
};

/** Forest plot geometry: Cliff's delta on a fixed axis from -1 to +1. */
const FOREST = { width: 360, height: 26, pad: 10 };

interface ForestRow {
  key: string;
  protein: string;
  role: string;
  n: string;
  effect: string;
  hl: string;
  medians: string;
  p: string;
  q: string;
  coverage: string;
  mechanism: string;
  tested: boolean;
  excludesZero: boolean;
  control: boolean;
  x: number;
  x1: number;
  x2: number;
}

function xDelta(v: number | null | undefined): number {
  const d = Math.max(-1, Math.min(1, v ?? 0));
  return FOREST.pad + ((d + 1) / 2) * (FOREST.width - 2 * FOREST.pad);
}

function toForestRow(r: CandidateRow): ForestRow {
  const tested = r.tested && r.delta !== null && r.delta !== undefined;
  return {
    key: r.key,
    protein: r.protein,
    role: ROLE_LABEL[r.role] ?? r.role,
    n: `${r.n_comp} vs ${r.n_unc}`,
    effect: tested ? `${signed(r.delta)} (${signed(r.delta_lo)} to ${signed(r.delta_hi)})` : 'not tested',
    hl: tested ? `${signed(r.hl_log2)} (${signed(r.hl_lo)} to ${signed(r.hl_hi)})` : '–',
    medians: tested ? `${fixed(r.median_comp)} / ${fixed(r.median_unc)} / ${fixed(r.median_ctrl)}` : '–',
    p: tested ? pText(r.p_stratified) : '–',
    q: tested ? pText(r.q_bh) : '–',
    coverage: tested
      ? `${r.coverage_rule}; plexes ${r.plexes_observed.length} of 11; detectable ${fixed(r.detectable_sd_a05, 1)} SD`
      : `fewer than 3 dogs in a group (plexes ${r.plexes_observed.join(', ')})`,
    mechanism: r.mechanism,
    tested,
    excludesZero: tested && ((r.delta_lo ?? 0) > 0 || (r.delta_hi ?? 0) < 0),
    control: r.role === 'positive_control',
    x: xDelta(r.delta),
    x1: xDelta(r.delta_lo),
    x2: xDelta(r.delta_hi),
  };
}

/** Strip plot geometry. */
const STRIP = { width: 520, height: 260, left: 52, right: 12, top: 12, bottom: 34 };
const GROUPS: { key: 'uncomplicated' | 'complicated' | 'control'; label: string }[] = [
  { key: 'uncomplicated', label: 'Uncomplicated' },
  { key: 'complicated', label: 'Complicated' },
  { key: 'control', label: 'Controls' },
];

/**
 * The proteome candidate-test view (SV-06b): the primary verdict and positive controls, a forest plot of
 * Cliff's delta for each protein of the fixed family, the values by dog for a chosen protein, the
 * sensitivity checks, the master-protein check and the plex layout. The page renders the explanation after it.
 */
@Component({
  selector: 'fs-experiment-proteome-candidate-test-view',
  standalone: true,
  imports: [FsBadgeComponent, FsCardComponent, FsDataGridComponent],
  templateUrl: './experiment-proteome-candidate-test-view.component.html',
  styleUrls: ['./experiment-proteome-candidate-test-view.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExperimentProteomeCandidateTestViewComponent {
  readonly detail = input.required<ExperimentDetailViewModel>();

  protected readonly forest = FOREST;
  protected readonly strip = STRIP;
  protected readonly zeroX = xDelta(0);
  protected readonly ticks = [-1, -0.5, 0, 0.5, 1].map(v => ({ v, x: xDelta(v), label: signed(v, 1).replace('+0.0', '0') }));

  private find<T>(kind: string): T | null {
    return parsePayload<T>(this.detail().results.find(r => r.kind === kind));
  }

  protected readonly primary = computed(() => this.find<PrimaryPayload>('primary_result'));
  protected readonly tests = computed(() => this.find<RowsPayload>('candidate_tests'));
  protected readonly secondaryPayload = computed(() => this.find<RowsPayload>('secondary'));
  protected readonly dogs = computed(() => this.find<DogValuesPayload>('dog_values'));
  protected readonly sens = computed(() => this.find<SensitivityPayload>('sensitivity'));
  protected readonly master = computed(() => this.find<MasterCheckPayload>('master_check'));
  protected readonly plex = computed(() => this.find<PlexPayload>('plex_layout'));

  protected readonly forestRows = computed(() => (this.tests()?.rows ?? []).map(toForestRow));
  protected readonly secondaryRows = computed(() => (this.secondaryPayload()?.rows ?? []).map(toForestRow));

  protected readonly verdictIntent = computed(() => (this.primary()?.verdict === 'Supported' ? 'success' as const : 'info' as const));

  protected readonly forestColumns: FsGridColumn<ForestRow>[] = [
    { dataField: 'protein', caption: 'Protein', minWidth: 200 },
    { dataField: 'role', caption: 'Role', width: 190 },
    { dataField: 'n', caption: 'n (compl. vs uncompl.)', width: 150, alignment: 'right' },
    { dataField: 'effect', caption: "Cliff's delta (95% CI)", width: 190, alignment: 'right' },
    { dataField: 'hl', caption: 'HL shift, log2 (95% CI)', width: 190, alignment: 'right' },
    { dataField: 'medians', caption: 'Median compl. / uncompl. / controls', width: 230, alignment: 'right' },
    { dataField: 'p', caption: 'p (plex-stratified)', width: 130, alignment: 'right' },
    { dataField: 'q', caption: 'BH q', width: 80, alignment: 'right' },
    { dataField: 'coverage', caption: 'Coverage', minWidth: 260 },
  ];

  // ---- Values by dog -----------------------------------------------------------------------
  protected readonly selected = signal('hbb');
  protected readonly proteinTabs = computed(() => (this.dogs()?.proteins ?? []).map(p => ({ key: p.key, label: p.label })));
  protected readonly selectedProtein = computed(() =>
    this.dogs()?.proteins.find(p => p.key === this.selected()) ?? this.dogs()?.proteins[0] ?? null);

  protected readonly stripPlot = computed(() => {
    const p = this.selectedProtein();
    if (!p) {
      return null;
    }
    const vals = p.points.map(pt => pt.value).filter((v): v is number => v !== null);
    if (!vals.length) {
      return { label: p.label, points: [], yTicks: [], groups: [], missing: p.points.length };
    }
    let lo = Math.min(...vals);
    let hi = Math.max(...vals);
    if (hi - lo < 1e-6) {
      lo -= 0.5; hi += 0.5;
    }
    const padY = (hi - lo) * 0.08;
    lo -= padY; hi += padY;
    const plotH = STRIP.height - STRIP.top - STRIP.bottom;
    const plotW = STRIP.width - STRIP.left - STRIP.right;
    const colW = plotW / GROUPS.length;
    const y = (v: number) => STRIP.top + (1 - (v - lo) / (hi - lo)) * plotH;
    const groups = GROUPS.map((g, i) => {
      const gv = p.points.filter(pt => pt.group === g.key && pt.value !== null).map(pt => pt.value as number).sort((a, b) => a - b);
      const med = gv.length ? (gv.length % 2 ? gv[(gv.length - 1) / 2] : (gv[gv.length / 2 - 1] + gv[gv.length / 2]) / 2) : null;
      const cx = STRIP.left + colW * (i + 0.5);
      return { key: g.key, label: `${g.label} (n ${gv.length})`, cx, medY: med === null ? null : y(med), med,
        x1: cx - colW * 0.3, x2: cx + colW * 0.3 };
    });
    const counters: Record<string, number> = {};
    const points = p.points.filter(pt => pt.value !== null).map(pt => {
      const gi = GROUPS.findIndex(g => g.key === pt.group);
      const k = pt.group;
      counters[k] = (counters[k] ?? 0) + 1;
      // deterministic horizontal jitter from the order of the dog in its group
      const jitter = (((counters[k] * 37) % 17) / 16 - 0.5) * colW * 0.45;
      return { id: pt.dog_id, group: pt.group, cx: STRIP.left + colW * (gi + 0.5) + jitter, cy: y(pt.value as number),
        title: `${pt.dog_id} · plex ${pt.plex} · ${fixed(pt.value, 3)}` };
    });
    const step = (hi - lo) / 4;
    const yTicks = [0, 1, 2, 3, 4].map(i => {
      const v = lo + i * step;
      return { y: y(v), label: v.toFixed(2) };
    });
    return { label: p.label, points, yTicks, groups, missing: p.points.filter(pt => pt.value === null).length };
  });

  protected fmtSigned(v: number | null | undefined): string {
    return signed(v);
  }

  protected fmtP(p: number | null | undefined): string {
    return pText(p);
  }

  protected selectProtein(key: string): void {
    this.selected.set(key);
  }

  // ---- Sensitivity, master check, plex layout ---------------------------------------------
  protected readonly sensRows = computed(() => (this.sens()?.rows ?? []).map(r => ({
    key: r.key,
    protein: r.protein + (r.in_family === false ? ' (secondary)' : ''),
    primary: r.tested ? `${signed(r.delta)}, p ${pText(r.p_stratified)}` : 'not tested',
    unstrat: r.tested ? `${signed(r.delta_unstratified)}, p ${pText(r.p_unstratified)}` : '–',
    lopo: r.tested ? `${signed(r.lopo_min)} to ${signed(r.lopo_max)}${r.lopo_sign_change ? ' (sign changes)' : ''}` : '–',
    ivc: r.tested ? `${signed(r.delta_infected_vs_control)}, p ${pText(r.p_infected_vs_control)}` : '–',
    rho: r.tested ? `${signed(r.rho_with_hbb)} (n ${r.n_rho})` : '–',
  })));
  protected readonly sensColumns: FsGridColumn<Record<string, string>>[] = [
    { dataField: 'protein', caption: 'Protein', minWidth: 200 },
    { dataField: 'primary', caption: 'Primary: delta, p', width: 150, alignment: 'right' },
    { dataField: 'unstrat', caption: 'S1 unstratified', width: 150, alignment: 'right' },
    { dataField: 'lopo', caption: 'S2 leave one plex out', width: 200, alignment: 'right' },
    { dataField: 'ivc', caption: 'S3 infected vs controls', width: 180, alignment: 'right' },
    { dataField: 'rho', caption: 'S5 rho with Hb beta', width: 150, alignment: 'right' },
  ];

  protected readonly masterRows = computed(() => (this.master()?.rows ?? []).map(r => ({
    candidate: r.candidate,
    named: r.named_accessions.map((a, i) => `${a} (${r.named_status[i] === 'IsMasterProtein' ? 'master' : 'candidate'})`).join(', '),
    quantity: `${r.quantity_accession} · ${r.quantity_gene || 'no gene'} · ${r.quantity_description}`,
    quality: `${r.coverage_pct}% coverage, ${r.unique_peptides} unique peptide${r.unique_peptides === 1 ? '' : 's'}, ${r.psms} PSMs`,
    check: r.check,
    family: r.in_family ? 'yes' : 'no',
  })));
  protected readonly masterColumns: FsGridColumn<Record<string, string>>[] = [
    { dataField: 'candidate', caption: 'Candidate', width: 170 },
    { dataField: 'named', caption: 'Named accessions', minWidth: 240 },
    { dataField: 'quantity', caption: 'Quantity used', minWidth: 280 },
    { dataField: 'quality', caption: 'Identification', width: 260 },
    { dataField: 'check', caption: 'Master check', minWidth: 240 },
    { dataField: 'family', caption: 'In family', width: 90 },
  ];

  protected readonly plexColumns: FsGridColumn<Record<string, unknown>>[] = [
    { dataField: 'plex', caption: 'Plex', width: 80 },
    { dataField: 'complicated', caption: 'Complicated', width: 120, alignment: 'right' },
    { dataField: 'uncomplicated', caption: 'Uncomplicated', width: 130, alignment: 'right' },
    { dataField: 'control', caption: 'Controls', width: 100, alignment: 'right' },
  ];
}
