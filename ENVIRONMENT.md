# Computational environment

The public figure-and-table workflow uses Python and R on a standard CPU. Its dependency files are [code/requirements.txt](code/requirements.txt) and [code/setup.R](code/setup.R).

## Local setup

Use Python 3.10 or newer and R 4.3 or newer. Follow the Windows or Linux/macOS commands in the [main README](README.md). `code/setup.R` installs missing R packages or updates packages below its minimum versions; installation requires access to the configured package repositories.

For an existing Python environment, install dependencies with `python -m pip install -r code/requirements.txt`. Install or check the R plotting dependencies with `Rscript code/setup.R`.

The default plotting workflow uses cowplot, data.table, dplyr, ggplot2, ggprism, gridExtra, patchwork, readr, scales and tidyr in R, and NumPy, pandas, Matplotlib, SciPy, GeoPandas and Shapely in Python, together with their dependencies. The setup files specify the applicable version requirements. Regression estimation has additional dependencies listed in [code/regression/README.md](code/regression/README.md).

## Selecting Rscript

The runner checks `RSCRIPT`, then the system PATH, and then common Windows R installation locations. If Rscript is not found, set `RSCRIPT` to the full path of your installed `Rscript.exe` or `Rscript` executable. In PowerShell, the setup command with that variable is:

```powershell
& $env:RSCRIPT .\code\setup.R
```

Then run the Python entry point from the same terminal. The variable must refer to an existing executable, not to an R installation directory.

## Environments and run records

The original analyses used R 4.4.0 and Python 3.13.3. The companion Code Ocean figure-and-table workflow used R 4.5.1 and Python 3.10.12. These are separate environments; GitHub does not provide the capsule's hosted runtime.

Each completed local run records its actual interpreter and package versions in `output/reproduction_manifest.json`. The figure-and-table workflow has also completed successfully in the author's Windows checkout. `code/requirements-tested.txt` is a recorded Python dependency snapshot; it is not a complete lockfile for every environment or for the upstream regression analyses.

## Execution and graphics

From the repository root, use `python code/run_public.py` with the configured Python environment. By default it reads `data/non-confidential/` and writes `output/`. It validates the released inputs, stages temporary working directories for the figure scripts and checks the expected figure and table outputs before reporting success. Per-script logs are written to `output/log/`.

Cairo support is required by the R graphics workflow. Font substitutions between operating systems can change text spacing. The public plotting workflow uses released processed figure/table inputs; regression estimation requires the underlying analysis datasets and is not part of that default run.

The files under `environment/` describe the companion Code Ocean build. They are not prerequisites for the local commands above. See [environment/README.md](environment/README.md) for those platform-specific instructions.
