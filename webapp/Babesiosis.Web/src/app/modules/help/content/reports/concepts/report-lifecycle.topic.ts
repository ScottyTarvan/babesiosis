import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Report lifecycle. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'A report moves through a fixed set of stages: it is defined, run for a period, rendered into documents, approved and distributed. This topic explains the terms you meet along the way and the states each one passes through.',
    },
    { kind: 'heading', text: 'The building blocks' },
    {
      kind: 'list',
      items: [
        'Report: the definition. It holds the name, the description and the components that make the report up. A report has no status of its own.',
        'Schedule: a named period the report is produced for, such as Q3 2026. It has a start and end date and can be archived. Archiving removes it from active use without deleting it.',
        'Batch: one run of a report for one schedule, across every entity the run selects.',
        'Instance: one rendered document inside a batch, produced for one entity or entity group.',
        'Run schedule: a rule that launches runs on a timer. It is not the same thing as a schedule. A schedule says which period a run covers. A run schedule says when a run happens.',
      ],
    },
    { kind: 'heading', text: 'Batches' },
    {
      kind: 'paragraph',
      text: 'A batch starts as Queued, becomes Running once Babesiosis has worked out which entities to run for, and ends as Completed or Failed. Only one batch is current for a report and schedule at a time. Launching a new one keeps the earlier batch for history but makes the new one current.',
    },
    {
      kind: 'list',
      items: [
        'Completed means every instance has finished processing. It does not mean every instance succeeded. A batch is never marked as partly failed, so open its instances to see which ones failed.',
        'Failed means the batch could not work out its entities. This happens when the entity list is too large and has been cut short.',
      ],
    },
    { kind: 'heading', text: 'Instances' },
    {
      kind: 'paragraph',
      text: 'An instance is Queued, Running, Completed, Failed or Cancelled. Only one instance is current for each combination of report, schedule, group and entity. A rerun makes the earlier instance non-current and creates a new one at the next version, so the full version history of one entity\'s document is kept. An instance replaced by a rerun before it started is set to Cancelled and is not rendered.',
    },
    {
      kind: 'paragraph',
      text: 'Rendering builds the instance from every component of the report that is not excluded, then merges the results into one PDF document. A Word component is converted to PDF before the merge. You can rerun a single instance without creating a new batch.',
    },
    { kind: 'heading', text: 'Approval and distribution' },
    {
      kind: 'paragraph',
      text: 'Each instance also has a distribution status, separate from its render status. The values are Approved, Distributed and Failed. An instance with no distribution status yet is called pending.',
    },
    {
      kind: 'list',
      items: [
        'A Completed instance with no distribution status is ready for approval.',
        'Approving sets the status to Approved and records who approved it and when. Revoking returns it to pending.',
        'An Approved instance, or one that previously failed to distribute, can be distributed. Distributing sets the status to Distributed, or to Failed with a message if delivery did not succeed.',
        'Every approval, revoke, distribution and failure is also written to a permanent distribution record. The instance shows only its current status. The record keeps the history.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'Approving and distributing are two separate actions with separate permissions, because sign-off and release are different authorities. A single approve or revoke on an ineligible instance gives an error. The approve all action skips ineligible instances without a message.',
    },
    { kind: 'heading', text: 'Distribution channels' },
    {
      kind: 'paragraph',
      text: 'A distribution channel is a delivery method that a report can be assigned to: Email, FTP, SFTP or a WhatsApp link. You define each channel once for the environment, then assign it to reports with a sequence and its own settings.',
    },
    {
      kind: 'note',
      intent: 'warning',
      text: 'Distributing an instance currently records the action and marks the instance Distributed, but does not send the document anywhere, whichever channel is assigned. Channel connection tests do work.',
    },
    { kind: 'heading', text: 'Run schedules' },
    {
      kind: 'paragraph',
      text: 'A run schedule belongs to one report. It sets a frequency, a time of day and a time zone, and can have a start and end date. Each time it fires it launches an ordinary batch with ordinary instances. It checks that its owner still has permission to run the report every time. If that permission is withdrawn, the next automatic run stops, but the run schedule itself stays enabled.',
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'Deleting a report is permanent. It also removes the images, PDF overrides and templates uploaded for its components.',
        'Render status and distribution status are independent. A Completed instance can be pending, Approved, Distributed or Failed on the distribution side.',
        'Manual runs and run schedules launch batches the same way, so their results move through the same stages.',
      ],
    },
  ],
};

export default body;
