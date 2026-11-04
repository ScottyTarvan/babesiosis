import { Injectable } from '@angular/core';
import { HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from 'app/core/services/auth.service';

@Injectable()
export class ApiHeadersHttpInterceptor implements HttpInterceptor {

  constructor(private authService: AuthService) { }

  intercept(req: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    const headers = this.getHeaders(req);

    const modifiedReq = req.clone({
      setHeaders: headers
    });

    return next.handle(modifiedReq);
  }

  private getHeaders(req: HttpRequest<unknown>): Record<string, string> {
    // Authorization only. The backend function key is NEVER sent from the browser —
    // Babesiosis.Proxy.App injects `x-functions-key` server-side from Key Vault and
    // strips any client-supplied copy of that header.
    const headers: Record<string, string> = {
      'Authorization': this.authService?.authToken || ''
    };

    return headers;
  }
}
