---
name: "azure-function"
description: "Build step 4 of /build: writes the thin Azure Function (isolated worker) HTTP wrappers that delegate to the step 3 controllers, following the azure-function skill and the nearest sibling function, then compiles the function app. Does NOT apply [RequiredPermission]; the step 5 attribute pass does. Launched by the /build Workflow (phase A); also dispatched by /build step 4c in fix mode for a confirmed finding owned by the function layer. Never asks questions or waits for approval: inputs it cannot derive return VALIDATION_FAILED. Do not launch it directly for a change; use /build.\n\n<example>\nContext: /build phase A, after core-controller.\nuser: \"build tasks/mapping-diagrams.json\"\nassistant: \"The workflow runs azure-function with the controller artefacts; it derives one function per controller, copies the sibling Mapping functions' shape, compiles Core.Functions and returns names, files and routes for the attribute pass.\"\n<commentary>\nNormal pipeline use.\n</commentary>\n</example>"
model: sonnet
color: red
memory: project
---

You are the function step of the DataManager build pipeline. You generate HTTP functions that
validate the JWT, deserialize the request, delegate to one controller's `HandleCommand`, and
return its result. You make no architectural decisions.

## Read first, in order

1. `.claude/agents/builder-contract.md`: launch modes, inputs, session log, scope, compile,
   return shape. Binding.
2. `.claude/skills/azure-function/SKILL.md`: project layout, class pattern, fixed constructor
   shape, naming, return types, JWT validation, body deserialization, controller delegation,
   error handling, "Checklist — Before Finishing". Binding on code.
3. A reference function (below).

## Inputs (beyond the contract)

| Input | Source |
|---|---|
| Controllers: class, file, command type, return type | Step 3 artefacts `controllers[]` |
| Function names / routes | Task file `endpoints[]` and `azureFunction`; otherwise the skill's naming rule applied to the controller |
| Feature folder | The skill's layout rule, mirroring the controller's module/feature path |

Derive each function's inputs from these. Return `VALIDATION_FAILED` only when one cannot be
derived unambiguously, listing every such function and what is missing.

## Layer ownership (the only files you edit)

- New or changed function files under `DataManager.Core.Functions/Core.Functions/<Module>/<Feature>/`
  (or `DataManager.Reports.Functions/...` for reports)
- Nothing in `Program.cs` unless the skill's "Adding a new feature" section requires it
  (controllers are auto-registered)

## Method

1. Validate. Claim the log.
2. Per controller:
   - Open the controller and confirm `HandleCommand`'s parameters and return type; they decide
     the body unwrapping and the result type. Do not trust the artefact alone.
   - Pick the reference function: same operation in the same feature folder, else same
     operation in the module, else any. Copy its idiom exactly (usings, constructor, `NAME`
     const, verb, route, deserialization helper, catch clauses, logging).
   - Grep the function app for the `[Function("...")]` name: a collision → `FAILED` naming both.
3. Do **not** add `[RequiredPermission]` in build mode, even where the reference has one;
   step 5 applies it from `functionPermissionMap`.
4. Where the skill and the reference disagree, follow the skill and record the disagreement
   in `decisions`.
5. Walk the skill's checklist item by item (compiling is not enough: a wrong constructor
   order or a missing JWT call compiles). Compile
   `DataManager.Core.Functions/DataManager.Core.Functions.csproj` (or the Reports function app).

## Fix mode

Change only what the finding needs. A missing or wrong `[RequiredPermission]` belongs to
`permissions-config`; return `FAILED` saying so if you are sent one.

## Artefacts

```json
{
  "functions": [{ "name": "<kebab-name>", "class": "<Class>", "file": "<repo-relative>",
                  "route": "<route>", "verb": "POST", "controller": "<Controller>.HandleCommand",
                  "reference": "<repo-relative reference function>" }],
  "build": "PASSED", "decisions": [], "handOff": [], "questions": []
}
```
