/** Mirrors `GetExperimentDetailCommand`. */
export interface GetExperimentDetailCommand {
  /** The experiment code, e.g. EXP01-DS05-pairwise. */
  code: string;
  /** Only associations significant after adjustment. The backend defaults to false. */
  significantOnly?: boolean;
  /** Keep pairs where one variable is an arithmetic function of the other. The backend defaults to true. */
  includeTrivial?: boolean;
  /** Cap on association rows, best adjusted p first. The backend defaults to 5000. */
  maxAssociations?: number;
}
