Description

Where to find agent documents. All paths are relative to `.claude/agents/`.


Architecture documents found in sub folder `architecture/`:

\*\* general.md - description of general architecture pattern, always read

\*\* core.md - description of core code libraries, always read

\*\* services.md - description of services pattern, dependency injection, read for backend development

\*\* controllers.md - description of backend controllers following MVC style, read for backend development

\*\* function-app.md - description of function apps acting as API layer, read for backend development

\*\* web-app.md - description of frontend angular app, read for frontend development


Product requirement documents found in sub folder `features/`:

\*\* features.md - instructions on where to find features, always read


Specification agents (product specification under `.claude/specs/`, not code):

\*\* spec-writer.md - orchestrator; one specification per module folder, state in `.claude/specs/working/spec-register.md`

\*\* spec-section-writer.md - worker; drafts or revises one sub-document from a truth report or the user's sources

\*\* spec-code-truth.md - read-only auditor used by spec-writer to ground and verify as-built modules

\*\* spec-gate.md - pre-build gate; rules a task file against the spec (PASS / BLOCKED / NO-DOCUMENT); feature-orchestrator step 0

\*\* spec-steward.md - structural maintenance per module (compact, de-duplicate, split/merge, register and working-area hygiene); proposes, applies only approved items; never changes binding meaning

Build agents (launched only by `/build`: its workflows, or step 4c in fix mode):

\*\* builder-contract.md - process contract all seven build agents read first: modes, inputs, session-log headings, layer ownership, compile, return shape

\*\* ui-builder.md - step 6, Angular UI port with fs-component + mocks; runs `npm run build` and `.claude/tools/permission-gate.js`; launched by /build step 3 via the Agent tool

\*\* model-data-config.md - step 1, entities + EF configs + DbContextBase wiring

\*\* permissions-config.md - step 2 (pass: registration) and step 5 (pass: attributes)

\*\* core-controller.md - step 3, controllers, commands, view models, permission key map

\*\* azure-function.md - step 4, HTTP function wrappers (no RequiredPermission)

\*\* unit-test-generator.md - step 7, xUnit tests + regression tests for fixed findings

\*\* sql-script-generator.md - step 8, idempotent T-SQL + ledger (revise unapplied in place, else delta)

Review agents (read-only, scoped to one /build session's diff; run in /build phase B step 6b):

\*\* dm-code-reviewer.md - correctness bugs across layer seams + DataManager traps, then cleanups; modelled on /code-review

\*\* dm-security-reviewer.md - exploitable vulnerabilities with a DataManager checklist; modelled on /security-review


\*\* feature-orchestrator.md - the build CONTRACT (sequence, schema, hand-offs, gates). Driven by the `/build` skill from the main session, not launched directly.

Personal tooling:

\*\* todo-keeper.md - to-do journal in `.claude/todo/` (one file per item + generated TODO.md via `.claude/tools/todo.js`); modes add (background capture with file:line context) and pick (suggest items for spare time); driven by `/todo`; read-only over source
