import { CommonModule } from '@angular/common';
import { HTTP_INTERCEPTORS, provideHttpClient, withInterceptorsFromDi, withXhr } from '@angular/common/http';
import { inject, NgModule, provideAppInitializer } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { AppRoutingModule } from 'app/app-routing.module';
import { AppComponent } from 'app/app.component';
import { ConfigurationService } from 'app/core/services/configuration.service';
import { ApiHeadersHttpInterceptor } from 'app/core/interceptors/api-headers.http.interceptor';
import { RequestTimingHttpInterceptor } from 'app/core/interceptors/request-timing.http.interceptor';
import { ServerErrorHttpInterceptor } from 'app/core/interceptors/server-error.http.interceptor';
import { MockApiHttpInterceptor } from 'app/_mocks/mock-api.interceptor';
import { StoreModule } from '@ngrx/store';
import { rootReducer } from 'app/layout';
import { provideGnomeUi } from '@fundstream-ai/gnome-ui';
import { APP_ICONS } from 'app/app-icons';

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    CommonModule,
    StoreModule.forRoot(rootReducer)
  ],
  providers: [
    // Runtime config must resolve before the first feature service is constructed —
    // they read their API base URL off ConfigurationService in their constructors.
    provideAppInitializer(() => inject(ConfigurationService).load()),
    { provide: HTTP_INTERCEPTORS, useClass: MockApiHttpInterceptor, multi: true },
    { provide: HTTP_INTERCEPTORS, useClass: ApiHeadersHttpInterceptor, multi: true },
    // UnauthorizedHttpInterceptor is not registered while the app has no sign-in:
    // it answers a 401 by logging out, which would bounce the user to a login
    // page that is no longer routed.
    { provide: HTTP_INTERCEPTORS, useClass: ServerErrorHttpInterceptor, multi: true },
    // No-op unless localStorage['fs.timings'] is set. See the class comment for
    // why mock mode records only config.json regardless of this position.
    { provide: HTTP_INTERCEPTORS, useClass: RequestTimingHttpInterceptor, multi: true },
    provideHttpClient(withXhr(), withInterceptorsFromDi()),
    // Registers the iconify-icon element offline (no request to api.iconify.design) with
    // the library's bundled Tabler subset, plus the Tabler icons Babesiosis's own
    // screens use (app-icons.ts, generated: see README "Icons").
    provideGnomeUi({ icons: APP_ICONS }),
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
