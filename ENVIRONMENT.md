# Computational environment

The public workflow uses Python and R on a standard CPU. No GPU is required.

## Dependencies

Use Python 3.10 or newer and R 4.3 or newer. `requirements.txt` lists compatible Python package ranges, and `code/setup.R` installs missing R packages or versions below the required minimum. The setup script checks installed package metadata before loading packages. Allow approximately 10–30 minutes for installation; network speed and source compilation can extend this.

The complete workflow was tested on Linux-6.18.44-x86_64-with-glibc2.39 with Python 3.12.14 and Rscript (R) version 4.4.3 (2025-02-28). It generated all 6 main figures, 27 Supplementary Figures and 35 Supplementary Tables in 137.1 seconds. This time excludes dependency installation and varies with available resources.

The Code Ocean postInstall setup was tested in a fresh local Python virtual environment. Code Ocean's hosted environment build and browser Reproducible Run are platform operations performed in the capsule.

## Tested Python packages

| Package | Version |
| --- | --- |
| numpy | 2.5.3 |
| pandas | 2.3.3 |
| matplotlib | 3.11.2 |
| scipy | 1.18.1 |
| geopandas | 1.2.0 |
| shapely | 2.1.2 |
| pyproj | 3.8.0 |
| pyogrio | 0.13.0 |

`requirements-tested.txt` records the directly used Python packages for the tested Python version. Use the compatible ranges in `requirements.txt` on other supported Python versions.

## Tested R packages

| Package | Version |
| --- | --- |
| cowplot | 1.2.0 |
| data.table | 1.18.6.1 |
| dplyr | 1.2.1 |
| ggplot2 | 4.0.3 |
| ggprism | 1.0.7 |
| gridExtra | 2.3.1 |
| patchwork | 1.3.2 |
| readr | 2.2.0 |
| scales | 1.4.0 |
| tidyr | 1.3.2 |

## Windows

`run.ps1` accepts `-PythonPath`, `-RscriptPath`, `-OutputDir` and `-Install`. Without an R path, it searches PATH, R's Windows registration and standard R installation directories. Direct invocation of `code/run_public.py` uses the same lookup. Set `RSCRIPT` to select a particular installed version.

## Code Ocean

Use the capsule's R base environment with R 4.3 or newer and Python 3.10 or newer. Configure `environment/postInstall` in the Environment editor. It creates `/opt/climate-solar-venv`, including pip, installs Python dependencies and checks R dependencies. On Ubuntu images, missing virtual-environment support is installed through apt-get. The setup does not depend on `/code` or `/data` being mounted during the environment build.

Set `/code/run` as the run file. It uses the Python environment created by postInstall, reads `/data/non-confidential/` and writes `/results/`. Dependencies are installed during the build, not during the Reproducible Run.

## Execution and graphics

The master workflow uses temporary working directories, a non-interactive Matplotlib backend and one numerical-library thread per plotting process. It checks that all expected PNG, PDF and table outputs exist before reporting success. Logs and the reproduction manifest record the actual run.

Cairo support in R is required for the SVG and PDF exports. Font substitutions across operating systems can change text spacing without changing plotted values.
