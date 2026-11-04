import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Linked services. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'A linked service is a saved connection to a system that Babesiosis reads from or writes to, such as a SQL Server database, a storage account or a web service. Datasets, activators and file definitions all point at a linked service to reach their target.',
    },
    {
      kind: 'paragraph',
      text: 'Use this screen to add, edit, test and delete linked services.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Open Data › Setup › Linked services. The list shows each linked service with its name, description, colour and type. Today the application works in the DEV environment only, so the list shows the services in that environment.',
    },
    { kind: 'heading', text: 'Linked service types' },
    {
      kind: 'list',
      items: [
        'SQL Server: a server name and database name, with either Entra ID (managed identity) sign-in or a username and password.',
        'Blob Storage: the storage account connection details.',
        'Event Grid: an endpoint and a key.',
        'Web API: an HTTP method, a URL, a query string and a request body. This type has no sign-in fields.',
        'Databricks: you can select this type, but the dialog shows no fields for it, so you cannot configure it yet.',
      ],
    },
    { kind: 'heading', text: 'What you can do' },
    {
      kind: 'list',
      items: [
        'Add a linked service. Enter a name, a description, a display colour and a type, then fill in the connection details for that type.',
        'Edit a linked service to change any of those values. Saving an edit stores the whole connection configuration again, so check every connection field before you save.',
        'Test the connection. Use the test action in the add or edit dialog to try the values you have typed before you save them. Use the test button on a row to try the saved connection.',
        'Delete a linked service you no longer need.',
      ],
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'The connection details and any password or key are stored securely, not in the list. When you save, they are written to that secure store first.',
    },
    { kind: 'heading', text: 'Deleting a linked service' },
    {
      kind: 'paragraph',
      text: 'Babesiosis refuses to delete a linked service that other items still use. Remove or repoint those items first. The message tells you why the delete cannot go ahead.',
    },
    {
      kind: 'list',
      items: [
        'A linked service is protected while any dataset, entity group, activator (as either of its linked services), file upload, file download, deployed dataset or dataset link still uses it.',
        'It is also protected while a deployment still points at it and names a dataset that is still live. The message gives the number of deployments involved.',
        'Deployments that have finished with a dataset that no longer exists do not block the delete. They stay in the deployment history.',
        'Source-to-dataset mappings do not block the delete. Deleting the service clears it from every mapping that names it.',
      ],
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'A linked service name must be unique within its environment. A duplicate name is refused when you add or edit.',
        'You do not choose an environment in the dialog. A new linked service belongs to the environment you are working in.',
        'If a linked service has changed since you opened it, your edit is refused.',
        'The test button on a Databricks row can be clicked, but it always returns a generic failure without trying to connect, because Databricks connections cannot be tested yet.',
        'If the secure store cannot remove the connection details after a delete, the delete still stands. The stored details are left behind and you are not told.',
      ],
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'The actions you see on each row depend on your permissions. You need the Read permission to see the list and to test a connection. Adding, editing and deleting each need their own permission, which your administrator grants in Roles.',
    },
  ],
};

export default body;
