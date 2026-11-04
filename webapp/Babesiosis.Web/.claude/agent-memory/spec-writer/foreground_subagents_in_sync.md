---
name: foreground-subagents-in-sync
description: Launch spec-code-truth and spec-section-writer with run_in_background false in sync/drift; a background launch lets the run hand back before verdicts arrive
metadata:
  type: feedback
---

Launch every validator and writer in sync and drift phases with `run_in_background: false`, parallel in one message.

**Why:** 2026-10-10 mapping-source-field-description sync. The validators went out in the background, and the harness forced a hand-back before they returned. The coordinator then had to re-launch the whole sync, and the second run's reports overwrote the first run's at the same paths.
**How to apply:** for every Agent call in phases 2-4, 7a, 8 and 9, set run_in_background false. Never end a turn just to wait. See [[subagent-return-checks]].
