# Code

Start with the repository's [main README](../README.md) for local setup, reproduction commands, output locations and data downloads.

| Directory or file | Purpose |
| --- | --- |
| `main/` | Main-figure scripts |
| `supplementary/` | Supplementary-figure scripts and table export |
| [regression/](regression/README.md) | Regression estimation code and required underlying inputs |
| `run_public.py` | Local figure-and-table reproduction entry point |
| `validate_public_inputs.py` | Released figure/table input checks |

Run the workflow from the repository root with `python code/run_public.py`, using the Python environment described in the main README. Local results are written to `output/` at that root. See the [output index](../OUTPUT_INDEX.md) and [data availability statement](../DATA_AVAILABILITY.md).
