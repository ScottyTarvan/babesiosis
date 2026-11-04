import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Files (Manage). Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'These two screens move files in and out of storage folders that were set up in Data › Setup. On File uploads you browse a drop point, upload files and delete files. On File downloads you browse a pick-up point and download files as a zip archive.',
    },
    { kind: 'heading', text: 'Where to find them' },
    {
      kind: 'paragraph',
      text: 'Open Data › Manage › File uploads or Data › Manage › File downloads. Each list shows the definitions in the current environment, loaded a page at a time from the server. The columns are Category, Name, Container, Description and Actions. The list has an Export button.',
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'A screen can only work on folders that have a definition in Setup. If a folder you need is missing, ask someone with Setup access to add it.',
    },
    { kind: 'heading', text: 'Uploading files' },
    {
      kind: 'list',
      items: [
        'Select a row, or select the Upload button. The upload dialog opens.',
        'Use the folder tree to open a folder. The files in it appear beside the tree.',
        'Drop files onto the drop zone. Each file uploads as soon as you drop it. There is no separate confirm step.',
        'If a file with the same name is already in the folder, Babesiosis asks "Replace it?". Confirm to overwrite the file, or cancel to leave it.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'A file cannot be larger than 100 MB. The browser checks this before it sends the file.',
    },
    { kind: 'heading', text: 'Deleting files' },
    {
      kind: 'paragraph',
      text: 'You can delete a file from the upload dialog after you confirm. You can delete files only, never folders, and only inside the drop point\'s own folder. Deleting a file that is already gone reports that it was not found.',
    },
    { kind: 'heading', text: 'Downloading files' },
    {
      kind: 'list',
      items: [
        'Select a row, or select its Browse Files action. The files browser opens.',
        'Open folders in the tree and tick the files you want. Your ticks stay in place when you move to another folder, so you can pick files from several folders.',
        'Select the download action in the footer to get every ticked file in one zip archive. A download action on a single row downloads just that file.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'Babesiosis checks the request before it starts. The files must be inside the pick-up point\'s folder, and their combined real size must not exceed 500 MB. A request over the limit is refused.',
    },
    {
      kind: 'paragraph',
      text: 'Folder names inside the zip start from the pick-up point\'s own folder. When the download finishes, the browser checks the archive is complete. It treats a download that stalls for 60 seconds as failed.',
    },
    { kind: 'heading', text: 'Permissions' },
    {
      kind: 'list',
      items: [
        'File uploads: Read, Upload, Delete and Export. The Export item is listed as Download in Roles.',
        'File downloads: Read, Download and Export. There is no delete permission, because you cannot delete from a pick-up point.',
        'Opening the upload dialog or the files browser needs only Read. A read-only user can open the upload dialog, but its drop zone is disabled. The same user can browse a pick-up point before any download.',
      ],
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'The uploads list reloads when the environment changes. Today the application works in the DEV environment only.',
        'A saved link to one definition\'s files opens the file downloads list, and the files browser for that definition opens as soon as the list loads.',
        'Older links to the file uploads and file downloads lists redirect to the current lists.',
      ],
    },
  ],
};

export default body;
