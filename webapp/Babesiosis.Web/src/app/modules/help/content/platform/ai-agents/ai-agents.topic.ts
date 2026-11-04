import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: AI agents. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'The AI agent service is a built-in background service. A feature of Babesiosis can hand it a piece of text and a set of instructions, and it asks an AI model for a single written answer. It has no screen of its own: you see its results inside the feature that uses it.',
    },
    {
      kind: 'paragraph',
      text: 'Today one feature uses it, the pipeline error translator. It rewrites raw error messages in pipeline logs into short, plain-English explanations.',
    },
    { kind: 'heading', text: 'What you see: translated pipeline errors' },
    {
      kind: 'paragraph',
      text: 'When a pipeline reports an error, the message is rewritten so that it reads clearly without technical knowledge. The rewritten message is formal and brief, up to about 100 words, in a single block of text. It says what went wrong and, in simple terms, why it might have happened.',
    },
    {
      kind: 'list',
      items: [
        'It includes a short summary of the technical error, with any error codes in square brackets at the end, so technical support can investigate.',
        'If the error mentions a Python or papermill notebook output path or name, that is included in the technical part.',
        'It leaves out stack traces, SQL and technical jargon.',
      ],
    },
    { kind: 'heading', text: 'When you see the original message instead' },
    {
      kind: 'paragraph',
      text: 'The original, untranslated message is kept whenever the service cannot or should not translate it. The pipeline does not fail when this happens. Common reasons:',
    },
    {
      kind: 'list',
      items: [
        'The service is switched off. This is the normal state of any environment that has not been set up for it, so pipeline messages stay raw there.',
        'The message is shorter than 50 characters. Short messages are not sent for translation.',
        'The AI provider did not answer in time, was busy, returned an error or returned no text, or an unexpected fault occurred.',
        'The provider key is missing, or no model has been chosen for the level the translator uses.',
      ],
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'Only the first 5,000 characters of a long message are used.',
        'The same error text seen again within 7 days gets the earlier translation back, without a new call to the provider.',
        'A call to the provider that fails with a busy or server error is tried once more before giving up. Each attempt is allowed 20 seconds for the translator.',
        'Every use of the service is recorded in a usage log, including calls that were skipped, switched off or answered from the earlier translation. Metadata such as the model used, token counts, cost and outcome is kept for 90 days.',
        'The translator does not store the text it sends or the answer it receives in the usage log, except that a provider error message, when one is returned, is kept there for 90 days and could repeat part of the text sent. The 7-day answer cache keeps the translated answer, which can include values from your data.',
      ],
    },
    {
      kind: 'note',
      intent: 'warning',
      text: 'The error text is sent to an external AI provider, OpenRouter, for translation. Raw pipeline errors can contain values from your data. There are no data-protection controls beyond the ones above, and this is a known risk that has not yet been resolved.',
    },
    { kind: 'heading', text: 'What administrators set up' },
    {
      kind: 'list',
      items: [
        'A global switch turns the service on for an environment. It is off until someone sets it, so no call is ever made from an unconfigured environment. Switching it off stops every result, including earlier answers.',
        'The provider key, kept securely, gives access to the AI provider.',
        'Four levels, Low, Medium, High and Max, each map to one model. The translator uses Low. Changing the model for a level is a configuration change with no deployment, but it takes effect after the host restarts.',
        'A time limit for each provider attempt applies by default, 30 seconds unless set, and no agent can ask for more.',
        'A separate environment switch decides whether prompt and answer text may be stored in the usage log. It is off in production.',
      ],
    },
    {
      kind: 'paragraph',
      text: 'The database changes for the service must be applied to an environment before the code that writes its usage log and answer cache is deployed there. Without them the usage log cannot be written and the answer cache cannot be read, so the translator keeps the raw messages.',
    },
    { kind: 'heading', text: 'Limits' },
    {
      kind: 'list',
      items: [
        'The service gives one answer to one request. It does not hold conversations, call tools or stream answers.',
        'There is no cap on how many calls a burst of pipeline messages can make, other than what the host and the provider allow.',
        'Agents are fixed in the product. They cannot be created or edited by users or administrators.',
        'There is no screen for the usage log. It is read directly from the database.',
        'Changing an agent\'s instructions does not clear its earlier answers. They are used until their 7 days end.',
      ],
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'An AI Agents grid under Logs, with filters by agent, tier, outcome and date range, is not yet available.',
    },
  ],
};

export default body;
