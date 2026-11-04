import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Entities. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'A report runs for a population of entities, such as clients or funds. You define that population as a tree of groups, and you can exclude individual entities from a group. All of this is done on the Groups screen.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'list',
      items: [
        'Open Reports › Setup and select Groups on the report\'s card. The Groups screen is the only place where a report\'s population is defined.',
        'After you add a report, the Groups screen opens straight away.',
        'The screen header shows the report name and its entity dataset, with a way back to Reports › Setup.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'A new report starts with one group named "All entities", with no filter and no grouping fields, so it produces its full population without further setup. You can rename it, narrow it or remove it. A report with no groups produces nothing.',
    },
    { kind: 'heading', text: 'Building the group tree' },
    {
      kind: 'paragraph',
      text: 'The tree is a single-column outline. Select a group to edit its name, grouping fields and filter in the editor beside the outline. A group can hold further groups.',
    },
    {
      kind: 'list',
      items: [
        'Add, remove and reorder groups among their siblings in the outline.',
        'A group cannot be moved under a different parent. Removing a group moves its child groups up to the removed group\'s parent.',
        'A grouping field splits a group\'s entities into value rows, one for each distinct combination of field values. A group with no grouping fields lists its entities directly.',
        'Preview shows what a group would return, even before you save it. Show SQL displays the query generated for it without running anything.',
        'Both use your current unsaved draft, including unsaved exclusions.',
      ],
    },
    { kind: 'heading', text: 'Rules for the tree' },
    {
      kind: 'list',
      items: [
        'Every group needs a name of up to 250 characters.',
        'Sibling groups cannot share a name.',
        'The tree can be at most 5 levels deep.',
        'A group can have at most 5 grouping fields, and at most 10 counting its parents.',
        'A group cannot group by a field that a parent group already uses.',
        'A grouping field must belong to the report\'s entity dataset, be marked as groupable, and not be a system field.',
        'A filter is checked when you save. A filter that refers to a column that does not exist stops the save.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'The same checks run as you work and again on the server. If any check fails, Save Groups is blocked until you fix it.',
    },
    { kind: 'heading', text: 'Seeing and excluding entities' },
    {
      kind: 'list',
      items: [
        'Select any group, leaf or not, to see its entity list: the entities that group resolves to at that level, before any child group narrows it.',
        'Where the group or its parents group by fields, the entities are shown in value rows. Entities load fifty at a time. Select Load more to see further ones.',
        'Every entity starts included. Untick an entity to add it to the selected group\'s excluded entities. Tick it again to remove it from that list.',
        'Ticking or unticking a value row does the same for every entity in it.',
        'An entity excluded on a group is excluded from that group\'s whole subtree.',
        'An excluded entity that is no longer in the group\'s population stays on the group\'s list, so you can remove it.',
      ],
    },
    { kind: 'heading', text: 'Which group an entity runs under' },
    {
      kind: 'list',
      items: [
        'Only leaf groups, those with no child groups, produce documents.',
        'An entity produces a document under exactly one leaf group: the first one, in tree order, whose population it is in. Reordering sibling groups changes that order.',
        'In a leaf group, an entity marked "also matches … — runs there" produces its document in an earlier leaf instead.',
        'In a group with sub-groups, "runs under …" names the leaf in another branch where the entity runs, and "won\'t produce a document" means it is in no leaf\'s population.',
      ],
    },
    { kind: 'heading', text: 'Saving the tree' },
    {
      kind: 'list',
      items: [
        'Save Groups saves the whole tree, exclusions included, in one step. Nothing is saved until you select it.',
        'Saving needs permission to edit the report. Without it, the tree is read-only. Viewing the screen needs permission to read the report.',
        'If someone else changed the report since you opened it, the save is refused.',
        'Saving the tree also requires the report\'s entity dataset to be an Entity-type dataset.',
        'Removing a group also removes its excluded entities and the component content set for it. If anything depends on the group, you are asked to confirm first.',
        'Reports already queued or produced for a removed group are left as they are.',
        'Saving an empty tree clears the groups. Clear the groups before changing the report\'s entity dataset if any group uses a filter, a grouping field or an excluded entity.',
        'Unsaved changes are protected when you leave the screen. Discard returns to the saved tree.',
      ],
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'A group marked Needs review was carried over from an earlier version and its filter was copied without being checked against the dataset. Edit or accept the filter, or clear it, to remove the mark.',
    },
    { kind: 'heading', text: 'Limits' },
    {
      kind: 'list',
      items: [
        'Each leaf group reads at most 50,000 entities. If a group reaches the limit, a single truncated indicator covers the whole report. It does not say which group was affected.',
        'Preview shows at most 1,000 distinct group-value combinations for the group being previewed.',
        'Preview and Show SQL only work on the report\'s entity dataset.',
        'A report with no entity dataset has no entities, whatever groups it holds.',
      ],
    },
  ],
};

export default body;
