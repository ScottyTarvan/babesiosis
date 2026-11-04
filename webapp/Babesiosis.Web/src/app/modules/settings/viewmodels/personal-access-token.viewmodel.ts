import { parseUtcDate } from 'app/core/types/utc-date';

/**
 * Mirrors `PersonalAccessTokenViewModel` (Core.Api Platform/McpTokens). `instanceId` is the
 * token's id. Never carries the secret or its hash — `prefix` alone identifies a token.
 */
export interface PersonalAccessTokenViewModel {
  instanceId: string;
  rowVersion?: string;
  name: string;
  prefix: string;
  createdDate: string;
  expiresAt: string;
  lastUsedAt?: string | null;
  revokedAt?: string | null;
  status: PersonalAccessTokenStatus;
}

export type PersonalAccessTokenStatus = 'Active' | 'Expired' | 'Revoked';

/**
 * Pins the token's DATETIME2 timestamps to UTC at the data boundary. They arrive with no zone
 * designator after a read (EF materialises them Unspecified), and the browser would otherwise
 * read them as local time — off by the user's offset (see core/types/utc-date.ts).
 */
export function normalisePersonalAccessToken(token: PersonalAccessTokenViewModel): PersonalAccessTokenViewModel {
  const utc = (v: string | null | undefined) => parseUtcDate(v)?.toISOString() ?? null;
  return {
    ...token,
    createdDate: utc(token.createdDate) ?? token.createdDate,
    expiresAt: utc(token.expiresAt) ?? token.expiresAt,
    lastUsedAt: utc(token.lastUsedAt),
    revokedAt: utc(token.revokedAt),
  };
}

/** `platform-mcp-tokens-search` — the caller's own tokens, newest first, plus the card's echo. */
export interface PersonalAccessTokensViewModel {
  tokens: PersonalAccessTokenViewModel[];
  permissions: Record<string, boolean>;
}

/** `platform-mcp-tokens-create` — the only response that ever carries the secret. */
export interface CreatedPersonalAccessTokenViewModel {
  token: PersonalAccessTokenViewModel;
  secret: string;
}
