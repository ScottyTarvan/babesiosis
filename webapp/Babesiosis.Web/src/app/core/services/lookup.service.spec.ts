import { TestBed } from '@angular/core/testing';
import { provideHttpClient, withXhr } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { EnvironmentType } from 'app/core/types/environment.type';
import { AuthService } from '@core/services/auth.service';
import { ConfigurationService } from '@core/services/configuration.service';
import {
  GetLookupItemCommand,
  GetLookupItemsCommand,
  LOOKUP_PAGE_SIZE,
  LookupService,
  ResolveLookupItemsCommand,
} from '@core/services/lookup.service';

/**
 * Pins the collapsed wire surface. The point of these tests is the collapse
 * itself: there is ONE route per operation and the field kind is nowhere in the
 * URL, because the server derives the source from `(datasetId, fieldId)`. A
 * regression that reintroduces a per-kind route, or that starts serialising the
 * old `searchOptions` triple into `search`, fails here.
 */
describe('LookupService', () => {
  const BASE = '/api/core';
  const DATASET = '11111111-1111-1111-1111-111111111111';
  const FIELD = '22222222-2222-2222-2222-222222222222';

  let service: LookupService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withXhr()),
        provideHttpClientTesting(),
        LookupService,
        { provide: AuthService, useValue: {} },
        { provide: ConfigurationService, useValue: { coreAPI: () => BASE } },
      ],
    });

    service = TestBed.inject(LookupService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('posts every value list to the one kind-free route', () => {
    service.getItems(new GetLookupItemsCommand(EnvironmentType.Dev, DATASET, FIELD, 'ban')).subscribe();

    const req = http.expectOne(`${BASE}/lookup-items-get`);
    expect(req.request.method).toBe('POST');
    // A plain prefix string, not a serialised searchExpr/searchOperation/searchValue blob.
    expect(req.request.body.search).toBe('ban');
    expect(req.request.body.fieldId).toBe(FIELD);
    // The cap the editor's "showing N of M" footer is measured against.
    expect(req.request.body.take).toBe(LOOKUP_PAGE_SIZE);
    req.flush({ items: [{ id: 7, name: 'Bank of Aruba' }], totalCount: 812 });
  });

  it('keeps the server totalCount rather than the page length', () => {
    let seen: { items: unknown[]; totalCount: number } | undefined;
    service.getItems(new GetLookupItemsCommand(EnvironmentType.Dev, DATASET, FIELD, ''))
      .subscribe(result => (seen = result));

    http.expectOne(`${BASE}/lookup-items-get`)
      .flush({ items: [{ id: 1, name: 'Angola' }], totalCount: 249 });

    expect(seen?.items.length).toBe(1);
    expect(seen?.totalCount).toBe(249);
  });

  it('defaults a missing list response to an empty page', () => {
    let seen: { items: unknown[]; totalCount: number } | undefined;
    service.getItems(new GetLookupItemsCommand(EnvironmentType.Dev, DATASET, FIELD, ''))
      .subscribe(result => (seen = result));

    http.expectOne(`${BASE}/lookup-items-get`).flush(null);

    expect(seen?.items).toEqual([]);
    expect(seen?.totalCount).toBe(0);
  });

  it('posts a single key to lookup-item-get', () => {
    service.getItem(new GetLookupItemCommand(EnvironmentType.Dev, DATASET, FIELD, '42')).subscribe();

    const req = http.expectOne(`${BASE}/lookup-item-get`);
    // The key goes up as a string whatever the field stores; the server types it.
    expect(req.request.body.key).toBe('42');
    req.flush({ id: 42, name: 'Namibia' });
  });

  it('resolves a batch of keys in one request, and keeps unresolved keys absent', () => {
    let seen: { id: number | null }[] | undefined;
    service.resolveItems(
      new ResolveLookupItemsCommand(EnvironmentType.Dev, DATASET, FIELD, ['1', '2', '3']))
      .subscribe(items => (seen = items as { id: number | null }[]));

    const req = http.expectOne(`${BASE}/lookup-items-resolve`);
    expect(req.request.body.keys).toEqual(['1', '2', '3']);
    // Key 2 resolves to nothing and is simply not in the answer — that absence
    // is how the grid marks a key failed and renders it raw.
    req.flush([{ id: 1, name: 'Angola' }, { id: 3, name: 'Botswana' }]);

    expect(seen?.length).toBe(2);
  });
});
