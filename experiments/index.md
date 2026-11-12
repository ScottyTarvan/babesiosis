# Experiments index: why do some dogs develop severe babesiosis?

Version 1, 2026-11-12. Runs started on 2026-11-12; the Status column and [ledger.md](ledger.md) say which.

**Research question.** Why do some dogs with babesiosis develop severe disease and others mild disease?

## How to use this folder

1. Read [rules.md](rules.md) once (10 KB). It holds the rules for every agent, the file contracts, the outcome lock and the report template.
2. Open the file of your package from the table below. Its "Read first" line names the parts of [data.md](data.md) (9 KB) that you need.
3. Do not start a package before the packages in its "Depends on" column are done.
4. Read [run-instructions.md](run-instructions.md) (20 KB) before you run a package. It tells you how much freedom you have (your own environment, any language and library), how to put the results in the database, show them in the web app and record the run in [ledger.md](ledger.md).

You do not need the files of other packages. A path that starts with `/` is from the repository root; other path rules are in [rules.md](rules.md).

## Packages

| Package | File | Question in short | Wave | Depends on | Fans out to sub-agents | Effort | Status |
|---|---|---|---|---|---|---|---|
| SV-META | [SV-META-meta-review.md](SV-META-meta-review.md) | The meta experiment: a final review of every result for research leads (severity, mechanism, human parallel) | 4 | All others | Refutation checks | Medium to large | Done |
| SV-G1 | [SV-G1-data-layer.md](SV-G1-data-layer.md) | Tidy files and one variable dictionary for all datasets | 0 | – | One per dataset | Medium | Done |
| SV-G2 | [SV-G2-literature-extraction.md](SV-G2-literature-extraction.md) | Extract markers and host or parasite factors tested against severity from 117 articles | 0 | – | Batches of about 10 articles | Large | Done |
| SV-01 | [SV-01-disease-space.md](SV-01-disease-space.md) | Is "severe" partly "late"? Stage against course in *B. rossi* | 1 | SV-G1 | No | Medium | Done |
| SV-02 | [SV-02-resistance-tolerance.md](SV-02-resistance-tolerance.md) | Parasite load, or damage per parasite? | a: 2, b: 1, c: user decision | a: SV-G2. b: SV-G1. c: SV-02a | By part | Medium, then large | a: Done. b: Done. c: Not started |
| SV-03 | [SV-03-evidence-matrix.md](SV-03-evidence-matrix.md) | Which markers hold up once definitions are aligned and cohorts are counted once? | 2 | SV-G2 | No | Medium | Done |
| SV-04 | [SV-04-il8-conflict.md](SV-04-il8-conflict.md) | Is the IL-8 conflict species, or sampling time and definition? | 1 | SV-G1 | No | Small to medium | Done |
| SV-05 | [SV-05-age-sex.md](SV-05-age-sex.md) | Do age, sex and neuter status change the amount or the form of severe disease? | 1 | SV-G1; step 3 needs SV-04 | No | Small | Done |
| SV-06 | [SV-06-mechanism-transfer.md](SV-06-mechanism-transfer.md) | Which mechanisms from human disease are unmeasured in dogs? Do any show in the proteome? | a: 0, b: 1 | a: –. b: SV-G1 | a: one per mechanism family | Medium | a: Done. b: Done |
| SV-07 | [SV-07-linkage-audit.md](SV-07-linkage-audit.md) | Which dogs appear in more than one file? | 0 | – | No | Small | Done |
| SV-08 | [SV-08-transcriptome-signatures.md](SV-08-transcriptome-signatures.md) | Do human severity signatures appear in the Beagle transcriptome? | 1 | SV-G1 | No | Medium | Done |
| SV-09 | [SV-09-axis-replication.md](SV-09-axis-replication.md) | Is there a second reproducible phenotype axis after anaemia and stage? | 2 | SV-G1, SV-01 | No | Medium | Done |
| SV-10 | [SV-10-new-data-designs.md](SV-10-new-data-designs.md) | Designs that need a new cohort: parasite genotype, host genetics, minimum dataset | 0 | – | One per memo | Medium | Done |
| SV-INT | [SV-INT-integration.md](SV-INT-integration.md) | One report across all packages | 3 | All others | No | Small | Done |

