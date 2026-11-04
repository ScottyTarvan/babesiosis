import { HttpClient, HttpEvent, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { AuthService } from 'app/core/services/auth.service';
import { Observable } from 'rxjs';

export interface HttpRequestOptions {
  goToServerErrorPage: boolean;
  retryCount: number;
}

export const defaultRequestOptions: HttpRequestOptions = {
  goToServerErrorPage: false,
  retryCount: 2
};

@Injectable()
export abstract class ServiceBase {

  defaultRequestOptions = {
    goToServerErrorPage: false,
    retryCount: 2
  };

  constructor(protected httpClient: HttpClient,
    protected authService: AuthService) {
  }

  private getOptions(options: Partial<HttpRequestOptions>): HttpRequestOptions {
    return {
      ...this.defaultRequestOptions,
      ...options
    };
  }

  get<T>(link: string, options: Partial<HttpRequestOptions> = this.defaultRequestOptions, params?: HttpParams): Observable<T> {
    return this.httpClient.get<T>(link, {
       params: params
    });
  }

  post<T>(link: string, body: any, options: Partial<HttpRequestOptions> = this.defaultRequestOptions): Observable<T> {
    return this.httpClient.post<T>(link, body);
  }

  postForm<T>(url: string, body: FormData,
    options: Partial<HttpRequestOptions> = this.defaultRequestOptions,
    params?: HttpParams): Observable<HttpEvent<T>> {

    return this.httpClient.post<T>(url, body, {
      observe: 'events',
      params: params,
      reportProgress: true
    });
  }

  postBlob(link: string,
    body: any,
    options: Partial<HttpRequestOptions> = this.defaultRequestOptions,
    params?: HttpParams): Observable<Blob> {

    return this.httpClient.post(link, body, {
      params: params,
      responseType: 'blob'
    });
  }

  put<T>(link: string, body: any, options: Partial<HttpRequestOptions> = this.defaultRequestOptions, params?: HttpParams): Observable<T> {
    return this.httpClient.put<T>(link, body, {
      params: params
    });
  }

  delete<T>(link: string, options: Partial<HttpRequestOptions> = this.defaultRequestOptions): Observable<T> {
    return this.httpClient.delete<T>(link, {});
  }
}

