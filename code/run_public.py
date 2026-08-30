#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE = ROOT / "code"
DATA = ROOT / "data" / "non-confidential"
OUTPUT = ROOT / "output"
RUNTIME = ROOT / ".runtime"

MAIN_CODE = CODE / "main"
SUPP_CODE = CODE / "supplementary"
MAIN_DATA = DATA / "aggregate_main"
SUPP_DATA = DATA / "aggregate_supplementary"

MAIN_OUT = OUTPUT / "figures"
SUPP_OUT = OUTPUT / "figures_appendix"
TABLE_OUT = OUTPUT / "tables_appendix"
LOG_OUT = OUTPUT / "log"


def require(path: Path, label: str | None = None) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Required {label or 'path'} not found: {path}")


def reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_contents(src: Path, dst: Path) -> None:
    require(src)
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


def rscript_executable() -> str:
    env = os.environ.get("RSCRIPT", "").strip()
    if env:
        p = Path(env)
        if not p.exists():
            raise FileNotFoundError(
                f"RSCRIPT environment variable points to a missing file: {p}"
            )
        return str(p)

    exe = shutil.which("Rscript")
    if exe:
        return exe

    raise RuntimeError("Rscript was not found in the execution environment.")


def run_script(path: Path, cwd: Path, rscript: str) -> None:
    suffix = path.suffix.lower()

    if suffix == ".r":
        cmd = [rscript, path.name]
    elif suffix == ".py":
        cmd = [sys.executable, path.name]
    else:
        raise RuntimeError(f"Unsupported public script type: {path}")

    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if proc.returncode != 0:
        print(f"\nFAILED: {path.name}", flush=True)
        if proc.stdout.strip():
            print(proc.stdout.rstrip(), flush=True)
        if proc.stderr.strip():
            print(proc.stderr.rstrip(), file=sys.stderr, flush=True)
        raise RuntimeError(
            f"Public reproduction step failed with exit code "
            f"{proc.returncode}: {path.name}"
        )


def discover_supplementary_scripts(code_dir: Path) -> list[Path]:
    candidates: list[tuple[int, set[int], Path]] = []

    for p in code_dir.iterdir():
        if not p.is_file() or p.suffix.lower() not in {".r", ".py"}:
            continue
        if p.name == "reproduce_supplementary_tables.py":
            continue

        m_range = re.match(
            r"^Supp_Figs_(\d{1,2})_(\d{1,2})(?:_|\.)(.*)\.(R|r|py)$",
            p.name,
        )
        m_single = re.match(
            r"^Supp_Fig_(\d{1,2})(?:_|\.)(.*)\.(R|r|py)$",
            p.name,
        )

        covered: set[int] | None = None

        if m_range:
            a, b = int(m_range.group(1)), int(m_range.group(2))
            if 1 <= a <= b <= 27 and b - a <= 10:
                covered = set(range(a, b + 1))
        elif m_single:
            n = int(m_single.group(1))
            if 1 <= n <= 27:
                covered = {n}

        if covered:
            candidates.append((min(covered), covered, p))

    candidates.sort(key=lambda x: (x[0], x[2].name.lower()))

    selected: list[Path] = []
    covered_all: set[int] = set()

    for _, covered, p in candidates:
        if covered - covered_all:
            selected.append(p)
            covered_all |= covered

    missing = sorted(set(range(1, 28)) - covered_all)

    if missing:
        raise RuntimeError(
            "Could not resolve Supplementary Figure scripts for: "
            + ", ".join(map(str, missing))
        )

    return selected


def table_number_from_runtime_name(path: Path) -> int | None:
    m = re.match(r"(?i)^supp_table(\d{2})(?:_|\.|$)", path.name)
    return int(m.group(1)) if m else None


def final_table_name(path: Path) -> str:
    m = re.match(r"(?i)^supp_table(\d{2})(.*)$", path.name)
    if not m:
        return path.name
    return f"Supplementary_Table_{m.group(1)}{m.group(2)}"


