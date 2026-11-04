import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: About FDM. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'Babesiosis (FDM) brings data from many source providers into one governed data warehouse. It then offers business modules that work directly on that same data. It is built for asset managers, wealth managers and discretionary fund managers.',
    },
    {
      kind: 'paragraph',
      text: 'Every module reads the same governed data. No module keeps its own copy, so there is no reconciliation between systems.',
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'Trading, Compliance, Query and Modelling are planned and not yet available.',
    },
    { kind: 'heading', text: 'How the modules fit together' },
    {
      kind: 'paragraph',
      text: 'FDM has two layers. The Data module is the core: it builds, maintains and governs the warehouse. The Reports, Trading, Compliance, Query and Modelling modules sit on top and all read from that warehouse. Your own data pipelines deliver source data into FDM. The Data module stores it safely, tracks its history and traces it back to its source.',
    },
    { kind: 'heading', text: 'The modules' },
    {
      kind: 'list',
      items: [
        'Data: lets non-technical users design and deploy a data warehouse by describing the data they need in business terms. FDM generates and maintains the database structures, loading processes and history tracking. Once data is deployed, you correct values, maintain classifications and organise records into groups on screens FDM provides. Manual corrections are kept separate from provider data, so they are not lost when data is reloaded.',
        'Data Quality: a section inside Data. It holds rules on dataset content that are checked after each load. Today the only rules are expectations.',
        'Data Lineage: a section inside Data. It holds source-to-dataset mappings and shows lineage from source to target.',
        'Reports: hosts and runs professionally designed reports built in established reporting tools. It runs reports across periods and groups of clients or funds, combines the results into single PDF, Word or Excel documents, and manages approval and distribution. Business users add commentary, images and branding without technical help.',
        'Trading (planned): a lightweight trading system in which you will set target weightings for client portfolios, and FDM will calculate the trades needed to reach them.',
        'Compliance (planned): will monitor portfolios against regulatory and internal investment limits and manage breaches through a review and remediation workflow.',
        'Query (planned): will let business users build their own dashboards and ad hoc reports on the data managed in FDM.',
        'Modelling (planned): for discretionary fund managers who run model portfolios. A change to a model will be applied across every linked portfolio.',
      ],
    },
    { kind: 'heading', text: 'Who each module is for' },
    {
      kind: 'list',
      items: [
        'Data, Data Quality: data owners and operations teams.',
        'Data Lineage: data analysts and data owners.',
        'Reports: reporting and client service teams.',
        'Trading: portfolio managers and dealers.',
        'Compliance: compliance officers.',
        'Query: business users and analysts.',
        'Modelling: discretionary fund managers.',
      ],
    },
    { kind: 'heading', text: 'Where to start' },
    {
      kind: 'paragraph',
      text: 'Start with the Data module, because every other module depends on the data it manages. Data topics in this help explain table types, the extra columns stored with each dataset, and environments.',
    },
  ],
};

export default body;
