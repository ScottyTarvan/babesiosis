import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Table types. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'Every dataset has a table type, chosen when the dataset is created. The type decides what the dataset holds, how loaded data is merged, whether history is kept and which objects FDM generates for it. There are six types: Entity, Attribute, Classification, Data Table, Lookup and Reference.',
    },
    { kind: 'heading', text: 'The six types' },
    {
      kind: 'list',
      items: [
        'Entity: business objects, such as funds or instruments. An Entity dataset has no parent. Loads insert new rows and update existing ones. History is not kept: a row is overwritten in place. Edited fields can be overridden by hand.',
        'Attribute: attributes of an entity. Each row belongs to a parent entity, and FDM links it to that entity automatically. Loads insert new rows and update existing ones in place, so history is not kept. Edited fields can be overridden by hand.',
        'Classification: time-variant attributes of an entity. Each row belongs to a parent entity and is valid for a date range. The start date defaults to 1753-01-01 and the end date to 9999-12-31. Each row is one version, so a load can add a new version or split an existing one. History is kept, and FDM detects a change by comparing the loaded values with the version already in force. Edited fields can be overridden by hand.',
        'Data Table: facts, such as holdings or prices. A Data Table has no parent. It links to entities through Entity fields you add to its design. FDM enforces each of those links with a foreign key where the target resolves, except where the rule excludes the column, for example one already keyed by an imported relationship. No history is kept. Edited fields are overwritten directly.',
        'Lookup: a simple list of values that you maintain by hand. It is never loaded, so it has no merge and no history. Edited fields are overwritten directly.',
        'Reference: lists that FDM owns, such as Country, Currency and Calendar. You cannot create one directly. It has no loading and no history. Its design cannot be changed and it cannot be torn down.',
      ],
    },
    { kind: 'heading', text: 'Merge rule' },
    {
      kind: 'paragraph',
      text: 'The Merge Rule control in the dataset editor appears only for a Data Table. Row-based is the default: each incoming row is matched to an existing row by its business key. Set-based is optional: the existing rows for a set are deleted and the incoming rows inserted. Every other type is fixed to row-based and shows no choice.',
    },
    {
      kind: 'note',
      intent: 'warning',
      text: 'With set-based merge, a Data Table does not enforce uniqueness on its business key. The only safeguard against duplicate keys in a load is the delete and insert of each set. For every other type, and for row-based Data Tables, the business key is enforced as unique. For Classification, the unique index also covers the date range.',
    },
    { kind: 'heading', text: 'Reference and system datasets' },
    {
      kind: 'list',
      items: [
        'To get a Reference dataset, use Import Reference Lists. The general create path refuses the Reference type.',
        'Design changes and teardown are locked for every Reference dataset.',
        'Country, Currency and Calendar are system datasets. FDM provides them from a fixed catalogue.',
        'Deploying a system dataset again brings its table into line with the catalogue. Missing rows are inserted, rows no longer in the catalogue are removed and changed values are updated. The change is all or nothing.',
        'Calendar covers 1970-01-01 to 2100-12-31 with exactly one row per day. Each row\'s identifier is its date written as yyyymmdd, for example 20580402 for 2 April 2058.',
        'Calendar has month-start, month-end, quarter-start and quarter-end flags. The month flags are 1 on the first and last day of each month. The quarter flags are 1 on the first and last day of each calendar quarter. Every other day is 0 for each flag. Quarters start on 1 January, 1 April, 1 July and 1 October.',
      ],
    },
    { kind: 'heading', text: 'What gets generated' },
    {
      kind: 'paragraph',
      text: 'When you deploy a dataset, FDM generates a store table that holds the current data. Entity, Attribute, Classification and Data Table also get a staging table and a load procedure. Lookup and Reference have neither, because they are never loaded.',
    },
    {
      kind: 'paragraph',
      text: 'Entity, Attribute, Classification, Data Table and Lookup also get an audit table. Reference has none.',
    },
    {
      kind: 'paragraph',
      text: 'Each dataset also gets a view to read it through. For Entity, Attribute and Classification the view shows each field\'s effective value, meaning the manual override where one applies. For the other types it reads the store table directly.',
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'Lookup is created, edited and torn down like Entity, Attribute, Classification and Data Table. It has no lock.',
        'Each type has its own permissions. Attribute and Classification share one set of permissions, except for the audit permissions: Attribute has its own audit group, and Reference has none.',
        'Not every action exists for every type. Reference is the most restricted: it does not offer Add, Edit, Link, Unlink or Upload.',
        'Approving, declining, resuming or abandoning a deployment run uses the same permissions as the dataset\'s type.',
        'In Manage, deleting rows is not supported on Entity, Attribute or Classification datasets.',
        'Dataset Link can create a dataset over an existing table. That dataset keeps the table\'s own schema and name for its whole life, whatever its type.',
        'Lookup and Reference have no source file, so a correction to their data cannot be traced back to a file.',
      ],
    },
  ],
};

export default body;
