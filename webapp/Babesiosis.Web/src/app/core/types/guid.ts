/**
 * The all-zero Guid — C#'s `Guid.Empty`, as it appears on the wire.
 *
 * Several backend commands type an id as a **non-nullable** `System.Guid`. JSON
 * `null` does not deserialize into one; it throws before any handler runs
 * (`Error converting value {null} to type 'System.Guid'`). Those contracts spell
 * "no id" as the empty Guid instead, so a frontend command holding an optional
 * id normalises with `id || EMPTY_GUID` on its way out.
 *
 * Lives in `core` rather than in one feature's command file because more than
 * one feature area needs it and a feature must not import from another feature.
 */
export const EMPTY_GUID = '00000000-0000-0000-0000-000000000000';
