import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Lineage. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'Lineage is how Babesiosis traces a row of data back to the event that wrote it. This topic explains the Batch ID on every row, the deployment log, the permanent audit trail of manual edits, and the check that stops a save overwriting a change made since the row was loaded.',
    },
    { kind: 'heading', text: 'Batch IDs' },
    {
      kind: 'paragraph',
      text: 'Every dataset row carries a Batch ID. When a load writes rows, it stamps the same Batch ID on every row it writes in that one load step. Use it to find the load that wrote a row.',
    },
    {
      kind: 'list',
      items: [
        'A Classification row\'s Batch ID shows the most recent load to touch it, not always the load that first created it.',
        'When a load splits a Classification version, it stamps the new row and the closed row with its own Batch ID. The batch that originally created the closed version cannot be recovered from that row.',
        'Where a manual write stamps a Batch ID, the ID is new. It does not match any pipeline run or deployment, so you cannot trace a manual edit back to one.',
      ],
    },
    { kind: 'heading', text: 'The deployment log' },
    {
      kind: 'paragraph',
      text: 'Each dataset deployment run is recorded as a header plus the full sequence of steps it took. A step keeps the statement it ran and its own log output. You can review each step\'s statement and log output afterwards. Steps cover creating, altering and tearing down datasets, linking a dataset, and rebuilding the hash for a store.',
    },
    {
      kind: 'list',
      items: [
        'The history is not permanent. A user with the permission to delete deployment logs can remove one run\'s step history at a time.',
        'Deleting a run also removes it from the history list.',
        'Deleting a log is not itself recorded anywhere.',
        'Older runs may show a retired step that new deployments no longer produce.',
      ],
    },
    { kind: 'heading', text: 'The audit trail of manual edits' },
    {
      kind: 'paragraph',
      text: 'Every manual change to a row is recorded permanently: who changed which field, when, and from what value to what value. The History drawer on the manage-data screen and the dataset audit page show these records.',
    },
    {
      kind: 'list',
      items: [
        'It covers every add, edit and delete made on the manage-data screens for Entity, Attribute, Classification, Data Table and Lookup datasets.',
        'Each changed field gets its own record. A save that changes several fields shares one edit identifier. A record shows the editor\'s name and email as they were at the time, the time of the edit, the kind of change, the row, and the shown value before and after.',
        'For a field that can be overridden, the record also shows the loaded value underneath the override.',
        'Pipeline loads, deployment re-seeds and a load overwriting a manual edit are not audited. Only changes are recorded: viewing, time-series views and exports are not logged.',
        'Reference datasets are read-only on the manage screens, so they have no audit trail.',
        'The audit is written together with the change. If the audit records cannot be written, the edit is not saved either. A dataset with no audit table refuses adds, edits and deletes.',
        'Records are never purged. They leave the user schema only when the dataset\'s store table is removed.',
        'Reading the audit needs its own permission, separate from the permission to read the data.',
        'There is no reason-for-change field and no audit export.',
      ],
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'The audit is kept in the warehouse database of the dataset\'s linked service, which must be Azure SQL Database, Azure SQL Managed Instance, or SQL Server 2022 or later.',
    },
    { kind: 'heading', text: 'What the row itself carries' },
    {
      kind: 'paragraph',
      text: 'Besides the audit trail, a manual write may leave a Batch ID on the row. The Batch ID carries no user name and no timestamp: use the audit trail to see who edited a row and when. Where a save stamps a Batch ID on the row, the save\'s edit identifier in the audit is that same value.',
    },
    {
      kind: 'list',
      items: [
        'Adding a row stamps a new Batch ID on every manually written dataset type: Entity, Attribute, Data Table, Lookup and Classification.',
        'Editing a Lookup row in place also stamps a new Batch ID.',
        'Editing a Classification row so that it splits stamps the new row with a new Batch ID. The closed row keeps its old Batch ID.',
        'Editing an Entity, Attribute or Data Table row in place, or a Classification row without a split, does not change its Batch ID. The Batch ID can then lag behind the true edit history, which is why the audit trail is the place to look.',
        'Only Data Table and Lookup rows can be deleted by hand. A delete does not mint a Batch ID, but the audit trail records it.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'When you add a row to an Entity, Attribute or Classification dataset, Babesiosis also keeps a copy of the value you added. This lets a manually added value keep showing through after a later pipeline load.',
    },
    { kind: 'heading', text: 'Edit conflicts' },
    {
      kind: 'paragraph',
      text: 'Every dataset type that supports manual edits guards against lost updates. When you edit or delete a row, Babesiosis checks that nobody has changed it since you loaded it. If someone has, or the row has gone, the change is refused as a conflict. Reload the data and try again.',
    },
    {
      kind: 'list',
      items: [
        'The check applies to all dataset types that support manual edits.',
        'Adding a row to a Data Table or Lookup dataset needs no check, because there is no existing row to protect.',
        'Every successful write renews the row\'s version, as does every split.',
      ],
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'A load procedure call stamps one Batch ID on every row it writes.',
        'A manual write\'s Batch ID is new each time and is never tied to a pipeline run or deployment.',
        'Deleting a deployment log needs its own permission, separate from the general delete permission on a dataset.',
        'The Batch ID is the way to trace a loaded row. For manual edits, the audit trail tells you who edited a row, when, and what changed.',
      ],
    },
  ],
};

export default body;
