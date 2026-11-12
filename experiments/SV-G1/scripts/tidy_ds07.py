"""Tidy DS07 (serum proteome, TMT sixplex, B. rossi, archived serum; SRC-C; article CB112).

Features: one record per dog. Values are log2(sample / plex standard) for each master protein, computed from the
'Abundances (Grouped)' columns of B_Proteins.txt (the export has no raw per-channel abundances), plus plex and channel.
Outcomes: 'complicated' (0/1, null for controls) from sample_list.xlsx.
"""
import csv
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tidylib import (RAW, built_from_entry, check, dict_row, median, neutral_ids, read_xlsx, var,  # noqa: E402
                     write_dataset)

DS = "DS07"
PROT = RAW / "DS07" / "B_Proteins.txt"
SLIST = RAW / "DS07" / "sample_list.xlsx"
CHANNELS = (127, 128, 129, 130, 131)
UNIT = "log2 ratio to plex standard"


def safe(acc):
    return "p_" + re.sub(r"[^a-z0-9]+", "_", acc.lower()).strip("_")


def main():
    notes = []
    # ---- sample list: groups and TMT layout
    rows = read_xlsx(str(SLIST))["Sheet1"]
    cell = lambda r, j: (r[j].strip() if j < len(r) and r[j] is not None and str(r[j]).strip() else None)  # noqa: E731
    group_of = {}
    raw_ids_with_space = []
    for r in rows:
        for jl, jid in ((0, 1), (3, 4)):
            lab, oid = cell(r, jl), cell(r, jid)
            if lab and oid and lab in ("Controls", "Complicated babesiosis", "Uncomplicated babesiosis"):
                if r[jid] != oid:
                    raw_ids_with_space.append(repr(r[jid]))
                group_of[oid] = lab
    layout = {}   # original id -> (plex number, channel)
    for r in rows:
        plex = cell(r, 10)
        if plex and re.match(r"^B\d+$", plex):
            k = int(plex[1:])
            for c, j in zip(CHANNELS, range(12, 17)):
                oid = cell(r, j)
                if oid:
                    if r[j] != oid:
                        raw_ids_with_space.append(repr(r[j]))
                    if oid in layout:
                        raise SystemExit(f"{oid} appears twice in the TMT layout")
                    layout[oid] = (k, c)
    if set(layout) != set(group_of):
        raise SystemExit(f"layout and group lists differ: {sorted(set(layout) ^ set(group_of))}")

    # ---- proteins
    with open(PROT, encoding="utf-8", newline="") as f:
        prow = list(csv.reader(f, delimiter="\t"))
    head, body = prow[0], prow[1:]
    ix = {c: i for i, c in enumerate(head)}
    masters = [r for r in body if r[ix["Master"]] == "IsMasterProtein"]
    grouped = lambda r, k, c: r[ix[f"Abundances (Grouped): F{k}, {c}"]]  # noqa: E731
    ratio = lambda r, k, c: r[ix[f"Abundance Ratio: (F{k}, {c}) / (F{k}, 126)"]]  # noqa: E731
    is_values = {grouped(r, k, 126) for r in masters for k in range(1, 12)} - {""}

    variables = [var("plex", "TMT plex", "sample_list.xlsx TMT layout (B1-B11) = F1-F11 in B_Proteins.txt"),
                 var("channel", "TMT channel", "sample_list.xlsx TMT layout (127-131)")]
    drows = [dict_row("plex", DS, "sample_list.xlsx col 10", "TMT plex", "", "B1-B11; equals PD fraction F1-F11."),
             dict_row("channel", DS, "sample_list.xlsx row 1, cols 12-16", "TMT channel", "", "Channel 126 is the pooled internal standard of each plex.")]
    gene_count = 0
    loc_count = 0
    two_unique = 0
    pvars = []
    for r in masters:
        acc = r[ix["Accession"]]
        desc = r[ix["Description"]]
        gm = re.search(r"\bGN=(\S+)", desc)
        gene = gm.group(1) if gm else None
        gene_count += gene is not None
        loc_count += bool(gene and gene.startswith("LOC"))
        short = re.sub(r"\s+OS=.*$", "", desc).strip()
        if int(r[ix["# Unique Peptides"]] or 0) >= 2:
            two_unique += 1
        name = safe(acc)
        orig = f"{acc} | gene {gene or 'none'} | {short}"
        pvars.append((name, r))
        variables.append(var(name, UNIT, orig))
        drows.append(dict_row(name, DS, f"Abundances (Grouped): F*, 127-131 / F*, 126; accession {acc}", UNIT,
                              "log2(sample grouped abundance / channel-126 grouped abundance of the same plex)",
                              f"Gene {gene or 'none (no GN= in description)'}; {short}; unique peptides {r[ix['# Unique Peptides']]}."))

    # ---- records
    ids = neutral_ids(DS, sorted(layout))
    records = []
    n_cells = n_null = 0
    agree = disagree = placeholder = 0
    max_dev = 0.0
    nonpos = 0
    for oid in sorted(layout, key=lambda o: ids[o]):
        k, c = layout[oid]
        vals = {"plex": f"B{k}", "channel": c}
        for name, r in pvars:
            a, s = grouped(r, k, c), grouped(r, k, 126)
            v = None
            if a and s:
                fa, fs = float(a), float(s)
                if fa > 0 and fs > 0:
                    v = round(math.log2(fa / fs), 6)
                else:
                    nonpos += 1
            q = ratio(r, k, c)
            if q and v is not None:
                dev = abs(v - math.log2(float(q)))
                max_dev = max(max_dev, dev)
                if dev < 0.01:
                    agree += 1
                else:
                    disagree += 1
            elif q and v is None:
                if q == "0.010":
                    placeholder += 1
                else:
                    disagree += 1
            vals[name] = v
            n_cells += 1
            n_null += v is None
        group = "control" if group_of[oid] == "Controls" else "infected"
        records.append({"dog_id": ids[oid], "group": group, "timepoint": "single" if group == "control" else "admission",
                        "day": None, "values": vals, "censored": {}})

    # unused channels of plex 11
    used11 = {c for (k, c) in layout.values() if k == 11}
    unused11 = [c for c in CHANNELS if c not in used11]
    spurious = sum(1 for r in masters for c in unused11 if grouped(r, 11, c))
    per_dog_n = [sum(1 for n, _ in pvars if rec["values"][n] is not None) for rec in records]
    per_protein_n = {n: sum(1 for rec in records if rec["values"][n] is not None) for n, _ in pvars}

    notes += [
        f"sample_list.xlsx: group lists in columns 0-1 (controls, uncomplicated) and 3-4 (complicated); TMT layout in columns "
        f"10-16 (plexes B1-B11, channel 126 = pooled internal standard 'IS1'-'IS11'). {len(layout)} dogs; every dog in the group "
        "lists is in the layout once and vice versa.",
        f"IDs with leading/trailing spaces were stripped: {', '.join(sorted(set(raw_ids_with_space)))}.",
        "Plex Bk in sample_list.xlsx is taken to be fraction Fk in B_Proteins.txt (same numbering, 11 of each; plex B11 holds "
        "only 2 samples). The file does not state this mapping explicitly.",
        f"B_Proteins.txt has {len(body)} protein rows; only rows with Master = 'IsMasterProtein' are used ({len(masters)} "
        "proteins). Candidate and rejected master rows are not used.",
        "Abundance columns: the export has no raw per-channel 'Abundance' columns and no 'Abundances (Normalized)' columns. It has "
        "'Abundances (Grouped)' (66 columns, 6 channels x 11 plexes; channel 126 is exactly "
        f"{', '.join(sorted(is_values))} wherever present, i.e. Proteome Discoverer scaled each plex to its internal standard) and "
        "'Abundance Ratio' (55 columns, sample / channel 126). Values here are log2(grouped abundance of the dog's channel / "
        "grouped abundance of channel 126 of the same plex), computed in this script. Because the grouped abundances are already "
        "scaled to the standard, this equals the log2 of PD's Abundance Ratio: "
        f"{agree} cells agree within 0.01 log2 units (max difference {max_dev:.4f}, from rounding to 1 decimal), {disagree} disagree.",
        f"'Abundance Ratio' has the value 0.010 in {placeholder} cells where the dog's grouped abundance is empty; this is Proteome "
        "Discoverer's minimum-ratio placeholder for a missing channel, not a measurement. Those cells are null.",
        f"Missing values are null: {n_null} of {n_cells} protein x dog cells ({100 * n_null / n_cells:.1f}%). The gaps follow the "
        "plex: a protein missing in a plex's standard (channel 126) is missing for all dogs of that plex. Proteins observed per dog: "
        f"median {median(per_dog_n)}, range {min(per_dog_n)}-{max(per_dog_n)}. Proteins observed in all {len(records)} dogs: "
        f"{sum(1 for v in per_protein_n.values() if v == len(records))}; in none: {sum(1 for v in per_protein_n.values() if v == 0)}.",
        f"Plex B11 channels {', '.join(map(str, unused11))} hold no sample but carry {spurious} non-empty grouped abundances "
        "(spurious signal). They are not read.",
        f"{gene_count} of {len(masters)} master proteins carry a gene symbol (GN= in the description); the other "
        f"{len(masters) - gene_count} have only a description (many 'Uncharacterized protein'). Of the gene symbols, "
        f"{loc_count} are 'LOC' placeholders. data.md gives 163 with a gene symbol; no count tried here reproduces 163 (see the "
        "checks file). The variable's 'original' field holds accession | gene | description.",
        f"{two_unique} master proteins have at least 2 unique peptides (the article's reporting rule); all {len(masters)} master "
        "proteins are kept, filter on the dictionary note if needed.",
        "Variable names are p_<UniProt accession> in lower case with non-alphanumerics replaced by '_'.",
        "Controls (IDs ending in 'z') are group 'control', timepoint 'single'; infected dogs are timepoint 'admission' (archived "
        "serum; the timing relative to treatment is not in the files). The complicated/uncomplicated label is in the outcomes file only.",
        "The pooled standard contains serum of all dogs, so the ratios are slightly self-referential (record).",
        "No covariates (age, sex, breed, clinical pathology) are in the files.",
    ]

    features = {"dataset_id": DS, "independent_source": "SRC-C", "species": "B. rossi",
                "built_from": [built_from_entry(PROT), built_from_entry(SLIST)],
                "variables": variables, "records": records, "cleaning_notes": notes}

    definition = ("Authors' class (CB112, from the earlier Onderstepoort criteria): complicated if the dog collapsed, had cerebral "
                  "signs (seizures, coma) or died within 24 h of admission, or met any clinical-pathology criterion (haematocrit "
                  "< 0.15 or > 0.5 L/L, urea > 13 mmol/L, creatinine > 120 umol/L, total bilirubin > 30 umol/L, glucose < 3.3 "
                  "mmol/L, lactate > 5 mmol/L, band neutrophils > 1.5 x10^9/L); uncomplicated if none. Null for healthy controls. "
                  "The defining variables are not in the files.")
    orecs = []
    for oid in sorted(layout, key=lambda o: ids[o]):
        g = group_of[oid]
        orecs.append({"dog_id": ids[oid], "original_id": oid,
                      "values": {"complicated": None if g == "Controls" else int(g == "Complicated babesiosis")}})
    outcomes = {"dataset_id": DS,
                "outcomes": [{"name": "complicated", "definition": definition, "includes_euthanasia": False}],
                "records": orecs}

    nsamp = len(records)
    cnt = lambda lab: sum(1 for o in layout if group_of[o] == lab)  # noqa: E731
    checks_list = [
        check("dogs", nsamp, 52, source="data.md; CB112 note: 52 dogs"),
        check("controls", cnt("Controls"), 20, source="data.md; CB112 note: 20 healthy"),
        check("uncomplicated", cnt("Uncomplicated babesiosis"), 18, source="data.md; CB112 note: 18 uncomplicated"),
        check("complicated", cnt("Complicated babesiosis"), 14, source="data.md; CB112 note: 14 complicated"),
        check("infected", cnt("Complicated babesiosis") + cnt("Uncomplicated babesiosis"), 32, source="CB112 full text: 32 infected"),
        check("master proteins with >= 2 unique peptides", two_unique, 128,
              source="CB112 full text: 128 proteins identified and quantified (>= 2 unique peptides, 1% FDR)"),
        check("master proteins", len(masters), 224, source="DS07 record: 224 IsMasterProtein rows"),
        check("master proteins with a gene symbol", gene_count, 163,
              source=f"data.md: 163 master proteins carry a gene symbol. Observed: {gene_count} with GN= ({loc_count} of them LOC), "
                     f"{gene_count - loc_count} non-LOC; none of these counts gives 163"),
        check("percent empty protein x sample cells (52 sample channels)", round(100 * n_null / n_cells, 1), 31.1, tol=0.05,
              source="DS07 record: 31.1% in the 52 sample channels"),
        check("plex B11 samples", len(used11), 2, source="data.md: plex B11 has 2 samples"),
        check("computed log2 ratio vs PD Abundance Ratio: disagreements", disagree, 0, source="internal consistency"),
        check("median proteins detected per sample within the record's 149-158",
              149 <= median(per_dog_n) <= 158, True, source="DS07 record: median 149-158 proteins detected per sample"),
    ]
    checks = {"dataset_id": DS, "checks": checks_list, "n_dogs": nsamp, "n_records": nsamp,
              "abundance_columns_used": "Abundances (Grouped): Fk, 127-131 and Fk, 126 (log2 of their ratio)"}
    write_dataset(features, outcomes, drows, checks)


if __name__ == "__main__":
    main()
