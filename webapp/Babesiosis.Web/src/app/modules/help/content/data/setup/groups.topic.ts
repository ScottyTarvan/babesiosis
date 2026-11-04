import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Groups. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'A group is a saved, filtered view over one root Entity dataset and the Attribute and Classification datasets joined to it. You compose the group, preview it, save it and then deploy it, which compiles it into a view in your database.',
    },
    {
      kind: 'paragraph',
      text: 'The group\'s display field represents each row of the group elsewhere in the product, for example in Reports.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Open Data › Setup › Groups. The list shows every group. The designer is where you compose, preview, save and deploy a group.',
    },
    { kind: 'heading', text: 'What you can do' },
    {
      kind: 'list',
      items: [
        'Add, edit or delete a group from the list. The dialog holds the name, description, Linked Service, root dataset and display field.',
        'Choose the Linked Service only when you add the group. After that it is locked.',
        'Changing the Linked Service clears the root dataset and display field. Changing the root dataset clears the display field. The display field stays disabled until you choose a root dataset.',
        'In the designer, set the root and add members. Each member gets an alias and a place in the join order.',
        'When you add a member, the dataset picker explains how each candidate would join to the root and marks datasets already in the group.',
        'Build the filter from the columns the designer offers. Preview shows the matching rows without saving anything.',
        'Preview can show Classification membership as at a date you choose. It also accepts a change you have not saved yet. Results stop at 200 rows.',
        'Save replaces the group\'s whole membership with what the designer shows.',
        'The script view shows the SQL that deploying the saved group would run, without deploying it.',
        'Deploy creates or updates the group\'s view.',
        'Delete drops the group\'s view and then removes the group. The datasets it was built from are not touched. You can force the delete through if dropping the view fails.',
      ],
    },
    { kind: 'heading', text: 'Filter columns' },
    {
      kind: 'list',
      items: [
        'Root entity columns can be filtered unless they are system fields. Only columns marked visible appear in the group\'s view.',
        'Member columns can always be filtered, but they never add columns to the view. A member narrows or matches rows only.',
        'A field that points at another dataset, including Country and Currency, shows that dataset\'s display value in the filter instead of the raw key.',
        'If that dataset or field can no longer be found, the filter falls back to the raw key and the designer shows a warning.',
        'A joined Classification dataset only ever contributes each entity\'s covering version.',
      ],
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'A group has exactly one root. It must be an Entity dataset that is already deployed.',
        'Members must be Attribute or Classification datasets that reference the root entity. They must share the root\'s linked service and environment.',
        'A group can have at most 10 members and 100 joins in total.',
        'Once a group has members, the list dialog will not let you point it at a different root dataset.',
        'An alias must be a valid identifier, unique in the group, and different from the root entity\'s column names. It is capped at 32 characters.',
        'Names that are too long are shortened. A number is added if the shortened name clashes with another.',
        'The display field must be a visible field of the root entity that is included in the view. Fields from other datasets are refused.',
        'Two fields under one alias can end up with the same column name. The designer warns you but does not block you.',
        'A member shows a drift flag when the dataset it uses has been redeployed since the group was last deployed. Saving keeps the flag. A successful deploy clears it.',
        'The designer still opens when a member has drifted or no longer matches. Deploy refuses while any warning stands.',
        'Deploy also refuses if the display field is missing, hidden or not included, or if the filter cannot be turned into SQL.',
        'Deploy refuses if another group in the same environment would end up with the same view name.',
        'Only SQL Server linked services are supported for deploy.',
        'If a deploy fails, the previously deployed view stays in place.',
        'A deployed view always evaluates Classification joins as at today. The preview date is never carried into a deployment.',
      ],
    },
    { kind: 'heading', text: 'Permissions' },
    {
      kind: 'list',
      items: [
        'The Entity group item lets you view the list and add, edit or delete a group.',
        'The Entity group designer item lets you open the designer, preview, save and deploy.',
      ],
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'Parent-child hierarchies that point duplicate records at one parent record are not yet available in Data, and neither is identity resolution across source systems.',
    },
  ],
};

export default body;
