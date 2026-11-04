---
name: sql-applied-state-goes-stale
description: Spec "SQL NNNN not applied" limitations go stale when the user applies scripts outside a build session; check ledger.json on every data-lineage/data sync
metadata:
  type: feedback
---

Spec limitation lines like "SQL 0074 is not applied to any database" (mappings.md §5 L3, appendix rows, index §6/§7) went stale within a day: the user applied 0074 to dm-dev-za-db2 between sessions, and three documents plus the index still said "not applied" (found in the 2026-09-29 mapping-remove-status sync).

**Why:** `.claude/sql/ledger.json` `applied` map is the source of truth and changes without any session log; spec text copies of it drift silently.
**How to apply:** in every sync, grep the touched documents and the module index for script numbers / "not applied" and compare against the ledger's `applied` map. Word the spec as "applied on <db>, the only database the ledger tracks" rather than "any database", and keep applied-state detail to one L-limitation plus one appendix row, linking from other documents. See [[subagent-return-checks]].
