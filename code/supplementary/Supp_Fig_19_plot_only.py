# Supplementary Fig. 19
# Propensity-score distributions before and after matching.
#
# Plots the supplied density-curve coordinates.
# See SOURCE_DATA.md for input definitions.

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------
CODE_DIR = Path(__file__).resolve().parent
ROOT_DIR = CODE_DIR.parent
DATA_DIR = ROOT_DIR / "data"
OUT_DIR = ROOT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = DATA_DIR / "supp_fig19_propensity_density.csv"


# ---------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans"],
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "axes.linewidth": 0.85,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "xtick.major.size": 3.5,
    "ytick.major.size": 3.5,
})


def clean_axis(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


# ---------------------------------------------------------------------
# Coordinate smoothing
# ---------------------------------------------------------------------
def gaussian_kernel(sigma_points: float):
    """Return a normalized one-dimensional Gaussian kernel."""
    radius = max(2, int(round(4.0 * sigma_points)))
    x = np.arange(-radius, radius + 1, dtype=float)
    k = np.exp(-0.5 * (x / sigma_points) ** 2)
    return k / k.sum()


def smooth_stored_curve(frame: pd.DataFrame, sigma_points: float, n_grid: int = 700):
    """Interpolate stored curve coordinates and apply Gaussian smoothing."""
    q = frame[["propensity_score", "density"]].copy()

    q["propensity_score"] = pd.to_numeric(
        q["propensity_score"], errors="coerce"
    )
    q["density"] = pd.to_numeric(
        q["density"], errors="coerce"
    )

    q = (
        q.replace([np.inf, -np.inf], np.nan)
        .dropna()
        .sort_values("propensity_score")
    )

    q = (
        q.groupby("propensity_score", as_index=False)["density"]
        .median()
        .sort_values("propensity_score")
    )

    if len(q) < 5:
        raise ValueError("Too few curve coordinates to draw Fig. 19.")

    xmin = float(q["propensity_score"].min())
    xmax = float(q["propensity_score"].max())

    x_grid = np.linspace(xmin, xmax, n_grid)

    y_grid = np.interp(
        x_grid,
        q["propensity_score"].to_numpy(float),
        q["density"].to_numpy(float),
    )

    kernel = gaussian_kernel(sigma_points)
    pad = len(kernel) // 2

    y_pad = np.pad(
        y_grid,
        pad_width=pad,
        mode="edge",
    )

    y_smooth = np.convolve(
        y_pad,
        kernel,
        mode="same",
    )[pad:-pad]

    y_smooth = np.maximum(y_smooth, 0.0)

    return x_grid, y_smooth


# ---------------------------------------------------------------------
# Read plotting source
# ---------------------------------------------------------------------
if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Missing plotting input:\n{INPUT_FILE}"
    )

d = pd.read_csv(
    INPUT_FILE,
    encoding="utf-8-sig",
)

required = {
    "stage",
    "group",
    "propensity_score",
    "density",
}

missing = required.difference(d.columns)
if missing:
    raise ValueError(
        "Fig. 19 plotting input is missing column(s): "
        + ", ".join(sorted(missing))
    )


# ---------------------------------------------------------------------
# Draw
# ---------------------------------------------------------------------
fig, axes = plt.subplots(
    1,
    2,
    figsize=(10.2, 5.4),
    sharey=True,
)

# Line styles and smoothing parameters for each group.
curve_specs = [
    ("Control (Non-Solar)", "blue", (0, (5, 5)), 8.5),
    ("Treatment (Solar)", "red", "solid", 4.5),
]

for ax, stage in zip(axes, ["Unmatched", "Matched"]):
    for group, color, linestyle, sigma in curve_specs:

        q = d.loc[
            d["stage"].eq(stage)
            & d["group"].eq(group)
        ].copy()

        if q.empty:
            raise ValueError(
                f"No plotting coordinates for {stage} / {group}"
            )

        x, y = smooth_stored_curve(
            q,
            sigma_points=sigma,
            n_grid=700,
        )

        ax.plot(
            x,
            y,
            color=color,
            linestyle=linestyle,
            linewidth=1.9,
            solid_capstyle="round",
            dash_capstyle="butt",
            label=group,
        )

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 3.3)

    ax.set_xticks([
        0, 0.2, 0.4, 0.6, 0.8, 1.0
    ])
    ax.set_xticklabels([
        "0", "0.20", "0.40", "0.60", "0.80", "1"
    ])

    ax.set_yticks([
        0, 1, 2, 3
    ])

    ax.tick_params(
        axis="both",
        labelsize=12,
    )

    clean_axis(ax)

# Show y tick labels on the right panel as in the SI
axes[1].tick_params(labelleft=True)

axes[0].set_ylabel(
    "Density",
    fontsize=14,
)

# Titles ABOVE legend
fig.text(
    0.27, 0.94,
    "Unmatched",
    ha="center",
    va="bottom",
    fontsize=17,
    fontweight="bold",
)

fig.text(
    0.74, 0.94,
    "Matched",
    ha="center",
    va="bottom",
    fontsize=17,
    fontweight="bold",
)

# Shared legend BELOW titles
handles, labels = axes[0].get_legend_handles_labels()

fig.legend(
    handles,
    labels,
    loc="upper center",
    bbox_to_anchor=(0.5, 0.895),
    ncol=2,
    frameon=False,
    fontsize=12,
    handlelength=1.9,
    columnspacing=0.8,
    handletextpad=0.5,
)

fig.supxlabel(
    "Propensity Score",
    fontsize=14,
    y=0.06,
)

fig.subplots_adjust(
    left=0.10,
    right=0.98,
    bottom=0.15,
    top=0.84,
    wspace=0.08,
)


# ---------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------
png_path = OUT_DIR / "Supplementary_Fig_19.png"
pdf_path = OUT_DIR / "Supplementary_Fig_19.pdf"

fig.savefig(
    png_path,
    dpi=600,
    bbox_inches="tight",
    pad_inches=0.04,
)

fig.savefig(
    pdf_path,
    bbox_inches="tight",
    pad_inches=0.04,
)

plt.close(fig)

print("Supplementary Fig. 19 reproduced.")
print(png_path)
print(pdf_path)
