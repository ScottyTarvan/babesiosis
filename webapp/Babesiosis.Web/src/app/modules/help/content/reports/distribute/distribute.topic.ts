import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Distribute. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'note',
      intent: 'warning',
      text: 'Distribute currently records that a document was distributed, but does not send it anywhere. Nothing is emailed, uploaded or otherwise delivered to a recipient. Choosing Email, FTP, SFTP or WhatsApp for a report in Setup does not change this.',
    },
    {
      kind: 'paragraph',
      text: 'Use the Distribute screens to approve the documents a report has produced and then release them. Approving is the sign-off step. A document can only be distributed once someone with the Approve permission has approved it.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Open Reports › Distribute. The first screen is a deck of cards, one per report in the selected environment. Select View Documents on a card to see that report\'s individual documents.',
    },
    { kind: 'heading', text: 'The deck' },
    {
      kind: 'paragraph',
      text: 'Each card shows the report\'s name and description, and the run date, the user who ran it and the schedule name for its most recent run. It shows "not run" if the report has never run. Four counters cover the documents in that run that have completed:',
    },
    {
      kind: 'list',
      items: [
        'Pending: completed, with no approval yet.',
        'Approved: signed off and ready to distribute.',
        'Distributed: released.',
        'Failed: distribution did not succeed.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'A zero still shows, greyed. A progress bar reads "distributed of total". It shows a failure colour if any document failed, a success colour once every document is distributed, and a neutral colour otherwise.',
    },
    {
      kind: 'list',
      items: [
        'Approve All approves every pending document on the card.',
        'Distribute All distributes every approved document on the card.',
        'Both buttons need the matching permission and something eligible. Both are held while the run is still rendering, so they cannot act on an unfinished set. Each asks you to confirm, naming the report and how many documents it will affect.',
        'Search by report name, description or schedule name. Filter by progress: fully distributed, pending, partially distributed or nothing pending.',
        'Refresh picks up changes made by other users. The deck does not refresh on its own.',
      ],
    },
    { kind: 'heading', text: 'The documents grid' },
    {
      kind: 'paragraph',
      text: 'This grid lists every current, completed document for the report. You can narrow it by period or schedule, and the filter applies as soon as you change it. The columns are Entity Group, Entity, Period, Execution Version, Rendered On, Distribution Status, Approved By, Approved On and Distributed On. A Distribution Message column is hidden by default, because it only has content for failed documents.',
    },
    {
      kind: 'paragraph',
      text: 'Distribution Status shows Pending, Approved, Distributed or Failed. You can filter on it, but you cannot sort by it. On each row you can use Preview, Approve or Revoke, Distribute and History. Select rows on the current page to use Approve Selected and Distribute Selected from the toolbar.',
    },
    { kind: 'heading', text: 'Approving and revoking' },
    {
      kind: 'list',
      items: [
        'Approve is available on a completed document that is Pending. It sets the status to Approved and records who approved it and when.',
        'Revoke is available on an Approved document. It returns the document to Pending and clears the approver and approval date.',
        'Neither action asks for confirmation, because you may repeat them many times in a batch and each undoes the other.',
        'There is no reject with a reason. Revoke is the only way to undo an approval, and it records no reason.',
      ],
    },
    { kind: 'heading', text: 'Distributing' },
    {
      kind: 'list',
      items: [
        'Distribute works on Approved documents. It sets the status to Distributed and records the date and the channel\'s message.',
        'It also works on Failed documents. Failed is not a final state, so distributing again is the way to retry.',
        'A document that is not yet approved, or is already distributed, cannot be distributed.',
        'Distributing cannot be undone. The row-level and selected actions ask you to confirm, and warn that a distributed document cannot be recalled. Distribute All asks too.',
        'If a bulk distribute partly fails, the grid tells you whether all were distributed, all failed, or some of each. Open History on a failed document to see the reason.',
      ],
    },
    { kind: 'heading', text: 'History' },
    {
      kind: 'paragraph',
      text: 'Select History on a row to see every approval, revoke, distribution and failure for that document, newest first. Each entry shows the action, who did it, when, and the channel\'s message for a distribution. The dialog is read-only and loads fresh each time you open it.',
    },
    { kind: 'heading', text: 'Permissions' },
    {
      kind: 'list',
      items: [
        'Read lets you see the deck and the documents grid.',
        'Approve lets you approve and revoke.',
        'Distribute lets you distribute, including retrying a failed document.',
        'Preview uses the Run screen\'s preview permission, not a Distribution one.',
      ],
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'Pending is how a document with no distribution status yet is shown. It is a reading, not a stored state.',
        'Bulk actions skip any document that is no longer eligible, for example one that someone else approved a moment earlier. A single-row action on an ineligible document is refused with an error naming it.',
        'Only another user\'s action can change the deck without you clicking. Use Refresh to see it.',
      ],
    },
  ],
};

export default body;
