import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Run. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'Use the Run screen to run a report for a period and a set of entities. Babesiosis renders one PDF document for each entity or group, and you follow progress on the report\'s card.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Open Reports › Run. The screen is a deck of cards, one per report, rather than a grid. Each card shows the report\'s latest run with its version, status and run date. If a recurring schedule exists, it also shows the next scheduled run time.',
    },
    { kind: 'heading', text: 'What you can do' },
    {
      kind: 'list',
      items: [
        'Run opens the run wizard for that report.',
        'Download saves the output of completed instances. One instance downloads as a PDF. More than one downloads as a zip file of separate PDFs.',
        'View Instances opens the list of individual results for the run, with their versions, preview and rerun.',
        'Schedule opens a dialog for running the report on a timer.',
        'Search and filter the deck by status to find a report quickly.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'Each of Run, Download, View Instances and Schedule is controlled by its own permission item in Roles, so you may be able to use some of them and not others.',
    },
    { kind: 'heading', text: 'Running a report' },
    {
      kind: 'paragraph',
      text: 'The wizard opens from a report\'s card, so the report is already chosen. It has three steps. Each step must be valid before you can move on, and nothing is saved until you confirm on the last step.',
    },
    {
      kind: 'list',
      items: [
        'Period: choose an existing period or define a new one.',
        'Entities: choose the entities or groups the run covers. Entities marked as excluded for the report are not offered.',
        'Confirm: review your choices and launch.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'The confirmation is an "are you sure" prompt, not an approval. Confirming queues the run straight away. Approval comes later, after the run completes, on the Distribute screen.',
    },
    { kind: 'heading', text: 'What happens when you launch' },
    {
      kind: 'list',
      items: [
        'A new period is created if you defined one. Otherwise the period you chose is reused.',
        'The report\'s previous current run for the same period is replaced as the current one.',
        'The new run is queued as the next version.',
        'The run is passed to the rendering engine, which builds one document for each entity or group.',
      ],
    },
    { kind: 'heading', text: 'Progress' },
    {
      kind: 'paragraph',
      text: 'A run is Queued, Running, Completed or Failed. While a run is Queued or Running, its card updates every few seconds. The progress bar never goes backwards. Starting a new run for the same report resets the bar to zero.',
    },
    { kind: 'heading', text: 'How output is produced' },
    {
      kind: 'paragraph',
      text: 'Each instance is a single PDF per entity or group. Babesiosis does not combine several entities into one document, and it does not produce Word or Excel output. A report can be authored from a Word document, but that is converted to PDF during rendering.',
    },
    {
      kind: 'paragraph',
      text: 'The rendering engine works through the report\'s components in their set order and skips any component excluded for that entity. It handles three kinds of component:',
    },
    {
      kind: 'list',
      items: [
        'PDF: content PDFs whose pages pass through unchanged.',
        'Telerik: a report template that is rendered to PDF. Uploaded fonts are not used; rendering uses the fonts bundled with the report engine.',
        'MS Word: a Word template that has its transform values substituted in, keeping the document\'s formatting, and is then converted to PDF.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'All the component outputs are joined, page by page, into one PDF with no page numbers, bookmarks or generated contents page. If nothing was produced, you get a one-page document stating that the report has no content. The file name comes from the format you configured, or a default name if you set none.',
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'Table of Contents and DevExpress components are not yet rendered. A component of either type adds nothing to the document and you get no warning, even though a Table of Contents can be fully configured at setup.',
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'If you choose All Entities and the list is too large, so it is cut short, the run is still queued. The rendering engine then refuses it and the run shows as Failed with a message.',
        'A run is marked Completed when every instance has finished, even if some instances failed. Open View Instances to see the result for each one.',
        'If one instance fails, the rest still complete. A failed instance can be rerun on its own.',
        'Approval does not hold up rendering. It applies only after an instance completes.',
        'Download needs at least one completed instance. With none, you get a general error.',
        'The Schedule dialog reuses the wizard\'s Period and Entities steps.',
        'The Run Schedules screen has its own Run Now action. It needs the same Run permission as this screen.',
      ],
    },
  ],
};

export default body;
