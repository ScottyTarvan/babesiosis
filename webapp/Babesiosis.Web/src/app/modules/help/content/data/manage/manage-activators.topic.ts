import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Activators (Manage). Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'An activator publishes an event so that something downstream, such as a load, can react to it. Use this screen to run activators on demand and to supply the values they need.',
    },
    {
      kind: 'paragraph',
      text: 'You can run both Manual and Timer activators here. Creating, editing, scheduling, pausing and resuming activators, and reviewing run history, are done in Data › Setup › Activators.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Open Data › Manage › Activators. The list shows every activator in the current environment. Filtering, sorting and paging all happen on the server.',
    },
    { kind: 'heading', text: 'Columns' },
    {
      kind: 'list',
      items: [
        'Linked Service: the Event Grid linked service the activator publishes through.',
        'Type: Manual or Timer.',
        'Data Service: the linked service that Entity and Lookup parameter choices are read from. Hidden by default.',
        'Category: a free-text grouping.',
        'Name and Description.',
        'Event Name: the event published to subscribers.',
        'Enabled: shown for Timer activators only. You cannot change it here. Pausing and resuming is done in Setup.',
        'Actions: the Run action.',
      ],
    },
    { kind: 'heading', text: 'Running an activator' },
    {
      kind: 'list',
      items: [
        'Select the row, or select Run in its Actions column.',
        'Fill in the parameter dialog. Parameters appear in the order they were set up, each with an editor that suits its data type.',
        'Check that every required parameter has a value, then select Run.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'The activator publishes one payload that holds a value for every named parameter, whether or not you changed it. Parameters with no name are not published.',
    },
    {
      kind: 'list',
      items: [
        'A Boolean parameter starts as false and is never mandatory, even if marked required.',
        'A multi-select Entity or Lookup parameter starts with nothing selected and publishes an empty list if you leave it.',
        'A single-select Entity or Lookup parameter starts with no selection. An Entity parameter publishes the selected record\'s identifier. A Lookup parameter publishes its name.',
        'A Date publishes as the chosen day at midnight.',
        'Any other parameter you leave blank publishes no value.',
      ],
    },
    { kind: 'heading', text: 'Running a Timer activator by hand' },
    {
      kind: 'paragraph',
      text: 'Use this to run an occurrence again, for example one that was skipped or failed. A manual run does not move the activator\'s next scheduled time.',
    },
    {
      kind: 'paragraph',
      text: 'A manual run also ignores whether the activator is enabled. An activator that was paused, or that Babesiosis disabled because its schedule became invalid or ran out, can still be run here. Running it does not re-enable it.',
    },
    { kind: 'heading', text: 'Run outcomes' },
    {
      kind: 'paragraph',
      text: 'Every run is recorded with when it ran, its outcome, a message and the payload. A manual run also records who started it. A manual run records Published or Failed. Skipped happens only to Timer runs, for example when a required value is missing.',
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'This screen does not show run history. To review what an activator has run, use the History action in Data › Setup › Activators.',
    },
    { kind: 'heading', text: 'Opening a run from a link' },
    {
      kind: 'paragraph',
      text: 'A link with an activator in its address shows only that activator and opens its run dialog straight away. If the activator does not exist in the current environment, the list is simply empty and no error appears.',
    },
    { kind: 'heading', text: 'Permissions' },
    {
      kind: 'list',
      items: [
        'Read: needed to load the list and the choices for Entity and Lookup parameters.',
        'Run: needed to open the run dialog from a row or the Run action, and to submit it. A link that opens a run dialog directly still needs Run to submit.',
        'Download: needed to export the grid to CSV.',
      ],
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'Manage has no permission to create, edit or delete activators. Those are Setup permissions.',
    },
  ],
};

export default body;
