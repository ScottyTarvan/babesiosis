import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Overview. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'note',
      intent: 'info',
      text: 'The Trading module is planned and is not yet available. This page describes what it is intended to offer.',
    },
    {
      kind: 'paragraph',
      text: 'Trading is a lightweight trading system for small to medium-sized asset and wealth managers. You will set target weightings for client portfolios by fund, asset class or manager, and FDM will calculate the trades needed to reach them. It is meant to replace manual, spreadsheet-based trade calculation and instruction with a controlled, repeatable process.',
    },
    { kind: 'heading', text: 'How it is intended to work' },
    {
      kind: 'list',
      items: [
        'Set targets on a client portfolio\'s weightings, by fund, asset class or manager.',
        'FDM takes the portfolio\'s current holdings at market value and calculates the trades required to reach the targets.',
        'The trade plan is the unit of work. Within it you adjust targets until the plan meets its objective.',
        'FDM stores currency conversion rates so that trades can cross currencies.',
        'FDM loads bank account data and stops cash balances going below zero, to avoid overdraft costs.',
        'When a plan is settled, FDM generates trade instruction documents and emails them to brokers automatically.',
        'Trading reads holdings, market values, currency rates and bank balances from the governed data in FDM and keeps no copy of it.',
      ],
    },
    { kind: 'heading', text: 'What it is not for' },
    {
      kind: 'list',
      items: [
        'Order routing beyond email. Whether more routing is added later is still open.',
        'Managing model portfolios. Use the Modelling module for that.',
        'Regulatory limit checking. Use the Compliance module for that.',
      ],
    },
  ],
};

export default body;
