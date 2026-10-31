# Rooftop solar responds to extreme heat and reduces energy poverty among rural households

`code/regression/` contains the main regression estimation scripts. These require the underlying analysis datasets and are not executed by the default figure-and-table reproduction workflow.

Processed county-level daily, monthly and hourly supporting datasets: [County_Inputs.zip](https://github.com/ShunlinJIN/Climate-solar-rooftop-adoption/releases/download/data-20261031/County_Inputs.zip). Extract the ZIP into the repository root to create `data/county_inputs/`. These files are distributed as Release assets rather than ordinary Git files.

**Authors:** Shunlin Jin, Xianling Long, Yana Jin, Weidong Wang, and Shiqiu Zhang  
**Corresponding authors:** Xianling Long and Yana Jin

The workflow generates **6 main figures, 27 Supplementary Figures and 35 Supplementary Tables**. All figures are exported as PDF and PNG. Figures 1, 2, 3, 4 and 5 and Supplementary Figures 7 and 19 also have SVG exports. Table outputs are CSV files with English titles and notes.

## Reproducible Run

Configure `environment/postInstall` in the capsule's Environment editor, and set `/code/run` as the run file. Click **Reproducible Run** after the environment is built. The workflow reads `/data/non-confidential/` and writes all outputs to `/results/` without interactive input or data downloads.

| Results location | Contents |
| --- | --- |
| `/results/figures/` | Main figures |
| `/results/figures_appendix/` | Supplementary Figures |
| `/results/tables_appendix/` | Table CSVs and English titles and notes |
| `/results/log/` | Individual script logs |
| `/results/reproduction_manifest.json` | Software versions, runtime and output checksums |

A complete successful run ends with `Reproduction completed successfully.` The workflow uses a standard CPU; no GPU is required. Dependency setup and tested versions are described in `ENVIRONMENT.md`.

## Local execution of an exported capsule

From the exported capsule root containing `code/` and `data/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r code/requirements.txt
Rscript code/setup.R
python code/run_public.py
```

Local outputs are written to `output/`. On Windows, use `.venv\Scripts\Activate.ps1` to activate the virtual environment, or invoke its Python executable directly. Rscript can be selected through the `RSCRIPT` environment variable.

## Scripts and source data

### One file per figure

The `code/main/` directory contains exactly six complete scripts and no subdirectories:

| Figure | Script |
| --- | --- |
| 1 | `Figure_1.R` |
| 2 | `Figure_2.R` |
| 3 | `Figure_3.py` |
| 4 | `Figure_4.R` |
| 5 | `Figure_5.py` |
| 6 | `Figure_6.R` |

`code/supplementary/` contains `Supp_Fig_01` through `Supp_Fig_27`, with
`.py` or `.R` according to the interpreter. Every figure has its own complete
script, including its figure-specific functions. Figures 25 and 26 have separate
scripts. `Supplementary_Tables.py` exports all 35 supplementary tables and notes.
There are no figure-specific subdirectories or separate helper scripts in either
figure directory. Source data remain in the existing `data/non-confidential/`
directories and are not embedded in the code.

| Location | Contents |
| --- | --- |
| `code/main/` | Main-figure scripts |
| `code/supplementary/` | Supplementary-figure scripts and table export |
| `code/regression/` | Main-text regression estimation code |
| `data/non-confidential/aggregate_main/` | Main-figure source data |
| `data/non-confidential/aggregate_supplementary/` | Supplementary figure and table source data |

Table 3 has separate Panel A and Panel B CSV files. Other multipart tables identify their panels within a single CSV. `supplementary_table_notes.json` supplies the exported titles and notes.

Supplementary Table 17 Panel F uses the same reported current-income sample as Tables 13 and 29 (989 adopters; 492 below and 497 at or above RMB 15,960 per person per year, excluding RRPV revenue). `financing_current_income_counts.csv` supplies its aggregate numerators and denominators. The other financing panels retain their own stated samples.

The runner validates current figure/table numbering, Panel F denominators and proportions, and key shared source values before creating outputs. This input-only check can also be run without R:

```bash
python /code/validate_public_inputs.py --data-dir /data/non-confidential
```

See `OUTPUT_INDEX.md` for the output-to-input mapping. Data access arrangements are described in `DATA_AVAILABILITY.md`.

## Repositories

- [Public source repository](https://github.com/ShunlinJIN/Climate-solar-rooftop-adoption)
- [Anonymous review mirror](https://anonymous.4open.science/r/Climate-solar-27C0/)

## License

Source code is released under the MIT License (`LICENSE`). The accompanying non-identifying source data are released under CC BY 4.0 (`DATA_LICENSE.md`).

Figure 6 retains the full adopter labels with smaller panel-c axis text and also exports `Figure_6.svg`.
