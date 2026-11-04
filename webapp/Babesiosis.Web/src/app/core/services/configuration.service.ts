import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { catchError, map, Observable, of } from 'rxjs';

/**
 * Runtime configuration, fetched from `assets/config.json` by an APP_INITIALIZER
 * before the app renders. Ported from FIT.Angular's ConfigurationService.
 *
 * This replaces the old build-time `src/environments/environment*.ts` files: one
 * artifact is built once and promoted across dev/uat/prod, with the `#{token}#`
 * placeholders in config.json substituted by the release pipeline at deploy time.
 *
 * `proxyBaseUrl` is what decides whether requests go through Babesiosis.Proxy.App,
 * and the switch is which assets folder the build overlays — NOT a build-mode check.
 * (`isDevMode()` would be wrong here: the `development` configuration is unoptimized
 * yet still deploys to Azure via `npm run deploy:dev`.)
 *
 * - Local (the `local` build config, which `npm start` serves) overlays
 *   `public-local/assets/config.json`, which sets `proxyBaseUrl: ""`. Paths stay
 *   relative, so the ng dev server's
 *   proxy.conf.json routes them straight to the Functions host (6060) and Reports
 *   host (7070). The gateway is bypassed entirely and never needs to run locally.
 *
 * - Deployed (`development` / `production`) ship `public/assets/config.json` with the
 *   `#{proxy-base-url}#` token, which the release pipeline replaces with the gateway's
 *   absolute URL. Every call is then prefixed with it and goes through the proxy.
 *
 * Nothing here is secret. The backend function key is NEVER sent to the browser —
 * Babesiosis.Proxy.App injects `x-functions-key` server-side from Key Vault, which
 * is exactly why deployed builds must not fall back to bypassing it silently.
 */
@Injectable({ providedIn: 'root' })
export class ConfigurationService {

  constructor(private http: HttpClient) { }

  client: string;
  userDataKey: string;
  allowEntraLogin: boolean;
  allowEmailLogin: boolean;
  proxyBaseUrl: string;
  useMockApi: boolean;
  /**
   * The MCP server URL shown in Account Settings' ready-to-paste `claude mcp add` command
   * (platform/mcp-server.md §3.13). Claude Code calls the Functions host directly, not the
   * gateway, so it is its own setting. Empty when not configured: the card then shows a
   * placeholder. Locally it defaults to the Functions host the dev proxy targets.
   */
  mcpServerUrl: string;

  // The proxy base paths are constants (the gateway exposes /api/core and /api/reports);
  // proxyBaseUrl is prefixed onto them. They are not configuration.
  private readonly CORE_API_PATH = '/api/core';
  private readonly REPORTS_API_PATH = '/api/reports';

  /**
   * Relative base — API paths are used as-is and the ng dev server proxies them.
   *
   * This is the local-dev value, and it is also the last-resort fallback. Never
   * hard-code a gateway host here: the previous fallback named a port nothing had
   * ever listened on, so a misconfigured build presented as a silent connection
   * failure instead of a config error.
   */
  private readonly RELATIVE_BASE_URL = '';

  load(): Observable<ConfigurationService> {
    return this.http.get<any>(`assets/config.json?t=${Date.now()}`)
      .pipe(
        catchError(error => {
          // Legacy has no error handling here, so a 404 or malformed JSON errors
          // the initializer and the app never boots with no diagnostic. Fall back
          // to the local-dev defaults and say so loudly instead.
          console.error(
            '[config] Failed to load assets/config.json — falling back to local defaults.',
            error);
          return of(null);
        }),
        map(boot => this.apply(boot)));
  }

  private apply(boot: any): ConfigurationService {
    this.proxyBaseUrl = this.resolveBaseUrl(boot?.proxyBaseUrl);
    this.client = this.asString(boot?.client, 'fundstream');
    this.userDataKey = this.asString(boot?.userDataKey, 'authf649fc9a5f55');
    this.allowEntraLogin = this.asBool(boot?.allowEntraLogin, true);
    this.allowEmailLogin = this.asBool(boot?.allowEmailLogin, true);
    this.useMockApi = this.asBool(boot?.useMockApi, false);
    this.mcpServerUrl = this.asString(
      boot?.mcpServerUrl,
      this.isLocal ? 'http://localhost:6070/runtime/webhooks/mcp' : '');
    return this;
  }

  /**
   * Three cases, in order:
   *
   * 1. An absolute http(s) URL — a deployed build with the token substituted. Use it,
   *    so every call is routed through the gateway.
   * 2. An explicit empty string — the `public-local` overlay. Stay relative and let the
   *    dev-server proxy reach the backends directly.
   * 3. An unsubstituted `#{...}#` token — this is ONLY reachable in a deployed build
   *    whose release-pipeline substitution did not run, because local builds overlay an
   *    explicit "". Going relative there means quietly skipping the gateway (and with
   *    it the server-injected function key), so shout about it rather than let a broken
   *    deployment look merely unresponsive.
   */
  private resolveBaseUrl(value: string): string {
    if (typeof value === 'string' && /#\{.*\}#/.test(value)) {
      console.error(
        `[config] proxyBaseUrl is an unsubstituted token (${value}) — the release ` +
        'pipeline did not replace it. Falling back to relative paths, which bypasses ' +
        'Babesiosis.Proxy.App and will fail anywhere but local dev.');
      return this.RELATIVE_BASE_URL;
    }
    if (!value || !/^https?:\/\//i.test(value)) { return this.RELATIVE_BASE_URL; }
    return value.replace(/\/$/, '');
  }

  private isReplaced(value: any): boolean {
    return typeof value === 'string' && value.length > 0 && !/#\{.*\}#/.test(value);
  }

  private asString(value: any, fallback: string): string {
    return this.isReplaced(value) ? value : fallback;
  }

  private asBool(value: any, fallback: boolean): boolean {
    if (typeof value === 'boolean') { return value; }
    return this.isReplaced(value) ? /^true$/i.test(value.trim()) : fallback;
  }

  /** True for the `public-local` overlay: no gateway, calls go straight to the local hosts. */
  get isLocal(): boolean { return this.proxyBaseUrl === this.RELATIVE_BASE_URL; }

  /** `coreAPI('')` yields the base the feature services concatenate routes onto. */
  coreAPI(url: string): string { return `${this.proxyBaseUrl}${this.CORE_API_PATH}${url}`; }

  reportsAPI(url: string): string { return `${this.proxyBaseUrl}${this.REPORTS_API_PATH}${url}`; }
}
