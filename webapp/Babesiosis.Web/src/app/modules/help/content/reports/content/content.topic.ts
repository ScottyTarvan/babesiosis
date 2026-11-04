import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Content. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'Content is the commentary, colours, images and PDFs that appear in a report\'s output. Business users add and change it here, without touching the report\'s design.',
    },
    {
      kind: 'paragraph',
      text: 'You choose where a value applies: to the whole component, to one schedule, to a group of entities, or to a single entity. A scope with no value of its own can show the value it inherits from a scope above it.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Open Reports › Content. The page shows one card per report. Search to narrow the cards, then select Manage on a card to open that report\'s content hub.',
    },
    { kind: 'heading', text: 'The content hub' },
    {
      kind: 'list',
      items: [
        'The scope tree on the left has four levels: Component, Schedule, Entity group and Entity. Entity groups can nest inside each other. Select a node to work at that scope.',
        'The canvas shows the component\'s layout, filled in for the selected scope. Each content element the layout places appears as a clickable chip.',
        'The Unplaced tray sits below the canvas. It lists elements that belong to the component but have no place in the layout, so you can still reach them.',
        'Select a chip or a tray item to open the element editor.',
      ],
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'The canvas is a map of the layout, not a preview of the finished report. The final appearance comes from the uploaded report design, which the canvas cannot show.',
    },
    { kind: 'heading', text: 'What you can do' },
    {
      kind: 'list',
      items: [
        'Commentary: write text in the editor. It is either rich text or plain text, and the format is fixed when the element is set up. Template Assist beside the field lists the columns and functions you can use in the text, with snippets you can insert.',
        'Colours: choose one colour for the scope.',
        'Images: upload an image. The file is only stored when you save the element.',
        'PDFs: upload a PDF. You can also download the PDF that is stored.',
        'Clear a value by saving the field empty. The value for that scope is removed completely.',
      ],
    },
    { kind: 'heading', text: 'Inherited values' },
    {
      kind: 'paragraph',
      text: 'When a scope has no value of its own, the hub looks upward for the nearest value. It checks the entity group first, then the schedule, then the component. It shows the value it finds and tells you which level the value came from. It never takes a value from a different entity.',
    },
    {
      kind: 'list',
      items: [
        'Effective Content shows the value in force at the selected scope, including inherited values.',
        'This Scope Only shows just what is set directly at the selected scope.',
        'The hub remembers your choice in your browser.',
        'To change an inherited colour or commentary, start typing. The inherited value stays on screen and unlocks for editing.',
        'To change an inherited image or PDF, the field clears and you upload a new file.',
      ],
    },
    { kind: 'heading', text: 'Saving' },
    {
      kind: 'list',
      items: [
        'You edit one element at a time in the editor.',
        'If you try to move, change scope or close with unsaved work, you are asked to save, discard or cancel.',
        'If someone else changed the value since you opened it, your save is refused rather than overwriting their change. Reopen the element and try again.',
      ],
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'Pasting an image into a rich-text commentary field is rejected. Use an Image element instead.',
        'A commentary element\'s format, rich text or plain text, cannot be changed from this screen.',
        'You need permission to read Content to see the list and the hub. Each kind of content has its own edit permission, so you can have read access and still be unable to save a change to some or all of them.',
        'Downloading a PDF is a separate permission from replacing it.',
        'Actions you are not allowed to use are greyed out in advance.',
      ],
    },
  ],
};

export default body;
