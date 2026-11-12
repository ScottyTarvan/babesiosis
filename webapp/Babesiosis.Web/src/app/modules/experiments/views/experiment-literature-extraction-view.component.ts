import { ChangeDetectionStrategy, Component, computed, DestroyRef, inject, input, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import {
  FsCardComponent,
  FsChartComponent,
  fsChartCssColor,
  FsChartOptions,
  FsDataGridComponent,
  FsGridColumn,
  FsGridPager,
  fsObserveTheme,
  FsTextInputComponent,
} from '@core';
import { ExperimentDetailViewModel, parsePayload } from 'app/modules/experiments/viewmodels/experiment.viewmodel';

// ---- Payloads written by /experiments/SV-G2/scripts/build_results.py -------------------------

export interface ExtractionOverviewPayload {
  articles_in_scope: number;
  articles_extracted: number;
  articles_missing: string[];
  articles_with_associations: number;
  articles_without_associations: number;
  independent_units_in_scope: number;
  independent_units_with_associations: number;
  canine_units_with_associations: number;
  severity_definitions: number;
  association_rows: number;
  rows_significant: number;
  rows_not_significant: number;
  rows_not_tested: number;
  canonical_markers: number;
  markers_in_2plus_units: number;
  quote_check_rows: Record<string, number>;
  quote_check_definitions: Record<string, number>;
  rows_numbers_not_in_text: number;
  rows_schema_errors: number;
  rows_unmapped_marker: number;
}

export interface ExtractionMarkerRow {
  marker: string;
  marker_class: string;
  factor_type: string;
  units: number;
  articles: number;
  rows: number;
  units_sig_higher: number;
  units_sig_lower: number;
  units_not_significant: number;
  outcome_classes: string;
  species_groups: string;
}

export interface ExtractionClassRow {
  marker_class: string;
  factor_type: string;
  units: number;
  articles: number;
  markers: number;
  rows: number;
}

export interface ExtractionLoadMethodRow {
  marker: string;
  load_method: string;
  units: number;
  rows: number;
}

export interface ExtractionSpeciesRow {
  species_group: string;
  articles_in_scope: number;
  articles_with_rows: number;
  units_with_rows: number;
  rows: number;
}

export interface ExtractionOutcomeRow {
  outcome_class: string;
  definitions: number;
  units_defining: number;
  rows: number;
  units_with_rows: number;
}

export interface ExtractionDefinitionsPayload {
  outcome_classes: ExtractionOutcomeRow[];
  components: { component: string; definitions: number; units: number }[];
  mortality_euthanasia: { value: string; definitions: number }[];
  definition_sources: { value: string; definitions: number }[];
  settings: { value: string; articles: number }[];
  sample_timing: { value: string; articles: number }[];
}

export interface ExtractionUnitRow {
  independent_unit: string;
  is_cohort: boolean;
  articles: string;
  n_articles: number;
  articles_with_rows: number;
  definitions: number;
  rows: number;
  species_groups: string;
}

export interface ExtractionNotExtractedPayload {
  reasons: { reason: string; items: number; articles: number }[];
  articles_without_associations: { id: string; unit: string; species_group: string; skipped_infected_vs_healthy: number | null }[];
  articles_missing: string[];
}

export interface ExtractionAgreementSummary {
  articles: number;
  matched_pairs: number;
  ref_keys: number;
  other_keys: number;
  coverage_ref_found_by_other: number | null;
  coverage_other_found_by_ref: number | null;
  direction_agreement: number | null;
  significance_agreement: number | null;
  both_agree: number | null;
  significance_kappa: number | null;
  outcome_class: { jaccard_pooled: number | null; articles_identical_sets: number };
}

export interface ExtractionAgreementPayload {
  second?: ExtractionAgreementSummary;
  pilot?: ExtractionAgreementSummary;
  resolutions?: number;
}

/** One line of the agreement table. */
interface AgreementLine {
  id: string;
  label: string;
  articles: number;
  matched: number;
  coverage: string;
  significance: string;
  direction: string;
  kappa: string;
  classes: string;
}

/** Fixed hues for direction, readable on light and dark surfaces. */
const HIGHER = '#c6483a';
const LOWER = '#3366b0';
const NULL_GREY = '#8a8f98';

function fmt(x: number | null | undefined, digits = 2): string {
  return x === null || x === undefined ? '–' : x.toFixed(digits);
}

/**
 * The view for SV-G2, the severity literature extraction: coverage first, then the markers
 * and host or parasite factors counted by independent units and direction, the species,
 * the severity definitions, the cohorts, what could not be extracted and the agreement checks.
 */
@Component({
  selector: 'fs-experiment-literature-extraction-view',
  standalone: true,
  imports: [FormsModule, FsCardComponent, FsChartComponent, FsDataGridComponent, FsTextInputComponent],
  templateUrl: './experiment-literature-extraction-view.component.html',
  styleUrls: ['./experiment-literature-extraction-view.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExperimentLiteratureExtractionViewComponent implements OnInit {
  private readonly destroyRef = inject(DestroyRef);

  readonly detail = input.required<ExperimentDetailViewModel>();

  private readonly themeChanges = signal(0);
  protected readonly markerSearch = signal('');
  protected readonly topCount = 25;

  private result<T>(kind: string): T | null {
    return parsePayload<T>(this.detail().results.find(r => r.kind === kind));
  }

  protected readonly overview = computed(() => this.result<ExtractionOverviewPayload>('extraction_overview'));
  protected readonly markers = computed(() => this.result<{ rows: ExtractionMarkerRow[] }>('markers')?.rows ?? null);
  protected readonly classes = computed(() => this.result<{ rows: ExtractionClassRow[] }>('marker_classes')?.rows ?? null);
  protected readonly factors = computed(() =>
    this.result<{ rows: ExtractionMarkerRow[]; load_methods: ExtractionLoadMethodRow[] }>('host_parasite_factors'));
  protected readonly species = computed(() => this.result<{ rows: ExtractionSpeciesRow[] }>('species')?.rows ?? null);
  protected readonly definitions = computed(() => this.result<ExtractionDefinitionsPayload>('outcome_definitions'));
  protected readonly units = computed(() => this.result<{ rows: ExtractionUnitRow[]; cohorts: number }>('independent_units'));
  protected readonly notExtracted = computed(() => this.result<ExtractionNotExtractedPayload>('not_extracted'));
  protected readonly agreement = computed(() => this.result<ExtractionAgreementPayload>('agreement'));

  protected readonly quoteText = computed(() => {
    const q = this.overview()?.quote_check_rows ?? {};
    const total = Object.values(q).reduce((s, n) => s + n, 0);
    return `${(q['exact'] ?? 0) + (q['near'] ?? 0)} of ${total}`;
  });

  protected readonly agreementLines = computed<AgreementLine[]>(() => {
    const a = this.agreement();
    const line = (id: string, label: string, s?: ExtractionAgreementSummary): AgreementLine[] => s ? [{
      id, label, articles: s.articles, matched: s.matched_pairs,
      coverage: `${fmt(s.coverage_ref_found_by_other)} / ${fmt(s.coverage_other_found_by_ref)}`,
      significance: fmt(s.significance_agreement), direction: fmt(s.direction_agreement), kappa: fmt(s.significance_kappa),
      classes: `${fmt(s.outcome_class?.jaccard_pooled)} (${s.outcome_class?.articles_identical_sets ?? 0} of ${s.articles} identical)`,
    }] : [];
    return a ? [...line('second', 'Blind second extraction (20% random sample)', a.second),
      ...line('pilot', 'Calibration batch against the pilot extraction', a.pilot)] : [];
  });
  protected readonly secondAgreement = computed(() => this.agreement()?.second ?? null);

  private barOptions(categories: string[], series: { name: string; data: number[] }[], colors: string[], stacked: boolean,
                     xTitle: string): FsChartOptions {
    this.themeChanges();
    const grid = fsChartCssColor('--fs-color-border', '#d9d7d2');
    return {
      chart: { type: 'bar', stacked, toolbar: { show: false }, animations: { enabled: false } },
      series,
      colors,
      plotOptions: { bar: { horizontal: true, barHeight: '70%', borderRadius: 2 } },
      dataLabels: { enabled: false },
      grid: { borderColor: grid },
      xaxis: { categories, title: { text: xTitle }, labels: { formatter: (v: string) => `${Math.round(Number(v))}` } },
      yaxis: { labels: { maxWidth: 240, style: { fontSize: '11px' } } },
      legend: { show: series.length > 1, position: 'bottom' },
      tooltip: { shared: true, intersect: false },
    };
  }

  /** The top markers by independent units, split by the direction of their results. */
  protected readonly topMarkers = computed(() => (this.markers() ?? []).slice(0, this.topCount));
  protected readonly markerChart = computed<FsChartOptions>(() => {
    const top = this.topMarkers();
    return this.barOptions(top.map(m => m.marker), [
      { name: 'Units with a significant result, higher in severe', data: top.map(m => m.units_sig_higher) },
      { name: 'Units with a significant result, lower in severe', data: top.map(m => m.units_sig_lower) },
      { name: 'Units with a non-significant result', data: top.map(m => m.units_not_significant) },
    ], [HIGHER, LOWER, NULL_GREY], false, 'Independent units');
  });
  protected readonly markerChartHeight = computed(() => Math.max(320, 30 * this.topMarkers().length + 110));

  protected readonly speciesChart = computed<FsChartOptions>(() => {
    const rows = this.species() ?? [];
    return this.barOptions(rows.map(r => r.species_group), [
      { name: 'Independent units with rows', data: rows.map(r => r.units_with_rows) },
      { name: 'Articles in scope', data: rows.map(r => r.articles_in_scope) },
    ], [fsChartCssColor('--fs-color-chart-1', '#4b6bd6'), NULL_GREY], false, 'Count');
  });

  protected readonly outcomeChart = computed<FsChartOptions>(() => {
    const rows = this.definitions()?.outcome_classes ?? [];
    return this.barOptions(rows.map(r => r.outcome_class.replace(/_/g, ' ')), [
      { name: 'Independent units using the definition', data: rows.map(r => r.units_defining) },
    ], [fsChartCssColor('--fs-color-chart-2', '#2f9e8f')], false, 'Independent units');
  });

  protected readonly componentChart = computed<FsChartOptions>(() => {
    const rows = this.definitions()?.components ?? [];
    return this.barOptions(rows.map(r => r.component), [
      { name: 'Independent units', data: rows.map(r => r.units) },
    ], [fsChartCssColor('--fs-color-chart-3', '#c98a2b')], false, 'Independent units');
  });

  protected readonly filteredMarkers = computed(() => {
    const term = this.markerSearch().trim().toLowerCase();
    return (this.markers() ?? []).filter(m => !term || m.marker.toLowerCase().includes(term)
      || m.marker_class.toLowerCase().includes(term) || m.outcome_classes.includes(term) || m.species_groups.toLowerCase().includes(term));
  });

  protected readonly markerColumns: FsGridColumn<ExtractionMarkerRow>[] = [
    { dataField: 'marker', caption: 'Marker or factor', minWidth: 200 },
    { dataField: 'marker_class', caption: 'Class', width: 150 },
    { dataField: 'units', caption: 'Units', width: 75, alignment: 'right', sortOrder: 'desc', sortIndex: 0 },
    { dataField: 'articles', caption: 'Articles', width: 85, alignment: 'right' },
    { dataField: 'units_sig_higher', caption: 'Sig. higher', width: 95, alignment: 'right' },
    { dataField: 'units_sig_lower', caption: 'Sig. lower', width: 95, alignment: 'right' },
    { dataField: 'units_not_significant', caption: 'Not sig.', width: 85, alignment: 'right' },
    { dataField: 'outcome_classes', caption: 'Outcome classes', minWidth: 180 },
    { dataField: 'species_groups', caption: 'Species', minWidth: 160 },
  ];
  protected readonly factorColumns: FsGridColumn<ExtractionMarkerRow>[] = [
    { dataField: 'marker', caption: 'Factor', minWidth: 200 },
    { dataField: 'factor_type', caption: 'Type', width: 130 },
    { dataField: 'units', caption: 'Units', width: 75, alignment: 'right', sortOrder: 'desc', sortIndex: 0 },
    { dataField: 'articles', caption: 'Articles', width: 85, alignment: 'right' },
    { dataField: 'units_sig_higher', caption: 'Sig. higher', width: 95, alignment: 'right' },
    { dataField: 'units_sig_lower', caption: 'Sig. lower', width: 95, alignment: 'right' },
    { dataField: 'units_not_significant', caption: 'Not sig.', width: 85, alignment: 'right' },
    { dataField: 'species_groups', caption: 'Species', minWidth: 160 },
  ];
  protected readonly loadColumns: FsGridColumn<ExtractionLoadMethodRow>[] = [
    { dataField: 'marker', caption: 'Load measure', minWidth: 180 },
    { dataField: 'load_method', caption: 'Method', minWidth: 160 },
    { dataField: 'units', caption: 'Units', width: 75, alignment: 'right' },
    { dataField: 'rows', caption: 'Rows', width: 75, alignment: 'right' },
  ];
  protected readonly classColumns: FsGridColumn<ExtractionClassRow>[] = [
    { dataField: 'marker_class', caption: 'Marker class', minWidth: 170 },
    { dataField: 'factor_type', caption: 'Type', minWidth: 150 },
    { dataField: 'units', caption: 'Units', width: 75, alignment: 'right', sortOrder: 'desc', sortIndex: 0 },
    { dataField: 'articles', caption: 'Articles', width: 85, alignment: 'right' },
    { dataField: 'markers', caption: 'Markers', width: 85, alignment: 'right' },
    { dataField: 'rows', caption: 'Rows', width: 75, alignment: 'right' },
  ];
  protected readonly unitColumns: FsGridColumn<ExtractionUnitRow>[] = [
    { dataField: 'independent_unit', caption: 'Unit', width: 100 },
    { dataField: 'articles', caption: 'Articles', minWidth: 180 },
    { dataField: 'articles_with_rows', caption: 'With rows', width: 95, alignment: 'right' },
    { dataField: 'definitions', caption: 'Definitions', width: 100, alignment: 'right' },
    { dataField: 'rows', caption: 'Rows', width: 75, alignment: 'right', sortOrder: 'desc', sortIndex: 0 },
    { dataField: 'species_groups', caption: 'Species', minWidth: 160 },
  ];
  protected readonly agreementColumns: FsGridColumn<AgreementLine>[] = [
    { dataField: 'label', caption: 'Comparison', minWidth: 240 },
    { dataField: 'articles', caption: 'Articles', width: 85, alignment: 'right' },
    { dataField: 'matched', caption: 'Matched pairs', width: 115, alignment: 'right' },
    { dataField: 'coverage', caption: 'Coverage (first / second)', width: 180 },
    { dataField: 'significance', caption: 'Significance agreement', width: 175, alignment: 'right' },
    { dataField: 'kappa', caption: 'Kappa', width: 75, alignment: 'right' },
    { dataField: 'direction', caption: 'Direction agreement', width: 155, alignment: 'right' },
    { dataField: 'classes', caption: 'Outcome classes (Jaccard)', minWidth: 200 },
  ];
  protected readonly pager: FsGridPager = { visible: true, showPageSizeSelector: true, allowedPageSizes: [15, 30, 100], showInfo: true };

  ngOnInit(): void {
    this.destroyRef.onDestroy(fsObserveTheme(() => this.themeChanges.update(n => n + 1)));
  }
}
