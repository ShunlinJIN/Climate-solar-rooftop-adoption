# -*- coding: utf-8 -*-
"""
Supplementary Fig. 3 — FINAL plot-only version

Reads:
    data/supp_fig03_daily_flows.csv

Writes:
    output/Supplementary_Fig_03.png
    output/Supplementary_Fig_03.pdf

This version follows the historical final R plotting code:
- 7-day right-aligned rolling means;
- light raw daily lines in the background;
- PV generation: blue;
- self-consumed PV electricity: orange;
- grid-imported electricity: green dashed;
- grid-exported electricity: light orange ribbon;
- legend order and date ticks aligned with the current SI.
"""

from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
from matplotlib.lines import Line2D


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------
CODE_DIR = Path(__file__).resolve().parent
ROOT = CODE_DIR.parent
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

INPUT = DATA_DIR / "supp_fig03_daily_flows.csv"

if not INPUT.exists():
    raise FileNotFoundError(
        f"Missing Fig. 3 input:\n{INPUT}"
    )


# ---------------------------------------------------------------------
# Read public aggregate data
# ---------------------------------------------------------------------
d = pd.read_csv(
    INPUT,
    parse_dates=["date"],
)

required = {
    "date",
    "pv_generation_kwh",
    "self_consumed_pv_kwh",
    "grid_imported_kwh",
    "grid_exported_kwh",
}

missing = required.difference(d.columns)
if missing:
    raise ValueError(
        "Missing Fig. 3 column(s): "
        + ", ".join(sorted(missing))
    )

d = (
    d.sort_values("date")
    .drop_duplicates("date")
    .reset_index(drop=True)
)

for col in [
    "pv_generation_kwh",
    "self_consumed_pv_kwh",
    "grid_imported_kwh",
    "grid_exported_kwh",
]:
    d[col] = pd.to_numeric(
        d[col],
        errors="coerce",
    )

if d[
    [
        "pv_generation_kwh",
        "self_consumed_pv_kwh",
        "grid_imported_kwh",
    ]
].isna().any().any():
    raise ValueError(
        "Fig. 3 input contains missing values in required flow series."
    )


# ---------------------------------------------------------------------
# 7-day right-aligned rolling means, matching zoo::rollmean(..., align='right')
# ---------------------------------------------------------------------
WINDOW = 7

d["pv_generation_smooth"] = (
    d["pv_generation_kwh"]
    .rolling(
        window=WINDOW,
        min_periods=WINDOW,
    )
    .mean()
)

d["self_consumed_smooth"] = (
    d["self_consumed_pv_kwh"]
    .rolling(
        window=WINDOW,
        min_periods=WINDOW,
    )
    .mean()
)

d["grid_imported_smooth"] = (
    d["grid_imported_kwh"]
    .rolling(
        window=WINDOW,
        min_periods=WINDOW,
    )
    .mean()
)


# ---------------------------------------------------------------------
# Exact historical colors
# ---------------------------------------------------------------------
PV_BLUE = "#1f77b4"
SELF_ORANGE = "#E69F00"
GRID_GREEN = "#009E73"
EXPORT_ORANGE = "#D55E00"


# ---------------------------------------------------------------------
# Draw
# ---------------------------------------------------------------------
fig, ax = plt.subplots(
    figsize=(8.4, 4.8)
)

# A. Grid-exported electricity:
#    shaded area between smoothed self-consumption and smoothed PV generation.
valid_ribbon = (
    d["pv_generation_smooth"].notna()
    & d["self_consumed_smooth"].notna()
)

ax.fill_between(
    d.loc[valid_ribbon, "date"],
    d.loc[valid_ribbon, "self_consumed_smooth"],
    d.loc[valid_ribbon, "pv_generation_smooth"],
    color=EXPORT_ORANGE,
    alpha=0.18,
    linewidth=0,
    zorder=1,
)

# B. Raw daily lines in the background.
ax.plot(
    d["date"],
    d["pv_generation_kwh"],
    color=PV_BLUE,
    linewidth=0.35,
    alpha=0.35,
    zorder=2,
)

ax.plot(
    d["date"],
    d["self_consumed_pv_kwh"],
    color=SELF_ORANGE,
    linewidth=0.35,
    alpha=0.35,
    zorder=2,
)

ax.plot(
    d["date"],
    d["grid_imported_kwh"],
    color=GRID_GREEN,
    linewidth=0.35,
    alpha=0.35,
    linestyle="--",
    zorder=2,
)

# C. 7-day smoothed main lines.
ax.plot(
    d["date"],
    d["pv_generation_smooth"],
    color=PV_BLUE,
    linewidth=0.9,
    zorder=3,
)

ax.plot(
    d["date"],
    d["self_consumed_smooth"],
    color=SELF_ORANGE,
    linewidth=0.9,
    zorder=3,
)

ax.plot(
    d["date"],
    d["grid_imported_smooth"],
    color=GRID_GREEN,
    linewidth=0.9,
    linestyle="--",
    zorder=3,
)


# ---------------------------------------------------------------------
# Axes
# ---------------------------------------------------------------------
ax.set_xlabel(
    "Date",
    fontsize=11,
)

ax.set_ylabel(
    "Average Per Household Per Day (kWh)",
    fontsize=11,
)

ax.set_ylim(
    bottom=0,
)

# Match current SI temporal support.
ax.set_xlim(
    pd.Timestamp("2018-06-01"),
    pd.Timestamp("2020-12-31"),
)

# Jan / Jul ticks, as in the current SI.
ax.xaxis.set_major_locator(
    mdates.MonthLocator(
        bymonth=[1, 7],
        bymonthday=1,
    )
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
# Legend: exact SI reading order
# ---------------------------------------------------------------------
legend_handles = [
    Patch(
        facecolor=EXPORT_ORANGE,
        edgecolor="none",
        alpha=0.18,
        label="Grid-exported electricity",
    ),
    Line2D(
        [0], [0],
        color=GRID_GREEN,
        linewidth=0.9,
        linestyle="--",
        label="Grid-imported electricity",
    ),
    Line2D(
        [0], [0],
        color=PV_BLUE,
        linewidth=0.9,
        linestyle="-",
        label="PV generation",
    ),
    Line2D(
        [0], [0],
        color=SELF_ORANGE,
        linewidth=0.9,
        linestyle="-",
        label="Self-consumed PV electricity",
    ),
]

ax.legend(
    handles=legend_handles,
    loc="upper center",
    bbox_to_anchor=(0.5, 1.15),
    ncol=4,
    frameon=False,
    fontsize=9.2,
    handlelength=2.2,
    columnspacing=1.5,
)

fig.tight_layout()


# ---------------------------------------------------------------------
# Save figures only
# ---------------------------------------------------------------------
png = OUT_DIR / "Supplementary_Fig_03.png"
pdf = OUT_DIR / "Supplementary_Fig_03.pdf"

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

print("Supplementary Fig. 3 reproduced.")
print(png)
print(pdf)
