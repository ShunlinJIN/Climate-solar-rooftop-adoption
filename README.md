# Rooftop solar responds to extreme heat and reduces energy poverty among rural households

Code and released non-confidential source data accompanying the paper.

**Authors:** Shunlin Jin, Xianling Long, Yana Jin, Weidong Wang and Shiqiu Zhang  
**Corresponding authors:** Xianling Long and Yana Jin

The public workflow reproduces **6 main figures, 27 Supplementary Figures and 35 Supplementary Tables** from the included processed figure and table inputs. Regression estimation scripts are provided separately in [code/regression](code/regression/README.md); they require the underlying analysis datasets and are not executed by the figure-and-table workflow.

## Run locally

Download or clone this repository. Run the following commands from its root, the folder containing `code/` and `data/`. Install Python 3.10 or newer and R 4.3 or newer first. See [ENVIRONMENT.md](ENVIRONMENT.md) for dependency and Rscript configuration details.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\code\requirements.txt
Rscript .\code\setup.R
.\.venv\Scripts\python.exe .\code\run_public.py
```

### Linux or macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r code/requirements.txt
Rscript code/setup.R
.venv/bin/python code/run_public.py
```

No virtual-environment activation is required for these commands. A completed run ends with `Reproduction completed successfully.` The workflow uses a standard CPU.

| Local output | Contents |
| --- | --- |
| `output/figures/` | Main Figures 1-6 |
| `output/figures_appendix/` | Supplementary Figures 1-27 |
| `output/tables_appendix/` | Supplementary Table CSVs and English titles and notes |
| `output/log/` | Individual script logs |
| `output/reproduction_manifest.json` | Software versions, elapsed time and output checksums for the actual run |

Main Figures 1-6 have PDF, PNG and SVG exports. Supplementary Figures have PDF and PNG exports, with additional SVG exports where implemented. Supplementary Table 3 has separate Panel A and Panel B CSV files, so the 35 tables produce 36 table CSVs.

## Data and code

| Location | Contents |
| --- | --- |
| `code/main/` | One script for each main figure |
| `code/supplementary/` | Supplementary figure scripts and table export |
| `code/regression/` | County, household and rebound regression estimation scripts |
| `data/non-confidential/aggregate_main/` | Included main-figure inputs |
| `data/non-confidential/aggregate_supplementary/` | Included Supplementary Figure and Table inputs |
| `data/county_inputs/` | Additional county datasets after extracting the separate Release download |

The processed daily, monthly and hourly county datasets are distributed as **[County_Inputs.zip](https://github.com/ShunlinJIN/Climate-solar-rooftop-adoption/releases/download/data-20261031/County_Inputs.zip)** in [Release `data-20261031`](https://github.com/ShunlinJIN/Climate-solar-rooftop-adoption/releases/tag/data-20261031). These large files are Release attachments and do not appear in the repository's ordinary `data/` file listing or its automatically generated source-code ZIP. Extract `County_Inputs.zip` into the repository root to create:

- `data/county_inputs/county_daily.parquet`
- `data/county_inputs/county_monthly.parquet`
- `data/county_inputs/county_hourly.parquet`

The default figure-and-table workflow reads `data/non-confidential/` and does not require this additional download. The county files are supporting inputs; access to other underlying records may still be required to re-estimate a model. See [data/README.md](data/README.md) and [DATA_AVAILABILITY.md](DATA_AVAILABILITY.md) for details.

Use `code/run_public.py` as the local entry point. It supplies the temporary data and output paths expected by the individual figure scripts. The [output index](OUTPUT_INDEX.md) maps each result to its script and released inputs.

To check the released figure/table inputs without running R, use the Python executable from the same environment:

```powershell
.\.venv\Scripts\python.exe .\code\validate_public_inputs.py --data-dir .\data\non-confidential
```

On Linux or macOS, the equivalent command is `.venv/bin/python code/validate_public_inputs.py --data-dir data/non-confidential`.

## Code Ocean

A companion capsule is deposited at [Code Ocean](https://codeocean.com/capsule/7877886/tree). Capsule-specific environment-build and run instructions are in [environment/README.md](environment/README.md). Local GitHub runs use the commands and `output/` paths above.

## License and access

See [LICENSE](LICENSE) for the source-code license and [DATA_LICENSE.md](DATA_LICENSE.md) for the released source-data terms. Third-party and restricted records remain subject to their original access and redistribution conditions, as described in [DATA_AVAILABILITY.md](DATA_AVAILABILITY.md).
