# Climate-driven rooftop solar adoption alleviates rural energy poverty

Code and accompanying non-identifying source data for reproducing the figures and tables in the main text and Supplementary Information. The public workflow recreates the reported outputs; it does not re-estimate the empirical models from restricted household-level or provider records.

**Authors:** Shunlin Jin, Xianling Long, Yana Jin, Weidong Wang, and Shiqiu Zhang  
**Corresponding authors:** Xianling Long and Yana Jin

The workflow generates **6 main figures, 27 Supplementary Figures and 35 Supplementary Tables**. All figures are exported as PDF and PNG. Figures 1, 2, 3, 4 and 5 and Supplementary Figures 7 and 19 also have SVG exports. Table outputs are CSV files with English titles and notes.

## Local reproduction

Use Python 3.10 or newer and R 4.3 or newer. Dependency installation requires internet access; figure and table reproduction uses the included inputs without downloading data.

### Windows PowerShell

Open PowerShell in the package root, which contains `code/`, `data/` and `run.ps1`. Install dependencies and run the workflow:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 -Install
```

For subsequent runs, omit `-Install`. The launcher checks R on PATH, registered R installations and standard Windows installation directories. For a custom installation, specify both interpreters:

```powershell
.\run.ps1 -PythonPath "C:\path\to\python.exe" -RscriptPath "C:\path\to\Rscript.exe"
```

### macOS and Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
Rscript code/setup.R
python code/run_public.py
```

Install dependencies once. A later run needs only the last command. `RSCRIPT` can specify a full Rscript path when R is not on PATH. See `ENVIRONMENT.md` for dependencies and tested versions.

## Outputs

Local outputs are saved in `output/`:

| Location | Contents |
| --- | --- |
| `figures/` | Main figures |
| `figures_appendix/` | Supplementary Figures |
| `tables_appendix/` | Supplementary Tables and `Supplementary_Table_Notes.md` |
| `log/` | Individual script logs |
| `reproduction_manifest.json` | Runtime, software versions and output checksums |

A successful run ends with `Reproduction completed successfully.` Rerunning replaces the generated figure and table folders; source data are unchanged. Use a dedicated output directory.

To select a different output location or source-data directory:

```bash
python code/run_public.py --data-dir path/to/non-confidential --output-dir custom_output
```

The source directory must contain the `aggregate_main/` and `aggregate_supplementary/` subdirectories with the documented filenames and columns.

## Scripts and source data

| Location | Contents |
| --- | --- |
| `code/main/` | Main-figure scripts |
| `code/supplementary/` | Supplementary-figure scripts and table export |
| `data/non-confidential/aggregate_main/` | Main-figure source data |
| `data/non-confidential/aggregate_supplementary/` | Supplementary figure and table source data |

Table 3 has separate Panel A and Panel B CSV files. Other multipart tables identify their panels within a single CSV. `supplementary_table_notes.json` supplies the exported titles and notes.

Supplementary Table 17 Panel F uses the same reported current-income sample as Tables 13 and 29 (989 adopters; 492 below and 497 at or above RMB 15,960 per person per year, excluding RRPV revenue). `financing_current_income_counts.csv` supplies its aggregate numerators and denominators. The other financing panels retain their own stated samples.

The runner validates current figure/table numbering, Panel F denominators and proportions, and key shared source values before creating outputs. This input-only check can also be run without R:

```bash
python code/validate_public_inputs.py
```

See `OUTPUT_INDEX.md` for the output-to-input mapping and `SOURCE_DATA.md` for field definitions and units. Data access arrangements are described in `DATA_AVAILABILITY.md`.

## Repositories

- [Public source repository](https://github.com/ShunlinJIN/Climate-solar-rooftop-adoption)
- [Anonymous review mirror](https://anonymous.4open.science/r/Climate-solar-27C0/)

## License

Source code is released under the MIT License (`LICENSE`). The accompanying non-identifying source data are released under CC BY 4.0 (`DATA_LICENSE.md`).
