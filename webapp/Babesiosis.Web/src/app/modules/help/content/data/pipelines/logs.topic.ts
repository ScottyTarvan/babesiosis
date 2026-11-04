import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Pipeline logs. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'The Pipeline logs screen lists every run that your pipelines have reported, one row per run. Use it to see whether a run is still going, whether it completed or failed, and what error it reported.',
    },
    {
      kind: 'paragraph',
      text: 'You cannot add, edit or delete log rows. A row is created when an outside process first reports a run, and it is updated each time that process reports on the same run again.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Open Pipelines › Logs. This screen is also the page you land on after you sign in. It shows the runs of the environment you currently have selected.',
    },
    { kind: 'heading', text: 'What you can do' },
    {
      kind: 'list',
      items: [
        'Read the grid. The newest runs are first, sorted by Execution Date.',
        'Filter, sort and page the runs. These are applied across the whole environment\'s log, not just the rows on screen.',
        'Expand a row to read the full Message, and use the copy button to copy it.',
        'Show the hidden Batch ID and Execution ID columns from the Columns chooser.',
        'Export the grid to CSV.',
      ],
    },
    { kind: 'heading', text: 'Columns' },
    {
      kind: 'list',
      items: [
        'Status: where the run is. See below.',
        'Source: the source the run loaded from.',
        'Pipeline: the name of the pipeline the run belongs to.',
        'File Name: the file the run processed, for pipelines that load files.',
        'Execution Date: when Babesiosis first received the run. This is not a time reported by the outside process.',
        'Start Time and End Time: when the run started and completed, as reported by the outside process.',
        'Message: status or error detail.',
        'Batch ID: the identifier that traces the run\'s data through the warehouse. Hidden by default.',
        'Execution ID: the identifier the outside process gave this run. Hidden by default.',
      ],
    },
    { kind: 'heading', text: 'Statuses' },
    {
      kind: 'list',
      items: [
        'Executing, Queued and Paused: the run has not settled. The grid refreshes itself every few seconds while any visible row is in one of these.',
        'Completed and Failed: the run has settled. The grid stops refreshing once every visible run is Completed or Failed.',
        'None: the run has no status.',
      ],
    },
    { kind: 'heading', text: 'Filtering' },
    {
      kind: 'paragraph',
      text: 'Every column filters from its header except File Name, Message, Batch ID and Execution ID. Switching environment returns the grid to its first page and applies your filter and sort to the new environment.',
    },
    {
      kind: 'note',
      intent: 'warning',
      text: 'A warning banner appears if part of your filter could not be applied, so the results may not match it exactly. This happens when you match the Status column by its displayed label. Filter on the Status column directly instead.',
    },
    { kind: 'heading', text: 'Messages' },
    {
      kind: 'paragraph',
      text: 'Messages of 50 characters or more are translated into plainer wording where possible, and the Message column then shows the translated text. Shorter messages are shown exactly as received. If a translation is not available, you see the original message in full.',
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'An End Time that is more than five minutes in the future, or earlier than the run\'s Start Time, is rejected. The End Time stays as it was and the reason is added to the Message.',
        'A later report can correct an End Time that was already accepted.',
        'The CSV export contains only the page of rows currently loaded, not the whole filtered log.',
        'The Re-run action in the Actions column is always disabled. A logged run cannot be re-run from this screen.',
        'Without the read permission, you see a locked empty state instead of the grid.',
      ],
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'Clearing out old log rows is not yet available. Every reported run stays in the log.',
    },
  ],
};

export default body;
