#!/usr/bin/env python3
"""Reproduce the manuscript figures and supplementary outputs from source data."""
from __future__ import annotations
import argparse
import csv
import hashlib
from importlib.metadata import version, PackageNotFoundError
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from find_rscript import find_rscript
from validate_public_inputs import validate

CODE = Path(__file__).resolve().parent
ROOT = CODE.parent

def read_manifest(name):
    with (CODE / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

def software_versions(rscript):
    python_packages = {}
    for package in ['numpy', 'pandas', 'matplotlib', 'scipy', 'geopandas',
                    'shapely', 'pyproj', 'pyogrio']:
        try:
            python_packages[package] = version(package)
        except PackageNotFoundError:
            python_packages[package] = 'not installed'
    r_code = (
        'p <- c("cowplot", "data.table", "dplyr", "ggplot2", "ggprism", '
        '"gridExtra", "patchwork", "readr", "scales", "tidyr"); '
        'for (x in p) cat(x, as.character(packageVersion(x)), sep="=", fill=TRUE)'
    )
    result = subprocess.run([rscript, '--vanilla', '-e', r_code],
                            text=True, encoding='utf-8', errors='replace',
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    r_packages = dict(line.strip().split('=', 1) for line in result.stdout.splitlines()
                      if '=' in line)
    record = dict(python_packages=python_packages, r_packages=r_packages)
    if result.returncode:
        record['r_package_version_warning'] = result.stderr.strip()
    return record

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data/non-confidential")
    parser.add_argument("--output-dir", type=Path, default=Path("/results") if CODE == Path("/code") else ROOT / "output")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    data = args.data_dir.resolve()
    if output == data or data in output.parents or output == CODE or CODE in output.parents:
        raise ValueError("Choose an output directory outside the code and source-data directories.")
    for name in ["aggregate_main", "aggregate_supplementary"]:
        if not (data / name).is_dir(): raise FileNotFoundError(data / name)
    input_validation = validate(data)
    print("Public input validation: SUCCESS", flush=True)
    rscript = find_rscript()
    output.mkdir(parents=True, exist_ok=True)
    logs = output / "log"; logs.mkdir(exist_ok=True)
    # Only generated output folders are replaced; other files at the output root are preserved.
    for name in ["figures", "figures_appendix", "tables_appendix"]:
        p=output/name
        if p.exists(): shutil.rmtree(p)
        p.mkdir()
    env=os.environ.copy()
    env.update(MPLBACKEND="Agg", PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
    for key in ["OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"]:env[key]="1"
    started=time.monotonic(); steps=[]
    manifests={"main":read_manifest("main_figure_manifest.csv"),"supplementary":read_manifest("supplementary_figure_manifest.csv")}
    with tempfile.TemporaryDirectory(prefix="solar_reproduction_") as temporary:
        runtime=Path(temporary)
        for section, manifest in manifests.items():
            work=runtime/section
            shutil.copytree(CODE/section, work/"code", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            shutil.copytree(data/("aggregate_main" if section=="main" else "aggregate_supplementary"), work/"data")
            (work/"output").mkdir()
            entries=list(manifest)
            if section=="supplementary":entries.append(dict(figure="tables",script="reproduce_supplementary_tables.py",interpreter="python3"))
            for entry in entries:
                script=work/"code"/entry["script"]
                if not script.is_file():raise FileNotFoundError(script)
                command=[rscript if script.suffix.lower()==".r" else sys.executable, str(script)]
                label=("Main Figure " if section=="main" else "Supplementary Figure ")+entry["figure"]
                if entry["figure"]=="tables":label="Supplementary Tables 1–35"
                print("Running "+label+"...",flush=True)
                tick=time.monotonic()
                process=subprocess.run(command,cwd=script.parent,env=env,text=True,encoding="utf-8",errors="replace",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                log=logs/(section+"_"+script.stem+".log")
                log.write_text(process.stdout,encoding="utf-8")
                steps.append(dict(output=label,script=entry["script"],seconds=round(time.monotonic()-tick,3),returncode=process.returncode))
                if process.returncode:
                    raise RuntimeError(f"{label} failed. See {log}\n{process.stdout[-5000:]}")
            target=output/("figures" if section=="main" else "figures_appendix")
            prefix="Figure_" if section=="main" else "Supplementary_Fig_"
            for number in range(1, 7 if section == "main" else 28):
                stem = prefix + (str(number) if section == "main" else f"{number:02d}")
                for suffix in ["png", "pdf", "svg"]:
                    p = work / "output" / (stem + "." + suffix)
                    if p.is_file():
                        shutil.copy2(p, target / p.name)
            if section=="supplementary":
                for p in (work/"output/tables").iterdir():shutil.copy2(p,output/"tables_appendix"/p.name)
            print(("Main manuscript figures (1-6)" if section=="main" else "Supplementary figures (1-27)")+": SUCCESS",flush=True)
    expected=[]
    for folder,prefix,n in [("figures","Figure_",6),("figures_appendix","Supplementary_Fig_",27)]:
        for i in range(1,n+1):
            stem=prefix+(str(i) if n==6 else f"{i:02d}")
            for suffix in ["png","pdf"]:
                p=output/folder/(stem+"."+suffix)
                if not p.exists() or p.stat().st_size==0:raise RuntimeError(f"Missing or empty output: {p}")
                expected.append(p)
    table_files=list((output/"tables_appendix").glob("Supplementary_Table_*.csv"))
    numbers={int(p.name.split("_")[2].split(".")[0]) for p in table_files}
    if numbers != set(range(1,36)):raise RuntimeError("The generated table sets do not cover Tables 1–35")
    expected+=table_files
    for folder in ['figures','figures_appendix']:
        expected += [p for p in (output/folder).iterdir() if p.is_file() and p not in expected]
    expected += [p for p in (output/'tables_appendix').iterdir() if p.is_file() and p not in expected]
    print("Supplementary tables (1-35): SUCCESS",flush=True)
    report=dict(status="success", release="2026-10-09", input_validation=input_validation, python=sys.version.split()[0],platform=platform.platform(),
        software=software_versions(rscript),
        r=subprocess.check_output([rscript,"--version"],text=True,stderr=subprocess.STDOUT).strip(),
        elapsed_seconds=round(time.monotonic()-started,3),main_figures=6,supplementary_figures=27,supplementary_tables=35,
        steps=steps,outputs=[dict(file=str(p.relative_to(output)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(expected)])
    (output/"reproduction_manifest.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("\nReproduction completed successfully.",flush=True)
    print("All expected manuscript and Supplementary Information outputs were generated.",flush=True)
    print(f"Results are available in {output}.",flush=True)

if __name__ == "__main__":
    try: main()
    except Exception as exc:
        print(f"REPRODUCTION FAILED: {exc}",file=sys.stderr,flush=True)
        raise SystemExit(1)
