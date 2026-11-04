import {
  HelpModule,
  HelpTopicBody,
  HelpTopicEntry,
} from 'app/modules/help/help.viewmodel';

/**
 * Help & Support index — the whole outline as metadata, no body text
 * (spec `platform/help-support.md` §3.5–§3.7).
 *
 * This is the only file an agent reads to locate a topic: by module /
 * section / topic key, or by a specification document in `specRefs`. Each
 * topic's body lives in its own chunk at
 * `content/<module>/<section>/<topic>.topic.ts` and is loaded lazily.
 *
 * Adding, renaming or removing a topic is one entry here plus one chunk
 * file. A chunk that grows past ~150 lines is split into further topics.
 */

const CHUNK_ROOT = 'Babesiosis.Web/src/app/modules/help/content';

/** Builds a topic entry; the chunk path follows from the three keys. */
function topic(
  moduleKey: string,
  sectionKey: string,
  key: string,
  title: string,
  summary: string,
  specRefs: string[],
  load: () => Promise<{ default: HelpTopicBody }>,
): HelpTopicEntry {
  return {
    key,
    title,
    summary,
    specRefs,
    chunk: `${CHUNK_ROOT}/${moduleKey}/${sectionKey}/${key}.topic.ts`,
    load: () => load().then(m => m.default),
  };
}

