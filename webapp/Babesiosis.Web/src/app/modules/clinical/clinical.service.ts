import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { catchError, Observable, of, throwError } from 'rxjs';
import {
  ClinicalIndexViewModel,
  ClinicalPageViewModel,
} from 'app/modules/clinical/viewmodels/clinical.viewmodel';

/**
 * Reads the clinical manual. The manual is static files in `assets/clinical/`
 * (no API, no database): `index.json` is the rail, `<ID>.json` is one page.
 * The requests are plain GETs of the app's own assets, so the mock API
 * interceptor lets them through (it only takes `/api/...` URLs).
 */
@Injectable({
  providedIn: 'root'
})
export class ClinicalService {
  private readonly URL = 'assets/clinical';

  constructor(private readonly httpClient: HttpClient) { }

  getIndex(): Observable<ClinicalIndexViewModel> {
    return this.httpClient.get<ClinicalIndexViewModel>(`${this.URL}/index.json?t=${Date.now()}`);
  }

  /**
   * One page, or `null` when its file is not written yet. A missing file is a
   * 404 when deployed; the dev server answers it with the app's HTML instead,
   * which fails to parse as JSON (status 200). Both mean "not written".
   */
  getPage(id: string): Observable<ClinicalPageViewModel | null> {
    return this.httpClient
      .get<ClinicalPageViewModel>(`${this.URL}/${encodeURIComponent(id)}.json?t=${Date.now()}`)
      .pipe(
        catchError((err: HttpErrorResponse) =>
          err.status === 404 || err.status === 200 ? of(null) : throwError(() => err)),
      );
  }
}
