import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Datasets (Manage). Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'The Manage screens let you browse the data held in deployed datasets and, where your role allows, add, edit and delete rows by hand. One screen layout serves every dataset type: Entity, Attribute, Classification, Data table, Lookup and Reference.',
    },
    {
      kind: 'paragraph',
      text: 'Each screen builds itself from the dataset\'s field settings, so the columns you see and the cells you can edit differ from dataset to dataset.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Open Data › Manage › Data Warehouse and choose a dataset type: Entities, Attributes, Classifications, Data Tables or Lookups. The type page lists its datasets. Open one to see its rows in a grid.',
    },
    { kind: 'heading', text: 'The grid' },
    {
      kind: 'list',
      items: [
        'Only fields marked visible appear as columns, in the order set for the dataset.',
        'Only fields marked editable accept input.',
        'A field that stores a code, such as a lookup or a reference to another dataset, shows its readable label. You edit the underlying value.',
        'The grid loads one page at a time from the server. Choose a page size between 50 and 250 rows.',
      ],
    },
    { kind: 'heading', text: 'What you can do' },
    {
      kind: 'list',
      items: [
        'Add a row, on every type except Reference.',
        'Edit a row, on every type except Reference.',
        'Delete a row, on Data tables and Lookups only.',
      ],
    },
    { kind: 'heading', text: 'Adding a row' },
    {
      kind: 'list',
      items: [
        'On Entity, Attribute and Classification datasets, each value you enter is saved as the row\'s loaded value and, for a field that can be overridden, as its manual value too. The row reads the same as it would after a load of those values.',
        'On Data tables and Lookups there are no override columns, so the value is saved in the field itself.',
        'A Classification row is one version of a business key. You can add one only when no version of that key exists yet. The new version covers the dataset\'s full date range.',
        'After a Classification add, a later load of identical values detects no change. A load of different values updates or splits the version, and your manual values keep precedence until you clear them.',
      ],
    },
    { kind: 'heading', text: 'Editing a row' },
    {
      kind: 'list',
      items: [
        'On Entity, Attribute and Classification datasets, an edit changes only the manual (override) values. The loaded values are never touched.',
        'Clear a field to remove its override. The loaded value becomes the effective value again. A field you leave unchanged keeps its existing override.',
        'On a Lookup, an edit updates the field in place.',
        'An Attribute\'s parent entity can be set only when you add the row. The edit form does not let you change it.',
      ],
    },
    { kind: 'heading', text: 'Editing a Classification row' },
    {
      kind: 'paragraph',
      text: 'A Classification edit always targets one version, chosen by date. You supply an effective date, and the rows offered for editing are those whose version contains that date.',
    },
    {
      kind: 'list',
      items: [
        'Effective date equals the version\'s start date: the version is updated in place. Only its manual values change.',
        'Effective date is after the start date: the version is split. A new version runs from your effective date to the old version\'s end date. It keeps the old loaded values and combines the old manual values with what you entered. The old version closes the day before your effective date.',
        'Your override reaches only the version you edited, extended through a split to that version\'s end date. It is not carried onto a later version that already exists.',
      ],
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'Every edit, and every delete on a Data table or Lookup, is checked against the row as you last read it. If the row has changed since, the save is rejected. Reopen the grid to see the current values.',
        'Entity, Attribute and Classification rows cannot be deleted from these screens.',
        'Reference datasets show in the same grid but are read-only. Add, Edit and Delete are always refused for them.',
        'The system datasets Country, Currency and Calendar are Reference datasets, so they are read-only too.',
        'Each dataset type has its own permission group in Roles, except that Attribute and Classification share one. Reference grants only Read and Download.',
        'A dataset that has not been deployed with its store table, or that has no audit table, refuses adds, edits and deletes until it is redeployed.',
      ],
    },
    { kind: 'heading', text: 'Audit trail' },
    {
      kind: 'paragraph',
      text: 'Every manual add, edit and delete leaves a permanent audit record that names who made the change. Records are kept for Entity, Attribute, Classification, Data table and Lookup datasets. Reference datasets are read-only, so they have none.',
    },
    { kind: 'heading', text: 'What is recorded' },
    {
      kind: 'list',
      items: [
        'One record is kept for each field that changed. Each save groups its records together.',
        'Each record shows when the change was made (UTC), the editor\'s name and email as they were at the time, and whether it was an add, an edit or a delete.',
        'It also shows the row, identified by its business key and a readable label, and the field with its name at the time.',
        'The value before and after the change is the effective value shown on the screens, with its readable label for lookup fields.',
        'For a field that can be overridden, the record also keeps the loaded value under the override, and whether the override was set or cleared.',
        'A Classification record also shows the effective date. When an edit splits a version, the record points to the new version, with the version it closed beside it.',
        'An add records every field that holds a value. A delete records every field that held a value, so the deleted row stays on record.',
        'An edit records only the fields whose shown value or override actually changed.',
        'No reason for the change is captured.',
      ],
    },
    { kind: 'heading', text: 'Rules for audited saves' },
    {
      kind: 'list',
      items: [
        'A change and its audit records are saved together. If the audit cannot be written, nothing is saved, including the edit itself.',
        'A save that changes nothing writes nothing: no new version, no audit record. The row is returned as it was.',
        'An add with no values is refused.',
        'A delete of a row that held no values still records the row\'s key fields, so every delete leaves at least one record.',
        'If no user record can be found for you, the save is refused.',
        'Audit records are permanent. There is no audit export, and reading the audit is not itself recorded.',
      ],
    },
    { kind: 'heading', text: 'Viewing the audit' },
    {
      kind: 'list',
      items: [
        'History action: the Actions column on every type except Reference has a History action. Classification keeps its time-series action beside it. Without the audit permission the action is disabled.',
        'History drawer: opens at the side with one entry per save, such as who edited how many fields and when. Each entry lists its fields from before to after. A cleared override reads "Override cleared" with the loaded value now shown. A Classification entry shows its effective date.',
        'On a Classification row, the History action lists changes to every version of that row, not just the one you clicked.',
        'Dataset audit page: open it from the grid\'s page header. It is a filterable grid, loaded a page at a time, with the columns Edited At, User, Operation, Row, Field, Before and After. Classification datasets add Effective Date.',
        'The dataset audit page is the only place a deleted row can be found.',
      ],
    },
    { kind: 'heading', text: 'Audit permission' },
    {
      kind: 'paragraph',
      text: 'Viewing the audit needs its own permission, separate from the data Read permission. Roles has one audit group for each of Entity, Attribute, Classification, Data table and Lookup, each with Read only. Unlike the data permissions, Attribute has its own audit group and does not share Classification\'s. Having Read on a type\'s data gives no access to its audit. Reference has no audit group.',
    },
  ],
};

export default body;
