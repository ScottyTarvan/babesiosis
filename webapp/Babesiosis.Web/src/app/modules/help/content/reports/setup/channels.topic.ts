import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Channels. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'A distribution channel is a named, reusable way of delivering a report. You set channels up once, then assign them to the reports that should use them.',
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'Reports are not yet sent out over channels. Setting up, testing and assigning channels works, but no report is delivered to anyone today, and a channel does not yet say who receives a report. Delivery and recipients are not yet available.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'list',
      items: [
        'Reports › Setup › Channels lists all channels.',
        'Reports › Setup › Distribution lists the channels assigned to one report. Open it with View Distribution on a report in Reports › Setup.',
      ],
    },
    { kind: 'heading', text: 'Channel types' },
    {
      kind: 'list',
      items: [
        'Email: for sending reports by email.',
        'FTP: for delivering reports to an FTP destination.',
        'SFTP: for delivering reports to an SFTP destination. A connection test shows the destination\'s host key fingerprint. You can save the fingerprint into the channel to pin it against future changes.',
        'WhatsApp link: for sharing a download link over WhatsApp, through Meta\'s messaging service or through Twilio.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'Connection details such as hosts, credentials and tokens are stored securely. Secret values are never shown in full once saved. You only see whether they are set.',
    },
    { kind: 'heading', text: 'Managing channels' },
    {
      kind: 'paragraph',
      text: 'The Channels screen shows each channel\'s type, environment, enabled state and the number of reports using it.',
    },
    {
      kind: 'list',
      items: [
        'Add creates a channel. The name must be unique in the environment, and the connection settings must be accepted before the channel is saved.',
        'Edit changes a channel. Leave a secret field blank to keep the stored value. Only fields you fill in replace what is stored.',
        'A channel\'s type cannot be changed. Create a new channel of the type you need.',
        'Delete removes a channel. It is refused while the channel is assigned to any report. Remove every assignment first.',
        'Test checks a channel\'s connection. You can run it from the list, or from the add or edit form before you save.',
      ],
    },
    { kind: 'heading', text: 'Testing a connection' },
    {
      kind: 'list',
      items: [
        'Testing a form with blank secret fields uses the values already stored.',
        'For FTP and SFTP, the test uploads a small file and deletes it again. A login that can only read fails the test.',
        'For a WhatsApp link, the test also confirms that download links can be created.',
      ],
    },
    { kind: 'heading', text: 'Assigning channels to a report' },
    {
      kind: 'paragraph',
      text: 'On the Distribution screen you see the report\'s assigned channels in delivery order, and the channels you can still assign.',
    },
    {
      kind: 'list',
      items: [
        'A channel can be assigned only if it is in the same environment as the report, is enabled, and is not already assigned to that report.',
        'A new assignment goes to the end of the delivery order and starts with settings that suit the channel type.',
        'Edit the assignment to change its settings. Each assignment has its own enabled setting, separate from the channel\'s.',
        'Move Up and Move Down change the order one row at a time. The change is applied immediately and undone if it cannot be saved.',
        'Remove deletes an assignment. The remaining assignments keep their order, so a gap in numbering is normal.',
        'You cannot change which channel an assignment points to. Remove it and assign a different channel.',
      ],
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'A channel name is unique within an environment, not across them.',
        'Disabling a channel later does not remove or change its existing assignments.',
        'Editing a channel is refused if someone else changed it since you opened it.',
        'Two people editing the same assignment at once are not detected.',
        'Channels and a report\'s assignments have separate permissions. Both are separate from the permissions for approving and releasing reports.',
      ],
    },
  ],
};

export default body;
