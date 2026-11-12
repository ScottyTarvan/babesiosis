"""SV-06a database writer (way A of /experiments/run-instructions.md).

Reads out/db/SV-06-01-transfer-grid.json and writes the one dbo.experiment row and its dbo.experiment_result rows
in one transaction: update-or-insert the experiment by code, delete its result rows, insert the new ones.
Touches no other code. The connection string is read at run time from
/console/Babesiosis.Console/appsettings.Local.json (ConnectionStrings:Babesiosis) and converted for ODBC Driver 18.
Usage: python -I scripts/write_db.py [--dry-run]
"""
import json, os, sys
from datetime import datetime

import pyodbc

ROOT = r"C:\Workspaces\Babesiosis"
PKG = os.path.join(ROOT, "experiments", "SV-06", "a")
CODES = ["SV-06-01-transfer-grid"]


def odbc_conn_str():
    cs = json.load(open(os.path.join(ROOT, "console", "Babesiosis.Console", "appsettings.Local.json"), encoding="utf-8"))["ConnectionStrings"]["Babesiosis"]
    parts = dict(p.split("=", 1) for p in cs.split(";") if "=" in p)
    norm = {k.strip().lower(): v.strip() for k, v in parts.items()}
    out = ["Driver={ODBC Driver 18 for SQL Server}", f"Server={norm.get('server') or norm.get('data source')}",
           f"Database={norm.get('database') or norm.get('initial catalog')}"]
    if norm.get("integrated security", "").lower() in ("true", "sspi", "yes"):
        out.append("Trusted_Connection=yes")
    else:
        out += [f"UID={norm.get('user id') or norm.get('uid')}", f"PWD={norm.get('password') or norm.get('pwd')}"]
    out.append("Encrypt=" + ("yes" if norm.get("encrypt", "true").lower() in ("true", "yes", "mandatory") else "no"))
    if norm.get("trustservercertificate", "").lower() in ("true", "yes"):
        out.append("TrustServerCertificate=yes")
    return ";".join(out)


def write(cur, load):
    e = load["experiment"]
    for k in ("code", "name", "method"):
        assert e[k], k
    assert len(e["code"]) <= 60 and len(e["name"]) <= 200 and len(e["method"]) <= 50
    kinds = [r["kind"] for r in load["results"]]
    assert len(kinds) == len(set(kinds)) and "interpretation" in kinds
    run_at = datetime.strptime(e["run_utc"], "%Y-%m-%dT%H:%M:%SZ")
    params = json.dumps(e["parameters"], ensure_ascii=False, allow_nan=False)
    cur.execute("SELECT experiment_id FROM dbo.experiment WHERE experiment_code = ?", e["code"])
    row = cur.fetchone()
    vals = (e["name"], e["description"], e["method"], params, e["script"], e["script_version"], run_at,
            e["n_subjects"], e["n_variables"], e["n_tests"], e["summary"])
    if row:
        eid = row[0]
        cur.execute("""UPDATE dbo.experiment SET name=?, description=?, method=?, dataset_id=NULL, parameters=CAST(? AS NVARCHAR(MAX)), script=?, script_version=?,
                       run_at=?, n_subjects=?, n_variables=?, n_tests=?, summary=?, loaded_at=SYSUTCDATETIME() WHERE experiment_id=?""", *vals, eid)
    else:
        cur.execute("""INSERT INTO dbo.experiment (experiment_code, name, description, method, dataset_id, parameters, script, script_version,
                       run_at, n_subjects, n_variables, n_tests, summary) OUTPUT INSERTED.experiment_id VALUES (?,?,?,?,NULL,CAST(? AS NVARCHAR(MAX)),?,?,?,?,?,?,?)""",
                    e["code"], *vals)
        eid = cur.fetchone()[0]
    cur.execute("DELETE FROM dbo.experiment_result WHERE experiment_id = ?", eid)
    for r in load["results"]:
        payload = json.dumps(r["payload"], ensure_ascii=False, allow_nan=False)
        assert payload[0] in "{[" and len(r["kind"]) <= 40 and len(r["title"]) <= 200
        cur.execute("INSERT INTO dbo.experiment_result (experiment_id, result_kind, title, payload, sort_order) VALUES (?,?,?,CAST(? AS NVARCHAR(MAX)),?)",
                    eid, r["kind"], r["title"], payload, r["sort_order"])
    return eid, len(load["results"])


def main():
    dry = "--dry-run" in sys.argv
    loads = [json.load(open(os.path.join(PKG, "out", "db", f"{c}.json"), encoding="utf-8")) for c in CODES]
    total = sum(len(json.dumps(r["payload"])) for l in loads for r in l["results"])
    print(f"payload bytes: {total}")
    assert total < 1_000_000
    conn = pyodbc.connect(odbc_conn_str(), autocommit=False)
    try:
        for load in loads:
            cur = conn.cursor()
            eid, n = write(cur, load)
            if dry:
                conn.rollback(); print(f"dry run: {load['experiment']['code']} id {eid}, {n} results (rolled back)")
            else:
                conn.commit(); print(f"written: {load['experiment']['code']} id {eid}, {n} results")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
