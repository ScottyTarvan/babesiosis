import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { ItemViewModel } from 'app/core/viewmodels/item.viewmodel';
import { EnvironmentType } from 'app/core/types/environment.type';
import { Observable, map } from 'rxjs';
import { AuthService } from '@core/services/auth.service';
import { ConfigurationService } from '@core/services/configuration.service';
import { ServiceBase } from '@core/services/service-base';

/**
 * The `lookup-*` endpoints — value lists for a single field of a deployed
 * dataset, resolved out of that dataset's own store rather than the setup
 * database.
 *
 * **Three routes, no kinds.** There used to be an endpoint triple per field kind
 * (entity / lookup / reference-lookup / country / currency / master), because
 * each kind resolved against a different store through a different data-factory
 * method. The server now resolves that itself: `(datasetId, fieldId)` yields a
 * single `LookupSource` descriptor — which store, which key column, which
 * display column, which predicate — so the kind no longer rides in the URL and
 * the client no longer needs to know it. `-items-get` searches and caps a list
 * (and reports how many matched in total), `-item-get` resolves one stored key
 * back to its display text, and `-items-resolve` resolves a BATCH of stored keys
 * in one round trip.
 *
 * A field is identified by two ids together: the dataset's `instanceId` and the
 * field's `instanceId`, both Guids. Neither is the integer `referenceDatasetId`
 * the setup metadata uses — see `EntityGroupFilterViewModel` for that trap.
 * `fieldId` is **required** on all three routes: the old "an empty fieldId falls
 * back to the dataset's single field of that kind" shortcut belonged to the
 * country/currency routes and died with them.
 *
 * Ported from the legacy `@shared/services/lookup.service` and its six
 * `Lookup*DataSource` wrappers. The wrappers are not ported: `<fs-data-grid>`'s
 * remote lookup already provides the search / page / resolve-by-key contract they
 * hand-rolled around a DevExtreme `CustomStore`.
 */
@Injectable({ providedIn: 'root' })
export class LookupService extends ServiceBase {
  private URL: string;

  constructor(httpClient: HttpClient, authService: AuthService, configService: ConfigurationService) {
    super(httpClient, authService);
    this.URL = configService.coreAPI('');
  }

  /**
   * One capped page of a field's value list, plus the honest count of how many
   * values matched the search before the cap.
   */
  getItems(command: GetLookupItemsCommand): Observable<LookupItemsViewModel> {
    return this.post<LookupItemsViewModel>(`${this.URL}/${LOOKUP_ITEMS_GET}`, command)
      .pipe(map(result => ({
        items: (result?.items ?? []).map(i => new ItemViewModel<number>(i)),
        totalCount: result?.totalCount ?? 0,
      })));
  }

  /** One stored key resolved to its display item. */
  getItem(command: GetLookupItemCommand): Observable<ItemViewModel<number>> {
    return this.post<ItemViewModel<number>>(`${this.URL}/${LOOKUP_ITEM_GET}`, command)
      .pipe(map(item => new ItemViewModel<number>(item)));
  }

  /**
   * A BATCH of stored keys resolved to their display items — the grid's
   * `resolveByKeys` contract in one round trip.
   *
   * Keys the source cannot resolve are simply absent from the response (the
   * grid marks those failed and renders the raw key), so the result is not
   * positional and may be shorter than `keys`. The server rejects more than
   * {@link LOOKUP_RESOLVE_CHUNK} keys in one call.
   */
  resolveItems(command: ResolveLookupItemsCommand): Observable<ItemViewModel<number>[]> {
    return this.post<ItemViewModel<number>[]>(`${this.URL}/${LOOKUP_ITEMS_RESOLVE}`, command)
      .pipe(map(items => (items ?? []).map(i => new ItemViewModel<number>(i))));
  }
}

/** The value list for one field, searched and capped. */
export const LOOKUP_ITEMS_GET = 'lookup-items-get';
/** One stored key -> its display item. */
export const LOOKUP_ITEM_GET = 'lookup-item-get';
/** Many stored keys -> their display items, one round trip. */
export const LOOKUP_ITEMS_RESOLVE = 'lookup-items-resolve';

/**
 * `lookup-items-get` -> `GetLookupItemsCommand`.
 *
 * ## Search is a plain prefix string
 *
 * `search` used to be a serialised DevExtreme `searchOptions` JSON blob whose
 * `searchExpr` / `searchOperation` / `searchValue` triple had to be present in
 * full or the server silently returned an unfiltered list — a list that still
 * looks like a working dropdown, which is what made the failure invisible
 * (Zimbabwe, on a country list ordered A to Z, past the 150 cap).
 *
 * The collapsed endpoint takes the search text itself. The match is a **prefix**
 * (`LIKE @search + '%'`), which is what makes it sargable against the display
 * field's index: "amer" does not find "Bank of America", and that is the
 * accepted trade (target architecture D2). There is no second search mode.
 */
export class GetLookupItemsCommand {
  constructor(
    public environment: EnvironmentType,
    public datasetId: string,
    public fieldId: string,
    public search: string,
    public take: number = LOOKUP_PAGE_SIZE,
  ) { }
}

/**
 * `lookup-item-get` -> `GetLookupItemCommand`.
 *
 * `key` is the STORED value, stringified. The server types it from the field's
 * own descriptor — numeric for every id-keyed kind, text for a plain Lookup —
 * so the client never has to decide.
 */
export class GetLookupItemCommand {
  constructor(
    public environment: EnvironmentType,
    public datasetId: string,
    public fieldId: string,
    public key: string,
  ) { }
}

/**
 * `lookup-items-resolve` -> `ResolveLookupItemsCommand`.
 *
 * `keys` are the STORED values, stringified — the same shape `-item-get` takes,
 * which for a plain Lookup field is the display text itself and for every other
 * kind is a numeric store key.
 */
export class ResolveLookupItemsCommand {
  constructor(
    public environment: EnvironmentType,
    public datasetId: string,
    public fieldId: string,
    public keys: string[],
  ) { }
}

/**
 * `lookup-items-get` response — the capped page plus the size of the set it
 * was capped from. `totalCount` is the server's count of everything matching the
 * search, NOT `items.length`: the difference between the two is exactly what the
 * editor reports as "showing N of M".
 */
export interface LookupItemsViewModel {
  items: ItemViewModel<number>[];
  totalCount: number;
}

/**
 * The list endpoint caps itself at 150 rows, matching the legacy data
 * sources, which overrode whatever the editor asked for with `skip = 0` and
 * `take = 150` on every call. A dataset field can have far more distinct values
 * than that, which is why the editor searches rather than scrolls.
 */
export const LOOKUP_PAGE_SIZE = 150;

/**
 * The server's per-call ceiling on `lookup-items-resolve` — more keys than this
 * in one command is a 400, not a truncated answer. It matches the grid's own
 * resolve chunk size (`FS_GRID_LOOKUP_RESOLVE_CHUNK`), which is what keeps the
 * manage screen's `resolveByKeys` a single POST per chunk.
 */
export const LOOKUP_RESOLVE_CHUNK = 100;
