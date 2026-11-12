import { ChangeDetectionStrategy, Component, computed, input, output } from '@angular/core';

/** One candidate on the evidence map. Every value comes from `out/evidence_map.csv` (SV-META `build_load.py`). */
export interface EvidencePoint {
  id: string;
  short_label: string;
  label: string;
  tier: string;
  lead_rank: number | null;
  /** Canine evidence: independent dog-level sources in the expected direction; 0 = gap lead. */
  x: number;
  x_of: number;
  x_basis: string;
  /** Human evidence: verified human records that agree in direction; null = not assessed. */
  y: number | null;
  y_disagree: number | null;
  y_basis: string;
  mixed: boolean;
  slot: number;
  slots: number;
  verdict: string;
}

export interface EvidenceMapPayload {
  points: EvidencePoint[];
  x_title: string;
  y_title: string;
  footnote: string;
}

interface Mark extends EvidencePoint {
  cx: number;
  cy: number;
  r: number;
  isLead: boolean;
  labelText: string;
  labelX: number;
  anchor: 'start' | 'end';
  tip: string;
}

const W = 760;
const H = 460;
const PAD = { left: 70, right: 24, top: 18, bottom: 58 };
/** Vertical spacing of marks that share an (x, y) cell, horizontal spacing inside the not-assessed band (px). */
const STACK_DY = 17;
const STACK_DX = 12;

/**
 * Evidence map of the SV-META candidates: canine evidence (horizontal) against human evidence (vertical), colour = tier.
 * Leads are drawn large and labelled; rejected candidates (tier X) only when `showRejected` is on, dimmed.
 * It is a map of evidence, not a score: there is no probability and no ranking value on it.
 */
@Component({
  selector: 'fs-meta-evidence-map',
  standalone: true,
  templateUrl: './meta-evidence-map.component.html',
  styleUrls: ['./meta-evidence-map.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MetaEvidenceMapComponent {
  readonly data = input.required<EvidenceMapPayload>();
  readonly activeId = input<string | null>(null);
  readonly showRejected = input(false);
  readonly pick = output<string>();

  protected readonly w = W;
  protected readonly h = H;
  protected readonly pad = PAD;

  private readonly domain = computed(() => {
    const pts = this.data().points;
    const xMax = Math.max(1, ...pts.map(p => p.x));
    const yMax = Math.max(1, ...pts.map(p => p.y ?? 0));
    return { xMax, yMax };
  });

  private sx(v: number): number {
    const { xMax } = this.domain();
    const lo = -0.7;
    const hi = xMax + 0.7;
    return PAD.left + ((v - lo) / (hi - lo)) * (W - PAD.left - PAD.right);
  }

  /** y = -1 is the "not assessed" band below zero. */
  private sy(v: number): number {
    const { yMax } = this.domain();
    const lo = -1.6;
    const hi = yMax + 0.7;
    return H - PAD.bottom - ((v - lo) / (hi - lo)) * (H - PAD.top - PAD.bottom);
  }

  protected readonly xTicks = computed(() =>
    Array.from({ length: this.domain().xMax + 1 }, (_, v) => ({ v, x: this.sx(v), label: v === 0 ? '0 (gap)' : String(v) })));

  protected readonly yTicks = computed(() =>
    Array.from({ length: this.domain().yMax + 1 }, (_, v) => ({ v, y: this.sy(v), label: String(v) })));

  protected readonly gapBand = computed(() => ({ x: this.sx(-0.45), w: this.sx(0.45) - this.sx(-0.45), y: PAD.top, h: this.sy(-0.5) - PAD.top }));
  protected readonly naBand = computed(() => ({ x: PAD.left, w: W - PAD.left - PAD.right, y: this.sy(-0.5), h: this.sy(-1.6) - this.sy(-0.5), ly: this.sy(-1) }));
  protected readonly axisY = computed(() => this.sy(-1.6));

  protected readonly marks = computed<Mark[]>(() => {
    const { xMax } = this.domain();
    return this.data().points
      .filter(p => p.lead_rank !== null || this.showRejected())
      .map(p => {
        const isLead = p.lead_rank !== null;
        const offset = p.slot - (p.slots - 1) / 2;
        const na = p.y === null;
        const cx = this.sx(p.x) + (na ? offset * STACK_DX : 0);
        const cy = this.sy(na ? -1 : p.y!) + (na ? 0 : offset * STACK_DY);
        const right = p.x >= xMax - 0.5;
        const tip = `${p.short_label} (${p.id}, tier ${p.tier}${isLead ? ', lead ' + p.lead_rank : ''})\n`
          + `Canine: ${p.x_basis}\nHuman: ${p.y_basis}\nRefutation: ${p.verdict}`;
        return {
          ...p, cx, cy, isLead, r: isLead ? 8 : 5,
          labelText: isLead ? `${p.lead_rank} ${p.short_label}` : '',
          labelX: right ? cx - 13 : cx + 13,
          anchor: right ? 'end' : 'start',
          tip,
        } as Mark;
      })
      // draw rejected first so leads sit on top
      .sort((a, b) => Number(a.isLead) - Number(b.isLead));
  });

  protected readonly tierLegend = ['A', 'B', 'C', 'D', 'X'];

  protected onPick(m: Mark): void {
    if (m.isLead) {
      this.pick.emit(m.id);
    }
  }
}
