import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Overview. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'note',
      intent: 'info',
      text: 'The Compliance module is planned and is not yet available. This page describes what it is intended to offer.',
    },
    {
      kind: 'paragraph',
      text: 'Compliance will monitor portfolios against regulatory and internal investment limits, identify breaches and manage them through a structured review and remediation workflow. It is meant to cut manual compliance checking and let you re-run rules straight after a breach is resolved.',
    },
    { kind: 'heading', text: 'How it is intended to work' },
    {
      kind: 'list',
      items: [
        'A limit rule is generally a weighting within an outer grouping, for example a portfolio\'s exposure to a single issuer, manager or domicile.',
        'Rules run against holdings and market values from the governed data in FDM, and report breaches.',
        'Each breach enters a workflow in which a compliance officer inspects it and records its remediation.',
        'After remediation, you can re-run the rules immediately to confirm the breach is cleared.',
        'The module will ship with regulatory rulebooks in place, including Regulation 28 for South African retirement funds. You will also be able to define internal limits.',
        'At large portfolio volumes, rules can optionally be deployed to Spark for high-performance calculation.',
        'Compliance keeps no copy of the data. It reads holdings, market values and classifications such as issuer, manager, domicile and asset class.',
      ],
    },
    { kind: 'heading', text: 'What it is not for' },
    {
      kind: 'paragraph',
      text: 'Compliance does not generate trades to correct a breach. The Trading or Modelling module does that.',
    },
  ],
};

export default body;
