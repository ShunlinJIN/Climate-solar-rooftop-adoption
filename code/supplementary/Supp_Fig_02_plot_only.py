# -*- coding: utf-8 -*-
"""
Supplementary Fig. 2 - PUBLIC plot-only reproduction.

Reads only:
    data/supp_fig02_distribution_data.csv

No real county IDs or county names are required.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib as mpl


def _trapezoid(y, x):
    # NumPy-version-compatible composite trapezoidal integration.
    trapezoid = getattr(np, "trapezoid", None)
    if trapezoid is not None:
        return trapezoid(y, x)
    return np.trapz(y, x)


CODE_DIR = Path(__file__).resolve().parent
ROOT = CODE_DIR.parent
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

INPUT = DATA_DIR / "supp_fig02_distribution_data.csv"

if not INPUT.exists():
    raise FileNotFoundError(
        f"Missing public Fig. 2 dataset:\n{INPUT}"
    )

d = pd.read_csv(
    INPUT,
    dtype={
        "panel": "string",
        "anon_id": "string",
    },
)

required = {
    "panel",
    "anon_id",
    "in_four_sample_provinces",
    "value",
}

missing = required.difference(d.columns)
if missing:
    raise ValueError(
        "Fig. 2 public dataset is missing column(s): "
        + ", ".join(sorted(missing))
    )

d["value"] = pd.to_numeric(d["value"], errors="coerce")
d["in_four_sample_provinces"] = pd.to_numeric(
    d["in_four_sample_provinces"],
    errors="raise",
).astype(int)

if d["value"].isna().any():
    raise ValueError("Public Fig. 2 dataset contains missing value rows.")

TARGETS = {
    "a": {"sample_n": 380, "national_n": 2846, "overlap": 0.75},
    "b": {"sample_n": 338, "national_n": 2297, "overlap": 0.80},
    "c": {"sample_n": 183, "national_n": 1462, "overlap": 0.73},
    "d": {"sample_n": 296, "national_n": 2263, "overlap": 0.72},
}


def densities_and_overlap(sample, national):
    sample = np.asarray(sample, dtype=float)
    national = np.asarray(national, dtype=float)

    lower = min(float(sample.min()), float(national.min()))
    upper = max(float(sample.max()), float(national.max()))

    pooled = np.concatenate([sample, national])
    pooled_sd = np.std(pooled, ddof=1)
    pooled_bandwidth = pooled_sd * (len(pooled) ** (-1.0 / 5.0))

    sample_sd = np.std(sample, ddof=1)
    national_sd = np.std(national, ddof=1)

    sample_factor = pooled_bandwidth / sample_sd if sample_sd > 0 else "scott"
    national_factor = pooled_bandwidth / national_sd if national_sd > 0 else "scott"

    sample_kde = gaussian_kde(sample, bw_method=sample_factor)
    national_kde = gaussian_kde(national, bw_method=national_factor)

    plot_pad = 0.04 * (upper - lower) if upper > lower else 1.0
    plot_grid = np.linspace(lower - plot_pad, upper + plot_pad, 600)

    sample_density = sample_kde(plot_grid)
    national_density = national_kde(plot_grid)

    overlap_grid = np.linspace(lower, upper, 1000)
    overlap = float(
        _trapezoid(
            np.minimum(
                sample_kde(overlap_grid),
                national_kde(overlap_grid),
            ),
            overlap_grid,
        )
    )

    return plot_grid, sample_density, national_density, overlap


mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans"],
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

NATIONAL_COLOR = "#3C78A8"
SAMPLE_COLOR = "#E89032"

panel_specs = {
    "a": {
        "title": "Long-term temperature",
        "xlabel": "Mean daily temperature (\u00B0C)",
    },
    "b": {
        "title": "County income",
        "xlabel": "Per-capita disposable income (1,000 RMB)",
    },
    "c": {
        "title": "Educational resources",
        "xlabel": "Teachers per 1,000 residents",
    },
    "d": {
        "title": "Rural population share",
        "xlabel": "Rural population share (%)",
    },
}

fig, axes = plt.subplots(2, 2, figsize=(8.8, 6.4))
axes = axes.ravel()

metrics = []

for ax, panel in zip(axes, ["a", "b", "c", "d"]):
    q = d.loc[d["panel"].eq(panel)].copy()

    national = q["value"].to_numpy(float)
    sample = q.loc[
        q["in_four_sample_provinces"].eq(1),
        "value",
    ].to_numpy(float)

    grid, sample_density, national_density, overlap = (
        densities_and_overlap(sample, national)
    )

    target = TARGETS[panel]

    if len(national) != target["national_n"]:
        raise RuntimeError(
            f"Panel {panel}: national N mismatch "
            f"({len(national)} != {target['national_n']})."
        )

    if len(sample) != target["sample_n"]:
        raise RuntimeError(
            f"Panel {panel}: sample N mismatch "
            f"({len(sample)} != {target['sample_n']})."
        )

    if round(overlap + 1e-12, 2) != target["overlap"]:
        raise RuntimeError(
            f"Panel {panel}: overlap mismatch "
            f"({overlap:.6f}; expected {target['overlap']:.2f})."
        )

    ax.plot(
        grid,
        national_density,
        color=NATIONAL_COLOR,
        linewidth=1.7,
        linestyle=(0, (5, 4)),
        label="All mainland counties",
    )

    ax.plot(
        grid,
        sample_density,
        color=SAMPLE_COLOR,
        linewidth=2.0,
        linestyle="solid",
        label="Counties in the four sample provinces",
    )

    ax.set_title(panel_specs[panel]["title"], fontsize=11, pad=12)
    ax.set_xlabel(panel_specs[panel]["xlabel"], fontsize=10)
    ax.set_ylabel("Density", fontsize=10)
    ax.set_ylim(bottom=0)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_position(("outward", 8))
    ax.spines["bottom"].set_position(("outward", 8))
    ax.tick_params(
        axis="both",
        labelsize=9,
        width=1.0,
        length=4,
        direction="out",
    )

    ax.text(
        -0.10,
        1.08,
        panel,
        transform=ax.transAxes,
        fontsize=14,
        fontweight="bold",
        ha="left",
        va="top",
    )

    ax.text(
        0.97,
        0.95,
        f"Overlap = {overlap:.2f}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9,
    )

    metrics.append({
        "panel": panel,
        "sample_n": len(sample),
        "national_n": len(national),
        "overlap": overlap,
    })

handles, labels = axes[0].get_legend_handles_labels()

fig.legend(
    handles,
    labels,
    loc="upper center",
    bbox_to_anchor=(0.5, 1.015),
    ncol=2,
    frameon=False,
    fontsize=9.5,
    handlelength=2.8,
)

fig.subplots_adjust(
    left=0.09,
    right=0.98,
    bottom=0.10,
    top=0.88,
    wspace=0.30,
    hspace=0.42,
)

png = OUT_DIR / "Supplementary_Fig_02.png"
pdf = OUT_DIR / "Supplementary_Fig_02.pdf"
metrics_out = OUT_DIR / "Supplementary_Fig_02_reproduction_metrics.csv"

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

pd.DataFrame(metrics).to_csv(
    metrics_out,
    index=False,
    encoding="utf-8",
)

print("Supplementary Fig. 2 reproduced from anonymized observations.")
print(png)
print(pdf)
print(metrics_out)
