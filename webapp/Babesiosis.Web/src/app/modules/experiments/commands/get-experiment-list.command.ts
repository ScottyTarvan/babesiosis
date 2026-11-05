/** Mirrors `GetExperimentListCommand`. Every run is returned; the panel filters client-side. */
export interface GetExperimentListCommand {
  /** Only runs over this dataset code, e.g. DS05. */
  datasetCode?: string;
}
