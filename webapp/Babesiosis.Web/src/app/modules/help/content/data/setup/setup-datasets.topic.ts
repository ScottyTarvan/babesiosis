import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Datasets (Setup). Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'A dataset is a table you define in Babesiosis: its fields, keys and indexes. When you deploy it, Babesiosis creates its tables and view in your database, plus a load procedure for Entity, Attribute, Classification and Data datasets. Pipelines then load data into it.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Open Data › Setup › Data Warehouse and choose a table type. Each table type has its own list. A row shows the name, linked service, description and deployment state, plus the merge rule or reference column where the type has one. Deployment state refreshes on its own.',
    },
    { kind: 'heading', text: 'List rows and actions' },
    {
      kind: 'list',
      items: [
        'A normal row is a defined dataset. You can edit, open, export, unlink or delete it.',
        'A link placeholder row means a Link Table attempt is in progress or failed. Use Continue, Resume or Delete.',
        'A tombstone row marks a dataset that was unlinked or deleted. Use Dismiss to clear it.',
        'Create adds a dataset. Link Table attaches an existing database table instead of generating a new one.',
        'Import uploads a dataset definition as JSON. A name already used by a dataset of the same table type in the same environment is refused. Export downloads one from the row menu.',
        'Create, Link Table, Import and Export each need their own permission.',
      ],
    },
    { kind: 'heading', text: 'Creating and editing' },
    {
      kind: 'list',
      items: [
        'The dialog takes the name, export file name, description and linked service. Data datasets also take a merge rule, row-based or set-based.',
        'The table type comes from the list you opened the dialog from. You cannot change it later.',
        'Classification and Attribute datasets can link to an Entity dataset and choose which of its fields is the display label. You can change this later.',
        'If someone else changed the dataset since you opened it, your save fails instead of overwriting their change.',
      ],
    },
    { kind: 'heading', text: 'The dataset hub' },
    {
      kind: 'paragraph',
      text: 'Open a dataset to see its tabs. A tab you may not read is disabled. Lookup and Reference datasets have no Keys tab. Leaving General with unsaved edits raises a save-and-continue prompt. Edits on other tabs are not checked.',
    },
    {
      kind: 'list',
      items: [
        'General edits the name, export file name, description, merge rule and linked reference. It has its own Save and Reset. The linked service is read-only.',
        'System Fields shows the columns the platform adds, such as the Batch ID and the action code. Classification adds start date, end date, hash key and previous version. You can change a system field\'s visibility.',
        'Keys sets the business key: the fields that identify a record when data loads.',
        'Indexes adds your own indexes. A newly ticked field is Ascending. The platform builds key and system indexes itself, so they are not listed.',
        'Deployment lists the tables, procedures and views created for the dataset. Select one to see its script.',
        'Validations lists the checks on the definition, each passed or failed, with a summary. The checks run each time you open the tab.',
        'Diagnostics compares the design with the database and offers repair actions, including Finish and unblock. Actions that would drop something ask you to confirm first.',
      ],
    },
    { kind: 'heading', text: 'Fields' },
    {
      kind: 'list',
      items: [
        'Add, edit, remove and reorder fields on the Fields tab. Reordering one tab does not move keys or index columns.',
        'A name is 2 to 100 characters: letters, digits and underscore, starting with a letter. It must be unique in the dataset and cannot match a system field.',
        'A new field goes after the existing ones and is never a key. Set keys on the Keys tab.',
        'Only one field can be Fixed. Marking another clears the first without a message.',
        'You cannot change a field\'s type, or remove it, while a relationship or deployed index uses it. The message says what still uses it.',
        'Removing a field that other things show as a display field only warns you. A design index that includes it loses the field too.',
        'Every change marks the dataset Changes Pending.',
        'A field\'s manual merge rule decides its extra columns. Loaded Only has no manual or effective column. Manual Only has a manual column only. The other rules have both.',
      ],
    },
    { kind: 'heading', text: 'Field types' },
    {
      kind: 'list',
      items: [
        'Numbers: Small Integer, Integer, Big Integer, Decimal, Float and Money. Use Decimal, not Float, for exact figures. Decimal takes precision 1 to 38 and scale 1 to 38, not above precision.',
        'Text and Unicode Text take a length of 1 to 4000. Use Unicode Text for accents or non-Latin characters: Text is stored in the database\'s code page, and characters outside it are not safe.',
        'Date, Date Time, Time and True/False. Date Time stores no time zone offset.',
        'Country and Currency pick from the system lists. Entity, Lookup and Reference Lookup need a deployed dataset and a display field from it.',
        'Most types accept a default value. Entity, Lookup and Reference Lookup do not.',
      ],
    },
    { kind: 'heading', text: 'Deploying' },
    {
      kind: 'list',
      items: [
        'Use the dataset\'s Deploy action. It is refused if the dataset is already deploying, is a tombstone or link placeholder, has a failing validation, or has an active run.',
        'A dataset that was imported and never deployed must be adopted with Link first. On a first deployment, a name already used by another object is refused.',
        'Babesiosis then plans the changes and pauses at Awaiting approval. Every planned run needs approval. Destructive steps are marked in the plan.',
        'Approve or cancel the run with the permission for its action: Deploy for Deploy and Patch, otherwise Delete, Unlink or Link.',
        'Every run is recorded in the deployment log, with its steps, its status, and who started and approved it.',
        'Planning is blocked if the database no longer matches what was last deployed, unless an earlier half-finished run explains it. Use Diagnostics. Unlink and delete runs are never blocked this way.',
        'A deployment is refused if adding a foreign key would fail because existing values have no matching target row. Fix the data, then resume the run.',
        'A new not-nullable field with no default blocks deployment once the dataset already holds rows.',
        'A Country or Currency field deploys without a foreign key, with a warning, if neither target exists. Warnings do not stop a deployment.',
        'The run actions are Deploy, Patch, Link, Unlink, Delete and Remediate. Remediate comes from Diagnostics and skips planning and approval.',
        'A run is active in every status except Succeeded and Abandoned. Resume or abandon a Failed, Cancelled or Blocked run before starting another. A failed, cancelled or blocked Remediate run does not block a new run.',
      ],
    },
    { kind: 'heading', text: 'Audit table, unlink and delete' },
    {
      kind: 'list',
      items: [
        'Entity, Attribute, Classification, Data and Lookup datasets get an audit table beside the store table, created by the first deployment. It keeps the permanent record of manual edits. Reference datasets have none.',
        'The audit table is append-only. Redeploying never rebuilds or drops it. Renaming, removing or retyping a field leaves it unchanged.',
        'A dataset with an audit table will not deploy to a warehouse other than Azure SQL Database, Azure SQL Managed Instance or SQL Server 2022 or later.',
        'Before changing anything, a deployment checks that its database login has the ledger permissions it needs. A delete that removes the store data checks too.',
        'A deployed dataset with no audit table cannot take manual adds, edits or deletes. Diagnostics shows a warning and the next deployment creates the table.',
        'Diagnostics only checks that the audit table exists. It is never counted as drift or as an extra object, and is never offered for removal. Link Table never offers it as a candidate.',
        'A delete that removes the store data also drops the audit table. SQL Server keeps a dropped audit table\'s data under a new name, so it leaves the schema but is not erased.',
        'An unlink or delete that keeps the store table keeps the audit table and its history. The teardown preview lists the audit table, without a row count.',
        'Linking an existing table creates no audit table. The next deployment gives the dataset one, reusing a kept table so the history continues. Until then manual edits are refused.',
      ],
    },
    { kind: 'heading', text: 'Loading data' },
    {
      kind: 'list',
      items: [
        'Entity, Attribute, Classification and Data datasets get a staging table and a load procedure. A pipeline lands data in staging, then calls the load. Lookup and Reference datasets get neither.',
        'Row-based merge matches on the full business key. New keys are inserted and matching keys updated. Keys missing from the batch are left alone.',
        'A Data dataset using row-based merge can delete a row when its staged row is flagged as a deletion.',
        'Set-based merge, for Data datasets only, deletes every row for each set key in the batch, then inserts the new rows as one unit. It is how a reload retires dropped records.',
        'A null in the batch keeps the existing value for Entity and Classification. It overwrites the value for Attribute and row-based Data.',
        'If any staged row is invalid, an atomic load stops before changing anything. Otherwise it loads the valid rows and reports a warning.',
        'By default the batch\'s staging rows are cleared after the load, even if it failed. A failed batch then cannot be retried from staging.',
      ],
    },
    { kind: 'heading', text: 'Classification history' },
    {
      kind: 'list',
      items: [
        'Each business key has contiguous versions. Exactly one covers any date. The open version ends on 9999-12-31 and a first version starts on 1753-01-01.',
        'A load compares the incoming hash key with the covering version at the effective date. If they match, nothing changes. Dates are compared without time of day.',
        'The same date as the version start updates it in place. A later date closes the version the day before and adds a new one, carrying manual values forward.',
        'The hash key covers loaded values only, so manual overrides never trigger a change and loads never change overrides.',
        'A manual add is allowed only when the key has no version yet. A manual edit changes one version and does not carry forward to later versions that already exist.',
        'Redeploying after a change that alters how values are written as text can recalculate stored hash keys. Renaming or widening a field does not.',
      ],
    },
    {
      kind: 'note',
      intent: 'warning',
      text: 'Known issue: a manual edit that splits a Classification version fails when the dataset has at least one overridable field. In-place edits and manual adds are not affected.',
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'Reference datasets, such as Country and Currency, are locked against schema edits, creation and teardown. The server refuses these changes. Dataset names are not forced to be unique, apart from on import.',
    },
  ],
};

export default body;
