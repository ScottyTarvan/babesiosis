import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Data contract. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'The data contract describes the data a report reads and how that data is checked. A report reads data in two separate ways. The entity tree decides who the report runs for. Transforms supply what the report says about each entity.',
    },
    { kind: 'heading', text: 'One dataset per report' },
    {
      kind: 'paragraph',
      text: 'Every report is bound to exactly one dataset, and a report cannot be saved without one. The dataset should be an Entity dataset. The create report dialog only offers Entity datasets. The type is checked again once the report has entity tree nodes, when you list a node\'s columns, preview a node or view its SQL.',
    },
    {
      kind: 'paragraph',
      text: 'The tree uses only the bound dataset\'s own fields. Entity groups and hierarchies, attribute datasets and classification datasets take no part in it. Grouping, filtering and column choices all use the dataset\'s effective values.',
    },
    { kind: 'heading', text: 'The entity tree' },
    {
      kind: 'paragraph',
      text: 'The report\'s dataset rows are organised into a tree of groups. The individual entities at the bottom of the tree are what each report instance is produced for. Each node has:',
    },
    {
      kind: 'list',
      items: [
        'Grouping fields: the dataset fields used to group or aggregate the node\'s entities.',
        'A filter: narrows the entities in the node.',
        'A sequence: the node\'s order among its siblings.',
      ],
    },
    { kind: 'heading', text: 'Limits' },
    {
      kind: 'list',
      items: [
        'A tree can be at most 5 levels deep.',
        'A node can have at most 5 grouping fields.',
        'A chain from the root down to one node can have at most 10 grouping fields.',
        'A node name can be at most 250 characters.',
      ],
    },
    { kind: 'heading', text: 'How the tree is checked' },
    {
      kind: 'paragraph',
      text: 'A dataset can be redeployed and change shape after you build a tree, so Babesiosis checks each node\'s grouping fields and filter every time you save them. It checks again whenever the tree is opened for editing, previewed or run. A field that has been renamed or removed fails the same way at each point. You find out before a run is attempted, not when it fails.',
    },
    {
      kind: 'paragraph',
      text: 'The save check translates the filter and then discards it. Nothing is run against your data. A dataset redeploy is only noticed the next time the tree is opened, saved or run.',
    },
    { kind: 'heading', text: 'Row limits and truncation' },
    {
      kind: 'paragraph',
      text: 'A node preview and a run both cap how many rows they read. If more rows exist than the cap allows, the result is marked as truncated. The entities screen and the node preview both show this. A truncated node may not be safe to run until you narrow it further. Every read is also limited to 50,000 rows and 1,000 groups. Babesiosis does not give an exact count beyond the cap.',
    },
    { kind: 'heading', text: 'Viewing the generated SQL' },
    {
      kind: 'paragraph',
      text: 'You can view the exact SQL statement and parameters that a node would run. Every filter and grouping value reaches the query as a parameter, never as text added into the statement, and this view lets you confirm that.',
    },
    { kind: 'heading', text: 'Periods' },
    {
      kind: 'paragraph',
      text: 'A period never changes which entities or groups the tree selects. Only the tree\'s grouping fields and filters decide that. The period is passed to the report\'s content and transforms when the report is rendered.',
    },
    { kind: 'heading', text: 'Transforms' },
    {
      kind: 'paragraph',
      text: 'A transform runs SQL or a stored procedure that you write, against a linked service that you name. It has no dataset binding and no column allow-list. A renamed or dropped column is not caught when you save. The query fails when the report runs. Report authors build transform and content logic from a fixed, named and versioned set of template functions.',
    },
    {
      kind: 'paragraph',
      text: 'A transform can store a schema snapshot, filled in when you run a successful manual test. It reflects the last successful test, not the current state of the linked service. A separate option on a transform, off by default, delivers its output to templates as typed values instead of text.',
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'Checking a transform against its data when you save it is not yet available. Only the entity tree is checked at save time.',
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'A period, such as Q3 2026, is the reporting period a run covers. A run schedule is a rule that launches runs on a timer. They are different records and should not be confused.',
        'A tree carried over from the earlier group model can be marked as needing review, because its filter or dataset could not be rebuilt automatically. The node still works. Check and re-author it before you rely on it.',
      ],
    },
  ],
};

export default body;
