/**
 * Client-side timing, off unless a developer turns it on.
 *
 * The switch is `localStorage` rather than `config.json` on purpose: the local
 * config file is untracked, so a flag added there is invisible to everyone else
 * and lost on a fresh clone, and a deployed build would need a release to
 * toggle it. A localStorage key is per-developer, per-browser, survives a reload
 * and needs no rebuild:
 *
 * ```js
 * localStorage.setItem('fs.timings', '1'); // then reload
 * ```
 *
 * The value is read ONCE per page load and cached. Toggling therefore takes a
 * reload, which is deliberate — a flag that can change mid-session produces
 * measurements with a hole in them.
 */

const STORAGE_KEY = 'fs.timings';

let enabled: boolean | null = null;

/** Whether to record and log. Cached after the first call. */
export function timingsEnabled(): boolean {
  if (enabled === null) {
    try {
      enabled = window.localStorage.getItem(STORAGE_KEY) === '1';
    } catch {
      // Private mode, blocked site data, or a non-browser context. Off is the
      // right answer and must never be an exception the caller has to handle.
      enabled = false;
    }
  }
  return enabled;
}

/** One phase of a multi-step measurement. */
export interface TimingPhase {
  readonly label: string;
  readonly durationMs: number;
}

/**
 * A measurement spanning several phases — the shape the manage-data edit cycle
 * needs, where the interesting number is not any single request but the whole
 * commit → save → reload → repaint round.
 *
 * Phases are cumulative slices of one run: each `phase()` call closes the span
 * since the previous one. `total()` is wall clock since `startTimingRun`.
 */
export class TimingRun {
  private readonly startedAt = now();
  private lastAt = this.startedAt;
  private readonly phases: TimingPhase[] = [];

  constructor(private readonly name: string) { }

  /** Closes the span since the last phase (or since the start) under `label`. */
  phase(label: string): void {
    const at = now();
    this.phases.push({ label, durationMs: at - this.lastAt });
    this.lastAt = at;
  }

  /**
   * Closes the run and logs it. Called after a repaint where the caller wants
   * render time included — see the `afterPaint` helper below.
   */
  end(): void {
    const total = now() - this.startedAt;
    const rows: Record<string, { ms: number }> = {};
    for (const phase of this.phases) {
      // Suffixed rather than overwritten: a phase can legitimately repeat, and
      // silently collapsing two into one would hide exactly that.
      rows[uniqueKey(rows, phase.label)] = { ms: round(phase.durationMs) };
    }
    rows['TOTAL'] = { ms: round(total) };

    console.groupCollapsed(`%c[timings] ${this.name} — ${round(total)}ms`, 'color:#0a7');
    console.table(rows);
    console.groupEnd();
  }
}

/** Starts a run, or returns null when timing is off (callers use `?.`). */
export function startTimingRun(name: string): TimingRun | null {
  return timingsEnabled() ? new TimingRun(name) : null;
}

/**
 * Runs `callback` after the browser has painted.
 *
 * Two frames, not one: the first `requestAnimationFrame` fires BEFORE the paint
 * that the just-applied DOM changes produce, so a callback there measures up to
 * the start of rendering rather than the end of it. Waiting one more frame puts
 * the callback after the paint has actually happened, which is the moment the
 * user perceives the grid as settled — the whole point of measuring this.
 */
export function afterPaint(callback: () => void): void {
  requestAnimationFrame(() => requestAnimationFrame(callback));
}

/**
 * Parses a `Server-Timing` header into rows.
 *
 * The backend emits `total;dur=842, s0;dur=181;desc="dataset.load"` — positional
 * metric names with the readable label in `desc` (see `RequestTimingScope`), so
 * the label is what is surfaced here and the name is dropped.
 */
export function parseServerTiming(header: string | null): TimingPhase[] {
  if (!header) return [];

  const phases: TimingPhase[] = [];
  for (const metric of header.split(',')) {
    const parts = metric.split(';').map(part => part.trim());
    const name = parts[0];
    if (!name) continue;

    let durationMs = 0;
    let label = name;
    for (const part of parts.slice(1)) {
      if (part.startsWith('dur=')) durationMs = Number(part.slice(4)) || 0;
      else if (part.startsWith('desc=')) label = part.slice(5).replace(/^"|"$/g, '');
    }
    phases.push({ label, durationMs });
  }
  return phases;
}

function uniqueKey(rows: Record<string, unknown>, label: string): string {
  if (!(label in rows)) return label;
  let n = 2;
  while (`${label} (${n})` in rows) n++;
  return `${label} (${n})`;
}

function round(ms: number): number {
  return Math.round(ms * 10) / 10;
}

function now(): number {
  return performance.now();
}
