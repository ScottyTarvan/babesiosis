import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Data MCP tools. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'The data module of the MCP server gives an AI assistant tools to inspect dataset designs, check proposed fields, trace mapping lineage, change a dataset\'s design, deploy it, read design guidance and run activators. Every tool and prompt name starts with data_.',
    },
    {
      kind: 'paragraph',
      text: 'The assistant uses these tools as you. It needs your MCP Access permission plus the same permission items you would need in the application. If one is missing, the call fails with forbidden and the permission name, and no data is returned. To connect an assistant, see the MCP server topic.',
    },
    { kind: 'heading', text: 'Rules that apply to every tool' },
    {
      kind: 'list',
      items: [
        'Tools work in the DEV environment only, and a dataset given by name must be in DEV. Given an id, a read tool can also show a dataset outside DEV. The tools that change things refuse a dataset outside DEV.',
        'A dataset can be named by id or by name. A name must match one dataset. If two datasets share a name, the assistant is told both ids and table types and should repeat the call with the id.',
        'No separate MCP write permission exists. If you can make a change in Setup and hold MCP Access, you can make it through the assistant.',
        'Changes follow the same rules as the Setup screens, including the lock on Reference and system datasets, and they mark the dataset Changes Pending.',
        'No tool creates, renames or deletes a dataset, edits system fields, starts a teardown, link or import, or makes any mapping change. Create a dataset in Data › Setup › Datasets.',
      ],
    },
    { kind: 'heading', text: 'Inspecting datasets' },
    {
      kind: 'list',
      items: [
        'data_list_datasets lists datasets, optionally filtered by name text or table type. Each row shows the id, name, table type, deployment state and user field count. You see only table types whose Read permission you hold.',
        'data_get_dataset returns one dataset\'s design: details, user fields, system fields, business key fields and indexes with their fields, and deployment state. It needs the table type\'s Read item plus Dataset Field Read, Dataset Key Read and Dataset Index Read.',
        'data_describe_sql_data_types lists every field type the Add Field dialog offers, with parameter bounds, default-value rules, reference targets, the SQL Server type and warnings. Text is non-Unicode, so characters outside the Latin code page need Unicode Text.',
        'data_list_lookup_targets shows which datasets and display fields a reference field on a dataset may point to.',
        'data_validate_fields is a dry run. It checks proposed fields as the server and the Add Field dialog would, and reports each field as ok or with errors. Nothing is saved and the dataset does not become Changes Pending.',
      ],
    },
    { kind: 'heading', text: 'Design guidance' },
    {
      kind: 'paragraph',
      text: 'data_get_knowledge_base reads a set of five guidance articles on dataset design: overview, dataset metadata, dataset deployment, manual editing and business rules. With no arguments it lists them with version and published date. Give an article to get its table of contents, and a section number or all to read text. It needs MCP Access only and returns no data from your tenant.',
    },
    {
      kind: 'paragraph',
      text: 'The prompt data_design_dataset_from_file starts a design from a vendor sample file. Optionally describe the file. The assistant reads the guidance, recommends a dataset type, keys, merge pattern and field types, and changes nothing until you agree. Once you agree it can apply the design in DEV. Destructive steps and deployment approvals still need your explicit yes.',
    },
    { kind: 'heading', text: 'Mapping lineage' },
    {
      kind: 'paragraph',
      text: 'Three read-only tools show which source columns feed which target dataset fields. They need Mapping Read plus MCP Access.',
    },
    {
      kind: 'list',
      items: [
        'data_list_mappings lists mappings by name, optionally for one target dataset. Rows show the source, Source Type, linked service, target datasets, source field counts and mapped counts, and who created and last changed the mapping.',
        'data_get_mapping returns one mapping by id or name: its source definition, source fields, target datasets with their bindable fields, and bindings, with a type advisory where source and target types disagree.',
        'data_get_field_lineage shows, for a target dataset, which source fields feed each field across all mappings, and lists the fields no mapping feeds. Give a field name to look at one field.',
      ],
    },
    {
      kind: 'note',
      intent: 'warning',
      text: 'The mapping tools return each source field\'s sample value, up to 255 characters. Sample file content therefore reaches the AI provider. No tool returns file rows.',
    },
    { kind: 'heading', text: 'Changing a dataset design' },
    {
      kind: 'list',
      items: [
        'data_add_dataset_field, data_update_dataset_field and data_delete_dataset_field change user fields. They need Dataset Field Add, Update or Delete. Add and update refuse anything the Add Field dialog would refuse. On update, only the properties sent change.',
        'data_set_dataset_key sets the full ordered list of business key fields. It needs Dataset Key Update. It is refused on Lookup and Reference datasets.',
        'data_add_dataset_index, data_update_dataset_index and data_delete_dataset_index change indexes. They need Dataset Index Add, Update or Delete. An index needs at least one field. The two system indexes cannot be changed or deleted. Included columns cannot be set or changed.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'Update tools can take the version shown by data_get_dataset. If the field or index changed since, the update is refused as a stale copy.',
    },
    { kind: 'heading', text: 'Validating and deploying' },
    {
      kind: 'list',
      items: [
        'data_validate_dataset runs every validation rule and returns each rule with its result, as the Validations tab does. It needs Dataset Diagnostics Read.',
        'data_deploy_dataset runs validation first. If any rule fails it returns the failing rules and starts no run. Otherwise it starts a Deploy run, which plans and then waits at the approval gate. It needs the table type\'s Deploy item.',
        'data_get_deployment returns a run\'s status and plan steps, with destructive steps marked. Give a deployment id or a dataset for its latest run. It needs Dataset Deployment Read.',
        'data_approve_deployment approves a run waiting at the approval gate.',
        'data_cancel_deployment declines a run waiting at the approval gate, which cancels it. A run that is planning, queued or running cannot be cancelled this way.',
        'data_abandon_deployment abandons a Failed, Cancelled or Blocked run so the dataset can be deployed again.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'Approve, cancel and abandon need the permission item for the run\'s action and the dataset\'s table type, for example the Deploy item for a Deploy run. They can act on a run that any user started.',
    },
    { kind: 'heading', text: 'Actions that need your confirmation' },
    {
      kind: 'paragraph',
      text: 'Six actions run only after a preview and your explicit yes. The first call changes nothing and returns the preview and a confirmation token. The second call, with the token, carries it out.',
    },
    {
      kind: 'list',
      items: [
        'Delete a field. The preview lists the field and what depends on it. If something blocks the delete, you see the blockers and warnings and no token is issued.',
        'Delete an index.',
        'Remove a field from the business key.',
        'Remove a field from an index.',
        'Approve a deployment. The preview is the plan, with destructive steps marked.',
        'Abandon a deployment. The preview shows the run, its action and its status.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'Adding a field to the key, reordering the key, starting a deployment and cancelling a deployment need no confirmation. Nothing physical changes before approval.',
    },
    { kind: 'heading', text: 'Activators' },
    {
      kind: 'paragraph',
      text: 'These tools find and run activators in DEV. They need Activator Read, plus Activator Run to run one.',
    },
    {
      kind: 'list',
      items: [
        'data_list_activators lists activators by name, optionally by trigger type (Manual or Timer). Rows show the category, event name, trigger type, enabled flag and parameter count.',
        'data_get_activator returns one activator and its named parameters in the order the run dialog shows them, with data type, whether required, whether multi-select, and the format to pass.',
        'data_search_activator_parameter_values searches the value list of a parameter that has one, with a match that contains the text, starts with it or equals it. It returns 25 values by default, at most 100.',
        'data_run_activator publishes the activator\'s event. Ask for a dry run to check everything and see the payload without publishing or recording anything. It needs Activator Run even for a dry run.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'The prompt data_run_activator guides the assistant through a run: find the activator, read its parameters, ask you for each value, dry run and show the payload, ask for your yes, run it, then report the outcome. A real run takes no confirmation token, so agree the dry run payload before you say yes.',
    },
    {
      kind: 'list',
      items: [
        'Date values are yyyy-MM-dd. Boolean values are true or false. Entity values are the item id and Lookup values are the item name, both from the value list.',
        'A required parameter with no value, an unknown parameter name, or a value not in its value list is refused. All problems are reported together and nothing is published.',
        'A real run is recorded as a manual run with you as the actor. It does not check whether the activator is enabled, so a disabled Timer activator can still be run by hand.',
        'If publishing fails the run is recorded as Failed and the assistant is told the activator could not be published.',
      ],
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'Data quality is part of the data module but has no tools yet.',
    },
  ],
};

export default body;
