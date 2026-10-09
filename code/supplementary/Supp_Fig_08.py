# -*- coding: utf-8 -*-
"""
Supplementary Fig. 8 — plotting from income distributions

Reads only:
    data/supp_fig08_income_density.csv
    data/supp_fig08_income_benchmark_shares.csv

Writes only:
    output/Supplementary_Fig_08.png
    output/Supplementary_Fig_08.pdf

Panel a displays the income distribution over 0–60 (1,000 RMB).
Panel b displays the shares below the stated income benchmarks.

No household-level raw data or identifiers are used.
"""

from pathlib import Path
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# =============================================================================
# Paths
# =============================================================================

CODE_DIR = Path(__file__).resolve().parent
ROOT = CODE_DIR.parent
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DENSITY_FILE = DATA_DIR / "supp_fig08_income_density.csv"
SHARES_FILE = DATA_DIR / "supp_fig08_income_benchmark_shares.csv"

if not DENSITY_FILE.exists():
    raise FileNotFoundError(f"Missing:\n{DENSITY_FILE}")
if not SHARES_FILE.exists():
    raise FileNotFoundError(f"Missing:\n{SHARES_FILE}")


density = pd.read_csv(DENSITY_FILE)
shares = pd.read_csv(SHARES_FILE)

required_density = {
    "group",
    "annual_income_thousand_rmb",
    "density",
}
required_shares = {
    "benchmark_key",
    "benchmark_label",
    "benchmark_rmb",
    "adopters_pct",
    "nonadopters_pct",
    "full_sample_pct",
}

if missing := required_density.difference(density.columns):
    raise ValueError("Fig. 8 density CSV missing field(s): " + ", ".join(sorted(missing)))
if missing := required_shares.difference(shares.columns):
    raise ValueError("Fig. 8 benchmark CSV missing field(s): " + ", ".join(sorted(missing)))


# =============================================================================
# Style
# =============================================================================

BLUE = "#168AAD"
GRAY = "#6C6C6C"
FULL_GRAY = "#B0B0B0"
GREEN = "#2E7D32"
ORANGE = "#C26D00"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans"],
    "font.size": 9.5,
    "axes.titlesize": 10.8,
    "axes.labelsize": 10,
    "legend.fontsize": 8.3,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


# =============================================================================
# Figure
# =============================================================================

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.8, 4.5))


# -----------------------------------------------------------------------------
# Panel a: KDEs + benchmark lines
# -----------------------------------------------------------------------------

for group, color in [
    ("RRPV adopters", BLUE),
    ("Non-adopters", GRAY),
]:
    q = density.loc[density["group"].eq(group)].sort_values("annual_income_thousand_rmb")
    if q.empty:
        raise ValueError(f"Missing density curve for {group}")

    ax1.plot(
        q["annual_income_thousand_rmb"],
        q["density"],
        color=color,
        linewidth=2.0,
        label=group,
    )


def benchmark_value(key: str) -> float:
    q = shares.loc[shares["benchmark_key"].eq(key)]
    if len(q) != 1:
        raise ValueError(f"Expected one row for benchmark {key}")
    return float(q["benchmark_rmb"].iloc[0]) / 1000.0


national_mean = benchmark_value("national_rural_mean")
jiangsu_mean = benchmark_value("jiangsu_rural_mean")

ax1.axvline(
    national_mean,
    linestyle="--",
    linewidth=1.6,
    color=GREEN,
    label="National rural mean (2023)",
)
ax1.axvline(
    jiangsu_mean,
    linestyle="-.",
    linewidth=1.6,
    color=ORANGE,
    label="Jiangsu rural mean (2023)",
)

ax1.set_xlim(0, 60)
ax1.set_xticks(np.arange(0, 61, 10))
ax1.set_ylim(bottom=0)
ax1.set_xlabel("Annual per-capita household income (1,000 RMB)")
ax1.set_ylabel("Density")
ax1.set_title(
    "Survey income distribution and external benchmarks",
    loc="left",
    fontweight="bold",
    pad=8,
)
ax1.text(
    -0.07,
    1.055,
    "a",
    transform=ax1.transAxes,
    ha="left",
    va="top",
    fontsize=13,
    fontweight="bold",
)
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)
ax1.spines["left"].set_linewidth(1.0)
ax1.spines["bottom"].set_linewidth(1.0)
ax1.tick_params(direction="out", length=4, width=0.9)
ax1.grid(False)
ax1.legend(frameon=False, loc="upper right")


# -----------------------------------------------------------------------------
# Panel b: benchmark shares
# -----------------------------------------------------------------------------

order = [
    "national_rural_mean",
    "national_rural_median",
    "jiangsu_rural_mean",
    "national_county_p40",
]
labels = [
    "Below national\nrural mean",
    "Below national\nrural median",
    "Below Jiangsu\nrural mean",
    "Below national\ncounty P40",
]

plot_shares = shares.set_index("benchmark_key").loc[order].reset_index()
x = np.arange(len(order))
width = 0.22

groups = [
    ("RRPV adopters", "adopters_pct", BLUE),
    ("Non-adopters", "nonadopters_pct", GRAY),
    ("Full sample", "full_sample_pct", FULL_GRAY),
]

for i, (group, column, color) in enumerate(groups):
    vals = plot_shares[column].to_numpy(float)
    xpos = x + (i - 1) * width

    ax2.bar(
        xpos,
        vals,
        width=width,
        color=color,
        alpha=0.28,
        edgecolor=color,
        linewidth=0.8,
    )
    ax2.scatter(
        xpos,
        vals,
        color=color,
        s=24,
        zorder=3,
        label=group,
    )

ax2.set_xticks(x)
ax2.set_xticklabels(labels)
ax2.set_ylabel("Households below benchmark (%)")
ax2.set_title(
    "Position relative to national and provincial benchmarks",
    loc="left",
    fontweight="bold",
    pad=8,
)
ax2.text(
    -0.07,
    1.055,
    "b",
    transform=ax2.transAxes,
    ha="left",
    va="top",
    fontsize=13,
    fontweight="bold",
)
ax2.set_ylim(0, 100)
ax2.set_yticks(np.arange(0, 101, 20))
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
ax2.spines["left"].set_linewidth(1.0)
ax2.spines["bottom"].set_linewidth(1.0)
ax2.tick_params(direction="out", length=4, width=0.9)
ax2.grid(False)
ax2.legend(frameon=False, loc="upper right")

fig.tight_layout(w_pad=2.4)


# =============================================================================
# Save figures only
# =============================================================================

png = OUT_DIR / "Supplementary_Fig_08.png"
pdf = OUT_DIR / "Supplementary_Fig_08.pdf"

fig.savefig(png, dpi=600, bbox_inches="tight", pad_inches=0.08)
fig.savefig(pdf, bbox_inches="tight", pad_inches=0.08)
plt.close(fig)

print("Supplementary Fig. 8 reproduced.")
print(png)
print(pdf)
