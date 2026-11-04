import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: Great Expectations runner. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'Babesiosis checks the content of each loaded dataset with Great Expectations, an open-source data-validation library. You write rules in the application, and a runner evaluates them against the dataset after a load. The results come back for you to review.',
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'The runner is not yet called by the load pipelines. Until that is wired up it runs standalone only, so results appear only for runs that have been started that way.',
    },
    { kind: 'heading', text: 'From rule to result' },
    {
      kind: 'list',
      items: [
        'You add or edit rules on a dataset\'s Rules tab. Babesiosis checks them before saving.',
        'Each save publishes the dataset\'s enabled rules as a manifest. You can also publish by hand with Publish Manifest.',
        'Once load pipelines call it, the runner reads the manifest for each table a load wrote and evaluates the rules against that table in the warehouse.',
        'Babesiosis receives the summary and stores a run, a result for each rule and an exception for each failing record of a row-level rule.',
        'You review the run on the dataset\'s Runs tab and acknowledge exceptions.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'A failed validation never fails the load pipeline that triggered it. Validation is observation, not a gate.',
    },
    { kind: 'heading', text: 'Rules' },
    {
      kind: 'paragraph',
      text: 'A rule belongs to one dataset. It has a type, a name, a description, a severity, an origin and an Enabled setting that defaults to on.',
    },
    {
      kind: 'list',
      items: [
        'Severity is Info, Warning or Critical. The worst failed severity summarises a run.',
        'Origin is Manual, or Metadata when you accepted the rule from a proposal.',
        'A rule\'s name must be unique within its dataset.',
        'Only enabled rules are checked. A dataset with no enabled rules has nothing to evaluate, and its table is skipped without error.',
      ],
    },
    { kind: 'heading', text: 'Rule types' },
    {
      kind: 'paragraph',
      text: 'You choose from a fixed list of 45 rule types that work on SQL Server. In the Add Rule dialog, the Type field is a tree grouped by what the rule checks: Schema, Completeness, Volume, Uniqueness, Numeric, Validity and Sql. Select a group to open it, then choose a type. Type is required, and the search box filters types by name.',
    },
    {
      kind: 'list',
      items: [
        'Some types check the table as a whole, such as the row count being between two bounds.',
        'Some check each row\'s value in a column, such as not empty or in a set.',
        'Some check one statistic of a column, such as the mean, maximum or distinct count.',
        'Some compare two or more columns on the same row.',
        'The custom SQL type fails a row for each row your query returns.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'The form after the Type field changes to suit the chosen type. Some types let you set the share of rows that must pass, a value above 0 and up to 1. Rules that match patterns using regular expressions, and rules that compare against another source, are not offered.',
    },
    {
      kind: 'paragraph',
      text: 'When you save, Babesiosis lists every problem it finds rather than stopping at the first.',
    },
    {
      kind: 'list',
      items: [
        'Column choices must be fields of this dataset, of a type the rule accepts.',
        'Ranges need at least one bound, and the minimum cannot exceed the maximum.',
        'A custom SQL query must contain {batch}, start with SELECT and have no semicolon. It cannot contain INSERT, UPDATE, DELETE, MERGE, EXEC, EXECUTE, DROP, ALTER or TRUNCATE as a whole word.',
      ],
    },
    { kind: 'heading', text: 'Limit a rule to some rows' },
    {
      kind: 'paragraph',
      text: 'Rule types that allow it also accept a row condition. This limits the rule to some rows, for example only rows where Status is Active.',
    },
    {
      kind: 'list',
      items: [
        'Conditions sit in blocks. The first is labelled Where and each further block is labelled Or where.',
        'Each condition has a column, an operator and a value, except the empty checks, which need no value.',
        'Conditions in one block must all be true. A row qualifies if any block is true.',
        'Operators compare one value (equal, not equal, greater, less, greater or equal, less or equal), test against a set (in, not in), or check for empty values (is null, is not null).',
        'There can be at most 100 conditions in total.',
      ],
    },
    { kind: 'heading', text: 'Suggest From Metadata' },
    {
      kind: 'paragraph',
      text: 'Suggest From Metadata reads the dataset\'s fields and existing rules and proposes rules that you have not saved yet. It does nothing until you ask for it. Tick the proposals you want, edit or discard the rest, and accept. Accepted proposals are saved together or not at all.',
    },
    {
      kind: 'list',
      items: [
        'The table\'s columns match the set of user fields, in order.',
        'Not empty for each field that cannot be empty and is not a key.',
        'Uniqueness over the business key, single or compound.',
        'A maximum length for each bounded text field.',
      ],
    },
    { kind: 'paragraph', text: 'It does not propose column-type rules or value-in-set rules for lookup fields.' },
    { kind: 'heading', text: 'Publishing' },
    {
      kind: 'list',
      items: [
        'Every add, edit, delete and accepted proposal republishes the dataset\'s rules after the save completes.',
        'If publishing fails, you see a warning but the save still stands. Use Publish Manifest to try again.',
        'A dataset that is not deployed to the current environment publishes nothing.',
      ],
    },
    { kind: 'heading', text: 'Reviewing results' },
    {
      kind: 'paragraph',
      text: 'On a dataset\'s Runs tab, the first grid lists the latest runs, newest first, up to 50. Select a run to see its results, one for each rule. Select a result to see its exceptions. Choosing a new run or result clears the grids below it.',
    },
    {
      kind: 'list',
      items: [
        'A result shows whether the rule passed, how many rows failed and a sample of the failing values.',
        'Only rules that check each row\'s value can list failing records. Table-level and statistic rules report a single observed value.',
        'The exceptions grid has one column for each key column of the dataset.',
        'Select exception rows, then Acknowledge or Unacknowledge. This needs the Acknowledge permission. The unacknowledged-only toggle shows just the exceptions still to review.',
        'The results grid can copy a result\'s query, so you can find the failing rows in the warehouse yourself.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'If a run could not complete, it appears as an error run with Critical severity and no results.',
    },
    { kind: 'heading', text: 'Retention' },
    {
      kind: 'paragraph',
      text: 'Old runs are deleted every day at 02:30 UTC. Runs older than the configured retention, 7 days by default, are removed with their results and exceptions, acknowledged exceptions included. Review runs before then.',
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'The whole table is evaluated each time. Partitioned checks, such as one day at a time, are not available.',
        'There is no email notice of failures. Review results in the application.',
        'There is no way to try a rule against the table before you save it.',
      ],
    },
  ],
};

export default body;
