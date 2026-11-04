import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Environments. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'An environment is a scope that FDM stamps on its records. The four environments are Development, UAT, Pre-production and Production. Linked services, datasets, pipelines, pipeline logs, expectations, entity groups, activators, file uploads and downloads, mappings, diagrams, Data Health collector records, reports and distribution channels each belong to one environment.',
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'The application currently works in Development only. The control for switching environment has been removed, and nothing in the product reads or writes UAT, Pre-production or Production. Moving a dataset definition from one environment to another is not available.',
    },
    { kind: 'heading', text: 'How environments work' },
    {
      kind: 'list',
      items: [
        'FDM keeps its records for all environments in one shared place. The environment is a label on each record, not a separate copy of your setup.',
        'Your deployed data tables carry no environment column. The environment is decided by which database a table was deployed into, never by a value inside the table.',
        'Every screen that is scoped to an environment shows only that environment\'s records, and today that is always Development.',
      ],
    },
    { kind: 'heading', text: 'Linked services and targets' },
    {
      kind: 'paragraph',
      text: 'A linked service holds the connection to a target database. Each linked service belongs to exactly one environment, and FDM looks up its connection details (server and database) from a secure store when it needs them.',
    },
    {
      kind: 'list',
      items: [
        'An environment can have more than one linked service, each pointing at a different database. A name must be unique within an environment.',
        'A deployed dataset reaches its database through the specific linked service it uses, not through its environment alone.',
        'The linked services list is paged for each environment.',
        'The linked service form has no environment field. A new linked service is always stamped with the current environment, Development.',
        'To read the linked services list you need the permission to read linked services in Setup.',
      ],
    },
    { kind: 'heading', text: 'Deployment targets' },
    {
      kind: 'paragraph',
      text: 'SQL Server is the only database FDM currently deploys datasets to. Linked services can also be Databricks, blob storage, event grid or web API, but those are not places FDM deploys data tables to.',
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'Databricks cannot be configured yet. The linked service form shows no fields for it and its connection test is disabled. PostgreSQL, Databricks and Snowflake as deployment targets are not yet available.',
    },
  ],
};

export default body;
