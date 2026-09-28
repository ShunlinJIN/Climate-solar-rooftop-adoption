# Computational environment

The workflow uses Python and R on a standard CPU. No GPU is required.

## Installation

Use Python 3.10 or newer and R 4.3 or newer. Install Python dependencies with `python -m pip install -r requirements.txt` and R dependencies with `Rscript code/setup.R`. The R setup script installs missing packages and updates packages that are below the required versions. Installation requires internet access; the reproduction workflow uses the included data and does not download inputs.

The complete workflow was tested locally on Ubuntu 24.04.3 LTS (x86_64; Linux kernel 6.18.44) with Python 3.12.14 and R 4.3.3. Both the repository entry point and the Code Ocean run script were tested with the same source data. The output reproduction_manifest.json records the operating system, Python and R versions, package versions, elapsed time and output checksums for each completed run. The complete local runs took 148.756 seconds through the repository entry point and 149.338 seconds through the Code Ocean run script, approximately 2.5 minutes in each case. These timings exclude dependency installation.

## Tested Python packages

| Package | Python 3.12.14 | Python 3.10.21 |
| --- | --- | --- |
| numpy | 2.3.5 | 2.2.6 |
| pandas | 2.2.3 | 2.3.3 |
| matplotlib | 3.10.8 | 3.10.9 |
| scipy | 1.17.0 | 1.15.3 |
| geopandas | 1.1.4 | 1.1.4 |
| shapely | 2.1.2 | 2.1.2 |
| pyproj | 3.8.0 | 3.7.1 |
| pyogrio | 0.13.0 | 0.13.0 |

The complete Python/R workflow was tested with Python 3.12.14. All Python plotting and table-export scripts were also tested with Python 3.10.21 after creating a clean environment from a Python installation without pip. `requirements-tested.txt` records the Python 3.12.14 package versions; `requirements.txt` provides compatible ranges for installation. Each completed workflow records its actual versions in `reproduction_manifest.json`.

## Tested R packages

| Package | Version |
| --- | --- |
| cowplot | 1.2.0 |
| data.table | 1.14.10 |
| dplyr | 1.1.4 |
| ggplot2 | 4.0.3 |
| ggprism | 1.0.7 |
| gridExtra | 2.3 |
| patchwork | 1.3.2 |
| readr | 2.1.5 |
| scales | 1.4.0 |
| tidyr | 1.3.1 |

## Execution

The master script runs each plotting script in an isolated temporary working folder and writes final outputs to the selected output directory. It sets a non-interactive Matplotlib backend and limits numerical-library thread counts. Individual script logs and a machine-readable reproduction manifest accompany the outputs.

In Code Ocean, use the supplied `environment/postInstall` to prepare the environment, and set `code/run` as the run file. The setup creates an isolated Python environment at `/opt/climate-solar-venv`, bootstraps pip there and installs the required Python packages. On Ubuntu R images, missing virtual-environment support is installed automatically with `apt-get`. The run file uses this same Python environment. Inputs are read from `/data/non-confidential/`, and generated files are written to `/results/`.

Default fonts are available through R and Matplotlib. Font substitutions across operating systems may slightly change text spacing without changing plotted values.

## Local troubleshooting

If Windows cannot find Rscript, set its installed location in PowerShell before running. For example, with R 4.5.1:

```powershell
$env:RSCRIPT = "C:\Program Files\R\R-4.5.1\bin\Rscript.exe"
& $env:RSCRIPT code/setup.R
python code/run_public.py
```

Use the R version and location installed on your computer. The optional `run.ps1` wrapper accepts `-RscriptPath`.
