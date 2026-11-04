import { v4 as uuidv4 } from 'uuid';

export class ViewModel {
  /**
   * The row's id — server-assigned for a stored row, minted here for a new one.
   *
   * A new row must reach the server with a REAL Guid, never null and never the
   * empty Guid. Backend view models inherit `InstanceId` from their own
   * `ViewModel` as a **non-nullable `System.Guid`**, so a JSON `null` fails
   * Newtonsoft deserialization before any controller runs — `Error converting
   * value {null} to type 'System.Guid'` — and the empty Guid deserializes fine
   * but is then copied straight onto the stored row by AutoMapper, becoming that
   * row's permanent id and colliding on the next add.
   *
   * Hence the fallback below rather than a plain assignment: an `obj` that
   * carries no id (an add payload the server had nothing to echo into) keeps the
   * id the initialiser above minted. Without it the initialiser was dead for
   * every caller that passed an object, which is why several dialogs still mint
   * their own `crypto.randomUUID()` into the form — belt and braces that this
   * makes redundant rather than wrong.
   *
   * "Carries no id" is decided by {@link isRealInstanceId}, not by `??`. A blank
   * string and the empty Guid are as unusable as `null` — the first fails
   * deserialization, the second becomes the stored row's permanent id and
   * collides on the next add — yet both survive `??`, so a caller seeding a new
   * row with `{ instanceId: '' }` would post that empty value straight through.
   */
  instanceId?: string = uuidv4();
  rowVersion?: string;
  permissions: Map<string, boolean>;

  constructor(obj?: ViewModel | Partial<ViewModel>) {
    if (obj) {
      this.instanceId = isRealInstanceId(obj?.instanceId) ? obj.instanceId : this.instanceId;
      this.rowVersion = obj?.rowVersion;
      this.permissions = obj.permissions
        ? (obj.permissions instanceof Map
            ? new Map(obj.permissions)
            : new Map(Object.entries(obj.permissions as Record<string, boolean>)))
        : new Map<string, boolean>();
    }
  }
}

/** The empty Guid — a value the server accepts and then cannot tell apart from a real id. */
const EMPTY_GUID = '00000000-0000-0000-0000-000000000000';

/**
 * True when `value` is an id worth keeping — anything else means the caller had
 * no id and should be given the freshly minted one.
 */
export function isRealInstanceId(value: unknown): value is string {
  if (typeof value !== 'string') return false;
  const trimmed = value.trim();
  return trimmed.length > 0 && trimmed !== EMPTY_GUID;
}
