/**
 * Body of `auth-sso-exchange` — trades the authorization code the identity
 * provider hands back for a Babesiosis JWT. Mirrors `SsoExchangeCommand`.
 */
export class SsoExchangeCommand {
  constructor(public code: string) { }
}
