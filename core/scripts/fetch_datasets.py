"""Download public dataset files with size caps, checksums and provenance.

Input: a JSON spec (list of {"dataset_id", "files": [{"url", "name", "expected_size"?}],
"source_record", "linked_articles"}). Files go to data/raw/<dataset_id>/<name>; original
bytes are kept unmodified. Limits: 50 MB per file and 250 MB in total across
data/raw (existing files count). Files over the cap are skipped and logged, never truncated.

Appends one row per actually-downloaded file to data/manifest.jsonl (url, retrieval
time, size, SHA-256, content type). Skips files already present with a manifest row.

Usage (from canine-babesiosis-review/):
    python -I scripts/fetch_datasets.py data/fetch_spec.json
"""
import datetime as dt
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
MANIFEST = ROOT / "data" / "manifest.jsonl"
FILE_CAP = 50 * 1024 * 1024
TOTAL_CAP = 250 * 1024 * 1024
UA = "canine-babesiosis-review/1.0"


def total_size():
    return sum(p.stat().st_size for p in RAW.rglob("*") if p.is_file())


def main():
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    done = set()
    if MANIFEST.exists():
        for l in open(MANIFEST, encoding="utf-8"):
            r = json.loads(l)
            done.add((r["dataset_id"], r["file"]))
    log = []
    for ds in spec:
        for f in ds["files"]:
            dest = RAW / ds["dataset_id"] / f["name"]
            rel = dest.relative_to(ROOT).as_posix()
            if (ds["dataset_id"], rel) in done and dest.exists():
                continue
            if f.get("expected_size") and f["expected_size"] > FILE_CAP:
                log.append({"dataset_id": ds["dataset_id"], "url": f["url"], "status": "skipped_over_50MB", "expected_size": f["expected_size"]})
                continue
            req = urllib.request.Request(f["url"], headers={"User-Agent": UA})
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    clen = r.headers.get("Content-Length")
                    if clen and int(clen) > FILE_CAP:
                        log.append({"dataset_id": ds["dataset_id"], "url": f["url"], "status": "skipped_over_50MB", "content_length": int(clen)})
                        continue
                    data = r.read(FILE_CAP + 1)
                    ctype = r.headers.get("Content-Type")
                    final_url = r.geturl()
            except Exception as e:  # noqa: BLE001
                log.append({"dataset_id": ds["dataset_id"], "url": f["url"], "status": f"error:{type(e).__name__}:{e}"})
                continue
            if len(data) > FILE_CAP:
                log.append({"dataset_id": ds["dataset_id"], "url": f["url"], "status": "skipped_over_50MB"})
                continue
            if total_size() + len(data) > TOTAL_CAP:
                log.append({"dataset_id": ds["dataset_id"], "url": f["url"], "status": "skipped_total_cap"})
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            row = {"dataset_id": ds["dataset_id"], "file": rel, "url": f["url"], "final_url": final_url,
                   "retrieved_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                   "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "content_type": ctype,
                   "source_record": ds.get("source_record"), "linked_articles": ds.get("linked_articles", [])}
            with open(MANIFEST, "a", encoding="utf-8") as m:
                m.write(json.dumps(row, ensure_ascii=False) + "\n")
            log.append({"dataset_id": ds["dataset_id"], "url": f["url"], "status": "downloaded", "bytes": len(data)})
    out = ROOT / "data" / "fetch_log.jsonl"
    with open(out, "a", encoding="utf-8") as fh:
        for r in log:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    for r in log:
        print(r["dataset_id"], r["status"], r["url"][-60:])
    print(f"total data/raw = {total_size() / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
