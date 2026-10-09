# -*- coding: utf-8 -*-
"""
Supplementary Fig. 5 — plotting from aggregate data

Reads:
    data/supp_fig05_monthly_flows.csv

Writes:
    output/Supplementary_Fig_05.png
    output/Supplementary_Fig_05.pdf

Plotting conventions:
- stack order identical to the Supplementary Information;
- exact R color mapping;
- alpha = 0.7;
- y-axis fixed at 0–40;
- four-month date ticks aligned with the Supplementary Information;
- legend order identical to the Supplementary Information.
"""

from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------
CODE_DIR = Path(__file__).resolve().parent
ROOT = CODE_DIR.parent
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

INPUT = DATA_DIR / "supp_fig05_monthly_flows.csv"

if not INPUT.exists():
    raise FileNotFoundError(
        f"Missing Fig. 5 input:\n{INPUT}"
    )


# ---------------------------------------------------------------------
# Read public aggregate data
# ---------------------------------------------------------------------
d = pd.read_csv(
    INPUT,
    parse_dates=["month"],
).sort_values("month")

required = {
    "month",
    "pv_to_grid_kwh",
    "pv_to_battery_kwh",
    "grid_to_consumption_kwh",
    "direct_consumption_kwh",
    "battery_to_consumption_kwh",
    "battery_remaining_kwh",
}

missing = required.difference(d.columns)
if missing:
    raise ValueError(
        "Missing Fig. 5 column(s): "
        + ", ".join(sorted(missing))
    )

for col in required.difference({"month"}):
    d[col] = pd.to_numeric(
        d[col],
        errors="coerce",
    )

if d[
    list(required.difference({"month"}))
].isna().any().any():
    raise ValueError(
        "Fig. 5 input contains missing flow values."
    )


# ---------------------------------------------------------------------
# Stack order = bottom to top in the Supplementary Information
# ---------------------------------------------------------------------
series = [
    (
        "pv_to_grid_kwh",
        "PV to Grid",
        "#87CEEB",  # R: skyblue
    ),
    (
        "pv_to_battery_kwh",
        "PV to Battery",
        "#A0522D",  # R: sienna
    ),
    (
        "grid_to_consumption_kwh",
        "Grid to Consumption",
        "#008B00",  # R: green4
    ),
    (
        "direct_consumption_kwh",
        "Direct Consumption",
        "#4682B4",  # R: steelblue
    ),
    (
        "battery_to_consumption_kwh",
        "Battery to Consumption",
        "#CD853F",  # R: tan3
    ),
    (
        "battery_remaining_kwh",
        "Battery Remaining",
        "#66CDAA",  # R: mediumaquamarine
    ),
]


# ---------------------------------------------------------------------
# Draw
# ---------------------------------------------------------------------
fig, ax = plt.subplots(
    figsize=(8.4, 4.8)
)

ax.stackplot(
    d["month"],
    *[
        d[col].to_numpy(float)
        for col, _, _ in series
    ],
    colors=[
        color
        for _, _, color in series
    ],
    alpha=0.70,
    linewidth=0,
)


# ---------------------------------------------------------------------
# Axes: exact historical settings
# ---------------------------------------------------------------------
ax.set_ylabel(
    "Average Household Electricity Dynamics",
    fontsize=12,
)

ax.set_xlabel(
    "Time",
    fontsize=12,
)

ax.set_ylim(
    0,
    40,
)

ax.set_yticks(
    [0, 10, 20, 30, 40]
)

ax.set_xlim(
    pd.Timestamp("2018-06-01"),
    pd.Timestamp("2020-12-31"),
)

# Explicit four-month ticks to reproduce the Supplementary Information:
# 2018-08, 2018-12, 2019-04, ...
tick_dates = pd.date_range(
    start="2018-08-01",
    end="2020-12-01",
    freq="4MS",
)

ax.set_xticks(
    tick_dates
)

ax.xaxis.set_major_formatter(
    mdates.DateFormatter("%Y-%m")
)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.tick_params(
    axis="both",
    direction="out",
    labelsize=10,
    width=0.5,
)

ax.grid(False)


# ---------------------------------------------------------------------
# Legend order exactly as shown in the SI:
# row 1: Battery Remaining | Direct Consumption | PV to Battery
# row 2: Battery to Consumption | Grid to Consumption | PV to Grid
# ---------------------------------------------------------------------
color_lookup = {
    label: color
    for _, label, color in series
}

legend_order = [
    "Battery Remaining",
    "Direct Consumption",
    "PV to Battery",
    "Battery to Consumption",
    "Grid to Consumption",
    "PV to Grid",
]

legend_handles = [
    Patch(
        facecolor=color_lookup[label],
        edgecolor="none",
        alpha=0.70,
        label=label,
    )
    for label in legend_order
]

ax.legend(
    handles=legend_handles,
    loc="upper center",
    bbox_to_anchor=(0.5, 1.19),
    ncol=3,
    frameon=False,
    fontsize=9.2,
    columnspacing=1.4,
    handlelength=1.6,
)

fig.tight_layout()


# ---------------------------------------------------------------------
# Save figures only
# ---------------------------------------------------------------------
png = OUT_DIR / "Supplementary_Fig_05.png"
pdf = OUT_DIR / "Supplementary_Fig_05.pdf"

fig.savefig(
    png,
    dpi=600,
    bbox_inches="tight",
    pad_inches=0.03,
)

fig.savefig(
    pdf,
    bbox_inches="tight",
    pad_inches=0.03,
)

plt.close(fig)

print("Supplementary Fig. 5 reproduced.")
print(png)
print(pdf)
