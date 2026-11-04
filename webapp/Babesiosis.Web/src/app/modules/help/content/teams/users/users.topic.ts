import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Users. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'Users are the people who sign in to Babesiosis. An administrator creates each user, sets their password, and then gives them access by adding them to roles.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Open Manage › Users. The grid lists the users. Deactivated users are hidden by default. Widen the filter to include them.',
    },
    { kind: 'heading', text: 'What you can do' },
    {
      kind: 'list',
      items: [
        'Add a user with their name, email, mobile and landline numbers with country codes, a password, and the administrator setting.',
        'Edit a user. Leave the password blank to keep the existing one.',
        'Deactivate a user, and restore a deactivated one.',
        'Export the list.',
      ],
    },
    { kind: 'heading', text: 'Adding a user' },
    {
      kind: 'paragraph',
      text: 'You choose the new user\'s password. No email is sent and there is no activation step. The user can sign in as soon as you save. Tell them their email and password yourself.',
    },
    {
      kind: 'paragraph',
      text: 'The email address is how a user signs in, so give every user a different one. You cannot make someone a super administrator from this screen.',
    },
    { kind: 'heading', text: 'Giving a user access' },
    {
      kind: 'paragraph',
      text: 'You assign roles from Manage › Roles, not from this screen. Open the role, go to its members and assign the user.',
    },
    { kind: 'heading', text: 'Deactivating and restoring' },
    {
      kind: 'list',
      items: [
        'Deactivating a user blocks them from signing in, by password or by single sign-on, and removes them from the default list.',
        'Restoring a user reverses this. There is no separate status beyond deactivated or not.',
        'You cannot deactivate your own account.',
        'Deactivating and restoring need the same permission.',
      ],
    },
    { kind: 'heading', text: 'Signing in' },
    {
      kind: 'list',
      items: [
        'Password: users sign in with their email and password.',
        'Single sign-on: users sign in through the identity provider. Single sign-on never creates a user. The user must already exist here with the same email, otherwise sign-in fails.',
        'Forgotten password: users can request a reset by email for their own account. They receive a time-limited link and do not need an administrator.',
      ],
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'Changing the administrator setting, when you add or edit a user, needs a separate elevation permission on top of the ordinary add or edit permission. A role can be granted it on the Roles screen.',
        'If someone else changes a user after you load them, your edit is rejected instead of overwriting their change. Reload and try again.',
        'Editing a user never changes their super administrator status or whether they are deactivated.',
        'Passwords are never shown on screen.',
        'Exporting needs its own download permission, because the grid holds personal contact details.',
      ],
    },
    {
      kind: 'note',
      intent: 'warning',
      text: 'Changing your own password or updating your own profile from the application settings does not work at present. Use the forgotten-password reset, or ask an administrator to edit your user and set a new password.',
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'Inviting users by email, so that they choose their own password, is not yet available.',
    },
  ],
};

export default body;
