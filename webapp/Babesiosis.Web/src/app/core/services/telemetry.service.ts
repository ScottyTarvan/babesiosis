import { Injectable, isDevMode } from '@angular/core';

/**
 * Spec §11 — telemetry stub. A future PR can swap the implementation for a
 * real analytics backend (Application Insights, Segment, etc.); the call
 * sites are the contract.
 */
@Injectable({ providedIn: 'root' })
export class TelemetryService {
  track(event: string, props?: Record<string, unknown>): void {
    if (!isDevMode()) return;

    console.debug('[telemetry]', event, props ?? {});
  }
}
