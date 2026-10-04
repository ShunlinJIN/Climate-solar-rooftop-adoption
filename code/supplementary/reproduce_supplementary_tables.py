#!/usr/bin/env python3
"""Validate and export Supplementary Tables 1–35 and their notes."""
from pathlib import Path
import csv
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "output" / "tables"
OUT.mkdir(parents=True, exist_ok=True)
REQUIRED_PANELS = {12: set("ABCD"), 27: set("ABC"), 28: set("AB"), 29: set("ABCDE"),
                   31: set("AB"), 32: set("ABCDEFGHI"), 33: set("ABCDE"), 34: set("ABC")}
sources = sorted(DATA.glob("supp_table*.csv"))
tables = {}
for path in sources:
    match = re.fullmatch(r"supp_table(\d{2})(?:_panel[A-Z])?\.csv", path.name)
    if not match:
        raise ValueError(f"Unrecognized table source: {path.name}")
    number = int(match[1])
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    if not reader.fieldnames or not rows:
        raise ValueError(f"Empty table: {path.name}")
    tables.setdefault(number, []).append((path, rows))
if set(tables) != set(range(1, 36)):
    raise ValueError(f"Expected Tables 1–35; found {sorted(tables)}")
for number, expected in REQUIRED_PANELS.items():
    actual = {row["panel"] for _, rows in tables[number] for row in rows}
    if actual != expected:
        raise ValueError(f"Table {number}: expected panels {sorted(expected)}, found {sorted(actual)}")
notes = json.loads((DATA / "supplementary_table_notes.json").read_text(encoding="utf-8"))
if set(notes) != {str(n) for n in range(1,36)}:
    raise ValueError("Table notes do not cover all 35 tables")
manifest = []
note_text = ["# Supplementary table notes", "",
             "CSV files contain the accompanying table source data. Blank cells denote omitted, inapplicable or unreported statistics; they are not zeros.", ""]
for number, entries in sorted(tables.items()):
    for path, rows in entries:
        name = re.sub(r"^supp_table", "Supplementary_Table_", path.name)
        target = OUT / name
        shutil.copy2(path, target)
        manifest.append(dict(table_number=number, title=notes[str(number)]["title"],
                             source_file=path.name, output_file=name, rows=len(rows),
                             sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    note_text.extend(["## " + notes[str(number)]["title"], "",
                      "Source data: " + ", ".join("["+re.sub(r"^supp_table", "Supplementary_Table_", p.name)+"]("+re.sub(r"^supp_table", "Supplementary_Table_", p.name)+")" for p, _ in entries), ""])
    if notes[str(number)]["notes"]:
        note_text.extend([notes[str(number)]["notes"], ""])
(OUT / "Supplementary_Table_Notes.md").write_text("\n".join(note_text), encoding="utf-8")
with (OUT / "supplementary_tables_manifest.csv").open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(manifest[0]))
    writer.writeheader(); writer.writerows(manifest)
print("Supplementary Tables 1–35 and notes exported successfully.")
