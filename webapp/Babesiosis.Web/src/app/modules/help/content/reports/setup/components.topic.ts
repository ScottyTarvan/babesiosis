import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Components. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'A component is one building block of a report. A report is built from components, and each component is set up, laid out and filled with content on its own. The list order is the order they are considered when the report is built.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Open Reports › Setup and select View Components on a report. Components are listed in a rail on the left. Select one to open its tabs: General, Entities, Layout and Transforms. Telerik components also have a Connections tab.',
    },
    { kind: 'heading', text: 'Managing components' },
    {
      kind: 'list',
      items: [
        'Add a component by giving it a name, a type and an optional description.',
        'Move a component up or down from its row menu.',
        'Delete a component from its row menu.',
        'A component that is not fully set up is flagged Not configured.',
      ],
    },
    { kind: 'heading', text: 'Component types' },
    {
      kind: 'list',
      items: [
        'Telerik holds a report designed in Telerik Reporting. Its uploaded fonts are not used when a report runs yet. It is configured once every report file it needs is linked.',
        'PDF holds a single attached PDF document. It is always configured.',
        'MS Word holds a Word document template. It is configured once the document is linked.',
        'Table Of Contents is declared as a table of contents for the report. It is always configured.',
        'DevExpress holds a report designed in DevExpress. You cannot choose it for a new component.',
      ],
    },
    {
      kind: 'note',
      intent: 'warning',
      text: 'Only Telerik, PDF and MS Word components produce output when a report runs. A Table Of Contents or DevExpress component adds nothing to the finished report, and no error is shown.',
    },
    {
      kind: 'paragraph',
      text: 'A component\'s type is fixed when you create it. To change the type, delete the component and add a new one.',
    },
    { kind: 'heading', text: 'General tab' },
    {
      kind: 'list',
      items: [
        'Holds the name, the description and the settings for the component\'s type.',
        'Telerik components show fonts and the main report file. MS Word components show the document. Pick the file here.',
        'A picked file is held until you save the tab. Everything is then saved together.',
      ],
    },
    { kind: 'heading', text: 'Entities tab' },
    {
      kind: 'paragraph',
      text: 'The Entities tab decides which of the report\'s entities this component produces content for.',
    },
    {
      kind: 'list',
      items: [
        'The grid on the left lists the report\'s entities. Use Is Included to switch an entity on or off for this component.',
        'The tree on the right shows the selected entity\'s content elements, grouped by kind. Tick or untick individual elements.',
        'Each change is saved straight away. If it fails, the change is undone.',
        'The PDFs group appears only on PDF components. A PDF element on any other kind of component cannot be switched per entity here.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'A component carries four kinds of content: Commentary, Colours, Images and PDFs. You switch them on per entity in the Entities tab and place them in the Layout tab. Business users then fill them in under Reports › Content.',
    },
    { kind: 'heading', text: 'Layout tab' },
    {
      kind: 'paragraph',
      text: 'The Layout tab is where you arrange a component\'s content elements on a page. A component has one page. You choose a paper size such as A4 or Letter, or a custom width and height, plus orientation and margin. You also set a snap size for the ruler. Blocks are positioned and sized in millimetres.',
    },
    {
      kind: 'list',
      items: [
        'Block kinds are Text, Table, Chart, Custom, Image, Branding, Attachment and Divider.',
        'Text, Table, Chart and Custom blocks each take one commentary element.',
        'An Image block takes one image. A Branding block takes any number of colours. An Attachment block takes any number of PDFs.',
        'The side panel lists the component\'s elements as chips. Drag a chip onto a block to place it. Double-click a block to rename it.',
        'Deleting an element also removes it from the layout, so a block never points at something that no longer exists.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'If someone else saved the layout while you were editing, your save is refused. You then choose Keep Mine or Take Theirs.',
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'The layout is a mock-up of how content is arranged. It is not the real appearance of the finished report, which comes from the uploaded report design.',
    },
    {
      kind: 'note',
      intent: 'warning',
      text: 'Older layouts drawn in an earlier layout editor are not converted. Saving from the Layout tab replaces such a layout permanently. A layout saved here does not appear on the Content hub canvas, and the check that warns you before deleting an element still in use does not see it.',
    },
    { kind: 'heading', text: 'Transforms tab' },
    {
      kind: 'paragraph',
      text: 'A transform is a named query that supplies data to commentary. It belongs to the component, not to one commentary, so a single edit reaches every commentary that uses it. Several transforms can feed one commentary, in a set order.',
    },
    {
      kind: 'list',
      items: [
        'A transform has a Name, unique within the component, an optional description, a Linked Service, a command type, and the command text.',
        'Only SQL linked services are offered. The command type is either a query or a stored procedure.',
        'New transforms are added at the end of the list in the side panel, and the list cannot be reordered yet.',
        'Every run passes six values to the command: the component, the schedule, the schedule start date, the schedule end date, the entity group and the entity. A command that does not need a value ignores it.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'Commentary text is written in a template language. A built-in function library covers percentages, currency, number formatting, period names and basis points. A value a function cannot read gives an empty result rather than an error.',
    },
    { kind: 'heading', text: 'Testing a transform' },
    {
      kind: 'list',
      items: [
        'Use Test to run the transform as it stands in the open dialog. You do not need to save first.',
        'A test uses a placeholder for the schedule and stops after 15 seconds by default.',
        'The result shows up to 20 rows by default and tells you if it was cut short.',
        'A failed test shows its error message in the tab.',
      ],
    },
    { kind: 'heading', text: 'Linking transforms to commentary' },
    {
      kind: 'list',
      items: [
        'The board shows one row per commentary that has at least one transform linked. Commentary with none yet is listed separately until you start placing one.',
        'Drag a transform from the side panel onto a row to link it. You can also drag a link within a row, or to another row.',
        'Without a mouse, click a transform to select it, then click where it should go.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'Deleting a transform removes all of its links first. The confirmation names every commentary that will lose it.',
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'Only the General tab waits for a Save. Entity toggles, layout saves and transform changes take effect immediately.',
        'Deleting a component also deletes its images, PDFs and, for a Telerik component, its report files. It does not remove a Telerik font file or an MS Word document file from storage.',
      ],
    },
  ],
};

export default body;
