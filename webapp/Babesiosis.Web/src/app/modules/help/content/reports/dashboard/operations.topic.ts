import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Operations dashboard. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'note',
      intent: 'info',
      text: 'This dashboard is partly built. It currently shows sample figures, not a live measure of your report runs, approvals or distributions. Approving from it is not saved and is lost when you reload the page. The page subtitle and the pipeline card say the data is live. That wording is not accurate yet.',
    },
    {
      kind: 'paragraph',
      text: 'The operations dashboard is the home page of the Reports module. It gives one view of where report documents are in their journey: waiting to render, rendering, waiting for approval and being distributed.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Use the module switcher in the top bar to choose Reports, or select Dashboard in the sidebar. The Reports option and the sidebar entry only appear if you have permission to view reports.',
    },
    { kind: 'heading', text: 'What is on the dashboard' },
    {
      kind: 'list',
      items: [
        'Pipeline rail: a row of circles for Queued, Running, Completed, Approved, Distributing and Distributed, each showing a count. The circle grows with the count. The Distributed count is the total sent in the last 30 days across all report types. None of the six counts change when you select a report type in the matrix.',
        'Header alerts: flag an instance that has been running too long, an approval that has been waiting too long, and one alert for each delivery channel type that has a failed delivery.',
        'Report-type matrix: a fixed summary table with one row per report type and no paging. Select a row to narrow the approval queue and the distribution board to that report type. With no row selected they show every type. A legend below the matrix explains the colour marks: queued, running, completed, completed but waiting past a limit, approved and distributing.',
        'Approval queue: lists pending approvals, up to five at a time. The rest are counted in the "N more in queue" figure. A bar on each entry shows its age and is full at three days outstanding.',
        'Distribution board: a grid showing the delivery state of each report instance. A recipients column shows a delivered-against-total bar across all channels, and a count of failed deliveries when there are any.',
        'Run horizon: a 20-day timeline of scheduled runs.',
      ],
    },
    { kind: 'heading', text: 'What you can do' },
    {
      kind: 'list',
      items: [
        'New Report Type takes you to report setup.',
        'Run Now takes you to the Run screen.',
        'Review and Open Queue take you to the Distribute screen. The "N more in queue" link goes there too. There is no separate approval queue screen.',
        'Review appears once for each entry in the approval queue, so you may see several Review controls at once. They all lead to the same place.',
        'Approve on a queue entry marks the entry as approved on the screen and shows a confirmation message. It does not send the approval anywhere and does not survive a reload. To approve for real, use the Distribute screen.',
      ],
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'The run horizon and the clock in the page header both use the same fixed date built into the sample data, not today\'s date. They always agree with each other, but neither shows the real date.',
        'The channel state in the distribution board is shown as a coloured dot with a tinted fill. This differs from the plain icon and label used in other grids.',
      ],
    },
  ],
};

export default body;
