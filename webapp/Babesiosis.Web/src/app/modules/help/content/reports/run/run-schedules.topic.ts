import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Run schedules. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'A run schedule launches a report automatically, on a timer, without anyone present. You set how often it fires, which period it covers and which entities it runs for. Each firing produces an ordinary run, which moves through rendering, approval and distribution like a manual one.',
    },
    {
      kind: 'paragraph',
      text: 'A run schedule is not the same as a period on the Setup screens. A period is a named date range, such as Q3 2026. A run schedule decides when a run happens, and either uses one of those periods or asks for the current one each time it fires.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Open Reports › Run › Schedules. You can also select Schedule on a report\'s card on the Run screen. That opens the same dialog with the report already chosen.',
    },
    { kind: 'heading', text: 'What the list shows' },
    {
      kind: 'paragraph',
      text: 'The grid lists every run schedule in the current environment. Its columns include a plain-language description of the recurrence, the bound period, a summary of the entity selection, whether the schedule is enabled, and the outcome, timing and message of its most recent occurrence. To narrow the list to one report, use the filter on the report name column.',
    },
    { kind: 'heading', text: 'What you can do' },
    {
      kind: 'list',
      items: [
        'Add creates a run schedule. Edit changes one.',
        'The enabled switch turns a run schedule on or off. If the change is refused, the switch goes back and a message appears.',
        'Run Now launches the schedule\'s next run immediately, outside its recurrence.',
        'History opens a paged list of every occurrence for that schedule, newest first. Each row links to the run it produced, where there is one.',
        'Delete removes the run schedule.',
      ],
    },
    { kind: 'heading', text: 'Creating a run schedule' },
    {
      kind: 'paragraph',
      text: 'The dialog has four steps: Recurrence, Period, Entities and Review. Steps are gated, so you can only move on once the earlier steps are valid. Nothing is saved until you save on the last step. A name must be unique within its report.',
    },
    {
      kind: 'list',
      items: [
        'Recurrence: set a frequency of Daily, Weekly or Monthly, a time of day and the time zone that time is read in. Weekly rules also need the days of the week. Monthly rules also need a day of the month. A day of zero means the last day of the month, and a day beyond a short month\'s length uses that month\'s last day. You can add a start date and an end date. Outside that window the schedule produces no occurrences.',
        'Period: choose a fixed period, so every occurrence uses the same named period. Or choose to use whichever period the report\'s calendar treats as current on the day the occurrence fires, read in the schedule\'s time zone.',
        'Entities: choose all entities in the report\'s current population, or a selected subset of groups and entities.',
        'Review: check the summary. A preview lists several upcoming occurrences.',
      ],
    },
    { kind: 'heading', text: 'Time and daylight saving' },
    {
      kind: 'paragraph',
      text: 'Times are worked out in the schedule\'s own time zone. A time that falls inside the hour skipped when clocks go forward moves to the end of that gap. A time that happens twice when clocks go back uses the earlier one.',
    },
    { kind: 'heading', text: 'How automatic runs work' },
    {
      kind: 'paragraph',
      text: 'Babesiosis checks every five minutes for enabled run schedules that are due. It does not run a catch-up when the system starts. For each due schedule it works through these steps:',
    },
    {
      kind: 'list',
      items: [
        'It claims the occurrence, so the same occurrence cannot launch twice.',
        'It checks that the schedule\'s owner still has permission to run the report.',
        'It works out the period.',
        'It skips the occurrence if the previous one is still in progress.',
        'It checks the chosen entities against the report\'s current population. An entity that has left the population is dropped from that occurrence rather than failing it. Up to ten dropped names are recorded, with any remainder shown as a count.',
        'It launches the run.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'One schedule failing does not stop the others. Each occurrence is recorded in History as Launched, Skipped or Failed, with a message.',
    },
    { kind: 'heading', text: 'Run Now' },
    {
      kind: 'paragraph',
      text: 'Run Now launches straight away from the stored settings. It does not recheck the owner\'s permission or recheck the chosen entities. It does not move the next automatic run time, so it never uses up or postpones the next scheduled firing. History records who ran it.',
    },
    { kind: 'heading', text: 'Permissions' },
    {
      kind: 'list',
      items: [
        'Four permission items control the screen: read the list, add, edit and delete.',
        'Run Now is controlled by the permission to run a report manually, not by a run schedule permission.',
      ],
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'Turning a schedule off clears its next run time. Turning it back on works out a fresh next run time, so it does not fire for a time that passed while it was off.',
        'Saving an edit makes you the schedule\'s owner. The dialog tells you this before you confirm. An edit made against an out-of-date version of the schedule is refused.',
        'Editing replaces the whole entity selection.',
        'Deleting a run schedule is permanent. Runs it already launched are kept, but they no longer link to the deleted schedule.',
        'If the owner loses permission to run the report, automatic runs stop but the schedule stays enabled.',
        'An occurrence that another process claimed first leaves no History entry.',
      ],
    },
  ],
};

export default body;
