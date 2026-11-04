---
name: sibling-pointer-goes-stale
description: Level 3 pointer sections that summarise a level 4 split (e.g. mappings.md §3.6 -> mappings-source.md) go stale when the level 4 doc's control/wording changes; grep them on every sync
metadata:
  type: feedback
---

A level 3 feature doc keeps a one-paragraph pointer to its level 4 split (data-lineage `mappings.md` §3.6
"Source tab" summarises `mappings-source.md` §3.1–§3.5). A sync that only revises the level 4 doc leaves the
pointer's wording stale (2026-09-29 source-tab redesign: §3.6 still said "its dropdown" after the control
became a segmented control; the validator only checked the level 4 doc).

**Why:** validators and writers are scoped to one document; nobody else reads the sibling pointer.
**How to apply:** after a level 4 revise, grep the sibling level 3 doc for the changed term (control name,
button name) and apply a one-line companion pointer fix with a change-log row, citing the same validation
report. See [[subagent-return-checks]], [[sql-applied-state-goes-stale]].
