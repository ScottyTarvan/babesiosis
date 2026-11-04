import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Adjacent columns. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'Some datasets keep up to three columns for each editable field: the value that was loaded, the value someone entered by hand, and the effective value that people and other modules actually read. Keeping them side by side means a manual correction is never lost when data is reloaded.',
    },
    {
      kind: 'paragraph',
      text: 'This applies only to Entity, Attribute and Classification datasets. Data Table, Lookup and Reference datasets have no manual or effective columns. Editing a field on a Data Table or Lookup overwrites the loaded value directly, so nothing records what it first loaded with. Reference rows cannot be edited in Manage.',
    },
    { kind: 'heading', text: 'The four merge rules' },
    {
      kind: 'paragraph',
      text: 'Each editable field has a merge rule. The rule decides which columns the field gets and which value wins.',
    },
    {
      kind: 'list',
      items: [
        'Manual | Loaded: the field has loaded, manual and effective columns. The manual value wins when there is one; otherwise the loaded value shows.',
        'Loaded | Manual: the same three columns, but the loaded value wins when there is one. The manual value shows only when the loaded value is empty.',
        'Manual Only: loaded and manual columns. The manual value is the value that counts. There is no separate effective column, but readers still see the field under its own name. Manage does not let you override a Manual Only field, because there is no loaded value to fall back to if you reverted.',
        'Loaded Only: a loaded column only. The field cannot be overridden from Manage.',
      ],
    },
    { kind: 'heading', text: 'What changes each column' },
    {
      kind: 'list',
      items: [
        'A load writes the loaded column and never changes a manual value. The effective value updates by itself.',
        'Add in Manage writes what you enter to both the loaded and manual columns. A value entered by hand looks the same in the loaded column as one that arrived by load. A later load of the same value passes through unchanged, and a load of a different value updates the row.',
        'Edit in Manage changes the manual column. The loaded value underneath is left in place, so the next load can still update it.',
        'Clearing a manual value makes the loaded value effective again.',
      ],
    },
    { kind: 'heading', text: 'Classification edits and versions' },
    {
      kind: 'paragraph',
      text: 'Only Classification datasets have an effective date. If your edit takes effect on the row\'s existing start date, the change is made in place. If it takes effect after the start date and on or before the end date, the end date being inclusive, the current version is closed and a new one opens. This is a normal edit, not an error.',
    },
    {
      kind: 'paragraph',
      text: 'A load can also split a period. In both cases the new row carries forward the manual values already in force, so an override is not lost. A manual change never causes a load to see a change, and a load never alters a manual override.',
    },
    { kind: 'heading', text: 'Reading the data' },
    {
      kind: 'paragraph',
      text: 'Each dataset with these columns has a generated view with one column per field, named for the field, whichever merge rule it uses. Read through this view rather than the store table. The differences between the four rules then stay hidden.',
    },
    {
      kind: 'paragraph',
      text: 'Entity datasets also carry a linked ID. It uses the manual override of the linking value first, then the loaded linking value, then the row\'s own identifier.',
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'To tell whether a value is overridden, compare the effective value with the loaded value. A manual value being present does not prove an override, because a row added by hand has the same value in both columns.',
        'Every add or edit in Manage is stamped with a version. If someone else changed the row since you opened it, your edit is rejected, so two people cannot overwrite each other without noticing.',
        'You can add and edit Entity, Attribute and Classification rows in Manage but not delete them. Delete is available only for Data Table and Lookup datasets.',
        'Do not end a field name in _Manual or _Effective. These endings are reserved for the generated columns. FDM warns you when you design such a field, and the warning does not block deployment.',
      ],
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'A tool that looks for a column named after the field with an _Effective ending will miss Manual Only fields. Read the generated view instead.',
    },
  ],
};

export default body;
