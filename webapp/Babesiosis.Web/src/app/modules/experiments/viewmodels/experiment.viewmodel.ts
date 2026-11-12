/** Mirrors `ExperimentListItemViewModel`: one run in the left-hand panel. */
export interface ExperimentListItemViewModel {
  code: string;
  name: string;
  /** pairwise_association, clustering, ... */
  method: string;
  datasetCode: string | null;
  datasetTitle: string | null;
  articleCode: string | null;
  articleTitle: string | null;
  /** ISO date-time, UTC. */
  runAt: string | null;
  subjectCount: number | null;
  variableCount: number | null;
  testCount: number | null;
  /** Significant after adjustment and not trivial. */
  findingCount: number;
  summary: string | null;
}

/** Mirrors `ExperimentListViewModel`. */
export interface ExperimentListViewModel {
  items: ExperimentListItemViewModel[];
  datasetCount: number;
}

/** Mirrors `ExperimentDatasetViewModel`. */
export interface ExperimentDatasetViewModel {
  code: string;
  title: string;
  articleCode: string | null;
  articleTitle: string | null;
  articleSourceUrl: string | null;
  repository: string | null;
  sourceRecord: string | null;
  licence: string | null;
  independentSource: string | null;
  species: string | null;
  subjectCount: number;
  /** JSON array of the tidy script's cleaning notes. */
  notes: string | null;
}

/** Mirrors `ExperimentVariableViewModel`: one entry of the dataset's variable dictionary. */
export interface ExperimentVariableViewModel {
  code: string;
  name: string;
  unit: string | null;
  /** N numeric, O ordinal, C categorical, D date, T text. */
  dataType: string;
  domain: string | null;
  derived: boolean;
  /** JSON array of parent codes. */
  derivedFrom: string | null;
  includeDefault: boolean;
  refLow: number | null;
  refHigh: number | null;
  description: string | null;
  /** JSON object of level to count, categorical variables only. */
  levels: string | null;
}

/** Mirrors `ExperimentAssociationViewModel`: one tested pair. */
export interface ExperimentAssociationViewModel {
  variableA: string;
  variableAName: string;
  variableB: string;
  variableBName: string;
  /** spearman, mann_whitney, kruskal_wallis or chi_square. */
  test: string;
  estimate: number | null;
  /** rho, eta_squared or cramers_v. */
  estimateLabel: string | null;
  n: number;
  pValue: number | null;
  pAdjusted: number | null;
  significant: boolean;
  trivial: boolean;
  direction: string | null;
  /** JSON detail. */
  detail: string | null;
}

/** Mirrors `ExperimentResultViewModel`: one method-specific payload, JSON as text. */
export interface ExperimentResultViewModel {
  kind: string;
  title: string | null;
  payload: string;
  sortOrder: number;
}

/** Mirrors `ExperimentDetailViewModel`. */
export interface ExperimentDetailViewModel {
  code: string;
  name: string;
  description: string | null;
  method: string;
  /** JSON. */
  parameters: string | null;
  script: string | null;
  scriptVersion: string | null;
  runAt: string | null;
  subjectCount: number | null;
  variableCount: number | null;
  testCount: number | null;
  findingCount: number;
  significantCount: number;
  summary: string | null;
  dataset: ExperimentDatasetViewModel | null;
  variables: ExperimentVariableViewModel[];
  associations: ExperimentAssociationViewModel[];
  associationsTruncated: boolean;
  results: ExperimentResultViewModel[];
}

// ---- Result payloads (the shapes the experiment scripts write) ----------------------------

/** `spearman_matrix`: square matrix over the numeric variables, by code. */
export interface SpearmanMatrixPayload {
  variables: string[];
  rho: (number | null)[][];
  n: number[][];
}

/** `variable_clusters`: average-linkage blocks of variables that move together. */
export interface VariableClustersPayload {
  clusters: { members: string[]; mean_abs_rho: number | null }[];
  singletons: string[];
}

/** `interpretation`: the script's explanation of the run, as plain-text sections. */
export interface InterpretationPayload {
  sections: { heading: string; paragraphs: string[] }[];
}

/** Parses a result's JSON payload; null when the result is missing or the JSON is unreadable. */
export function parsePayload<T>(result: ExperimentResultViewModel | undefined | null): T | null {
  if (!result?.payload) {
    return null;
  }
  try {
    return JSON.parse(result.payload) as T;
  } catch {
    return null;
  }
}

/** Parses a JSON column that may be null or unreadable. */
export function parseJson<T>(text: string | null | undefined, fallback: T): T {
  if (!text) {
    return fallback;
  }
  try {
    return JSON.parse(text) as T;
  } catch {
    return fallback;
  }
}

/** Display names for `method`. Unknown methods show their code. */
export const METHOD_LABELS: Record<string, string> = {
  pairwise_association: 'Pairwise associations',
  clustering: 'Clustering',
  data_layer_coverage: 'Data layer coverage',
  literature_extraction: 'Literature extraction',
  disease_space_map: 'Disease-space map',
};

export function methodLabel(method: string | null | undefined): string {
  return (method && METHOD_LABELS[method]) || method || 'Unknown method';
}

/** Display names for the statistical tests. */
export const TEST_LABELS: Record<string, string> = {
  spearman: 'Spearman',
  mann_whitney: 'Mann-Whitney',
  kruskal_wallis: 'Kruskal-Wallis',
  chi_square: 'Chi-square',
};

/** Short symbols for the effect-size labels. */
export const ESTIMATE_SYMBOLS: Record<string, string> = {
  rho: 'rho',
  eta_squared: 'eta²',
  cramers_v: "Cramer's V",
};
