import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';
import { FsBadgeComponent, FsBadgeIntent } from '@core';

export interface LeadForestRow {
  source: string;
  species: string;
  measure: string;
  n: string;
  oriented_effect: number | null;
  ci_low: number | null;
  ci_high: number | null;
  p: number | null;
  circular: string;
  known_driver: string;
}

export interface HumanChip {
  disease: string;
  agrees: boolean;
  doi: string;
  claim: string;
}

/** One research lead, as `build_load.py` writes it to the `leads` payload. */
export interface LeadCard {
  rank: number;
  tier: string;
  kind: string;
  lead_id: string;
  candidate_id: string;
  short_name: string;
  hypothesis: string;
  evidence: string;
  human_counterpart: string;
  human_doi: string[];
  parallel_new: string;
  refuted_by: string;
  next_existing: string;
  next_new_dogs: string;
  minimum_dataset: string;
  forest: LeadForestRow[];
  combined: string;
  canine_line: string;
  human: HumanChip[];
  refuted_short: string;
  existing_short: string;
  new_short: string;
  md_short: string;
  refutation_verdict: string;
}

const TIER_INTENT: Record<string, FsBadgeIntent> = { A: 'success', B: 'primary', C: 'info', D: 'warning', X: 'secondary' };
const FW = 300;
const FH = 22;
const FP = 10;

function fx(v: number): number {
  const c = Math.max(-1, Math.min(1, v));
  return FP + ((c + 1) / 2) * (FW - 2 * FP);
}

function fmt(v: number | null | undefined): string {
  return v === null || v === undefined ? '–' : v.toFixed(2);
}

/** The card of one lead: hypothesis, canine evidence (forest or "no canine data"), human chips, next steps; long text in Details. */
@Component({
  selector: 'fs-meta-lead-card',
  standalone: true,
  imports: [FsBadgeComponent],
  templateUrl: './meta-lead-card.component.html',
  styleUrls: ['./meta-lead-card.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MetaLeadCardComponent {
  readonly lead = input.required<LeadCard>();

  protected readonly fw = FW;
  protected readonly fh = FH;
  protected readonly zeroX = fx(0);
  protected readonly ticks = [-1, -0.5, 0, 0.5, 1].map(v => ({ v, x: fx(v), label: v.toFixed(1) }));

  protected readonly rows = computed(() => this.lead().forest.map((r, i) => {
    const hasCi = r.ci_low !== null && r.ci_high !== null;
    const e = r.oriented_effect ?? 0;
    return {
      ...r, id: i, hasCi, x: fx(e), x1: hasCi ? fx(r.ci_low!) : fx(e), x2: hasCi ? fx(r.ci_high!) : fx(e),
      strong: hasCi && (r.ci_low! > 0 || r.ci_high! < 0),
      text: `${fmt(r.oriented_effect)}${hasCi ? ` (${fmt(r.ci_low)} to ${fmt(r.ci_high)})` : ''} · n ${r.n}`,
    };
  }));

  protected readonly agreeCount = computed(() => this.lead().human.filter(h => h.agrees).length);

  protected tierIntent(t: string): FsBadgeIntent {
    return TIER_INTENT[t] ?? 'secondary';
  }

  protected doiLink(doi: string): string {
    return `https://doi.org/${doi}`;
  }
}
