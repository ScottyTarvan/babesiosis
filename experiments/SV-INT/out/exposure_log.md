# Combined exposure log (all packages)

Built by `SV-INT/scripts/build.py` from every package's `exposure.md`. SV-INT itself opened no outcomes file.

| Package | Source file | Entry |
|---|---|---|
| SV-01 | SV-01/exposure.md | 2026-11-12 / shared/tidy/DS05.outcomes.json / 4a86691b3b97aefe846803c6d5784d96b35bd75b4b33d1f74d519d3d8365eba0 / 7c272692530ce89c0857ec971fd9b75578e407e643ce1d85c50a1f7d67d6a98f |
| SV-02 | SV-02/exposure.md | 2026-11-12 / a / none (no dog-level outcomes file). Published aggregate results in `/experiments/SV-G2/associations_v2.csv` / dad666990e2414cc80f49b554eea932a3b92c512d120789a2b7c61edd6f8f46f / The parasitaemia rows were listed before `a/spec.md` was written, to set the eligibility rules; the synthesis is not blind to them |
| SV-02 | SV-02/exposure.md | 2026-11-12 / b / `/experiments/shared/tidy/DS02.outcomes.json` (`habitus_score`; `died` as a plot label only) / 0b44ffb3d1dab6e244c2d6f441a6bd747c890010d8d4009e92b6587bb2ac7724 / Before the spec was written, a format probe printed the outcome definitions and the `died` value of 2 dogs (both 0); no habitus value was seen. That dog 6 died on day 4 was already in `data.md` |
| SV-03 | SV-03/exposure.md | 2026-11-12 / no dog-level outcomes file opened; inputs are published group results (SV-G2/associations_v2.csv, definitions_v2.csv) / spec 25f2cc933b6d7bc93b26ac90a1f973dd6523bc9b37df5f9a6d017ec47718a884 |
| SV-04 | SV-04/exposure.md | 2026-11-12 / shared/tidy/S-CB050.outcomes.json / d2657b5321d1dd8528d8e363a8bf621398df32b538301d68df81976562f2d813 / 22c7da5db7ad2e3ee20189dddf790bb63ae12a5b670baf849c69f9de89914742 |
| SV-04 | SV-04/exposure.md | 2026-11-12 / shared/tidy/S-CB017.outcomes.json / 11f98f2bae04842d46d493e00246d8dc275da2a7bcc307188f8002ead6f4f046 / 22c7da5db7ad2e3ee20189dddf790bb63ae12a5b670baf849c69f9de89914742 |
| SV-05 | SV-05/exposure.md | 2026-11-12 / shared/tidy/S-CB050.outcomes.json / d2657b5321d1dd8528d8e363a8bf621398df32b538301d68df81976562f2d813 / dd68cbd66a738637cead48e9707a08a3c3fec84d5fd0286307d804b475e1782f |
| SV-05 | SV-05/exposure.md | 2026-11-12 / SV-04/out/perturbation.csv (column `severe` = S-CB050 died; read but not used) / 88e1e3c48148d205870d3535545595ae3105c275c4781251a04d2d2db8cfde7b / dd68cbd66a738637cead48e9707a08a3c3fec84d5fd0286307d804b475e1782f |
| SV-06a | SV-06/a/exposure.md | 2026-11-12 / none opened (part a uses no dog-level labels) / 93fc808887e8b5b42ee269ec3851d148553502a6446e2417daad4b860d76b6b2 |
| SV-06b | SV-06/b/exposure.md | 2026-11-12 / shared/tidy/DS07.outcomes.json (sha256 596e092a2b3df0f95057347467d9d48295703a77b0fef62df2391e6db5eb5962) / a23e9c00852211c91cf0b3789b50d1f1fb870579180ab955acb3f71bab6ab8e1 |
| SV-07 | SV-07/exposure.md | 2026-11-12 / /core/data/raw/S-CB050/PMC7040022_supplementaryFiles.zip!Table_1.DOCX (column `Outcome`) / be985d2414d9 / Already seen (death list in data.md). Used only to check that DS04 fatal dogs link to deaths |
| SV-07 | SV-07/exposure.md | 2026-11-12 / /core/data/raw/DS04/* (all infected dogs died) / be985d2414d9 / Outcome fixed by design |
| SV-07 | SV-07/exposure.md | 2026-11-12 / /core/data/raw/DS07/sample_list.xlsx (complicated / uncomplicated lists) / be985d2414d9 / Group lists used as ID lists for the numbering test; no proteome value read |
| SV-08 | SV-08/exposure.md | 2026-11-12 / /experiments/shared/tidy/DS02.outcomes.json (outcome definitions only) / – (before spec) / Format probe: printed the two outcome definitions (`died`, `habitus_score`); no value was printed. That dog 6 died on day 4 was already in data.md. Habitus values were already seen by SV-01 and SV-02b in other packages, not in this one |
| SV-08 | SV-08/exposure.md | 2026-11-12 / /experiments/shared/tidy/DS02.outcomes.json (`habitus_score` values, `original_id`) / e7fdfabd75da / Opened after the spec was hashed; used only for the deterioration day |
| SV-09 | SV-09/exposure.md | 2026-11-12 / shared/tidy/DS05.outcomes.json / 4a86691b3b97aefe846803c6d5784d96b35bd75b4b33d1f74d519d3d8365eba0 / 3f98321b72ecfae1a89a27c8e932118c3b9b4e841144ec8a343515f604118270 |
| SV-09 | SV-09/exposure.md | 2026-11-12 / shared/tidy/S-CB050.outcomes.json / d2657b5321d1dd8528d8e363a8bf621398df32b538301d68df81976562f2d813 / 3f98321b72ecfae1a89a27c8e932118c3b9b4e841144ec8a343515f604118270 |
| SV-09 | SV-09/exposure.md | 2026-11-12 / shared/tidy/S-CB017.outcomes.json / 11f98f2bae04842d46d493e00246d8dc275da2a7bcc307188f8002ead6f4f046 / 3f98321b72ecfae1a89a27c8e932118c3b9b4e841144ec8a343515f604118270 |
| SV-10 | SV-10/exposure.md | 2026-11-12 / none / 37d9c576a99c |
| SV-G1 | SV-G1/exposure.md | 2026-11-12 / shared/tidy/DS02.outcomes.json / – (no outcome lock) / written; death count checked |
| SV-G1 | SV-G1/exposure.md | 2026-11-12 / shared/tidy/DS03.outcomes.json / – / written (empty) |
| SV-G1 | SV-G1/exposure.md | 2026-11-12 / shared/tidy/DS05.outcomes.json / – / written; no label statistic |
| SV-G1 | SV-G1/exposure.md | 2026-11-12 / shared/tidy/S-CB050.outcomes.json / – / written; label counts checked against data.md |
| SV-G1 | SV-G1/exposure.md | 2026-11-12 / shared/tidy/S-CB517.outcomes.json / – / written; label counts checked |
| SV-G1 | SV-G1/exposure.md | 2026-11-12 / shared/tidy/S-CB017.outcomes.json / – / written; label counts checked |
| SV-G1 | SV-G1/exposure.md | 2026-11-12 / shared/tidy/S-CB516.outcomes.json / – / written; label counts checked |
| SV-G1 | SV-G1/exposure.md | 2026-11-12 / shared/tidy/DS07.outcomes.json / – / written; label counts checked |
| SV-G1 | SV-G1/exposure.md | 2026-11-12 / shared/tidy/DS04.outcomes.json / – / written; label counts checked |
| SV-G2 | SV-G2/exposure.md | 2026-11-12 / none: SV-G2 reads published article texts only and opens no dog-level outcomes file / b1b12dafb767 |
