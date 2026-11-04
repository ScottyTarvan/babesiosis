import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Analyse. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'Analyse lets you trace how a report is put together. You pick a report, then walk through its components, the content elements on each, and the entities each element applies to. You can export the same information to a spreadsheet.',
    },
    {
      kind: 'paragraph',
      text: 'Analyse only reads. It does not change a report, a component, an element or an entity selection, and it does not show content such as commentary text, colours or images.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'The Analyse screens are not shown in the sidebar menu. You reach them at Reports › Analyse using the direct address.',
    },
    { kind: 'heading', text: 'The report list' },
    {
      kind: 'list',
      items: [
        'The list shows the reports you can analyse, with name and description.',
        'Sort and filter the list as you would any grid.',
        'Select a row, or Manage on the row, to open the explorer.',
        'Manage is disabled if you lack permission to open the explorer.',
      ],
    },
    {
      kind: 'note',
      intent: 'warning',
      text: 'The report list may show no reports in a live environment. The request does not say which environment to use, so reports tagged to an environment may not match. Whether this happens in practice has not been confirmed.',
    },
    { kind: 'heading', text: 'The explorer' },
    {
      kind: 'paragraph',
      text: 'The explorer has three panes that depend on each other.',
    },
    {
      kind: 'list',
      items: [
        'Components, on the left, lists every component in the order the report uses them, with its type.',
        'Elements, in the middle, lists the selected component\'s Commentary, Colours, Images and PDFs.',
        'Entities, on the right, lists the entities that the selected element reaches.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'The explorer opens with the first component and its first element already selected. Choosing another component reloads its elements and selects the first. Choosing another element reloads its entities.',
    },
    {
      kind: 'list',
      items: [
        'Filter the Elements pane by element type.',
        'Search the Elements pane by text. The search covers the elements already shown.',
        'Connections and Transforms are not listed, because they are not tied to entities.',
        'A PDF element is listed only for a PDF component.',
      ],
    },
    { kind: 'heading', text: 'Which entities are shown' },
    {
      kind: 'paragraph',
      text: 'The Entities pane lists every entity the report is bound to, minus any that are excluded. Exclusions are applied at three levels: for the whole report, for the component, and for the selected element. An excluded entity does not appear, and the pane does not say why. The same entity in two different groups appears as two separate rows.',
    },
    { kind: 'heading', text: 'Exporting' },
    {
      kind: 'list',
      items: [
        'Export on the explorer toolbar downloads a spreadsheet.',
        'The spreadsheet has one sheet each for Commentary, Colours, Images and PDFs.',
        'Each row is one combination of component, element and entity that remains after the three exclusion levels.',
        'The file is named after the report.',
      ],
    },
    { kind: 'heading', text: 'Permissions' },
    {
      kind: 'list',
      items: [
        'Analyse (read) lets the list load.',
        'Analyse data (read) lets you open the explorer and see its three panes.',
        'Analyse data (download) lets you use Export.',
      ],
    },
  ],
};

export default body;
