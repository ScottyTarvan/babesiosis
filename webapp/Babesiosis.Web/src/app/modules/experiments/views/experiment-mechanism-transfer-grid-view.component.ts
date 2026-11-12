import { ChangeDetectionStrategy, Component, computed, DestroyRef, inject, input, OnInit, signal } from '@angular/core';
import {
  FsBadgeComponent,
  FsCardComponent,
  FsChartComponent,
  fsChartCssColor,
  FsChartOptions,
  FsDataGridComponent,
  FsGridColumn,
  FsGridPager,
  fsObserveTheme,
} from '@core';
import { ExperimentDetailViewModel, parsePayload } from 'app/modules/experiments/viewmodels/experiment.viewmodel';

/** The result kinds that this view draws (SV-06a, method `mechanism_transfer_grid`). */
export const MECHANISM_TRANSFER_GRID_RESULT_KINDS: readonly string[] = [
  'primary_result', 'family_summary', 'transfer_grid', 'partb_handover',
];

type CanineStatus = 'none' | 'measured_no_severity' | 'severity_tested';

interface RankedRow {
  rank: number;
  mechanism_id: string;
  family: string;
  mechanism: string;
  human_grade: number;
  human_n_studies: number | null;
  human_conditions: string;
  human_direction: string;
  canine_status: CanineStatus;
  canine_assay: string;
  testable_now: string;
  severity_contrast_testable_now: string;
  ds07_master: string;
  human_key_dois: string;
  assay_evidence: string;
}

interface PrimaryPayload {
  n_mechanisms: number;
  n_seed: number;
  n_added: number;
  n_gap: number;
  status_counts: Record<CanineStatus, number>;
  n_grade_ge2: number;
  n_grade_ge2_gap: number;
  share_grade_ge2_gap: number | null;
  n_grade3: number;
  n_grade3_severity_tested: number;
  premise: string;
  n_ranked: number;
  n_ranked_in_ds07: number;
  excluded_no_assay: string[];
  ranked: RankedRow[];
}

interface FamilyRow {
  family: string;
  mechanisms: number;
  none: number;
  measured_no_severity: number;
  severity_tested: number;
  gaps: number;
  grade_ge2: number;
  ranked: number;
  agent_summary: string;
}

interface GridRow {
  mechanism_id: string;
  family: string;
  mechanism: string;
  added_by_agent: string;
  human_conditions: string;
  hu_articles: string;
  human_grade: number | null;
  human_n_studies: number | null;
  human_direction: string;
  cb_note_hits: number;
  cb_text_hits: number;
  cb_confirmed: string;
  canine_status: CanineStatus;
  canine_severity_units: number | null;
  canine_assay: string;
  testable_now: string;
  severity_contrast_testable_now: string;
  ds07_master: string;
  ds02_measured: string;
  gap: string;
  rank: number | string;
  human_key_dois: string;
  canine_dog_babesiosis_dois: string;
  assay_evidence: string;
  notes: string;
}

interface HandoverPayload {
  file: string;
  rows: { partb_candidate: string; ds07: string; mechanisms: string }[];
}

const STATUS_LABEL: Record<CanineStatus, string> = {
  none: 'Never measured in canine babesiosis',
  measured_no_severity: 'Measured, no severity contrast',
  severity_tested: 'Tested against severity',
};

/** Short family label: "F1 Haemolysis and haem scavenging" -> "F1 Haemolysis …". */
function shortFamily(f: string): string {
  return f.length > 34 ? `${f.slice(0, 32)}…` : f;
}

/** The first DOI of a "; "-separated list, as a link target. */
function firstDoi(s: string | null | undefined): string | null {
  const d = (s ?? '').split(';').map(x => x.trim()).find(x => x.startsWith('http'));
  return d ?? null;
}

/**
 * The mechanism transfer grid (SV-06a): mechanisms linked to severity in malaria, human babesiosis and sepsis, graded for
 * human evidence, canine severity evidence, canine assay and whether a public file can test them now. The ranked gaps
 * first, then the canine status by family, the full grid and the hand-over to part b (DS07 candidate proteins).
 */
