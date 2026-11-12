import { ChangeDetectionStrategy, Component, computed, input, signal } from '@angular/core';
import { FsBadgeComponent, FsBadgeIntent, FsCardComponent, FsDataGridComponent, FsGridColumn } from '@core';
import { ExperimentDetailViewModel, parsePayload } from 'app/modules/experiments/viewmodels/experiment.viewmodel';

/** The result kinds that this view draws (SV-INT, method `integration_synthesis`). */
export const INTEGRATION_SYNTHESIS_RESULT_KINDS: readonly string[] = [
  'primary_result', 'lines', 'independent_sources', 'foundations', 'candidates', 'decisions', 'exposure_log',
];

interface VerdictRow {
  key: string;
  label: string;
  verdict: string;
  verdict_label: string;
  n_findings: number;
  codes: string[];
}

interface StrengthCount {
  strength: string;
  label: string;
  n: number;
}

interface PrimaryPayload {
  research_question: string;
  overall_answer: string;
  verdicts: VerdictRow[];
  n_experiments: number;
  n_findings: number;
  strength_counts: StrengthCount[];
  strength_classes: Record<string, string>;
  caveat: string;
}

interface Finding {
  code: string;
  asked: string;
  found: string;
  effect: string;
  n: string;
  sources: string[];
  detectable: string;
  strength: string;
}

interface LinePayload {
  key: string;
  label: string;
  question: string;
  verdict: string;
  verdict_label: string;
  verdict_text: string;
  packages: string[];
  findings: Finding[];
}

interface SourceRow {
  source: string;
  files: string;
  species: string;
  setting: string;
  outcome: string;
  used_by: string;
}

interface FoundationRow {
  code: string;
  found: string;
}

interface CandidateRow {
  name: string;
  codes: string;
  evidence: string;
  why_not_predictor: string;
}

interface DecisionRow {
  decision: string;
  raised_by: string;
  kind: string;
}

interface ExposureRow {
  package: string;
  file: string;
  entry: string;
}

const VERDICT_INTENT: Record<string, FsBadgeIntent> = {
  supported: 'success',
  contradicted: 'danger',
  not_supported_underpowered: 'warning',
  cannot_address: 'secondary',
};

/** Strength classes in the order of the matrix columns, weakest evidence of an effect first. */
const STRENGTH_SHORT: Record<string, string> = {
  no_data: 'No data',
  design_only: 'Design only',
  instrument_failed: 'Instrument failed',
  null_underpowered: 'Null, underpowered',
  negative: 'Negative',
  restates_known: 'Restates known',
  weak: 'Weak',
  descriptive: 'Descriptive',
};

const STRENGTH_INTENT: Record<string, FsBadgeIntent> = {
  no_data: 'secondary',
  design_only: 'info',
  instrument_failed: 'danger',
  null_underpowered: 'warning',
  negative: 'warning',
  restates_known: 'danger',
  weak: 'primary',
  descriptive: 'info',
};

/**
 * The integration view (SV-INT): for each line of explanation (time, load, host, parasite, response) the verdict, then what each
 * contributing experiment asked, what it found and how strong the evidence is, with its code. Below: independent sources after the
 * linkage audit, candidates (not predictors), the merged decisions for the user and the combined exposure log. No new test.
 */
@Component({
  selector: 'fs-experiment-integration-synthesis-view',
  standalone: true,
  imports: [FsBadgeComponent, FsCardComponent, FsDataGridComponent],
  templateUrl: './experiment-integration-synthesis-view.component.html',
  styleUrls: ['./experiment-integration-synthesis-view.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExperimentIntegrationSynthesisViewComponent {
  readonly detail = input.required<ExperimentDetailViewModel>();

  private payload<T>(kind: string) {
    return computed(() => parsePayload<T>(this.detail().results.find(r => r.kind === kind)));
  }

  protected readonly primary = this.payload<PrimaryPayload>('primary_result');
  protected readonly lines = this.payload<LinePayload[]>('lines');
  protected readonly sources = this.payload<SourceRow[]>('independent_sources');
  protected readonly foundations = this.payload<FoundationRow[]>('foundations');
  protected readonly candidates = this.payload<CandidateRow[]>('candidates');
  protected readonly decisions = this.payload<DecisionRow[]>('decisions');
  protected readonly exposure = this.payload<ExposureRow[]>('exposure_log');

  /** The line the reader picked on the verdict strip; null shows every line. */
  protected readonly selected = signal<string | null>(null);

  protected readonly shownLines = computed(() => {
    const all = this.lines() ?? [];
    const key = this.selected();
    return key ? all.filter(l => l.key === key) : all;
  });

  protected readonly strengthKeys = Object.keys(STRENGTH_SHORT);

  /** Line by strength class: number of findings in each cell. */
  protected readonly matrix = computed(() => (this.lines() ?? []).map(l => ({
    key: l.key,
    label: l.label,
    verdict: l.verdict,
    verdictLabel: l.verdict_label,
    cells: this.strengthKeys.map(s => {
      const codes = l.findings.filter(f => f.strength === s).map(f => f.code);
      return { strength: s, n: codes.length, codes: codes.join(', ') };
    }),
  })));

  protected readonly exposureRows = computed(() => (this.exposure() ?? []).map((r, i) => ({ ...r, id: i })));

  protected readonly exposureColumns: FsGridColumn<Record<string, unknown>>[] = [
    { dataField: 'package', caption: 'Package', width: 90 },
    { dataField: 'file', caption: 'Log file', width: 170 },
    { dataField: 'entry', caption: 'Entry (date / file opened / hashes / note)', minWidth: 500 },
  ];

  protected pick(key: string): void {
    this.selected.update(cur => (cur === key ? null : key));
  }

  protected verdictIntent(v: string): FsBadgeIntent {
    return VERDICT_INTENT[v] ?? 'secondary';
  }

  protected strengthIntent(s: string): FsBadgeIntent {
    return STRENGTH_INTENT[s] ?? 'secondary';
  }

  protected strengthLabel(s: string): string {
    return STRENGTH_SHORT[s] ?? s;
  }

  protected strengthTitle(s: string): string {
    return this.primary()?.strength_classes?.[s] ?? s;
  }

  protected link(code: string): string {
    return `/experiments/${code}`;
  }
}
