import { ChangeDetectionStrategy, Component, computed, input, signal } from '@angular/core';
import { FsBadgeComponent, FsBadgeIntent, FsCardComponent, FsDataGridComponent, FsGridColumn, FsTabItem, FsTabsComponent } from '@core';
import { ExperimentDetailViewModel, parsePayload } from 'app/modules/experiments/viewmodels/experiment.viewmodel';
import { EvidenceMapPayload, MetaEvidenceMapComponent } from 'app/modules/experiments/views/meta-review/meta-evidence-map.component';
import { LeadCard, MetaLeadCardComponent } from 'app/modules/experiments/views/meta-review/meta-lead-card.component';

/** The result kinds that this view draws (SV-META, method `meta_review`). */
export const META_REVIEW_RESULT_KINDS: readonly string[] = ['primary_result', 'evidence_map', 'leads', 'themes', 'candidates', 'census', 'refutation'];

interface TierCount {
  tier: string;
  n: number;
  label: string;
  definition: string;
}

interface PrimaryPayload {
  headline: string;
  answer: string;
  tier_counts: TierCount[];
  n_candidates: number;
  n_census_rows: number;
  n_census_tests: number;
  n_census_pass: number;
  m_themes: number;
  n_leads: number;
  caveat: string;
}

interface ThemeRow {
  theme: string;
  theme_label: string;
  row_type: string;
  source: string;
  species: string;
  measure: string;
  n: string;
  oriented_effect: number | null;
  ci_low: number | null;
  ci_high: number | null;
  p: number | null;
  q_themes: number | null;
  loso_max_p: number | null;
  sources_in_direction: string;
  circular: string;
  known_driver: string;
  literature_calls: string;
  scale: string;
}

interface ThemesPayload {
  rows: ThemeRow[];
  footnote: string;
}

interface CandidateRow {
  id: string;
  label: string;
  tier: string;
  provisional_tier: string;
  kind: string;
  evidence: string;
  novelty_where: string;
  refutation_verdict: string;
  refutation_reason: string;
}

interface CensusRow {
  row_id: string;
  experiment: string;
  measure: string;
  comparison: string;
  dataset: string;
  source: string;
  n: string;
  effect: string;
  ci: string;
  p: string;
  q: string;
  role: string;
  screen: string;
  tier: string;
  candidates: string;
  file: string;
}

interface RefutationRow {
  candidate_id: string;
  by: string;
  reason_tested: string;
  result: string;
  rejects: string;
}

const TIER_INTENT: Record<string, FsBadgeIntent> = { A: 'success', B: 'primary', C: 'info', D: 'warning', X: 'secondary' };

/** Forest geometry: effect from -1 to +1 on Cliff's delta / rho scale. */
const FOREST = { width: 320, height: 22, pad: 10 };

interface ForestRow extends ThemeRow {
  id: string;
  x: number;
  x1: number;
  x2: number;
  hasCi: boolean;
  strong: boolean;
  effectText: string;
}

function xOf(v: number): number {
  const c = Math.max(-1, Math.min(1, v));
  return FOREST.pad + ((c + 1) / 2) * (FOREST.width - 2 * FOREST.pad);
}

function fmt(v: number | null | undefined, d = 2): string {
  return v === null || v === undefined ? '–' : v.toFixed(d);
}

function fmtP(v: number | null | undefined): string {
  if (v === null || v === undefined) {
    return '–';
  }
  return v < 0.001 ? v.toExponential(1) : v.toFixed(3);
}

/**
 * The meta-review view (SV-META): a one-line headline with the tier counts; the evidence map of all candidates (canine evidence
 * against human evidence, colour = tier); one tab per research lead and the card of the selected lead only; then the supporting
 * tables (agreement by theme, candidates and refutation, result census) in sections that start closed.
 */
