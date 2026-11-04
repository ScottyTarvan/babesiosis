import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Overview. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'note',
      intent: 'info',
      text: 'The Modelling module is planned and is not yet available. This page describes what it is intended to offer.',
    },
    {
      kind: 'paragraph',
      text: 'Modelling is designed for discretionary fund managers (DFMs) who run model portfolios. A manager defines a model made up of underlying funds and weights, based on internal research, and links it to client portfolios and policies. When the model changes, FDM works out the impact on every linked portfolio and produces the trade instructions needed to realign them. The aim is that one model change is applied consistently across the whole client base.',
    },
    { kind: 'heading', text: 'How it is intended to work' },
    {
      kind: 'list',
      items: [
        'Define a model as a set of underlying funds with weights.',
        'Link the model to client portfolios or policies, each with its own holdings. The model acts as a pseudo fund for them.',
        'When the model\'s weights change, FDM drills through to every linked portfolio and policy and calculates the trades that realign each one to the new weights.',
        'FDM then generates trade instruction files in the formats required by the linked investment service provider (LISP) platforms used in South Africa.',
        'Modelling reads holdings, valuations and the fund universe from the governed data in FDM and keeps no copy of it.',
      ],
    },
    { kind: 'heading', text: 'What it is not for' },
    {
      kind: 'list',
      items: [
        'Setting targets on a single portfolio outside a model. Use the Trading module for that.',
        'Checking the resulting trades against limits. Use the Compliance module for that.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'The module is aimed at small to medium-sized DFMs.',
    },
  ],
};

export default body;
