/**
 * Mirrors `Babesiosis.Core.Models.Domain.AbstractDataType`.
 *
 * The C# enum is longer than this; these are the members that can appear on an
 * activator parameter — the seven `GetEventTriggerParametersController` offers,
 * plus `None`. Lives in `core/types` rather than beside one feature because two
 * features read it: `setup/event-triggers` authors parameters and
 * `manage/event-triggers` chooses a run-form editor from the same value.
 */
export enum AbstractDataType {
  None = 0,
  Text = 1,
  Integer = 2,
  Decimal = 4,
  Date = 6,
  Boolean = 7,
  Entity = 17,
  Lookup = 18,
}

/** Fallback labels — a response's own `dataTypes` projection replaces these. */
export const DATA_TYPE_LABELS: ReadonlyMap<AbstractDataType, string> = new Map([
  [AbstractDataType.Boolean, 'Boolean'],
  [AbstractDataType.Integer, 'Integer'],
  [AbstractDataType.Decimal, 'Decimal'],
  [AbstractDataType.Date, 'Date'],
  [AbstractDataType.Text, 'Text'],
  [AbstractDataType.Entity, 'Entity'],
  [AbstractDataType.Lookup, 'Lookup'],
]);

/**
 * The two data types that make a parameter point at a deployed dataset — so in
 * Setup they reveal the dataset / display-field pair, and in Manage they make
 * the run form's editor a server-searched lookup rather than a plain input.
 * The legacy `customizeItem` and `isLookup()` both tested exactly this pair.
 */
export function isReferenceType(type: AbstractDataType): boolean {
  return type === AbstractDataType.Entity || type === AbstractDataType.Lookup;
}
