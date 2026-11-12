import { Type } from '@angular/core';
import { ExperimentDataLayerCoverageViewComponent } from 'app/modules/experiments/views/experiment-data-layer-coverage-view.component';
import { DISEASE_SPACE_RESULT_KINDS, ExperimentDiseaseSpaceMapViewComponent } from 'app/modules/experiments/views/experiment-disease-space-map-view.component';
import { ExperimentLiteratureExtractionViewComponent } from 'app/modules/experiments/views/experiment-literature-extraction-view.component';
import { ExperimentPairwiseViewComponent } from 'app/modules/experiments/views/experiment-pairwise-view.component';
import { ExperimentLoadOutcomeSynthesisViewComponent } from 'app/modules/experiments/views/experiment-load-outcome-synthesis-view.component';
import { CYTOKINE_CONFLICT_RESULT_KINDS, ExperimentCytokineConflictViewComponent } from 'app/modules/experiments/views/experiment-cytokine-conflict-view.component';
import { ExperimentLinkageAuditViewComponent, LINKAGE_AUDIT_RESULT_KINDS } from 'app/modules/experiments/views/experiment-linkage-audit-view.component';
import { ExperimentReactionNormViewComponent, REACTION_NORM_RESULT_KINDS } from 'app/modules/experiments/views/experiment-reaction-norm-view.component';
import { AGE_SEX_CONTRAST_RESULT_KINDS, ExperimentAgeSexContrastViewComponent } from 'app/modules/experiments/views/experiment-age-sex-contrast-view.component';
import { EVIDENCE_MATRIX_RESULT_KINDS, ExperimentEvidenceMatrixViewComponent } from 'app/modules/experiments/views/experiment-evidence-matrix-view.component';
import { ExperimentStudyDesignViewComponent, STUDY_DESIGN_RESULT_KINDS } from 'app/modules/experiments/views/experiment-study-design-view.component';
import { ExperimentMechanismTransferGridViewComponent, MECHANISM_TRANSFER_GRID_RESULT_KINDS } from 'app/modules/experiments/views/experiment-mechanism-transfer-grid-view.component';
import { ExperimentTranscriptomeSignatureViewComponent, TRANSCRIPTOME_SIGNATURE_RESULT_KINDS } from 'app/modules/experiments/views/experiment-transcriptome-signature-view.component';
import { ExperimentProteomeCandidateTestViewComponent, PROTEOME_CANDIDATE_TEST_RESULT_KINDS } from 'app/modules/experiments/views/experiment-proteome-candidate-test-view.component';
import { AXIS_REPLICATION_RESULT_KINDS, ExperimentAxisReplicationViewComponent } from 'app/modules/experiments/views/experiment-axis-replication-view.component';
import { ExperimentIntegrationSynthesisViewComponent, INTEGRATION_SYNTHESIS_RESULT_KINDS } from 'app/modules/experiments/views/experiment-integration-synthesis-view.component';
import { ExperimentMetaReviewViewComponent, META_REVIEW_RESULT_KINDS } from 'app/modules/experiments/views/experiment-meta-review-view.component';

/**
 * One entry per experiment method: how the Experiments screen shows the experiments of that method.
 *
 * The rail on the left lists every row of dbo.experiment, so an experiment gets its link when its
 * rows are written. This registry gives the link something to show. To add a method:
 *
 *   1. Create the view component in `views/` (standalone, one required input `detail` of type
 *      `ExperimentDetailViewModel`).
 *   2. Add ONE import line and ONE entry below. Keep the entries in the order they were added;
 *      do not reorder or reformat the lines of other experiments.
 *
 * No other file of the screen needs a change. See /experiments/run-instructions.md, step 4.
 */
export interface ExperimentViewEntry {
  /** `experiment.method` in the database. */
  method: string;
  /** The name of the method on the rail and in the header. */
  label: string;
  /** The standalone view component. It receives the input `detail`. */
  component: Type<unknown>;
  /** The result kinds the component draws. Kinds that are not listed are shown below it as raw JSON. */
  kinds: readonly string[];
}

