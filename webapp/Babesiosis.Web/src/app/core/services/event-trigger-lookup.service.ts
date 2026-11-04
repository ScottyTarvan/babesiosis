import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { ItemViewModel } from 'app/core/viewmodels/item.viewmodel';
import { Observable, map } from 'rxjs';
import { AuthService } from '@core/services/auth.service';
import { ConfigurationService } from '@core/services/configuration.service';
import { ServiceBase } from '@core/services/service-base';

/**
 * Options for one activator parameter of type Entity or Lookup, read live from
 * the deployed dataset behind it.
 *
 * This lives in core rather than in either activator feature because **both**
 * areas need it: Manage runs an activator and needs real options in the run
 * form, and Setup previews that same form while authoring it. The endpoint is
 * `manage-`prefixed because that is the function's live name — it is not a
 * statement about which screen may call it. Its `RequiredPermission` is
 * `ManagePermissions.EventTriggerReadId`, so a caller without the Manage
 * activator Read grant gets a 403 and the editor renders its inline error;
 * that is the deliberate cost of not standing up a second endpoint.
 *
 * Distinct from {@link LookupService}, whose `lookup-*` routes address a field
 * by the dataset's and field's **Guids**. An activator parameter carries the
 * integer `referenceDatasetId` / `referenceDatasetDisplayFieldId` that setup
 * metadata uses, which those routes cannot take — which is why this endpoint
 * exists at all.
 */
@Injectable({ providedIn: 'root' })
export class EventTriggerLookupService extends ServiceBase {
  private URL: string;

  constructor(httpClient: HttpClient, authService: AuthService, configService: ConfigurationService) {
    super(httpClient, authService);
    this.URL = configService.coreAPI('');
  }

  /**
   * Searched and capped server-side (100 rows by default), so this is called per
   * keystroke-batch rather than once per dialog.
   */
  getParameterOptions(command: GetLookupOptionsCommand): Observable<ItemViewModel<number>[]> {
    return this.post<ItemViewModel<number>[]>(
      `${this.URL}/${EVENT_TRIGGER_LOOKUP_DATA_GET}`, command)
      .pipe(map(rows => (rows ?? []).map(r => new ItemViewModel<number>(r))));
  }
}

export const EVENT_TRIGGER_LOOKUP_DATA_GET = 'manage-event-triggers-get-lookup-data';

/**
 * `manage-event-triggers-get-lookup-data` -> `GetLookupOptionsCommand`.
 *
 * The whole parameter travels, not just its id: the controller re-reads the row
 * by `parameter.instanceId`, but the assertion messages quote `parameter.name`.
 *
 * `searchOptions` is the server-side search — `SearchExpr` names the column,
 * `SearchOperation` the SQL operator and `SearchValue` the term. The C# type
 * defaults `Take` to 100 and `Skip` to 0, so an unfiltered open returns the
 * first 100 rows rather than the whole dataset.
 */
export class GetLookupOptionsCommand {
  constructor(
    public parameter: Record<string, unknown>,
    public searchOptions: LookupSearchOptions,
  ) { }
}

/** Mirrors `Babesiosis.Core.DynamicQuery.SqlParser.DynamicQuerySearchOptions`. */
export interface LookupSearchOptions {
  searchExpr: string;
  searchOperation: string;
  searchValue: string;
  take?: number;
  skip?: number;
}
