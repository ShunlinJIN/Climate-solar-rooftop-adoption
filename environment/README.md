# Companion Code Ocean environment

This directory contains the environment configuration for the companion Code Ocean capsule. For a local GitHub run, use the [main README](../README.md) and [ENVIRONMENT.md](../ENVIRONMENT.md).

## Code Ocean build

Use the capsule's configured R/Python base environment. Configure the contents of `environment/postInstall` as the post-install script in the capsule's Environment editor. The script prepares `/opt/climate-solar-venv` and installs the required Python and R plotting dependencies during the environment build. It does not require `/code` or `/data` to be mounted during that build.

## Code Ocean run

Set `/code/run` as the capsule's run file and use **Reproducible Run** after the environment is built. In the capsule, the workflow reads `/data/non-confidential/` and writes `/results/`. Per-script logs and `reproduction_manifest.json` are saved with those outputs.

The local entry point is `python code/run_public.py`, which writes `output/` at the GitHub repository root by default.
