import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Instances. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'The Instances screen lists the documents a report has produced, one for each entity and schedule. You can follow their status, preview or download them, rerun one, and look back through earlier versions.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Open Reports › Run, then select View Instances on the report\'s card.',
    },
    { kind: 'heading', text: 'What the list shows' },
    {
      kind: 'paragraph',
      text: 'The grid shows the current result for every entity and schedule combination that has run for the report. Earlier, replaced results are not in this list. Open the versions dialog to see them. Each row shows:',
    },
    {
      kind: 'list',
      items: [
        'The entity and entity group name, as they were when the result was produced.',
        'The result\'s status.',
        'When it was created.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'The schedule filter offers the report\'s non-default schedules, with the most recent end date first. It shows at most 50, so the oldest are missing if a report has more. Choosing a schedule filters the list straight away.',
    },
    { kind: 'heading', text: 'Statuses' },
    {
      kind: 'list',
      items: [
        'Queued: waiting to be rendered. A rerun starts here.',
        'Running: being rendered.',
        'Completed: finished, with a stored document.',
        'Failed: rendering did not succeed. There is no document.',
        'Cancelled: replaced before it ran.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'While any row is Queued or Running, those rows refresh every three seconds, including after a rerun. The refresh stops when nothing is in progress. Rows update in place, so your selection is not lost.',
    },
    { kind: 'heading', text: 'What you can do' },
    {
      kind: 'list',
      items: [
        'Preview shows the stored document in a dialog. If the document cannot be fetched, you see an error message and the dialog does not open. If it arrives but cannot be shown, the dialog says so and offers Download instead.',
        'Download saves the same stored document to your computer.',
        'Rerun creates a new version for the same report, schedule, entity group and entity. The existing result stops being current. The new one is queued with the next version number and keeps the same entity and group names. Its status then updates as it renders.',
        'Versions opens a dialog listing every result for that report, schedule, entity group and entity, newest version first. You can preview and download each version. You cannot rerun from this dialog. A version that failed or has not finished has no document, so preview and download are unavailable for it.',
      ],
    },
    { kind: 'heading', text: 'Permissions' },
    {
      kind: 'paragraph',
      text: 'Seeing the list does not mean you can use every action. Preview, Download and Rerun are each allowed or refused separately for each result. Listing versions and downloading a version have their own permissions too.',
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'A version is just another result for the same report, schedule, entity group and entity. Versions are numbered in order.',
        'Entity and group names show what they were when the result was produced. Renaming an entity or group later does not change earlier results.',
        'Reruns are not protected against each other. Two reruns of the same result started close together are not guarded against.',
        'Results and their documents have no expiry or clean-up. Every version of every result appears to be kept indefinitely.',
        'The completed time is not shown as a column in the list or in the versions dialog.',
      ],
    },
  ],
};

export default body;
