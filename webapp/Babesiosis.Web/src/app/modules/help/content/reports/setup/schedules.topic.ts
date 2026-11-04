import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Schedules. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'A period is a named date range that a report is produced for. On screen these are called Periods. Every run of a report is tied to exactly one period, and the period\'s name is used in the output file name.',
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'A period is not a recurring run. It does not repeat or trigger anything. Recurring runs are set up under Run schedules, which pick a period when they launch.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Open Reports › Setup and select View Schedules on a report.',
    },
    { kind: 'heading', text: 'What you can do' },
    {
      kind: 'list',
      items: [
        'Add creates a period with a name, a description and a start and end date.',
        'Edit changes a period.',
        'Archive retires a period. It is hidden from the list, and a recurring run cannot use it.',
        'Restore brings an archived period back.',
        'Switch on the show archived toggle to include archived periods in the list.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'A period has no type such as Monthly or Quarterly. It is only a name and a date range that you choose.',
    },
    { kind: 'heading', text: 'Adding a period' },
    {
      kind: 'paragraph',
      text: 'When you open Add, the start date is pre-filled with the day after the latest existing period ends. The end date is pre-filled with the end of that month. You can change both before saving.',
    },
    {
      kind: 'paragraph',
      text: 'No background process creates periods for you. A period can also be created while you start a run from the Run wizard.',
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'The start date must not be later than the end date.',
        'A period name must be unique within its report. The same name can be used on a different report.',
        'If someone else changed the period since you opened it, your edit is refused.',
        'Archive and Restore share one permission.',
        'Every report also has a hidden default period covering all dates. It exists to hold content before any real period does. It is never shown, and cannot be edited, archived or selected.',
        'A recurring run that picks the current period chooses the period whose dates cover today. If more than one does, it uses the one with the latest end date, without a warning.',
        'An archived period cannot be used by a recurring run. The run will not launch.',
        'The Run wizard\'s own option to create a period does not check for a duplicate name.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'Other screens that show a period label its name as Schedule Name. It is the same value.',
    },
  ],
};

export default body;
