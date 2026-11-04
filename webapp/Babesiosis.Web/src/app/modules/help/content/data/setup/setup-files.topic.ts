import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Files (Setup). Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'A file definition tells Babesiosis which storage folder to use for moving files. A File Upload definition names a drop point, the folder that users upload files into. A File Download definition names a pick-up point, the folder that users download files from.',
    },
    {
      kind: 'paragraph',
      text: 'Use these Setup screens to create, edit and delete the definitions. Users then work with the files themselves on the Manage screens.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Open Data › Setup › File uploads or Data › Setup › File downloads. The two screens work the same way and keep separate lists. Each list loads from the server 25 rows at a time.',
    },
    { kind: 'heading', text: 'What you can do' },
    {
      kind: 'list',
      items: [
        'Add a definition. Choose the Linked Service, pick the Container Name from the storage tree, choose a Category, and enter a Name and Description.',
        'Edit a definition to change any of those values.',
        'Delete a definition you no longer need.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'The storage tree reads the linked service\'s live storage, so every path it offers exists at the moment you pick it. The Container Name holds the whole container and folder path you chose.',
    },
    { kind: 'heading', text: 'What a definition makes possible' },
    {
      kind: 'list',
      items: [
        'Once a File Upload definition exists, Data › Manage › File uploads can list, browse and upload files in its folder.',
        'Once a File Download definition exists, Data › Manage › File downloads can list, browse and download files from its folder as a zip archive.',
        'The Manage screens cannot work on a folder that has no definition. They cannot change a definition\'s container or environment. Only an edit here can do that.',
      ],
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'You do not choose an environment in the dialog. A definition belongs to the environment you are working in when you open it.',
        'Only the Name must be unique. Two definitions of the same type can point at the same folder.',
        'Babesiosis checks the path only when you pick it. If the folder is later removed from storage, nothing warns you until someone opens it on a Manage screen.',
        'If a definition has changed since you opened it, your edit is refused.',
      ],
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'Each definition type has its own Read, Add, Edit and Delete permission items in Setup. File uploads and File downloads do not share them, and they are separate from the permissions that control the Manage screens. Your administrator grants them in Roles.',
    },
  ],
};

export default body;
