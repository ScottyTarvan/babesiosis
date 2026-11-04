import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Activators (Setup). Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'An activator publishes an event through a linked service so that something downstream, such as a load, can react to it. A Manual activator is fired only by a user, never on a schedule. A Timer activator can also fire itself on a schedule.',
    },
    {
      kind: 'paragraph',
      text: 'Use this screen to define activators, set their schedules and parameters, pause them and review what they have run. To fire an activator by hand, use Data › Manage › Activators.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Open Data › Setup › Activators. The grid shows the Linked Service, Type, Category, Name, Description and Event Name of each activator, an Enabled switch, and a History action. A Data Service column is also available but hidden by default.',
    },
    { kind: 'heading', text: 'Defining an activator' },
    {
      kind: 'list',
      items: [
        'Give the activator a name, a description, a category and an event name.',
        'Choose the Type: Manual or Timer.',
        'Choose two linked services. Both are required. The first is the one the activator publishes through. The second, the Data Service, decides which datasets a parameter can offer as choices.',
        'For a Timer activator, set the schedule (see below).',
        'Add, edit, delete and reorder parameters as needed. Reordering a parameter needs the edit permission.',
      ],
    },
    { kind: 'heading', text: 'Setting a schedule' },
    {
      kind: 'paragraph',
      text: 'The schedule section appears only when the Type is Timer. You build the schedule from a fixed set of presets. There is no box for typing a cron expression and no time zone choice. Every schedule runs in South Africa Standard Time.',
    },
    {
      kind: 'list',
      items: [
        'Every 30 Minutes: fires on the half-hour, every hour.',
        'Hourly: fires once an hour, at :00 or :30.',
        'Daily: fires once a day at a time you choose.',
        'Weekly: fires on one or more days you choose, at a time you choose.',
        'Monthly: fires on a day from 1 to 28, or on the last day of the month.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'Times are picked from a half-hour grid, so the minutes are always :00 or :30. The designer can show a preview of the next occurrences, from 1 to 20, before you save.',
    },
    {
      kind: 'note',
      intent: 'warning',
      text: 'If you change the Type away from Timer, the schedule is cleared at once. Cancelling the dialog restores the saved activator.',
    },
    { kind: 'heading', text: 'Parameters and scheduled values' },
    {
      kind: 'paragraph',
      text: 'Each parameter has a name, a description, a data type, a setting for whether it is required, a setting for whether it accepts several selections, and a position in the order.',
    },
    {
      kind: 'paragraph',
      text: 'On a Timer activator, a parameter can also hold a scheduled value. This is the value published when the activator fires on its own schedule. Babesiosis checks the scheduled value against the parameter\'s data type when you save.',
    },
    {
      kind: 'list',
      items: [
        'Text, Integer, Date and similar types take a plain value of that type.',
        'A relative date takes one of seven fixed choices, such as today or the last day of the previous year. Babesiosis turns it into a real date each time the activator fires.',
        'An Entity or Lookup parameter takes a reference to one record in an Entity or Lookup dataset. Babesiosis keeps the record\'s name with it so the grid can show the name.',
      ],
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'The record name is captured when you save the parameter. If the record is renamed later, edit and save the parameter again to refresh the name.',
    },
    { kind: 'heading', text: 'Pausing and resuming' },
    {
      kind: 'paragraph',
      text: 'Use the Enabled switch to pause or resume a Timer activator. Pausing stops it firing on schedule and keeps its schedule and parameters. A Manual activator is always enabled and has no paused state. A paused activator can still be run by hand from Manage.',
    },
    { kind: 'heading', text: 'How the timer fires' },
    {
      kind: 'list',
      items: [
        'Babesiosis checks every 30 minutes for enabled Timer activators that are due, and publishes each one.',
        'After downtime, it does not replay missed runs. It fires at most one run, for the most recent due time.',
        'If a schedule is no longer valid, Babesiosis disables the activator and records a failed run.',
        'If a schedule has no further occurrence, Babesiosis disables the activator and adds a note about this to the run\'s message.',
        'Running an activator by hand never changes its next scheduled time.',
      ],
    },
    { kind: 'heading', text: 'Run history' },
    {
      kind: 'paragraph',
      text: 'Select History on a row to see its runs, shown in pages. Each entry shows the source (Timer or Manual), when it ran, the time a Timer run was scheduled for, the outcome, a message and the payload that was published. Runs are logged whether they succeeded or failed.',
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'The grid has no Schedule, Next Run, Last Run or Last Outcome columns. Use the schedule preview and the History action to see that information.',
    },
    { kind: 'heading', text: 'Permissions' },
    {
      kind: 'paragraph',
      text: 'Viewing, adding, editing and deleting an activator each need their own permission. Parameters follow the same split. Choosing records for an Entity or Lookup parameter also needs the Read permission for Manage activators, so an author without it cannot preview those choices.',
    },
  ],
};

export default body;
