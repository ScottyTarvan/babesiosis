import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Pipelines. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'A pipeline is a record of an outside data-loading process, typically an Azure Data Factory pipeline, that lands data for the warehouse. Registering it here lets Babesiosis receive its run status, show its health and check its runs against rules.',
    },
    {
      kind: 'paragraph',
      text: 'Babesiosis does not create, schedule or start these processes. It only holds each pipeline\'s identity and receives notice when a run finishes.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Open Pipelines › List. The list shows the pipelines of the environment you currently have selected. Each row shows Name, Code, Category, Source, Description and Health.',
    },
    { kind: 'heading', text: 'What you can do' },
    {
      kind: 'list',
      items: [
        'Add a pipeline. Category is required, and Name must be unique. Description and Source are optional. The system assigns the Code when you save.',
        'Edit a pipeline\'s details. The Code cannot be changed.',
        'Delete a pipeline.',
        'Watch a pipeline, or stop watching it, from the control on its row.',
        'Select a row\'s Health value, or the row\'s expand arrow, to open its expectation rules. Select it again to close them. See Pipeline expectations.',
      ],
    },
    { kind: 'heading', text: 'Pipeline details' },
    {
      kind: 'list',
      items: [
        'Name: the display name. It must be unique among all pipelines, across every environment, so a name used in one environment cannot be reused in another.',
        'Code: an eight-character identifier that the system assigns. The outside process reports its runs by this Code, so give it to whoever sets the process up. Do not try to change it, because anything already configured with the old Code would stop matching.',
        'Category: a free-text grouping.',
        'Source: a free-text label for where the data comes from.',
        'Description: free text.',
      ],
    },
    { kind: 'heading', text: 'Health' },
    {
      kind: 'paragraph',
      text: 'Health summarises the pipeline\'s expectation rules. A pipeline with no enabled rules shows No Expectations, and so does a pipeline the summary does not list. If the summary cannot be read at all, for example because you do not have permission to read expectations, every row shows No Expectations, but the list itself still works. A failed read is not reported as an error. If a change made in a drop-down is followed by a failed refresh, the values already shown stay in place.',
    },
    { kind: 'heading', text: 'Watching a pipeline' },
    {
      kind: 'paragraph',
      text: 'Watching a pipeline subscribes you to it. The control turns watching and email notification on together and off together, so you cannot watch without also opting in to email. Critical expectation rules send email to the people watching.',
    },
    {
      kind: 'note',
      intent: 'warning',
      text: 'A pipeline with no enabled expectation rules can appear as not watched even though your watch is in place. A watch you switch on for such a pipeline can revert the next time the list reads its health.',
    },
    { kind: 'heading', text: 'How runs are recorded' },
    {
      kind: 'paragraph',
      text: 'When an outside process finishes a run, it reports the run status, matched to the pipeline by its Code. Babesiosis records the run, and the pipeline\'s expectation rules are then checked, some straight away and the rest at the next regular check. Review the recorded runs in Pipelines › Logs.',
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'Delete is permanent. A deleted pipeline cannot be recovered.',
        'If someone else changes or deletes a pipeline after you load the list, your edit or delete is rejected instead of overwriting their change. Reload the list and try again.',
        'A pipeline is not linked to an activator or a linked service. Setting up an activator does not start a pipeline, and a pipeline finishing does not start an activator.',
        'The pipeline\'s environment only decides which list it appears in. It does not connect Babesiosis to wherever the process runs.',
      ],
    },
    { kind: 'heading', text: 'Permissions' },
    {
      kind: 'paragraph',
      text: 'Read, Add, Edit and Delete permissions control the list and its actions. Add, edit and delete stay visible but are disabled if you do not hold the permission. Viewing logs uses its own permission.',
    },
  ],
};

export default body;
