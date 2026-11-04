---
name: subagent-return-checks
description: spec-code-truth may fail to write its report file and spec-section-writer returns can misstate question IDs; check both cheaply before updating the register
metadata:
  type: feedback
---

Sub-agent hand-backs are not always consistent with what landed on disk.

- spec-code-truth (validation mode) sometimes returns the full report but says it could not write the output path. Write the file yourself from the hand-back (truth/ is in the write set) so the register's report path is real.
- spec-section-writer's revise return can contradict its draft return on question IDs (seen 2026-09-28: help-support.md said PL-32 both "unused" and "contact form placement"). Grep the document's `PL-nn` headings (not a full read) before recording IDs in the register and index.
- Writing a spec/truth file whose text contains source paths via Bash heredoc trips the orchestration-guard hook as an "unorchestrated source edit"; it is a false positive. Prefer the Write tool for those files.
- Validation marks content-authoring conventions (e.g. help "one topic per chunk, ~150 lines") UNVERIFIABLE when stated as behaviour. Don't delete user-sourced rules: have the writer restate them as authoring rules, say "nothing checks them today", and raise an enforcement question; pass 2 then confirms (seen 2026-09-28 help-support sync).

**Why:** the register and index are built from returns only; a wrong ID or missing report path propagates to spec-gate and sync.
**How to apply:** after every writer/validator return in any phase, before register/index updates.
