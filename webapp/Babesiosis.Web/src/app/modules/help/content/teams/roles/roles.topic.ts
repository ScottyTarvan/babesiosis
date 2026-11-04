import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Roles. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'A role is a named set of permissions. You give users access to Babesiosis by adding them to roles. Every screen in the application takes its permissions from the same list, so a role decides what its members can do across the whole application.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Open Manage › Roles. Each row has actions to edit or delete the role, view its permissions and manage its members. The actions you can use depend on your own permissions. Actions you cannot use are disabled.',
    },
    { kind: 'heading', text: 'What you can do' },
    {
      kind: 'list',
      items: [
        'Add a role with a name and a description. The name must be unique.',
        'Edit a role\'s name and description.',
        'Delete a role.',
        'View and change the permissions a role grants.',
        'Assign users to a role and remove them from it.',
        'Export the grid.',
      ],
    },
    { kind: 'heading', text: 'Setting a role\'s permissions' },
    {
      kind: 'paragraph',
      text: 'The permissions view groups the application\'s permissions by area and group. Each group has Read, Add, Update and Delete columns. Any other actions for a group, such as deploy or download, appear as extra chips. Tick what the role should grant and save.',
    },
    {
      kind: 'paragraph',
      text: 'The actions a permission can have are add, read, edit, delete, deploy, download, upload, run, link, unlink, approve, distribute and elevate. Some permissions are reserved for super administrators. They are not offered here and cannot be assigned to a role.',
    },
    { kind: 'heading', text: 'Managing members' },
    {
      kind: 'paragraph',
      text: 'Open a role\'s members to see who belongs to it. You can assign a user or remove one. Assigning a user who is already a member, or removing one who is not, changes nothing and shows no error.',
    },
    {
      kind: 'paragraph',
      text: 'To pick a user to assign, you need permission to read the user list. Without it, the assign dialog cannot look users up. You can still view a role\'s members without it.',
    },
    { kind: 'heading', text: 'Who holds what' },
    {
      kind: 'list',
      items: [
        'Super administrators hold every permission.',
        'Administrators hold every permission except the ones reserved for super administrators.',
        'Everyone else holds only what their roles grant.',
      ],
    },
    { kind: 'heading', text: 'Permissions for this screen' },
    {
      kind: 'list',
      items: [
        'Role: Read, Add, Edit, Delete and Download. They cover viewing, adding, editing and deleting roles, and exporting the grid.',
        'Role permissions: Read and Edit. They cover viewing and saving a role\'s permissions.',
        'Role member: Read and Edit. They cover viewing a role\'s members and assigning or removing them.',
      ],
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'Deleting a role removes its permissions and its memberships. Its former members lose whatever access that role gave them.',
        'If someone else changes a role after you load it, your edit is rejected instead of overwriting their change. Reload and try again.',
        'When you save a role\'s permissions, assign a member, remove a member or delete a role, the affected users\' permissions are refreshed straight away.',
        'Changing only a role\'s name or description does not change anyone\'s access.',
        'You can open the Roles screen without any Roles permission. You then see every action disabled.',
        'The Created column is always empty.',
      ],
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'Exporting needs the Role Download permission. A role that holds only Read cannot export the grid.',
    },
  ],
};

export default body;
