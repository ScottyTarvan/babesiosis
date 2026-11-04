import { HttpErrorResponse } from '@angular/common/http';
import { throwError } from 'rxjs';
import { MockRegistration } from 'app/_mocks/mock-handler';
import { CreatePersonalAccessTokenCommand } from 'app/modules/settings/commands/create-personal-access-token.command';
import {
  CreatedPersonalAccessTokenViewModel,
  PersonalAccessTokenViewModel,
  PersonalAccessTokensViewModel,
} from 'app/modules/settings/viewmodels/personal-access-token.viewmodel';

/**
 * `platform-mcp-tokens-*` — the Account Settings MCP token card. Mirrors the
 * Search / Create / RevokePersonalAccessToken controllers: own tokens only, newest
 * first, secret returned once on create, revoke refuses a token that is not Active.
 * The mock user holds MCP Access (`canCreate`).
 */
const DAY = 24 * 60 * 60 * 1000;
const iso = (offsetDays: number) => new Date(Date.now() + offsetDays * DAY).toISOString();

let rowVersionSeq = 1;
const nextRowVersion = () => btoa(`rv-${rowVersionSeq++}`);

const tokens: PersonalAccessTokenViewModel[] = [
  {
    instanceId: '6a0f3c1e-0d5b-4a8e-9b51-2f7c9d4e1a01', rowVersion: nextRowVersion(),
    name: 'Work laptop', prefix: 'dmpat_Xa91kQ', createdDate: iso(-12), expiresAt: iso(18),
    lastUsedAt: iso(-1), revokedAt: null, status: 'Active',
  },
  {
    instanceId: '6a0f3c1e-0d5b-4a8e-9b51-2f7c9d4e1a02', rowVersion: nextRowVersion(),
    name: 'Old desktop', prefix: 'dmpat_7Lm2Pz', createdDate: iso(-40), expiresAt: iso(-33),
    lastUsedAt: iso(-35), revokedAt: null, status: 'Expired',
  },
  {
    instanceId: '6a0f3c1e-0d5b-4a8e-9b51-2f7c9d4e1a03', rowVersion: nextRowVersion(),
    name: 'Test token', prefix: 'dmpat_Qw3eRt', createdDate: iso(-20), expiresAt: iso(70),
    lastUsedAt: null, revokedAt: iso(-19), status: 'Revoked',
  },
];

function randomSecret(): string {
  const bytes = new Uint8Array(32);
  crypto.getRandomValues(bytes);
  const b64 = btoa(String.fromCharCode(...bytes)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  return `dmpat_${b64}`;
}

function badRequest(message: string) {
  return throwError(() => new HttpErrorResponse({ status: 400, error: { message } }));
}

/** A read returns DATETIME2 values with no zone designator, exactly as EF serialises them. */
const unzoned = (v: string | null | undefined) => (v ? v.replace(/(\.\d+)?Z$/, '') : v ?? null);

export const platformMcpTokensSearchMock: MockRegistration<unknown, PersonalAccessTokensViewModel> = {
  route: 'platform-mcp-tokens-search',
  handler: () => ({
    tokens: [...tokens]
      .sort((a, b) => b.createdDate.localeCompare(a.createdDate))
      .map(t => ({
        ...t,
        createdDate: unzoned(t.createdDate)!,
        expiresAt: unzoned(t.expiresAt)!,
        lastUsedAt: unzoned(t.lastUsedAt),
        revokedAt: unzoned(t.revokedAt),
      })),
    permissions: { canCreate: true, canRevoke: true },
  }),
};

export const platformMcpTokensCreateMock: MockRegistration<CreatePersonalAccessTokenCommand, CreatedPersonalAccessTokenViewModel> = {
  route: 'platform-mcp-tokens-create',
  handler: body => {
    const name = (body?.name ?? '').trim();
    if (!name) return badRequest('Name is required.');
    if (name.length > 100) return badRequest('Name must be at most 100 characters.');
    const days = body?.expiryDays || 30;
    if (![7, 30, 90].includes(days)) return badRequest('Expiry must be 7, 30 or 90 days.');

    const secret = randomSecret();
    const token: PersonalAccessTokenViewModel = {
      instanceId: crypto.randomUUID(), rowVersion: nextRowVersion(), name,
      prefix: secret.substring(0, 12), createdDate: iso(0), expiresAt: iso(days),
      lastUsedAt: null, revokedAt: null, status: 'Active',
    };
    tokens.unshift(token);
    return { token, secret };
  },
};

export const platformMcpTokensRevokeMock: MockRegistration<{ itemId: string; rowVersion?: string }, PersonalAccessTokenViewModel> = {
  route: 'platform-mcp-tokens-revoke',
  handler: body => {
    const token = tokens.find(t => t.instanceId === body?.itemId);
    if (!token) return badRequest('Token not found.');
    if (token.status !== 'Active') return badRequest(`The token is already ${token.status.toLowerCase()}.`);
    token.status = 'Revoked';
    token.revokedAt = iso(0);
    token.rowVersion = nextRowVersion();
    return { ...token };
  },
};
