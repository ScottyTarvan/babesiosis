/**
 * Server load options envelope.
 *
 * Mirrors the subset of the DevExtreme.AspNet.Data `DataSourceLoadOptions`
 * contract that the backend understands. Kept as a local type so the
 * frontend carries no dependency on the DevExtreme client library — the
 * JSON wire shape sent to the backend is unchanged. All fields optional.
 */
export interface LoadOptions {
  skip?: number;
  take?: number;
  sort?: unknown;
  filter?: unknown;
  group?: unknown;
  requireTotalCount?: boolean;
  requireGroupCount?: boolean;
  totalSummary?: unknown;
  groupSummary?: unknown;
  searchExpr?: unknown;
  searchOperation?: string;
  searchValue?: unknown;
}

export class SearchCommand {
  constructor(public loadOptions: LoadOptions = null) { }
}