Only the coordinator changes the Status column (Not started, Running, Done, Blocked).

## Why these packages

The earlier experiment programme (git commit `8d4c6d9`, deleted from the working tree on 2026-11-12) asked one kind of question: which marker tracks a severity label. It ran three experiments, all on DS05, which has no outcome label. The clustering result was negative (a continuum that restated anaemia grade).

This programme asks what makes dogs differ. It has five lines of explanation:

| Line | Question | Packages |
|---|---|---|
| Time | Is "severe" partly "late"? | SV-01 |
| Load | Do dogs differ in parasite load (resistance) or in damage per parasite (tolerance)? | SV-02 |
| Host | Do age, sex, neuter status and breed change the amount or the form of severe disease? | SV-05, SV-10 |
| Parasite | Does parasite genotype matter? | SV-10 |
| Response | Is severity the size of the inflammatory response or its balance? Which mechanisms known from human disease are unmeasured in dogs? | SV-04, SV-06, SV-08, SV-09 |

Two packages support all of them: the shared data layer (SV-G1) and the literature extraction (SV-G2, used by SV-02 and SV-03). SV-07 tells the other packages which files share dogs.

Two packages read the others. SV-INT asks if the five lines are supported. SV-META (the meta experiment, added on 2026-11-12) reads every result again for discovery: findings on severity, on a new mechanism, or on a parallel with a human disease, as a ranked list of research leads.

## Waves

```
Wave 0 (start together, no dependencies)
  SV-G1  data layer
  SV-G2  literature extraction
  SV-06a human-to-dog transfer grid
  SV-07  linkage audit
  SV-10  new-data design memos

Wave 1 (after SV-G1)
  SV-01  disease-space maps
  SV-02b reaction norms in the Beagles
  SV-04  IL-8 conflict
  SV-05  age, sex, neuter status        (step 3 waits for SV-04)
  SV-06b candidate tests in the proteome
  SV-08  human signatures in the Beagle transcriptome

Wave 2
  SV-09  axis replication               after SV-G1 and SV-01
  SV-03  evidence matrix                after SV-G2
  SV-02a load-by-outcome synthesis      after SV-G2

Wave 3
  SV-INT integration report             after all others
  SV-02c author data request            user decision, after SV-02a

Wave 4
  SV-META meta experiment               after all others; first on the Experiments screen
```

All packages inside a wave can run at the same time: they share inputs but write to separate working folders. If agents are scarce, the recommended order is SV-G1, SV-G2 (started early because it is the longest), SV-01, SV-04, SV-02a.

## Notes for the coordinator

- Run each package in its own child session on the model Opus 5.5 (`claude-opus-5-5`). While `experiments/` is not committed, the session must share the main checkout: a new worktree would not contain the folder.
- Give each agent the path of this folder, its package ID and the name of its package file. For a sub-agent, name the files it may write.
- A package creates its own working folder (`/experiments/<package ID>/`) when it starts. `shared/` already holds the reader script; SV-G1 owns everything else in it.
- A session that runs in its own git worktree keeps its outputs on its own branch. Ask the user before you merge branches.
- SV-G2 is the longest package. Start it first and let SV-03 and SV-02a wait for it.
- When SV-G2 is done, ask the user whether the new extractions should replace the pilot under `/core/data/severity/`.

## Decisions that are open for the user

- Whether to send the case-numbering query that SV-07 drafts.
- Whether to send the dog-level data request that SV-02c drafts.

## Other files in this folder

| File | Holds |
|---|---|
| [rules.md](rules.md) | Rules, workspace layout and ownership, tidy file contract, outcome lock, statistical conventions, report template, reader notes |
| [run-instructions.md](run-instructions.md) | The steps of a run: claim, environment and analysis, database write, web app view, ledger. The freedom of tools and its limits, the content of the database rows, and the ledger rules |
| [ledger.md](ledger.md) | One row for each experiment that was run: status, database load, view, report |
| [data.md](data.md) | Dataset table, files that must not be pooled, file facts by dataset, linkage facts, literature inputs, what the data cannot support |
| `shared/io/rawio.py` | Standard-library reader for xlsx and docx files (optional) |
