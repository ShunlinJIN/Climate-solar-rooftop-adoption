# Capsule environment

Use an R environment with R 4.3 or newer and Python 3.10 or newer. Ubuntu 22.04 R images can use their existing Python interpreter.

## Build setup

In the capsule's **Environment** screen, replace the post-install script with the complete contents of `environment/postInstall`. This script must be configured in the Environment editor to run during the build phase.

The script creates an isolated Python environment at `/opt/climate-solar-venv`, including pip, and installs the Python and R dependencies. If the Ubuntu image lacks virtual-environment support, it installs `python3-venv` through apt-get. It checks Python dependency compatibility and verifies that the required R packages can load. Setup does not read `/code` or `/data` during the environment build.

## Run

Set `/code/run` as the run file. It uses the Python environment prepared by postInstall. Select **Reproducible Run** to build the environment and execute the workflow. Inputs are under `/data/non-confidential/`; outputs are written to `/results/`.

The environment build log records dependency-installation and postInstall errors. A successful workflow writes `reproduction_manifest.json` together with figures, tables and individual script logs. Software requirements and tested versions are documented in `/code/ENVIRONMENT.md`.

Platform documentation: https://docs.codeocean.com/osl-guide/getting-started/the-computational-environment/using-the-postinstall-script-for-further-customization