export const HELP_MODULES: readonly HelpModule[] = [
  // ---------------------------------------------------------------- Getting started
  {
    key: 'getting-started',
    label: 'Getting started',
    icon: 'rocket',
    status: 'implemented',
    summary: 'What FDM is and how the application is organised.',
    sections: [
      {
        key: 'overview',
        label: 'Overview',
        topics: [
          topic('getting-started', 'overview', 'about-fdm', 'About FDM',
            'The modules that make up Babesiosis and how they fit together.',
            ['fdm-overview.md'],
            () => import('app/modules/help/content/getting-started/overview/about-fdm.topic')),
        ],
      },
    ],
  },

  // ---------------------------------------------------------------- Data
  {
    key: 'data',
    label: 'Data',
    icon: 'database',
    status: 'implemented',
    summary: 'Define, load and manage the datasets that make up the data warehouse.',
    sections: [
      {
        key: 'concepts',
        label: 'Concepts',
        topics: [
          topic('data', 'concepts', 'table-types', 'Table types',
            'Entities, attributes, classifications, data tables, lookups and references.',
            ['data/concepts/table-types.md'],
            () => import('app/modules/help/content/data/concepts/table-types.topic')),
          topic('data', 'concepts', 'adjacent-columns', 'Adjacent columns',
            'The system columns stored alongside every dataset row.',
            ['data/concepts/adjacent-columns.md'],
            () => import('app/modules/help/content/data/concepts/adjacent-columns.topic')),
          topic('data', 'concepts', 'environments', 'Environments',
            'The environments FDM is designed for and the one it works in today.',
            ['data/concepts/environments.md'],
            () => import('app/modules/help/content/data/concepts/environments.topic')),
        ],
      },
      {
        key: 'dashboard',
        label: 'Dashboard',
        topics: [
          topic('data', 'dashboard', 'health', 'Health dashboard',
            'Widgets over warehouse metrics: volume, growth, activity, indexes and statistics.',
            [
              'data/dashboards/health.md',
              'data/dashboards/health-collector-settings.md',
              'data/dashboards/health-metrics-collector.md',
              'data/dashboards/health-anomaly-detection.md',
            ],
            () => import('app/modules/help/content/data/dashboard/health.topic')),
        ],
      },
      {
        key: 'manage',
        label: 'Manage',
        topics: [
          topic('data', 'manage', 'manage-datasets', 'Datasets',
            'Browse and edit the data held in deployed datasets.',
            ['data/manage/datasets.md', 'data/manage/datasets-audit.md'],
            () => import('app/modules/help/content/data/manage/manage-datasets.topic')),
          topic('data', 'manage', 'manage-files', 'Files',
            'Upload files into datasets and download extracts from them.',
            ['data/manage/files.md'],
            () => import('app/modules/help/content/data/manage/manage-files.topic')),
          topic('data', 'manage', 'manage-activators', 'Activators',
            'Run and monitor the activators that trigger loads.',
            ['data/manage/activators.md'],
            () => import('app/modules/help/content/data/manage/manage-activators.topic')),
        ],
      },
      {
        key: 'setup',
        label: 'Setup',
        topics: [
          topic('data', 'setup', 'linked-services', 'Linked services',
            'Connections to the databases, storage and services FDM reads from and writes to.',
            ['data/setup/linked-services.md'],
            () => import('app/modules/help/content/data/setup/linked-services.topic')),
          topic('data', 'setup', 'setup-datasets', 'Datasets',
            'Define datasets, their fields, deployment, loading and classification history.',
            [
              'data/setup/datasets.md',
              'data/setup/datasets-field-types.md',
              'data/setup/datasets-deployment.md',
              'data/setup/datasets-loading-merge.md',
              'data/setup/datasets-classification-history.md',
              'data/setup/datasets-design.md',
              'data/setup/datasets-deployment-runs.md',
            ],
            () => import('app/modules/help/content/data/setup/setup-datasets.topic')),
          topic('data', 'setup', 'groups', 'Groups',
            'Group related datasets so they can be managed together.',
            ['data/setup/groups.md'],
            () => import('app/modules/help/content/data/setup/groups.topic')),
          topic('data', 'setup', 'setup-activators', 'Activators',
            'Configure the schedules and events that start loads.',
            ['data/setup/activators.md'],
            () => import('app/modules/help/content/data/setup/setup-activators.topic')),
          topic('data', 'setup', 'setup-files', 'Files',
            'Configure file upload and download definitions.',
            ['data/setup/files.md'],
            () => import('app/modules/help/content/data/setup/setup-files.topic')),
        ],
      },
      {
        key: 'pipelines',
        label: 'Pipelines',
        topics: [
          topic('data', 'pipelines', 'pipelines', 'Pipelines',
            'Define the pipelines that move data into the warehouse.',
            ['data/pipelines/pipelines.md'],
            () => import('app/modules/help/content/data/pipelines/pipelines.topic')),
          topic('data', 'pipelines', 'logs', 'Pipeline logs',
            'Review pipeline runs, their status and their errors.',
            ['data/pipelines/logs.md'],
            () => import('app/modules/help/content/data/pipelines/logs.topic')),
          topic('data', 'pipelines', 'expectations', 'Pipeline expectations',
            'Rules on a pipeline\'s runs, managed from its row on the Pipelines list.',
            ['data/pipelines/expectations.md'],
            () => import('app/modules/help/content/data/pipelines/expectations.topic')),
        ],
      },
    ],
  },

  // ---------------------------------------------------------------- Data Lineage
  {
    key: 'data-lineage',
    label: 'Data Lineage',
    icon: 'arrows-join',
    status: 'in-progress',
    summary: 'Trace where data comes from and how it reached each dataset.',
    sections: [
      {
        key: 'mappings',
        label: 'Mappings',
        topics: [
          topic('data-lineage', 'mappings', 'mappings', 'Mappings',
            'Source-to-dataset mappings and how to maintain them.',
            ['data-lineage/mappings.md', 'data-lineage/mappings-source.md'],
            () => import('app/modules/help/content/data-lineage/mappings/mappings.topic')),
          topic('data-lineage', 'mappings', 'diagrams', 'Mapping diagrams',
            'Picture one or more mappings and export them as Excalidraw scenes.',
            ['data-lineage/diagrams.md'],
            () => import('app/modules/help/content/data-lineage/mappings/diagrams.topic')),
        ],
      },
      {
        key: 'lineage',
        label: 'Lineage & audit',
        topics: [
          topic('data-lineage', 'lineage', 'lineage', 'Lineage',
            'Batch IDs, the deployment log and auditing a row back to its load.',
            ['data-lineage/lineage.md'],
            () => import('app/modules/help/content/data-lineage/lineage/lineage.topic')),
        ],
      },
    ],
  },

  // ---------------------------------------------------------------- Data Quality
  {
    key: 'data-quality',
    label: 'Data Quality',
    icon: 'checkup-list',
    status: 'implemented',
    summary: 'Rules that check dataset content after each load.',
    sections: [
      {
        key: 'expectations',
        label: 'Expectations',
        topics: [
          topic('data-quality', 'expectations', 'expectations', 'Expectations',
            'Define the rules a dataset\'s rows must meet.',
            ['data-quality/expectations.md'],
            () => import('app/modules/help/content/data-quality/expectations/expectations.topic')),
        ],
      },
      {
        key: 'great-expectations',
        label: 'Great Expectations runner',
        topics: [
          topic('data-quality', 'great-expectations', 'great-expectations', 'Great Expectations runner',
            'How expectations are evaluated and where the results go.',
            ['data-quality/great-expectations.md'],
            () => import('app/modules/help/content/data-quality/great-expectations/great-expectations.topic')),
        ],
      },
    ],
  },

  // ---------------------------------------------------------------- Reports
  {
    key: 'reports',
    label: 'Reports',
    icon: 'report-analytics',
    status: 'implemented',
    summary: 'Design, run, schedule and distribute reports.',
    sections: [
      {
        key: 'concepts',
        label: 'Concepts',
        topics: [
          topic('reports', 'concepts', 'report-lifecycle', 'Report lifecycle',
            'From report definition to rendered, distributed output.',
            ['reports/concepts/report-lifecycle.md'],
            () => import('app/modules/help/content/reports/concepts/report-lifecycle.topic')),
          topic('reports', 'concepts', 'data-contract', 'Data contract',
            'The data a report expects and how it is supplied.',
            ['reports/concepts/data-contract.md'],
            () => import('app/modules/help/content/reports/concepts/data-contract.topic')),
        ],
      },
      {
        key: 'dashboard',
        label: 'Dashboard',
        topics: [
          topic('reports', 'dashboard', 'operations', 'Operations dashboard',
            'An overview of report runs, schedules and distribution.',
            ['reports/dashboards/operations.md'],
            () => import('app/modules/help/content/reports/dashboard/operations.topic')),
        ],
      },
      {
        key: 'run',
        label: 'Run',
        topics: [
          topic('reports', 'run', 'run', 'Run',
            'Run a report on demand and how it is rendered.',
            ['reports/run/run.md', 'reports/run/rendering-engine.md'],
            () => import('app/modules/help/content/reports/run/run.topic')),
          topic('reports', 'run', 'run-schedules', 'Run schedules',
            'Scheduled report runs and their history.',
            ['reports/run/run-schedules.md'],
            () => import('app/modules/help/content/reports/run/run-schedules.topic')),
          topic('reports', 'run', 'instances', 'Instances',
            'Review the output of individual report runs.',
            ['reports/run/instances.md'],
            () => import('app/modules/help/content/reports/run/instances.topic')),
        ],
      },
      {
        key: 'distribute',
        label: 'Distribute',
        topics: [
          topic('reports', 'distribute', 'distribute', 'Distribute',
            'Send report output to its recipients.',
            ['reports/distribute/distribute.md'],
            () => import('app/modules/help/content/reports/distribute/distribute.topic')),
        ],
      },
      {
        key: 'content',
        label: 'Content',
        topics: [
          topic('reports', 'content', 'content', 'Content',
            'Commentary, images and branding added to reports.',
            ['reports/content/content.md'],
            () => import('app/modules/help/content/reports/content/content.topic')),
        ],
      },
      {
        key: 'setup',
        label: 'Setup',
        topics: [
          topic('reports', 'setup', 'reports', 'Reports',
            'Create and configure report definitions.',
            ['reports/setup/reports.md'],
            () => import('app/modules/help/content/reports/setup/reports.topic')),
          topic('reports', 'setup', 'components', 'Components',
            'Report components, their layout and their transforms.',
            [
              'reports/setup/components.md',
              'reports/setup/components-layout.md',
              'reports/setup/components-transforms.md',
            ],
            () => import('app/modules/help/content/reports/setup/components.topic')),
          topic('reports', 'setup', 'entities', 'Entities',
            'The data entities a report draws on.',
            ['reports/setup/groups.md'],
            () => import('app/modules/help/content/reports/setup/entities.topic')),
          topic('reports', 'setup', 'schedules', 'Schedules',
            'Define when reports run.',
            ['reports/setup/schedules.md'],
            () => import('app/modules/help/content/reports/setup/schedules.topic')),
          topic('reports', 'setup', 'channels', 'Channels',
            'Distribution channels and their settings.',
            ['reports/setup/channels.md'],
            () => import('app/modules/help/content/reports/setup/channels.topic')),
        ],
      },
      {
        key: 'analyse',
        label: 'Analyse',
        topics: [
          topic('reports', 'analyse', 'analyse', 'Analyse',
            'Explore report data interactively.',
            ['reports/analyse/analyse.md'],
            () => import('app/modules/help/content/reports/analyse/analyse.topic')),
        ],
      },
    ],
  },

  // ---------------------------------------------------------------- Teams & access
  {
    key: 'teams',
    label: 'Teams & access',
    icon: 'users',
    status: 'implemented',
    summary: 'Users, roles and what each person can see and do.',
    sections: [
      {
        key: 'roles',
        label: 'Roles',
        topics: [
          topic('teams', 'roles', 'roles', 'Roles',
            'Roles and the permissions they grant.',
            ['data/teams/roles.md'],
            () => import('app/modules/help/content/teams/roles/roles.topic')),
        ],
      },
      {
        key: 'users',
        label: 'Users',
        topics: [
          topic('teams', 'users', 'users', 'Users',
            'Add users and assign them to roles.',
            ['data/teams/users.md'],
            () => import('app/modules/help/content/teams/users/users.topic')),
        ],
      },
    ],
  },

  // ---------------------------------------------------------------- Platform
  {
    key: 'platform',
    label: 'Platform',
    icon: 'plug-connected',
    status: 'implemented',
    summary: 'Connect AI assistants and agents to FDM.',
    sections: [
      {
        key: 'mcp',
        label: 'MCP server',
        topics: [
          topic('platform', 'mcp', 'mcp-server', 'MCP server',
            'Connect an AI assistant to FDM with a personal access token.',
            ['platform/mcp-server.md'],
            () => import('app/modules/help/content/platform/mcp/mcp-server.topic')),
          topic('platform', 'mcp', 'data-tools', 'Data MCP tools',
            'The data tools and prompts an AI assistant can use through the MCP server.',
            [
              'data/mcp-tools.md',
              'data/mcp-tools-writes.md',
              'data/mcp-tools-activators.md',
              'data/mcp-tools-lineage.md',
            ],
            () => import('app/modules/help/content/platform/mcp/data-tools.topic')),
        ],
      },
      {
        key: 'ai-agents',
        label: 'AI agents',
        topics: [
          topic('platform', 'ai-agents', 'ai-agents', 'AI agents',
            'The built-in AI agent service and the pipeline error translator it powers.',
            [
              'platform/ai-agents.md',
              'platform/ai-agents-pipeline-error-translator.md',
              'platform/ai-agents-audit-and-cache.md',
            ],
            () => import('app/modules/help/content/platform/ai-agents/ai-agents.topic')),
        ],
      },
    ],
  },

  // ---------------------------------------------------------------- Planned modules
  {
    key: 'query',
    label: 'Query',
    icon: 'search',
    status: 'planned',
    summary: 'Semantic models, dashboards and ad hoc reporting over FDM data.',
    sections: [
      {
        key: 'overview',
        label: 'Overview',
        topics: [
          topic('query', 'overview', 'overview', 'Overview',
            'What the Query module will offer.',
            ['query/query-spec.md'],
            () => import('app/modules/help/content/query/overview/overview.topic')),
        ],
      },
    ],
  },
  {
    key: 'modelling',
    label: 'Modelling',
    icon: 'chart-dots',
    status: 'planned',
    summary: 'Financial models built on warehouse data.',
    sections: [
      {
        key: 'overview',
        label: 'Overview',
        topics: [
          topic('modelling', 'overview', 'overview', 'Overview',
            'What the Modelling module will offer.',
            ['modelling/modelling-spec.md'],
            () => import('app/modules/help/content/modelling/overview/overview.topic')),
        ],
      },
    ],
  },
  {
    key: 'trading',
    label: 'Trading',
    icon: 'arrows-exchange',
    status: 'planned',
    summary: 'Trading data and workflows.',
    sections: [
      {
        key: 'overview',
        label: 'Overview',
        topics: [
          topic('trading', 'overview', 'overview', 'Overview',
            'What the Trading module will offer.',
            ['trading/trading-spec.md'],
            () => import('app/modules/help/content/trading/overview/overview.topic')),
        ],
      },
    ],
  },
  {
    key: 'compliance',
    label: 'Compliance',
    icon: 'shield-check',
    status: 'planned',
    summary: 'Compliance rules and monitoring.',
    sections: [
      {
        key: 'overview',
        label: 'Overview',
        topics: [
          topic('compliance', 'overview', 'overview', 'Overview',
            'What the Compliance module will offer.',
            ['compliance/compliance-spec.md'],
            () => import('app/modules/help/content/compliance/overview/overview.topic')),
        ],
      },
    ],
  },
];
