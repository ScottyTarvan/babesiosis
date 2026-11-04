/**
 * The readable half of a function-app error — the one extractor for every
 * screen that reports a failed request.
 *
 * `detail` first, and that ordering is the whole point: `HttpFunctionBase` puts
 * a generic caption in `message` ("Failed to unlink dataset") and the actual
 * assertion text — the sentence naming what is wrong and what to do — in
 * `detail`. Reading `message` first, as the inline `err?.error?.message`
 * extractors this replaces did, throws away every useful rejection the server
 * produces.
 *
 * A `ConcurrencyException` answers 409 with a bare string body rather than the
 * envelope, so that case is handled too. Branching on a *status code* is still
 * the caller's business — this only decides what the failure says, never what
 * it means.
 *
 * ## Where the message goes
 *
 * One render rule, so the same fault reads the same way everywhere:
 *
 *  - **A dialog-hosted flow** renders the error in the dialog — the user is
 *    mid-decision there, and a toast behind a modal goes unseen.
 *  - **A page-level action** toasts it *and* sets the page's error banner: the
 *    server's sentence names the state that blocked the action, and a toast
 *    evaporates before it is read.
 *  - **A page-level load** sets the banner only — there is no action to
 *    acknowledge, and an empty page needs the explanation where the content
 *    would have been.
 */
export function errorMessage(err: unknown, fallback: string): string {
  if (typeof err === 'string' && err.trim()) return err;

  const body = (err as { error?: unknown })?.error;
  if (typeof body === 'string' && body.trim()) return body;

  const envelope = body as { detail?: string; message?: string } | undefined;
  return envelope?.detail?.trim()
    || envelope?.message?.trim()
    || (err as { message?: string })?.message?.trim()
    || fallback;
}

/**
 * The other half of the same envelope `errorMessage` reads, but for BRANCHING rather than
 * DISPLAY: a machine-readable `code` — `DATASET_NOT_DEPLOYED`, `MAPPING_NAME_DUPLICATE`, etc,
 * see `CodedValidationException` / `MappingErrorCodes` on the server — that a caller can
 * switch on to do something other than show text (highlight a field, offer a different
 * action). `errorMessage` still owns what gets shown; this only tells the caller whether it
 * gets to make that choice.
 *
 * Returns `null` whenever there is nothing to branch on: a bare-string error body (the
 * `ConcurrencyException` 409 shape, which carries no code at all), a body with no `code`
 * key, or `code` absent for any other reason — a plain `ValidationException`'s 400 envelope
 * included, since only `CodedValidationException` populates it. Callers MUST still fall back
 * to `errorMessage` when this returns `null`; it is never itself a fallback.
 */
export function errorCode(err: unknown): string | null {
  if (typeof err === 'string') return null;

  const body = (err as { error?: unknown })?.error;
  if (typeof body !== 'object' || body === null) return null;

  const code = (body as { code?: unknown }).code;
  return typeof code === 'string' && code.trim() ? code : null;
}
