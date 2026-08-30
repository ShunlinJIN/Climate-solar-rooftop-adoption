#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Validate and export all public Supplementary Table CSV sources (1–35).

This script does not estimate models. It validates the public aggregate/table
source files and copies them to output/tables for the replication package.
"""

from pathlib import Path
import csv
import hashlib
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "output" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

LAST5_REQUIRED = {
    7:  {"panel", "row_label", "column_id", "display_value"},
    18: {"panel", "row_label", "column_id", "display_value"},
    25: {"row_label", "column_id", "display_value"},
    28: {"row_label", "column_id", "display_value"},
    32: {"panel", "row_label", "column_id", "display_value"},
}

def table_number(path: Path):
    m = re.match(r"(?i)^supp_table0*(\d+)(?:[^0-9].*)?\.csv$", path.name)
    return int(m.group(1)) if m else None

def nonempty_csv(path: Path):
    if path.stat().st_size <= 0:
        raise RuntimeError(f"Empty CSV: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        first = next(reader, None)
    if not header or first is None:
        raise RuntimeError(f"CSV has no data rows: {path}")
    return set(header)

def sha256(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

files = sorted(DATA.glob("supp_table*.csv"))
by_table = {i: [] for i in range(1, 36)}

for p in files:
    n = table_number(p)
    if n in by_table:
        by_table[n].append(p)

missing = [i for i in range(1, 36) if not by_table[i]]
if missing:
    print("ERROR — missing public table source(s):", ", ".join(map(str, missing)))
    sys.exit(1)

# Targeted schema validation for the five sources added in this patch.
for n, required in LAST5_REQUIRED.items():
    primary = DATA / f"supp_table{n:02d}.csv"
    if not primary.exists():
        print(f"ERROR — required file missing: {primary}")
        sys.exit(1)
    header = nonempty_csv(primary)
    absent = required - header
    if absent:
        print(f"ERROR — Table {n} missing columns: {sorted(absent)}")
        sys.exit(1)

# Validate every source is non-empty.
for n in range(1, 36):
    for p in by_table[n]:
        nonempty_csv(p)

# Clear prior generated table CSVs only.
for p in OUT.glob("*.csv"):
    p.unlink()

manifest_rows = []
copied = 0
for n in range(1, 36):
    for src in by_table[n]:
        dst = OUT / src.name
        shutil.copy2(src, dst)
        copied += 1
        manifest_rows.append({
            "table_number": n,
            "source_file": src.name,
            "output_file": dst.name,
            "bytes": dst.stat().st_size,
            "sha256": sha256(dst),
            "status": "ready",
        })

manifest = OUT / "supplementary_tables_manifest.csv"
with manifest.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(
        f,
        fieldnames=["table_number","source_file","output_file","bytes","sha256","status"]
    )
    w.writeheader()
    w.writerows(manifest_rows)

print("DONE")
print("Completed public table sources validated/exported: 35 / 35")
print(f"Public CSV files copied: {copied}")
print("Remaining table sources: none")
print(f"Output dir: {OUT}")
print(f"Manifest: {manifest}")
