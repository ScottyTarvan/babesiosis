# The AI agent of the web app

The "AI Agent" screen (`/ai-agent`) sends a question to the function `articles-agent-ask`. The agent is in `/webapp/Babesiosis.Agents` (`Articles/ArticleQuestionAgent.cs`): one model on OpenRouter with tools over three sources. The model answers only from what the tools return, and cites each source by its code.

## What the agent reads

| Source | Where the tools read it | Tools | Cited as |
|---|---|---|---|
| Articles | `dbo.article`, and `dbo.article_section` when `AppSettings:AiAgents:FullText` is on ([database.md](database.md)) | `search_articles`, `get_article_details`, `search_passages`, `get_article_outline`, `get_article_section`, `get_article_full_text` | `[CB024]`, `[CB004 Results]` |
| Experiments | `dbo.experiment` and `dbo.experiment_result`, read at each question | `list_experiments`, `get_experiment`, `get_experiment_result` | `[SV-05-01-age-death]` |
| Clinical manual | The page files `/webapp/Babesiosis.Web/public/assets/clinical/*.json`, embedded in `Babesiosis.Agents.dll` at build | `list_clinical_pages`, `get_clinical_page`, `search_clinical_manual` | `[SY05]`, `[TX00]` |

- **Experiments.** `list_experiments` gives one row for each run: the code, package, method, role, datasets, question and summary. `get_experiment` gives the question, the settings and the `interpretation` text of the run. `get_experiment_result` gives one result payload as JSON, in parts of 12,000 characters. An experiment is available to the agent when its rows are in the database (`/experiments/run-instructions.md`, step 3). No restart is necessary.
- **Clinical manual.** `get_clinical_page` gives a page by section: `overview`, `diagnosis`, `approach`, `treatments`, `prognosis`, `gaps`, `references`. `search_clinical_manual` is a keyword search (words, not meaning) over all pages, for a drug, a test or a finding. **Build the API again after a page file changes**: the agent reads the copy in the assembly, not the file that the Clinical screen loads.
- The package reports (`/experiments/<package>/report.md`) and the `/clinical/<ID>/report.md` files are not available to the agent.

## Rules in the agent's instructions

The instructions are in `BuildInstructions` in `ArticleQuestionAgent.cs`. They tell the model:

- which source to use for which kind of question, and to say which source each statement is from;
- that the experiments are this project's own analyses on small samples, not peer-reviewed findings: give the effect size, interval, number of dogs and role, report a null result in full, and do not use "subtype" or "endotype";
- that the clinical manual is compiled by AI agents and is not peer reviewed: give the status and evidence level of a treatment, give a dose only as the page writes it and with its context, and say that each dose must be checked against the product label;
- not to choose a treatment or a dose for an individual animal.

## The answer

The answer carries three lists, which the server resolves from the codes in the text: `citations` (articles), `experiments` and `clinicalPages`. A code that does not exist is dropped. On the screen, a citation of an experiment opens `/experiments/<code>` and a citation of a manual page opens `/clinical/<ID>`, each in a new tab, because the conversation is kept only on the open page.

## To add a source

1. Write a repository or reader and a tools class in `/webapp/Babesiosis.Agents` (pattern: `Experiments/`, `Clinical/`). A tool returns a note that the model can act on (for example the list of valid codes); it does not throw for a wrong code.
2. Register it in `AgentsServiceCollectionExtensions.cs`, add its tools in `ArticleQuestionAgent.AskAsync`, and describe the source in `BuildInstructions`.
3. Resolve its codes into the answer (`ArticleAnswer`, `ArticleAgentMessageViewModel`, `chat-message.viewmodel.ts`) and give the screen a link (`appLinks` in `ai-agent.component.ts`).
