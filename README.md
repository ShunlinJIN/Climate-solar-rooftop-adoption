# Climate-driven rooftop solar adoption alleviates rural energy poverty

## Public replication package

This repository contains the code and non-confidential source data required to
reproduce all displayed outputs in the manuscript and Supplementary Information.

The public reproduction generates:

- 6 main manuscript figures;
- 27 Supplementary Figures; and
- 35 Supplementary Tables.

Some upstream analyses use administrative, household electricity-flow,
telemetry, or household-survey source records that cannot be redistributed
under the applicable data-use, confidentiality, privacy, or third-party
redistribution conditions. Those restricted source records are not included in
this public repository. Upstream analytical code that depends exclusively on
those unavailable inputs is therefore not included in the public package.

The public package contains only code that can be executed with the released
non-confidential source data supplied here.

## Reproducible Run in Code Ocean

Click **Reproducible Run**.

A successful run reports:

```text
Main manuscript figures (1-6): SUCCESS
Supplementary figures (1-27): SUCCESS
Supplementary tables (1-35): SUCCESS

Reproduction completed successfully.
All expected manuscript and Supplementary Information outputs were generated.
Results are available in /results.
```

Generated files are available under:

```text
/results/
├── figures/
├── figures_appendix/
└── tables_appendix/
```

The verified complete Code Ocean reproduction takes approximately 3-4 minutes.

## Local reproduction

From the repository root, run:

```bash
python3 code/run_public.py
```

The local workflow writes outputs under `output/`.

## System requirements

The public workflow uses R and Python.

The complete reproduction has been verified in the Code Ocean capsule using
R 4.5.1 and the capsule's system Python 3 interpreter. Local development and
validation were also performed with R 4.4.0 and Python 3.13.

No GPU, accelerator, or other non-standard hardware is required.

Public Python dependencies are listed in:

```text
requirements.txt
```

The R and Python dependencies used by the public workflow are summarized in:

```text
ENVIRONMENT.md
```

## Installation

No manual installation step is required when using the Code Ocean capsule. The
capsule environment and dependencies are prepared automatically before a
Reproducible Run.

For local execution, install the dependencies listed in `ENVIRONMENT.md` and
`requirements.txt`.

## Public source data

The public reproduction uses:

```text
data/non-confidential/aggregate_main/
data/non-confidential/aggregate_supplementary/
```

These files contain non-identifying plotting and table inputs used to recreate
the displayed outputs. They are real replication source data, not synthetic
placeholders.

## Expected outputs

The current manuscript and Supplementary Information contain:

- 6 main figures;
- 27 Supplementary Figures; and
- 35 Supplementary Tables.

## Repository structure

```text
.
├── README.md
├── DATA_AVAILABILITY.md
├── ENVIRONMENT.md
├── LICENSE
├── DATA_LICENSE.md
├── requirements.txt
├── run.sh
│
├── code/
│   ├── run_public.py
│   ├── main/
│   └── supplementary/
│
└── data/
    └── non-confidential/
        ├── aggregate_main/
        └── aggregate_supplementary/
```

The Code Ocean capsule exposes the same materials through `/code`, `/data`, and
`/results`.

## Using the public scripts with other data

The plotting and table scripts can be used with other data that follow the same
schemas as the released files under `data/non-confidential/`. The released
source files provide the required variable names and output structure.

This public package is not intended to reconstruct restricted administrative
or household-level source records.

## Data availability

See `DATA_AVAILABILITY.md`.

## License

The public source code is released under the MIT License; see `LICENSE`.

The non-confidential replication data included in this repository are released
under CC BY 4.0; see `DATA_LICENSE.md`.

These licenses apply only to materials actually redistributed in this public
package and do not grant rights to third-party or restricted source records
that are not included.
