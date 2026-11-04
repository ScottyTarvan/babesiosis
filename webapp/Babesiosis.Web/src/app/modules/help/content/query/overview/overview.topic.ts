import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Overview. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'note',
      intent: 'info',
      text: 'The Query module is planned and is not yet available. This page describes what it is intended to offer.',
    },
    {
      kind: 'paragraph',
      text: 'Query will let business users build their own dashboards and ad hoc reports, with tables, charts and summary cards, on top of the data managed in FDM. It is meant as a simpler alternative to enterprise business intelligence tools, for firms with straightforward analytical needs, so that self-service analytics does not need a separate BI licence.',
    },
    { kind: 'heading', text: 'How it is intended to work' },
    {
      kind: 'list',
      items: [
        'An administrator or analyst defines a semantic model: a selection of datasets and the relationships between them, presented in business terms.',
        'End users build dashboards on top of the model by combining tables, charts and analytics cards. An analytics card shows a single summary value.',
        'Users can run ad hoc reports, which are tabular queries on a model, without help from a developer.',
        'Query reads the governed data in FDM and keeps no copy of it.',
      ],
    },
    { kind: 'heading', text: 'What it is not for' },
    {
      kind: 'list',
      items: [
        'Formatted, distributed client reporting. Use the Reports module for that.',
        'Replacing a full enterprise BI platform. Query covers simple, ad hoc dashboards and reports. Firms with more demanding needs are expected to keep a full BI product alongside FDM.',
        'Building or loading the underlying data. The Data module does that.',
      ],
    },
  ],
};

export default body;
