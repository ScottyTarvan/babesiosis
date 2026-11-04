import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Expectations. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'A dataset expectation is a rule about the content of a dataset\'s rows, such as no empty values, a value within a range, a value from a set, a maximum length, a condition across columns, or a custom SQL check. The rules are meant to be checked against the dataset after each load, and you review the results here. Load pipelines do not call the checks yet, so see the Great Expectations runner topic for when results appear.',
    },
    {
      kind: 'paragraph',
      text: 'These rules are about the data inside a dataset. Rules about a pipeline\'s run history are separate and are managed from Pipelines.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Open Data › Data Quality › Expectations. Data Quality sits above Setup in the sidebar. Every user who can see the Data area sees the item, but you need the Read permission to load the page. Without it you get a read-denied message.',
    },
    {
      kind: 'paragraph',
      text: 'Expectations are written and reviewed only here. The Setup Datasets pages have no expectations tab.',
    },
    { kind: 'heading', text: 'The dataset list' },
    {
      kind: 'paragraph',
      text: 'The landing page lists every dataset in every environment, one row each, whether or not it has rules. The subtitle reads, for example, N datasets, M with rules. It counts all datasets whatever filter is on. The list is sorted by Type, then Dataset.',
    },
    {
      kind: 'list',
      items: [
        'Type shows the dataset type with its icon, or No Type when it has none.',
        'Dataset is the dataset\'s name.',
        'Rules is how many rules the dataset has, enabled or not. A count above zero is tinted, and zero is grey.',
        'Enabled is ticked when the dataset has at least one enabled rule. You cannot change it here.',
        'Last Run shows when the dataset last ran, or Not run if it never has, including when it has no rules.',
        'Last Result is explained under Statuses below.',
        'Actions has an Open Rules button that opens the dataset\'s page, the same as selecting the row.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'The toolbar has Search, a quick filter of All, With Rules or Without Rules, Columns, Export and Refresh. On a narrow screen Columns, Export and Refresh move into an overflow menu. The quick filter, column filters and search combine, so a row shows only when it matches all of them.',
    },
    {
      kind: 'paragraph',
      text: 'The list loads in one go. If you lack Read you see only the read-denied message. Any other failure shows an error with Retry.',
    },
    { kind: 'heading', text: 'Statuses' },
    {
      kind: 'paragraph',
      text: 'Last Result summarises the dataset\'s latest run against its current rules.',
    },
    {
      kind: 'list',
      items: [
        'No rules means the dataset has no rules.',
        'Not run means it has rules but has never run.',
        'Passed means the latest run has no failed result for a current rule.',
        'N failed means that many results failed. It shows as a warning, or as danger when any failure is on a Critical rule.',
        'N failed · M critical shows the Critical failures separately when there are any.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'Sorting, filtering and exporting on Last Result use this label and not the raw counts.',
    },
    { kind: 'heading', text: 'The dataset page' },
    {
      kind: 'paragraph',
      text: 'Select a row to open the dataset\'s page. The header shows the dataset name and type with a Back link to the list. If the dataset cannot be found, you see a Dataset Not Found message with the Back link. Two tabs sit below: Rules and Runs. It always opens on Rules.',
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'Switching tabs reloads the tab you return to. On Runs, your selected run, result and exception rows and your place in the grid are not kept when you switch to Rules and back.',
    },
    { kind: 'heading', text: 'The Rules tab' },
    {
      kind: 'paragraph',
      text: 'The toolbar has three buttons on the right: Suggest From Metadata, Publish Manifest and Add Rule. Add Rule is the main action and is rightmost.',
    },
    {
      kind: 'list',
      items: [
        'The rules grid shows Type, Name, Column(s), Severity, Origin, Enabled, Last Result and Actions.',
        'Add Rule opens a dialog. Choose a Type from the tree grouped by what it checks, then fill in the form it shows for that type. Column pickers list the dataset\'s own fields.',
        'Edit rule opens the same dialog. Selecting the row does the same. A rule\'s type cannot be changed once it is saved.',
        'Delete rule asks you to confirm, then removes the rule.',
        'Suggest From Metadata proposes rules from the dataset\'s fields. Tick the ones you want and accept them. They are saved together or not at all.',
        'Publish Manifest publishes the current rules. Every rule save also does this for you.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'Edit and Delete are always shown. They are disabled when you lack the Edit or Delete permission.',
    },
    { kind: 'heading', text: 'The Runs tab' },
    {
      kind: 'paragraph',
      text: 'Runs shows three linked grids: the runs, the results of the selected run, and the exceptions of the selected result. How you review them is explained in the Great Expectations runner topic.',
    },
    { kind: 'heading', text: 'Permissions' },
    {
      kind: 'paragraph',
      text: 'Five items in the Setup group in Roles control Data Quality. The Roles screen lists them under Setup.',
    },
    {
      kind: 'list',
      items: [
        'Read opens the list and the dataset page, and reads rules, runs, results and exceptions.',
        'Add creates rules and accepts proposals.',
        'Edit changes a rule and publishes the manifest.',
        'Delete removes a rule.',
        'Acknowledge marks exceptions as acknowledged or not.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'Having only the expectation permissions is enough to author rules. You do not need access to the Setup Datasets screens. Buttons you cannot use are disabled, not hidden.',
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'Datasets that have never been deployed are listed too. You can write rules for them, but their rules are not published until the dataset is deployed.',
        'Deleting a dataset removes its rules. Its past runs are not removed, and the dataset leaves the list on the next load.',
        'Same-named datasets in different environments are not told apart, because the list shows no environment.',
        'The Export from the list includes an empty Actions column.',
      ],
    },
  ],
};

export default body;
