import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Mapping diagrams. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'A diagram is a picture of one or more mappings. It shows a block for each mapping\'s source and for each target dataset, with an arrow from every source field to the dataset field it feeds. Use it to document and explain how data flows.',
    },
    {
      kind: 'paragraph',
      text: 'A diagram is documentation only. It moves no data and never changes a mapping, a source or a dataset.',
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'Data Lineage is still being completed, so diagrams may not yet be available in every environment.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Open Data › Data Lineage › Diagrams, below Mappings. The list shows every diagram in the current environment.',
    },
    { kind: 'heading', text: 'The diagram list' },
    {
      kind: 'list',
      items: [
        'Name and Description identify the diagram.',
        'Mappings lists the mappings it shows, in diagram order.',
        'Created By, Created Date and Updated Date show its history.',
        'Open, Edit and Delete are row actions. Each is disabled, not hidden, if you lack the permission. Selecting a row also opens it.',
        'The list sorts by Name by default.',
      ],
    },
    { kind: 'heading', text: 'Create a diagram' },
    {
      kind: 'list',
      items: [
        'Select Add Diagram.',
        'Enter a Name (required, up to 128 characters, unique in the environment).',
        'Optionally enter a Description (up to 1024 characters).',
        'Save. The diagram opens empty in the designer.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'Edit reopens the same two fields, from the list or from Edit Details in the designer. If someone else changed the diagram at the same time, you are told and can reload.',
    },
    { kind: 'heading', text: 'The designer' },
    {
      kind: 'paragraph',
      text: 'The page header shows the diagram\'s name and description with four actions.',
    },
    {
      kind: 'list',
      items: [
        'Edit Details opens the name and description.',
        'Auto Arrange lays out every block again, with sources on the left and targets on the right.',
        'Export (Excalidraw) downloads the diagram.',
        'Save writes the diagram. An indicator beside it shows unsaved changes.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'The Mappings panel on the left has a search box and a checkbox list of every mapping in the environment. Each row shows the mapping name, its source name and its number of target datasets. The canvas fills the rest of the page.',
    },
    { kind: 'heading', text: 'Choose mappings' },
    {
      kind: 'list',
      items: [
        'Tick a mapping to place its source block, a block for each of its target datasets, and an arrow for each binding.',
        'You can tick several mappings. A dataset shared by two mappings is one block with arrows arriving from both.',
        'Untick a mapping to remove its source block and arrows. A dataset block stays while another ticked mapping targets it.',
        'If a mapping cannot be read, its row shows an error marker with the reason. It stays in your selection so saving does not lose it.',
        'The order you tick mappings in is the diagram order.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'A diagram always shows the current state of its mappings. It stores only which mappings it shows and where the blocks sit. Changes to a mapping appear the next time you open the diagram. If a mapping is deleted, it drops out of every diagram and the diagram stays.',
    },
    { kind: 'heading', text: 'Blocks and arrows' },
    {
      kind: 'list',
      items: [
        'A source block shows the source name, the mapping name beneath it, and one row for each source field with its type.',
        'A target block shows the dataset name with its schema, and one row for each field that can take a value, with its data type.',
        'A field that takes part in an arrow is emphasised. Hover over a block or row to highlight its arrows.',
        'A dataset that is no longer deployed shows a Not deployed note and no rows.',
        'Turn on Bound Fields Only to hide every row with no arrow. It is useful for large datasets and is saved with the diagram.',
      ],
    },
    { kind: 'heading', text: 'Arrange and zoom' },
    {
      kind: 'list',
      items: [
        'Drag a block by its header and its arrows follow. You can also focus a header and press the arrow keys to nudge it. Hold Shift for bigger steps.',
        'New blocks are placed automatically. Unticking and re-ticking a mapping in the same session restores its block positions.',
        'Zoom runs from 20% to 200% in steps of 10%. Use Zoom out and Zoom in, select the percentage to reset to 100%, or select Fit to show every block.',
        'Hold Ctrl (Cmd on a Mac) and turn the mouse wheel over the canvas to zoom. Zoom is not saved.',
      ],
    },
    { kind: 'heading', text: 'Save' },
    {
      kind: 'paragraph',
      text: 'Save writes the name, the ticked mappings in order, every block position and the Bound Fields Only setting. Save is disabled while any mapping is still loading, and a failed read never erases a saved arrangement.',
    },
    {
      kind: 'paragraph',
      text: 'If the diagram was saved elsewhere since you opened it, nothing is written. The designer says so and offers Reload, which discards your local changes. Leaving the page with unsaved changes asks you to confirm first.',
    },
    { kind: 'heading', text: 'Export to Excalidraw' },
    {
      kind: 'paragraph',
      text: 'Export (Excalidraw) downloads the diagram as a file named after the diagram, ending in .excalidraw. You can open and edit it in Excalidraw or other tools that support it. It shows the canvas as you see it now, including positions you have not saved.',
    },
    {
      kind: 'list',
      items: [
        'Each block becomes a group of boxes, one for the header and one for each visible field row.',
        'Each connector becomes an arrow attached to both rows, so moving a block in Excalidraw keeps its arrows attached.',
        'Colours are fixed whatever theme you use: a light blue source header and a light orange target header.',
        'Export needs only the Read permission and writes nothing to the server.',
      ],
    },
    { kind: 'heading', text: 'Permissions' },
    {
      kind: 'paragraph',
      text: 'Diagrams use the Mapping permissions in the Setup group in Roles.',
    },
    {
      kind: 'list',
      items: [
        'Read opens the list and the designer, and exports.',
        'Add creates a diagram.',
        'Edit saves the designer and the name and description.',
        'Delete deletes a diagram, after you confirm. This also removes its mapping selection and layout but never touches a mapping.',
      ],
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'Without Edit the designer is read-only. The checkbox list, Auto Arrange and Save are disabled. You can still drag blocks to tidy a view before exporting it, but you cannot save the result.',
    },
  ],
};

export default body;
