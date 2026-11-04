/** Mirrors `CreatePersonalAccessTokenCommand`. `expiryDays` is 7, 30 or 90. */
export interface CreatePersonalAccessTokenCommand {
  name: string;
  expiryDays: 7 | 30 | 90;
}
