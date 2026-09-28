# Climate-driven rooftop solar adoption alleviates rural energy poverty

Code and accompanying non-identifying source data for reproducing the figures and tables in the main text and Supplementary Information.

**Authors:** Shunlin Jin, Xianling Long, Yana Jin, Weidong Wang, and Shiqiu Zhang  
**Corresponding authors:** Xianling Long and Yana Jin

The complete workflow generates **6 main manuscript figures, 27 Supplementary Figures and 35 Supplementary Tables**. Figures are saved as PDF and PNG files. Tables are exported as CSV files with their English titles and notes.

## Reproducible Run in Code Ocean

Click **Reproducible Run** in the study's capsule. The `/code/run` entry point executes the complete workflow using the included data, without an interactive session or manual data selection.

A successful run ends with:

```text
Main manuscript figures (1-6): SUCCESS
Supplementary figures (1-27): SUCCESS
Supplementary tables (1-35): SUCCESS

Reproduction completed successfully.
All expected manuscript and Supplementary Information outputs were generated.
Results are available in /results.
```

Open **Results** to view or download the outputs:

| Directory or file | Contents |
| --- | --- |
| `/results/figures/` | Main figures, PDF and PNG |
| `/results/figures_appendix/` | Supplementary Figures, PDF and PNG |
| `/results/tables_appendix/` | Supplementary Tables, CSV, and English table notes |
| `/results/log/` | Individual script logs |
| `/results/reproduction_manifest.json` | Output inventory, checksums, software versions and runtime |

The workflow runs on a standard CPU and does not require a GPU or other specialized hardware. A complete run with the included data took approximately **2.5 minutes** in local tests on Ubuntu 24.04.3 LTS (x86_64), using Python 3.12.14 and R 4.3.3. Allow a few minutes once the computational environment is ready; runtime varies with available resources. The capsule environment supplies its dependencies automatically, so readers do not need to install them manually before a Reproducible Run.

## Local reproduction

Install Python 3.10 or newer and R 4.3 or newer. From the package root, which contains both `code/` and `data/`, install the dependencies once:

```bash
python -m pip install -r requirements.txt
Rscript code/setup.R
```

**Estimated installation time:** allow **10–30 minutes** to download and install dependencies on a typical desktop with Python and R already installed. Network speed and compilation of R packages can increase setup time.

Run the complete workflow:

```bash
python code/run_public.py
```

Outputs are written to `output/`, with the same figure, table and log subdirectories shown above. Rerunning replaces generated figure and table folders and leaves source data unchanged. On systems where Python is invoked as `python3`, use that command instead of `python`.

Software requirements, tested versions and local troubleshooting are documented in `ENVIRONMENT.md`.

## Scripts and source data

| Location | Contents |
| --- | --- |
| `code/main/` | Scripts for Figures 1-6 |
| `code/supplementary/` | Scripts for Supplementary Figures 1-27 and table export |
| `data/non-confidential/aggregate_main/` | Main-figure source data |
| `data/non-confidential/aggregate_supplementary/` | Supplementary figure and table source data |

Table 3 has separate Panel A and Panel B CSV files; these constitute one table. Multipart tables identify panels in the `panel` column. `Supplementary_Table_Notes.md` in the table output folder contains the corresponding titles and notes.

See `OUTPUT_INDEX.md` for the correspondence between manuscript outputs, scripts and inputs, and `SOURCE_DATA.md` for units and field conventions. The plotting and table-export scripts can also use source files following the same schemas. Keep the input filenames, required columns and `aggregate_main/` and `aggregate_supplementary/` subdirectories, and supply their parent directory with `--data-dir`:

```bash
python code/run_public.py --data-dir path/to/non-confidential --output-dir custom_output
```

## Source-code repositories

- [Public source repository](https://github.com/ShunlinJIN/Climate-solar-rooftop-adoption)
- [Anonymous review mirror](https://anonymous.4open.science/r/Climate-solar-27C0/)

## Data availability

All source-data inputs used by the public workflow are included under `data/non-confidential/`. Data access arrangements for the underlying records are described in `DATA_AVAILABILITY.md`.

## License

The public source code is released under the MIT License; see `LICENSE`. The accompanying non-identifying source data are released under CC BY 4.0; see `DATA_LICENSE.md`.
