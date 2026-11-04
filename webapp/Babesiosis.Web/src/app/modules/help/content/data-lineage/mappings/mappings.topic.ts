import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Mappings. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'A mapping records how the columns of an outside source feed the fields of one or more datasets. You describe the source, choose the datasets it loads into, and bind each source column to the dataset fields it feeds.',
    },
    {
      kind: 'paragraph',
      text: 'A mapping is design information. It carries no data and has no status or activation step.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Open Data › Data Lineage › Mappings. The list shows every mapping in the current environment. Switching environment reloads the list.',
    },
    { kind: 'heading', text: 'The mapping list' },
    {
      kind: 'list',
      items: [
        'Source is the name of the source the mapping describes.',
        'Name is the mapping\'s own name. The list sorts by Name by default.',
        'DataSets lists the target datasets.',
        'Fields Mapped shows how many source fields are bound, as mapped out of total.',
        'Created By and Created Date show who created the mapping and when.',
        'Row actions are Open, Edit and Delete. Each is disabled, not hidden, if you lack the matching permission.',
      ],
    },
    { kind: 'heading', text: 'Create a mapping' },
    {
      kind: 'list',
      items: [
        'Select Add. A dialog opens for the mapping\'s header.',
        'Enter a Name (required, up to 128 characters). It must be unique in the environment.',
        'Enter a Source (required, up to 128 characters). This is your name for the source itself, separate from the mapping\'s name.',
        'Optionally add a Description (up to 1024 characters), then choose a Linked Service (required). Only SQL Server linked services in the current environment are offered.',
        'Save. The mapping opens straight away so you can build its source and datasets.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'Edit reopens the same fields. If someone else changed the mapping at the same time, the dialog closes and the list shows a refresh banner.',
    },
    { kind: 'heading', text: 'Linked service rules' },
    {
      kind: 'list',
      items: [
        'A mapping\'s target datasets can only come from its linked service.',
        'You cannot change the linked service while any target dataset belongs to a different one. The message names the reason.',
        'A mapping with no linked service can still be viewed and can load a source file. Saving its header, changing its Source Type and adding datasets all wait until you choose a linked service.',
        'A mapping loses its linked service if that linked service is deleted. A linked service that still holds datasets cannot be deleted.',
      ],
    },
    { kind: 'heading', text: 'The mapping page' },
    {
      kind: 'paragraph',
      text: 'Open a mapping to see a summary sidebar and three tabs. The sidebar shows the Source, File, Format, Source Type and Linked Service, the target dataset names, and three counts for source fields, mapped fields and datasets. Select a count to jump to its tab. Delete sits apart from the other controls and is disabled, with a tooltip, when you cannot use it.',
    },
    {
      kind: 'list',
      items: [
        'Details holds the header fields. Edit them in place and select Save, or Reset to discard changes.',
        'Source holds the Source Type, the file upload and the source fields.',
        'Mapping holds the target datasets and the binding grid.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'If a tab holds unsaved work when you leave it, you are asked first. An edited Details tab offers Save And Continue, Continue Without Saving or Cancel. An unsaved file preview offers Discard Preview or Cancel.',
    },
    { kind: 'heading', text: 'Define the source' },
    {
      kind: 'paragraph',
      text: 'On the Source tab, choose a Source Type from the control in the card header: File, Excel, Database or API. The change saves as soon as you select it and needs the Edit permission. Changing it deletes nothing.',
    },
    {
      kind: 'list',
      items: [
        'File reads a delimited text file or a fixed-width text file. You choose the format and set its options.',
        'Excel reads a workbook. You choose the Sheet and the Header Row, which is the row number as Excel shows it.',
        'Drag a file onto the drop zone or browse for it. Files over 5 MB are refused.',
        'Picking a file, or changing a parse option, shows a preview of the fields found and what saving would change. Nothing is written yet.',
        'Select Save Fields to commit the preview, or Discard to drop it. If saving would remove fields, you must confirm exactly what will be lost first.',
        'Load File sits at the foot of the Source card. Discard and Save Fields appear beside it while a preview is on screen.',
        'The file itself is never kept. Only the options, the field list, one sample value per field and the original file name are saved.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'When you save a parse, fields are matched to the existing ones by name, ignoring case. A matching field keeps its bindings. A new column adds a field. A parsed field missing from the file is deleted along with its bindings. A column that was renamed counts as one removal and one addition.',
    },
    {
      kind: 'paragraph',
      text: 'You can also add a source field by hand, and rename, retype or resample any field. A name is required, up to 255 characters, and unique on the mapping. A hand-added field shows a Manual marker. A parse never removes it, and renaming a parsed field turns it into a manual one. Deleting a field also deletes its bindings.',
    },
    {
      kind: 'paragraph',
      text: 'If the file is not in your browser, changing a parse option saves the option only. It does not re-read the file, and the existing fields stay as they are. Upload the file again to see the effect.',
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'Database and API can be chosen as a Source Type, but they are not yet supported. The Source tab shows a not yet supported message and no file controls.',
    },
    { kind: 'heading', text: 'Choose target datasets' },
    {
      kind: 'list',
      items: [
        'On the Mapping tab, select Add DataSets. It is disabled until the mapping has a linked service.',
        'Tick datasets in the tree. It groups them by dataset type and lists only deployed datasets on the mapping\'s linked service that are not already on the mapping.',
        'Confirm. Each dataset becomes a column in the grid.',
        'To remove a dataset, remove its column and confirm. This deletes every binding that fed it. You can remove the last dataset.',
      ],
    },
    { kind: 'heading', text: 'Bind source fields to dataset fields' },
    {
      kind: 'paragraph',
      text: 'The Mapping tab is a grid with one row for each source field and one column for each dataset. A row shows the field\'s name and data type. Each cell holds the dataset fields that source field feeds.',
    },
    {
      kind: 'list',
      items: [
        'A source field can feed several dataset fields, including several in the same dataset.',
        'A cell saves as soon as you confirm your selection. There is no Save button.',
        'Only fields that can accept a value are offered. System fields and computed fields are left out.',
        'A dataset field already fed by another source field in that dataset is not offered in a different cell.',
        'A hint appears when the source type and the dataset field type look like a poor match, such as text into a number. It does not stop you saving.',
      ],
    },
    { kind: 'heading', text: 'When a dataset changes' },
    {
      kind: 'paragraph',
      text: 'When a target dataset is redeployed, any binding to a field that no longer exists or can no longer accept a value is deleted. Bindings are removed outright and not marked as broken, so check the grid after a redeployment. A new field needs no action.',
    },
    { kind: 'heading', text: 'Delete a mapping' },
    {
      kind: 'paragraph',
      text: 'Delete removes the mapping, its source, its source fields and its bindings in one step. You are asked to confirm, and it cannot be undone.',
    },
    { kind: 'heading', text: 'Permissions' },
    {
      kind: 'paragraph',
      text: 'The Mapping permissions Read, Add, Edit and Delete sit in the Setup group in Roles. Each control is disabled, not hidden, when you lack its permission. Changing the Source Type or linked service needs Edit.',
    },
  ],
};

export default body;
