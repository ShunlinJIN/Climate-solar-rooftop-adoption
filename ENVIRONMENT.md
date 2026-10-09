# Computational environment

The public workflow uses Python and R on a standard CPU. No GPU is required.

## Dependencies

Use Python 3.10 or newer and R 4.3 or newer. `requirements.txt` lists compatible Python package ranges, and `code/setup.R` installs missing R packages or versions below the required minimum. The runtime dependency requirements and Code Ocean post-install configuration are unchanged. Installation time depends on network speed and whether R dependencies must be compiled.

## Validation scope

The input-validation script, all 16 Python-based figures, and the export of all 35 Supplementary Tables (36 CSV files because Table 3 has two files) were executed with Python 3.13.5. Rscript was unavailable in this validation environment: the 17 R-based figures, the complete mixed-language workflow and a hosted Code Ocean Reproducible Run were not executed here. Run the master entry point in the configured Python/R environment to validate the complete package. Its success message is issued only after all required figure and table outputs exist.

`requirements-tested.txt` records the Python packages used in that Python-only validation. It is not a guarantee that these exact versions can be installed with every supported Python version; use `requirements.txt` for other supported environments.

| Python package | Version used |
| --- | --- |
| numpy | 2.3.5 |
| pandas | 2.2.3 |
| matplotlib | 3.10.8 |
| scipy | 1.17.0 |
| geopandas | 1.1.2 |
| shapely | 2.1.2 |
| pyproj | 3.7.2 |
| pyogrio | 0.12.1 |

## R dependencies

`code/setup.R` specifies and checks the minimum versions of cowplot, data.table, dplyr, ggplot2, ggprism, gridExtra, patchwork, readr, scales and tidyr. These requirements are inherited from the existing workflow; no R runtime or R package version was newly validated here.

## Windows

`run.ps1` accepts `-PythonPath`, `-RscriptPath`, `-OutputDir` and `-Install`. Without an R path, it searches PATH, R's Windows registration and standard R installation directories. Direct invocation of `code/run_public.py` uses the same lookup. Set `RSCRIPT` to select a particular installed version.

## Code Ocean

Use the capsule's R base environment with R 4.3 or newer and Python 3.10 or newer. Configure `environment/postInstall` in the Environment editor. It creates `/opt/climate-solar-venv`, including pip, installs Python dependencies and checks R dependencies. The setup does not depend on `/code` or `/data` being mounted during the environment build. An existing successfully built environment can be retained.

Set `/code/run` as the run file. It uses the Python environment created by postInstall, reads `/data/non-confidential/` and writes `/results/`. Dependencies are installed during the build, not during the Reproducible Run.

## Execution and graphics

The master workflow validates the released input structure before running plots, uses temporary working directories, a non-interactive Matplotlib backend and one numerical-library thread per plotting process. It checks that all expected PNG, PDF and table outputs exist before reporting success. Logs and the reproduction manifest record the actual run.

Cairo support in R is required by the R graphics workflow. Font substitutions across operating systems can change text spacing without changing plotted values. Figure and table reproduction uses the included aggregate inputs, not restricted household-level records.