@Component({
  selector: 'fs-experiment-mechanism-transfer-grid-view',
  standalone: true,
  imports: [FsBadgeComponent, FsCardComponent, FsChartComponent, FsDataGridComponent],
  templateUrl: './experiment-mechanism-transfer-grid-view.component.html',
  styleUrls: ['./experiment-mechanism-transfer-grid-view.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExperimentMechanismTransferGridViewComponent implements OnInit {
  private readonly destroyRef = inject(DestroyRef);

  readonly detail = input.required<ExperimentDetailViewModel>();

  private readonly themeChanges = signal(0);

  private payload<T>(kind: string) {
    return computed(() => parsePayload<T>(this.detail().results.find(r => r.kind === kind)));
  }

  protected readonly primary = this.payload<PrimaryPayload>('primary_result');
  protected readonly families = this.payload<{ rows: FamilyRow[] }>('family_summary');
  protected readonly grid = this.payload<{ rows: GridRow[] }>('transfer_grid');
  protected readonly handover = this.payload<HandoverPayload>('partb_handover');

  protected readonly pager: FsGridPager = { visible: true, showPageSizeSelector: true, allowedPageSizes: [10, 25, 50], showInfo: true };

  protected readonly sharePct = computed(() => {
    const s = this.primary()?.share_grade_ge2_gap;
    return s === null || s === undefined ? '–' : `${Math.round(100 * s)}%`;
  });

  protected readonly rankedRows = computed(() => (this.primary()?.ranked ?? []).map(r => ({
    ...r,
    statusText: STATUS_LABEL[r.canine_status] ?? r.canine_status,
    ds07Text: r.severity_contrast_testable_now === 'yes' ? `DS07: ${r.ds07_master}` : (r.testable_now === 'public_file' ? 'Beagle files only (DS06 RNA or DS02)' : 'stored samples'),
    humanText: `${r.human_grade} (${r.human_n_studies ?? '?'} cohorts; ${r.human_conditions})`,
    doi: firstDoi(r.human_key_dois) ?? '',
    assayDoi: firstDoi(r.assay_evidence) ?? '',
  })));
  protected readonly rankedColumns: FsGridColumn<Record<string, unknown>>[] = [
    { dataField: 'rank', caption: 'Rank', width: 64, alignment: 'right' },
    { dataField: 'mechanism', caption: 'Mechanism', minWidth: 260 },
    { dataField: 'family', caption: 'Family', width: 200 },
    { dataField: 'humanText', caption: 'Human grade (evidence)', minWidth: 210 },
    { dataField: 'human_direction', caption: 'With severity in people', minWidth: 200 },
    { dataField: 'statusText', caption: 'Dogs with babesiosis', width: 220 },
    { dataField: 'canine_assay', caption: 'Canine assay', width: 120 },
    { dataField: 'ds07Text', caption: 'Testable now', minWidth: 220 },
    { dataField: 'doi', caption: 'Key human DOI', minWidth: 220 },
  ];

  protected readonly familyChart = computed<FsChartOptions>(() => {
    this.themeChanges();
    const rows = this.families()?.rows ?? [];
    if (!rows.length) {
      return {};
    }
    const soft = fsChartCssColor('--fs-color-ink-soft', '#6b6862');
    return {
      chart: { type: 'bar', stacked: true, toolbar: { show: false }, animations: { enabled: false } },
      series: [
        { name: STATUS_LABEL.none, data: rows.map(r => r.none) },
        { name: STATUS_LABEL.measured_no_severity, data: rows.map(r => r.measured_no_severity) },
        { name: STATUS_LABEL.severity_tested, data: rows.map(r => r.severity_tested) },
      ],
      colors: [
        fsChartCssColor('--fs-color-chart-4', '#c6483a'),
        fsChartCssColor('--fs-color-chart-2', '#d99a2b'),
        fsChartCssColor('--fs-color-chart-1', '#4b6bd6'),
      ],
      plotOptions: { bar: { horizontal: true, barHeight: '65%' } },
      dataLabels: { enabled: true, style: { fontSize: '11px' } },
      legend: { position: 'bottom' },
      xaxis: {
        categories: rows.map(r => shortFamily(r.family)),
        title: { text: 'Mechanisms', style: { color: soft } },
        labels: { formatter: (v: string) => Number(v).toFixed(0) },
      },
      yaxis: { labels: { maxWidth: 260, style: { fontSize: '11px' } } },
      tooltip: { y: { formatter: (v: number) => `${v} mechanism${v === 1 ? '' : 's'}` } },
    };
  });

  protected readonly familyColumns: FsGridColumn<FamilyRow>[] = [
    { dataField: 'family', caption: 'Family', width: 240 },
    { dataField: 'mechanisms', caption: 'Mechanisms', width: 100, alignment: 'right' },
    { dataField: 'gaps', caption: 'Gaps', width: 70, alignment: 'right' },
    { dataField: 'grade_ge2', caption: 'Human grade ≥ 2', width: 130, alignment: 'right' },
    { dataField: 'ranked', caption: 'Ranked', width: 80, alignment: 'right' },
    { dataField: 'agent_summary', caption: 'Family agent summary', minWidth: 380 },
  ];

  protected readonly statusFilter = signal<CanineStatus | 'all'>('all');
  protected readonly statuses: (CanineStatus | 'all')[] = ['all', 'none', 'measured_no_severity', 'severity_tested'];
  protected readonly gridRows = computed(() => {
    const f = this.statusFilter();
    return (this.grid()?.rows ?? [])
      .filter(r => f === 'all' || r.canine_status === f)
      .map(r => ({
        ...r,
        statusText: STATUS_LABEL[r.canine_status] ?? r.canine_status,
        hits: `${r.cb_note_hits} / ${r.cb_text_hits}`,
        addedText: r.added_by_agent === 'yes' ? 'agent' : 'seed',
      }));
  });
  protected readonly gridColumns: FsGridColumn<Record<string, unknown>>[] = [
    { dataField: 'mechanism_id', caption: 'ID', width: 70 },
    { dataField: 'mechanism', caption: 'Mechanism', minWidth: 240 },
    { dataField: 'addedText', caption: 'From', width: 70 },
    { dataField: 'human_grade', caption: 'Human grade', width: 100, alignment: 'right' },
    { dataField: 'human_n_studies', caption: 'Human cohorts', width: 110, alignment: 'right' },
    { dataField: 'hu_articles', caption: 'HU notes', width: 140 },
    { dataField: 'hits', caption: 'CB keyword hits (notes / texts)', width: 140, alignment: 'right' },
    { dataField: 'cb_confirmed', caption: 'CB confirmed', minWidth: 180 },
    { dataField: 'statusText', caption: 'Dogs with babesiosis', width: 220 },
    { dataField: 'canine_severity_units', caption: 'Severity units', width: 100, alignment: 'right' },
    { dataField: 'canine_assay', caption: 'Canine assay', width: 120 },
    { dataField: 'testable_now', caption: 'Testable now', width: 150 },
    { dataField: 'ds07_master', caption: 'DS07 master protein', minWidth: 200 },
    { dataField: 'ds02_measured', caption: 'DS02 variable', width: 120 },
    { dataField: 'gap', caption: 'Gap', width: 60 },
    { dataField: 'rank', caption: 'Rank', width: 60, alignment: 'right' },
    { dataField: 'notes', caption: 'Notes', minWidth: 300 },
  ];

  protected readonly handoverColumns: FsGridColumn<Record<string, string>>[] = [
    { dataField: 'partb_candidate', caption: 'Part b candidate', width: 180 },
    { dataField: 'ds07', caption: 'DS07 protein (status, coverage)', minWidth: 320 },
    { dataField: 'mechanisms', caption: 'Grid mechanisms', minWidth: 160 },
  ];

  protected statusLabel(s: CanineStatus | 'all'): string {
    return s === 'all' ? 'All' : STATUS_LABEL[s];
  }

  ngOnInit(): void {
    this.destroyRef.onDestroy(fsObserveTheme(() => this.themeChanges.update(n => n + 1)));
  }
}
