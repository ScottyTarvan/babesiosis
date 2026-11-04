import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Pipeline expectations. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'An expectation is a rule on one pipeline\'s runs: finished by a deadline, runs at least every so often, does not fail, does not run too long or stall, or loads a row count close to a baseline built from earlier runs. Babesiosis checks each enabled rule on a five-minute cycle, when the rule is due. Four of the six kinds are also checked as soon as a run is recorded.',
    },
    {
      kind: 'paragraph',
      text: 'A rule belongs to one pipeline in one environment. You see and manage the rules of the environment you currently have selected. To see another environment\'s rules, switch environment.',
    },
    { kind: 'heading', text: 'Where to find them' },
    {
      kind: 'paragraph',
      text: 'Open Pipelines › List and expand a pipeline\'s row, or select its Health value. The drop-down lists that pipeline\'s rules and their status, including disabled rules, which are not marked as disabled. It does not show past breaches.',
    },
    { kind: 'heading', text: 'What you can do' },
    {
      kind: 'list',
      items: [
        'Add creates a rule on the expanded pipeline. The rule\'s name must be unique on that pipeline, but you can reuse a name on another pipeline.',
        'Edit changes a rule\'s name, type, severity, whether it is enabled and its settings. A rule always stays on the pipeline it was created for. A disabled rule is not checked and does not count towards Health.',
        'Mute stops a rule opening new breaches and sending emails. Unmute turns it back on. A muted rule is still checked.',
        'Delete removes the rule.',
        'Acknowledge records that you have seen a breach. It appears only while a rule has an open breach that nobody has acknowledged. The rule\'s row then shows that the breach is acknowledged and by whom.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'If someone else changes or deletes a rule while you have it open, your edit or delete is rejected instead of overwriting their change. Reload the drop-down and try again.',
    },
    { kind: 'heading', text: 'Rule types' },
    {
      kind: 'list',
      items: [
        'Completed by deadline: the run must complete by a cutoff time on the days you choose. Enter the cutoff and days in your local time.',
        'Minimum frequency: the pipeline must run at least once within the number of minutes you set.',
        'Must not fail: a run must not fail.',
        'Row count deviation: a run\'s row count must stay close to a baseline built from earlier runs. Earlier runs that moved zero rows are ignored. Until there are enough usable earlier runs, the rule reports Unknown.',
        'Maximum run duration: a run must not take longer than the maximum you set. The run needs both a start time and an end time, otherwise the rule reports Unknown.',
        'Run stalled: a run must not stall without completing.',
      ],
    },
    {
      kind: 'note',
      intent: 'warning',
      text: 'If you change a Completed by deadline rule into a Minimum frequency rule, clear the cutoff time first. Otherwise the days you pick can be shifted.',
    },
    { kind: 'heading', text: 'Severity and alerting' },
    {
      kind: 'list',
      items: [
        'Every rule has a severity of Warning or Critical.',
        'The alerting settings set how many checks in a row must breach before an alert is raised. They also set the minimum time before the same open breach is sent again.',
      ],
    },
    { kind: 'heading', text: 'Rule states' },
    {
      kind: 'list',
      items: [
        'Unknown: the rule cannot be judged yet, for example because there is too little history.',
        'Ok: the latest check passed. An open breach closes when a check returns Ok straight after a Breached check, even if the rule is muted.',
        'Pending: the latest check breached, but not often enough in a row to count as a breach yet. No breach is recorded while a rule is Pending.',
        'Breached: the rule has breached enough times in a row. A breach is recorded.',
      ],
    },
    {
      kind: 'note',
      intent: 'warning',
      text: 'If a rule moves from Breached to Unknown, its open breach stays open even when a later check returns Ok. This is a known issue and is not yet fixed.',
    },
    { kind: 'heading', text: 'Preview before you save' },
    {
      kind: 'paragraph',
      text: 'When you add or edit a rule, you can preview it first. The preview replays the rule against the pipeline\'s recent runs, up to 30 days and 2000 runs, and shows what it would have reported. A preview saves nothing and sends nothing.',
    },
    { kind: 'heading', text: 'Email' },
    {
      kind: 'paragraph',
      text: 'Only Critical rules send email. Emails go to the people watching the pipeline, and they are grouped per pipeline rather than sent one rule at a time. Use the watch control on the pipeline\'s row to watch it.',
    },
    { kind: 'heading', text: 'Permissions' },
    {
      kind: 'paragraph',
      text: 'Five permissions apply: read, add, edit, delete and acknowledge. An action is disabled if you do not hold its permission. Without the read permission you see a no-access message instead of the rules.',
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'A dashboard for triaging breaches across pipelines and reviewing breach history is not yet available.',
    },
  ],
};

export default body;
