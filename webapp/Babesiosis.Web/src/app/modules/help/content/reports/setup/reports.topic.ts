import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Reports. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'A report definition is the record that everything else in the Reports module hangs from. It holds the report\'s name, the dataset its entities come from and the tree that groups those entities. Components, periods, entities and distribution channels are set up against it.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Open Reports › Setup. The page shows one card per report for the current environment. Search by name, file name or description to narrow the cards.',
    },
    { kind: 'heading', text: 'What you can do' },
    {
      kind: 'list',
      items: [
        'Add opens the dialog to create a report.',
        'Edit opens the same dialog for an existing report.',
        'Delete removes the report.',
        'View Schedules opens the report\'s Periods.',
        'View Entities opens the report\'s Entities screen.',
        'View Components opens the report\'s Components screen.',
        'View Distribution opens the channels assigned to the report.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'Each action has its own permission. An action you may not use is disabled, not hidden.',
    },
    { kind: 'heading', text: 'The report dialog' },
    {
      kind: 'paragraph',
      text: 'The dialog has three tabs: Report, Groups and Entities. The Report tab holds these fields.',
    },
    {
      kind: 'list',
      items: [
        'Name is required, up to 200 characters, and must be unique in the environment.',
        'Description is optional.',
        'File name is optional. It is a pattern for naming the finished report file, made of fixed text and placeholders such as the entity, entity group, period or report name, and dates. Leave it blank and the system names the file itself.',
        'Linked Service (Platform) is required. Only SQL linked services are offered. You cannot change it after the report is created.',
        'Entity dataset is the reference dataset the report\'s entities come from. It is required.',
        'Display field is required with the entity dataset. It is the field that represents an entity in the tree and elsewhere.',
        'Password field is optional. You choose it from text or integer fields. Nothing uses its value when reports are produced yet.',
      ],
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'A report has no type, template or output-format setting. The template belongs to a report component. Use View Components to set it.',
    },
    { kind: 'heading', text: 'Groups and Entities tabs' },
    {
      kind: 'list',
      items: [
        'Groups is where you build the tree of entity groups. See the Entities topic for how the tree works.',
        'On a new report, Groups stays disabled until you choose an entity dataset.',
        'Entities lets you choose which entities are included. It stays disabled until the report has been saved and the form has no unsaved changes.',
      ],
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'Choosing a different Linked Service clears the entity dataset, the display field and the draft tree.',
        'If a change of dataset removes the chosen password field from the available fields, that choice is dropped without a warning.',
        'Once the tree has any groups, you cannot point the report at a different entity dataset unless you also clear the tree. The dialog asks you to confirm before it clears the tree.',
        'The tree has limits. It can be at most 5 levels deep, with at most 5 grouping fields on a group and at most 10 across a group and its parents. An over-limit tree blocks Save.',
        'Adding a report also creates a hidden default period. You do not see or manage it.',
        'Another person\'s change made while you edit is not silently overwritten. A stale save or delete is refused.',
      ],
    },
    {
      kind: 'note',
      intent: 'warning',
      text: 'Deleting a report is permanent. It also deletes the report\'s components and everything attached to them, including uploaded images, PDFs and template files.',
    },
  ],
};

export default body;