@Component({
  selector: 'fs-experiment-meta-review-view',
  standalone: true,
  imports: [FsBadgeComponent, FsCardComponent, FsDataGridComponent, FsTabsComponent, MetaEvidenceMapComponent, MetaLeadCardComponent],
  templateUrl: './experiment-meta-review-view.component.html',
  styleUrls: ['./experiment-meta-review-view.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExperimentMetaReviewViewComponent {
  readonly detail = input.required<ExperimentDetailViewModel>();

  private payload<T>(kind: string) {
    return computed(() => parsePayload<T>(this.detail().results.find(r => r.kind === kind)));
  }

  protected readonly primary = this.payload<PrimaryPayload>('primary_result');
  protected readonly leads = this.payload<LeadCard[]>('leads');
  protected readonly evidenceMap = this.payload<EvidenceMapPayload>('evidence_map');

  /** The candidate id of the selected lead; null = the first lead. */
  private readonly picked = signal<string | null>(null);
  protected readonly showRejected = signal(false);

  protected readonly leadTabs = computed<FsTabItem[]>(() => (this.leads() ?? []).map(l => ({
    key: l.candidate_id, label: `${l.rank} · ${l.short_name}`, count: `Tier ${l.tier}`,
  })));

  protected readonly activeLead = computed(() => {
    const all = this.leads() ?? [];
    const id = this.picked();
    return all.find(l => l.candidate_id === id) ?? all[0] ?? null;
  });

  protected readonly rejectedCount = computed(() => (this.evidenceMap()?.points ?? []).filter(p => p.lead_rank === null).length);

  protected selectLead(id: string): void {
    this.picked.set(id);
  }

  protected toggleRejected(): void {
    this.showRejected.update(v => !v);
  }
  protected readonly themes = this.payload<ThemesPayload>('themes');
  protected readonly candidates = this.payload<CandidateRow[]>('candidates');
  protected readonly census = this.payload<CensusRow[]>('census');
  protected readonly refutation = this.payload<RefutationRow[]>('refutation');

  protected readonly forest = FOREST;
  protected readonly zeroX = xOf(0);
  protected readonly ticks = [-1, -0.5, 0, 0.5, 1].map(v => ({ v, x: xOf(v), label: v.toFixed(1) }));

  /** Themes grouped, each with its indicator rows (forest) and its combined rows (text). */
  protected readonly themeGroups = computed(() => {
    const rows = this.themes()?.rows ?? [];
    const order: string[] = [];
    const byTheme = new Map<string, ThemeRow[]>();
    for (const r of rows) {
      if (!byTheme.has(r.theme)) {
        byTheme.set(r.theme, []);
        order.push(r.theme);
      }
      byTheme.get(r.theme)!.push(r);
    }
    return order.map(t => {
      const all = byTheme.get(t)!;
      const indicators: ForestRow[] = all.filter(r => r.row_type === 'indicator').map((r, i) => {
        const hasCi = r.ci_low !== null && r.ci_high !== null;
        const e = r.oriented_effect ?? 0;
        return {
          ...r,
          id: `${t}-${i}`,
          x: xOf(e),
          x1: hasCi ? xOf(r.ci_low!) : xOf(e),
          x2: hasCi ? xOf(r.ci_high!) : xOf(e),
          hasCi,
          strong: hasCi && (r.ci_low! > 0 || r.ci_high! < 0),
          effectText: `${fmt(r.oriented_effect)}${hasCi ? ` (${fmt(r.ci_low)} to ${fmt(r.ci_high)})` : ''} · p ${fmtP(r.p)}`,
        };
      });
      const combined = all.filter(r => r.row_type === 'combined');
      const literature = all.find(r => r.literature_calls)?.literature_calls ?? '';
      return { theme: t, label: all[0].theme_label, indicators, combined, literature, literatureOnly: all.some(r => r.row_type === 'literature_only') };
    });
  });

  protected readonly tierFilter = signal<string>('');
  protected readonly experimentFilter = signal<string>('');

  protected readonly experiments = computed(() => Array.from(new Set((this.census() ?? []).map(r => r.experiment))).sort());

  protected readonly censusRows = computed(() => {
    const t = this.tierFilter();
    const e = this.experimentFilter();
    return (this.census() ?? []).filter(r => (!t || (t === 'none' ? !r.tier : r.tier === t)) && (!e || r.experiment === e));
  });

  protected readonly censusColumns: FsGridColumn<CensusRow>[] = [
    { dataField: 'row_id', caption: 'Row', width: 70 },
    { dataField: 'experiment', caption: 'Experiment', width: 190 },
    { dataField: 'measure', caption: 'Measure', minWidth: 220 },
    { dataField: 'comparison', caption: 'Comparison', minWidth: 180 },
    { dataField: 'dataset', caption: 'Dataset', width: 110 },
    { dataField: 'source', caption: 'Source', width: 90 },
    { dataField: 'n', caption: 'n', width: 80 },
    { dataField: 'effect', caption: 'Effect', width: 90 },
    { dataField: 'ci', caption: '95% CI', width: 130 },
    { dataField: 'p', caption: 'p', width: 70 },
    { dataField: 'q', caption: 'q', width: 70 },
    { dataField: 'screen', caption: 'Screen', width: 70 },
    { dataField: 'tier', caption: 'Tier', width: 55 },
    { dataField: 'candidates', caption: 'Candidate', width: 85 },
    { dataField: 'file', caption: 'File:line', minWidth: 200 },
  ];

  protected readonly candidateColumns: FsGridColumn<CandidateRow>[] = [
    { dataField: 'id', caption: 'ID', width: 55 },
    { dataField: 'tier', caption: 'Tier', width: 55 },
    { dataField: 'label', caption: 'Candidate', minWidth: 240 },
    { dataField: 'kind', caption: 'Kind', width: 140 },
    { dataField: 'evidence', caption: 'Evidence', minWidth: 280 },
    { dataField: 'novelty_where', caption: 'Novelty check', minWidth: 260 },
    { dataField: 'refutation_verdict', caption: 'Refutation', width: 130 },
    { dataField: 'refutation_reason', caption: 'Why', minWidth: 280 },
  ];

  protected readonly refutationRows = computed(() => (this.refutation() ?? []).map((r, i) => ({ ...r, id: i })));

  protected readonly refutationColumns: FsGridColumn<Record<string, unknown>>[] = [
    { dataField: 'candidate_id', caption: 'Candidate', width: 85 },
    { dataField: 'by', caption: 'By', width: 150 },
    { dataField: 'reason_tested', caption: 'Reason tested', minWidth: 200 },
    { dataField: 'result', caption: 'Result', minWidth: 420 },
    { dataField: 'rejects', caption: 'Rejects', width: 70 },
  ];

  protected tierIntent(t: string): FsBadgeIntent {
    return TIER_INTENT[t] ?? 'secondary';
  }

  protected combinedText(c: ThemeRow): string {
    const q = c.q_themes !== null && c.q_themes !== undefined ? ` · BH q ${fmtP(c.q_themes)}` : '';
    return `${c.species}: ${c.sources_in_direction} sources in the expected direction · Stouffer Z ${fmt(c.oriented_effect)} · p ${fmtP(c.p)}${q} · leave-one-source-out max p ${fmtP(c.loso_max_p)}`;
  }

  protected setTier(v: string): void {
    this.tierFilter.set(v);
  }

  protected setExperiment(v: string): void {
    this.experimentFilter.set(v);
  }

}