export const EXPERIMENT_VIEWS: ExperimentViewEntry[] = [
  { method: 'pairwise_association', label: 'Pairwise associations', component: ExperimentPairwiseViewComponent,
    kinds: ['spearman_matrix', 'variable_clusters', 'top_associations', 'run_notes'] },
  { method: 'data_layer_coverage', label: 'Data layer coverage', component: ExperimentDataLayerCoverageViewComponent,
    kinds: ['dataset_summary', 'coverage_matrix', 'data_checks', 'cleaning_flags', 'dataset_links'] },
  { method: 'literature_extraction', label: 'Literature extraction', component: ExperimentLiteratureExtractionViewComponent,
    kinds: ['extraction_overview', 'markers', 'marker_classes', 'host_parasite_factors', 'species', 'outcome_definitions',
      'independent_units', 'not_extracted', 'agreement'] },
  { method: 'disease_space_map', label: 'Disease-space map', component: ExperimentDiseaseSpaceMapViewComponent,
    kinds: DISEASE_SPACE_RESULT_KINDS },
  { method: 'load_outcome_synthesis', label: 'Load-by-outcome synthesis', component: ExperimentLoadOutcomeSynthesisViewComponent,
    kinds: ['load_cells', 'unit_effects', 'load_by_outcome', 'low_load_list', 'damage_by_load_group', 'sensitivity'] },
  { method: 'cytokine_conflict', label: 'Cytokine conflict', component: ExperimentCytokineConflictViewComponent,
    kinds: CYTOKINE_CONFLICT_RESULT_KINDS },
  { method: 'linkage_audit', label: 'Linkage audit', component: ExperimentLinkageAuditViewComponent,
    kinds: LINKAGE_AUDIT_RESULT_KINDS },
  { method: 'reaction_norm', label: 'Reaction norms', component: ExperimentReactionNormViewComponent,
    kinds: REACTION_NORM_RESULT_KINDS },
  { method: 'age_sex_contrast', label: 'Age and sex contrasts', component: ExperimentAgeSexContrastViewComponent,
    kinds: AGE_SEX_CONTRAST_RESULT_KINDS },
  { method: 'evidence_matrix', label: 'Evidence matrix', component: ExperimentEvidenceMatrixViewComponent,
    kinds: EVIDENCE_MATRIX_RESULT_KINDS },
  { method: 'study_design', label: 'Study design memo', component: ExperimentStudyDesignViewComponent,
    kinds: STUDY_DESIGN_RESULT_KINDS },
  { method: 'mechanism_transfer_grid', label: 'Mechanism transfer grid', component: ExperimentMechanismTransferGridViewComponent,
    kinds: MECHANISM_TRANSFER_GRID_RESULT_KINDS },
  { method: 'transcriptome_signature', label: 'Transcriptome signatures', component: ExperimentTranscriptomeSignatureViewComponent,
    kinds: TRANSCRIPTOME_SIGNATURE_RESULT_KINDS },
  { method: 'proteome_candidate_test', label: 'Proteome candidate tests', component: ExperimentProteomeCandidateTestViewComponent,
    kinds: PROTEOME_CANDIDATE_TEST_RESULT_KINDS },
  { method: 'axis_replication', label: 'Axis replication', component: ExperimentAxisReplicationViewComponent,
    kinds: AXIS_REPLICATION_RESULT_KINDS },
  { method: 'integration_synthesis', label: 'Integration synthesis', component: ExperimentIntegrationSynthesisViewComponent,
    kinds: INTEGRATION_SYNTHESIS_RESULT_KINDS },
  { method: 'meta_review', label: 'Meta review', component: ExperimentMetaReviewViewComponent,
    kinds: META_REVIEW_RESULT_KINDS },
];

const BY_METHOD = new Map(EXPERIMENT_VIEWS.map(entry => [entry.method, entry]));

/** The registry entry of a method, or undefined when the method has no view yet. */
export function experimentView(method: string | null | undefined): ExperimentViewEntry | undefined {
  return method ? BY_METHOD.get(method) : undefined;
}
