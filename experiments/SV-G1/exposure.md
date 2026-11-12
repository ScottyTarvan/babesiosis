# SV-G1 exposure log

SV-G1 writes the outcomes files, so it reads every label column of the raw files. It computes no association with any label.
The only label-related numbers it computes are counts that `data.md` already states (for example 15 deaths in S-CB050,
18 complicated in S-CB017), used as row-count checks.

| Date | Outcomes file | Spec hash | Use |
|---|---|---|---|
| 2026-11-12 | shared/tidy/DS02.outcomes.json | – (no outcome lock) | written; death count checked |
| 2026-11-12 | shared/tidy/DS03.outcomes.json | – | written (empty) |
| 2026-11-12 | shared/tidy/DS05.outcomes.json | – | written; no label statistic |
| 2026-11-12 | shared/tidy/S-CB050.outcomes.json | – | written; label counts checked against data.md |
| 2026-11-12 | shared/tidy/S-CB517.outcomes.json | – | written; label counts checked |
| 2026-11-12 | shared/tidy/S-CB017.outcomes.json | – | written; label counts checked |
| 2026-11-12 | shared/tidy/S-CB516.outcomes.json | – | written; label counts checked |
| 2026-11-12 | shared/tidy/DS07.outcomes.json | – | written; label counts checked |
| 2026-11-12 | shared/tidy/DS04.outcomes.json | – | written; label counts checked |
