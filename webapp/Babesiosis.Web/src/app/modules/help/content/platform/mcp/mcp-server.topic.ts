import { HelpTopicBody } from 'app/modules/help/help.viewmodel';

/** Help topic: MCP server. Index entry: content/help-index.ts. */
const body: HelpTopicBody = {
  blocks: [
    {
      kind: 'paragraph',
      text: 'The MCP server lets an AI assistant such as Claude Code work with Babesiosis on your behalf. You connect the assistant once with a personal access token. After that, it can look up and, where your permissions allow, change things in Babesiosis using tools.',
    },
    {
      kind: 'paragraph',
      text: 'One server serves every module. The assistant acts as you: it can only do what your own permissions allow, and it works in the DEV environment only.',
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'Hosted deployment is still in progress. Everything below works on a local build. On a hosted environment you also need a functions key from your administrator, and the server address in the command may show a placeholder until your administrator sets it.',
    },
    { kind: 'heading', text: 'Where to find it' },
    {
      kind: 'paragraph',
      text: 'Open Account Settings. The MCP Access Tokens card sits with the Profile, Personal details and Change password cards. Its setup instructions are visible to every signed-in user.',
    },
    { kind: 'heading', text: 'What you need' },
    {
      kind: 'list',
      items: [
        'The MCP Access permission item, in the Platform category of Roles. You need it to create a token and for every tool call the assistant makes.',
        'Claude Code installed on your computer.',
        'On a hosted environment only: the functions key, which your administrator gives you. Leave it out when you run locally.',
      ],
    },
    { kind: 'heading', text: 'Connect Claude Code' },
    {
      kind: 'list',
      items: [
        'Open Account Settings and find the MCP Access Tokens card.',
        'Select Generate. Enter a name (up to 100 characters) and choose an expiry of 7, 30 or 90 days. The default is 30 days.',
        'Copy the secret straight away. It is shown once and cannot be shown again.',
        'Add the server to Claude Code. Paste the ready-made claude mcp add command shown after you generate the token, or add the server by hand to your Claude Code configuration under the name babesiosis.',
        'On a hosted environment, include the functions key from your administrator in the x-functions-key header.',
        'Check the connection, then start a new Claude Code session.',
      ],
    },
    {
      kind: 'note',
      intent: 'warning',
      text: 'Do not put a real token in a project configuration file that is committed to source control. The card never shows the functions key, and it shows placeholders where a value is not set.',
    },
    { kind: 'heading', text: 'Managing your tokens' },
    {
      kind: 'paragraph',
      text: 'The token list shows your own tokens only, with these columns: Name, Prefix, Created, Expires, Last Used and Status. The prefix is the short start of the secret and helps you tell tokens apart. Last Used is approximate.',
    },
    {
      kind: 'list',
      items: [
        'Active: not revoked and not expired.',
        'Expired: the expiry time has passed. This cannot be undone.',
        'Revoked: you revoked it. This cannot be undone.',
      ],
    },
    {
      kind: 'list',
      items: [
        'Use the Revoke row action on an Active token and confirm. It takes effect immediately.',
        'Tokens cannot be deleted. Expired and revoked tokens stay in the list.',
        'No token lasts forever. Generate a new one when it expires.',
      ],
    },
    { kind: 'heading', text: 'Rules to know' },
    {
      kind: 'list',
      items: [
        'Generate is enabled only if you hold MCP Access. If you lose MCP Access you can still see and revoke your tokens, but you cannot create tokens or use the tools.',
        'Your personal access token works only on the MCP server. Your sign-in token does not work there. The two credentials are not interchangeable.',
        'The assistant works in the DEV environment only. No tool takes an environment choice.',
        'Each tool also needs the permission items for what it does, for example Dataset Field Read to read fields. The assistant cannot do anything you could not do in the application.',
        'A new tool list is read when Claude Code connects, so start a new session after changes.',
      ],
    },
    { kind: 'heading', text: 'Finding what is available' },
    {
      kind: 'paragraph',
      text: 'Every tool and prompt name starts with the module it belongs to, for example data_list_datasets. Two built-in tools help the assistant find its way. platform_list_modules lists the modules that have tools, with their purpose, areas, and tool and prompt counts, and whether you hold a permission that one of their tools needs. platform_describe_module describes one module: its working rules and, for each tool and prompt, what it does, whether it changes anything, whether it needs confirmation and which permission items you hold or lack. Neither returns your data.',
    },
    { kind: 'heading', text: 'Confirming risky actions' },
    {
      kind: 'paragraph',
      text: 'Some actions, such as deleting a field or approving a deployment, take two calls. The first call changes nothing. It returns a preview of exactly what will happen and a confirmation token. The assistant should show you the preview and ask for an explicit yes. Only then does it repeat the call with the token to carry the action out.',
    },
    {
      kind: 'list',
      items: [
        'A confirmation token lasts 5 minutes.',
        'It works only for the same user, action, object and change it was issued for.',
        'It stops working if the object changes in the meantime. Ask for a fresh preview.',
        'It works once. Repeating a used token is refused and changes nothing.',
      ],
    },
    { kind: 'heading', text: 'Errors you may see' },
    {
      kind: 'paragraph',
      text: 'When something goes wrong the assistant receives a short error text and no data. Common ones:',
    },
    {
      kind: 'list',
      items: [
        'unauthenticated: the token is missing, expired, revoked or not a personal access token. Generate a new token.',
        'forbidden: followed by a permission name, for example MCP Access. Ask an administrator to add the permission item to your role.',
        'not-found: a dataset, mapping, activator, field or other item you named does not exist. The message lists valid choices where it can.',
        'ambiguous: a name matches more than one item. Repeat the request with the id.',
        'invalid: the request cannot be used, or a rule refused the change. The reason is given and nothing is changed.',
        'invalid: confirmation token: the token expired or no longer matches. Start again to get a new preview.',
        'error: the tool call failed: an unexpected failure. No detail is returned.',
        'error: confirmations are not configured on this server: a hosted server is missing a setting needed for confirmed actions. This applies even to the preview call. Nothing is changed. Tell your administrator.',
      ],
    },
    {
      kind: 'note',
      intent: 'info',
      text: 'Errors come back as ordinary text, so the assistant may not flag them as failures. Check what it reports. For the data tools themselves, see the Data MCP tools topic.',
    },
  ],
};

export default body;