def copy_files(files: list[Path], dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for p in files:
        shutil.copy2(p, dest / p.name)


def mirror_to_results() -> None:
    results = Path("/results")

    if not results.exists() or not os.access(results, os.W_OK):
        return

    for child in results.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()

    mapping = {
        MAIN_OUT: results / "figures",
        SUPP_OUT: results / "figures_appendix",
        TABLE_OUT: results / "tables_appendix",
    }

    for src, dst in mapping.items():
        if src.exists():
            shutil.copytree(src, dst)


def main() -> None:
    require(MAIN_CODE, "main-figure code directory")
    require(SUPP_CODE, "supplementary code directory")
    require(MAIN_DATA, "main non-confidential data directory")
    require(SUPP_DATA, "supplementary non-confidential data directory")

    rscript = rscript_executable()

    for p in [MAIN_OUT, SUPP_OUT, TABLE_OUT, LOG_OUT]:
        reset_dir(p)

    reset_dir(RUNTIME)

    main_runtime = RUNTIME / "main"
    supp_runtime = RUNTIME / "supplementary"

    for base in [main_runtime, supp_runtime]:
        (base / "code").mkdir(parents=True, exist_ok=True)
        (base / "data").mkdir(parents=True, exist_ok=True)
        (base / "output").mkdir(parents=True, exist_ok=True)

    copy_contents(MAIN_CODE, main_runtime / "code")
    copy_contents(MAIN_DATA, main_runtime / "data")
    copy_contents(SUPP_CODE, supp_runtime / "code")
    copy_contents(SUPP_DATA, supp_runtime / "data")

    main_scripts = [
        main_runtime / "code" / "Figure_1_plot_only.R",
        main_runtime / "code" / "Figure_2_plot_only.R",
        main_runtime / "code" / "Figure_3_plot_only.R",
        main_runtime / "code" / "Figure_4_plot_only.R",
        main_runtime / "code" / "Figure_5_plot_only.py",
        main_runtime / "code" / "Figure_6_plot_only.R",
    ]

    for p in main_scripts:
        require(p, "main-figure script")

    for p in main_scripts:
        run_script(p, main_runtime / "code", rscript)

    print("Main manuscript figures (1-6): SUCCESS", flush=True)

    supp_scripts = discover_supplementary_scripts(supp_runtime / "code")

    for p in supp_scripts:
        run_script(p, supp_runtime / "code", rscript)

    print("Supplementary figures (1-27): SUCCESS", flush=True)

    table_writer = supp_runtime / "code" / "reproduce_supplementary_tables.py"
    require(table_writer, "supplementary-table reproduction script")
    run_script(table_writer, supp_runtime / "code", rscript)

    main_png = sorted((main_runtime / "output").glob("Figure_*.png"))
    main_pdf = sorted((main_runtime / "output").glob("Figure_*.pdf"))
    supp_png = sorted((supp_runtime / "output").glob("Supplementary_Fig_*.png"))
    supp_pdf = sorted((supp_runtime / "output").glob("Supplementary_Fig_*.pdf"))

    copy_files(main_png + main_pdf, MAIN_OUT)
    copy_files(supp_png + supp_pdf, SUPP_OUT)

    runtime_tables = supp_runtime / "output" / "tables"
    require(runtime_tables, "supplementary-table output directory")

    runtime_table_csvs = sorted(runtime_tables.glob("supp_table*.csv"))

    table_numbers = {
        n
        for p in runtime_table_csvs
        if (n := table_number_from_runtime_name(p)) is not None
    }

    missing_tables = sorted(set(range(1, 36)) - table_numbers)

    if missing_tables:
        raise RuntimeError(
            "Missing Supplementary Table output sets: "
            + ", ".join(map(str, missing_tables))
        )

    if len(table_numbers) != 35:
        raise RuntimeError(
            f"Expected 35 Supplementary Table output sets; "
            f"found {len(table_numbers)}."
        )

    for src in runtime_table_csvs:
        shutil.copy2(src, TABLE_OUT / final_table_name(src))

    table_manifest = runtime_tables / "supplementary_tables_manifest.csv"
    if table_manifest.exists():
        shutil.copy2(table_manifest, TABLE_OUT / table_manifest.name)

    promoted_table_csvs = sorted(TABLE_OUT.glob("Supplementary_Table_*.csv"))

    promoted_table_numbers: set[int] = set()
    for p in promoted_table_csvs:
        m = re.match(r"^Supplementary_Table_(\d{2})", p.name)
        if m:
            promoted_table_numbers.add(int(m.group(1)))

    regenerated = (
        main_png
        + main_pdf
        + supp_png
        + supp_pdf
        + runtime_table_csvs
    )

    zero_byte = [p for p in regenerated if p.stat().st_size == 0]

    ok = (
        len(main_png) == 6
        and len(main_pdf) == 6
        and len(supp_png) == 27
        and len(supp_pdf) == 27
        and len(promoted_table_numbers) == 35
        and not zero_byte
    )

    if not ok:
        raise RuntimeError("Public reproduction completeness check failed.")

    print("Supplementary tables (1-35): SUCCESS", flush=True)

    shutil.rmtree(RUNTIME)
    mirror_to_results()

    print("", flush=True)
    print("Reproduction completed successfully.", flush=True)
    print("All expected manuscript and Supplementary Information outputs "
          "were generated.", flush=True)

    if Path("/results").exists():
        print("Results are available in /results.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("", flush=True)
        print("REPRODUCTION FAILED", flush=True)
        print(str(exc), flush=True)
        raise
