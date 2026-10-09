#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# -----------------------------------------------------------------------------
# Local functions and setup
# -----------------------------------------------------------------------------

from pathlib import Path
import textwrap

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

TEAL = "#2A9D8F"
CORAL = "#E76F51"
NAVY = "#264653"
GRAY = "#606060"
LIGHT = "#D9D9D9"

def project_paths(script_file: str):
    code_dir = Path(script_file).resolve().parent
    root = code_dir.parent
    data_dir = root / "data"
    out_dir = root / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    return data_dir, out_dir

def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, encoding="utf-8-sig", low_memory=False)

def set_style() -> None:
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "DejaVu Sans"],
        "font.size": 9.0,
        "axes.titlesize": 9.8,
        "axes.labelsize": 9.0,
        "xtick.labelsize": 8.0,
        "ytick.labelsize": 8.0,
        "legend.fontsize": 7.5,
        "axes.linewidth": 0.85,
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "xtick.major.size": 3.0,
        "ytick.major.size": 3.0,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })

def style_axis(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

def wrap_text(value: str, width: int) -> str:
    return textwrap.fill(
        str(value),
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    )

def heading(ax, letter: str, title: str, pad: float = 7) -> None:
    ax.text(
        -0.16, 1.04, letter,
        transform=ax.transAxes,
        ha="left", va="bottom",
        fontsize=10.2,
        fontweight="bold",
        clip_on=False,
    )
    ax.set_title(
        title,
        loc="center",
        pad=pad,
        fontsize=9.6,
        fontweight="normal",
    )

def forest(
    ax,
    data: pd.DataFrame,
    letter: str,
    title: str,
    xlabel: str,
    *,
    wrap_width: int | None = None,
    ytick_fontsize: float = 8.0,
    y_margin: float = 0.12,
) -> None:
    q = data.sort_values("x_order").iloc[::-1].reset_index(drop=True).copy()
    y = np.arange(len(q))

    estimate = pd.to_numeric(q["estimate"])
    low = np.minimum(
        pd.to_numeric(q["conf_low"]),
        pd.to_numeric(q["conf_high"]),
    )
    high = np.maximum(
        pd.to_numeric(q["conf_low"]),
        pd.to_numeric(q["conf_high"]),
    )
    low = np.minimum(low, estimate)
    high = np.maximum(high, estimate)

    ax.axvline(0, color=GRAY, linestyle="--", linewidth=0.65)
    ax.errorbar(
        estimate, y,
        xerr=[estimate - low, high - estimate],
        fmt="o",
        color=TEAL,
        ecolor=GRAY,
        markersize=4.0,
        capsize=2.3,
        linewidth=0.9,
    )

    labels = q["category"].astype(str).tolist()
    if wrap_width is not None:
        labels = [wrap_text(value, wrap_width) for value in labels]

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=ytick_fontsize)
    ax.set_xlabel(xlabel)
    ax.margins(y=y_margin)
    heading(ax, letter, title)
    style_axis(ax)

def save(fig, out_dir: Path, number: int) -> None:
    stem = out_dir / f"Supplementary_Fig_{number:02d}"
    fig.savefig(
        stem.with_suffix(".png"),
        dpi=600,
        bbox_inches="tight",
        pad_inches=0.05,
    )
    fig.savefig(
        stem.with_suffix(".pdf"),
        bbox_inches="tight",
        pad_inches=0.05,
    )
    plt.close(fig)
    print(f"Supplementary Fig. {number} reproduced.")

# -----------------------------------------------------------------------------
# Data, panels and export
# -----------------------------------------------------------------------------

DATA_DIR, OUT_DIR = project_paths(__file__)
set_style()
source = read_csv(DATA_DIR / "supp_fig21_source.csv")

fig, axes = plt.subplots(
    2, 2,
    figsize=(10.4, 6.4),
    gridspec_kw={"height_ratios": [1.08, 0.78]},
)
a, b, c, d = axes.ravel()

# Panel a
q = source.loc[source["panel"].eq("a")].copy()
order = (
    q[["x_order", "category"]]
    .drop_duplicates()
    .sort_values("x_order")["category"]
    .tolist()
)
for series, color in [
    ("Post-connection household-months", CORAL),
    ("Unconnected household-months", NAVY),
]:
    z = (
        q.loc[q["series"].eq(series)]
        .set_index("category")
        .loc[order]
        .reset_index()
    )
    a.errorbar(
        np.arange(len(z)),
        z["estimate"],
        yerr=[
            z["estimate"] - z["conf_low"],
            z["conf_high"] - z["estimate"],
        ],
        fmt="o-",
        color=color,
        markersize=2.7,
        linewidth=0.9,
        capsize=2,
        label=series,
    )

a.set_xticks(np.arange(len(order)))
a.set_xticklabels(order, rotation=0, ha="center", fontsize=6.5)
a.tick_params(axis="x", pad=3)
a.set_xlim(-0.45, len(order) - 0.55)
a.set_ylabel("Recorded bill (RMB/month)")
heading(a, "a", "Observed half-year mean electricity bills")
style_axis(a)
handles, labels = a.get_legend_handles_labels()

# Panel b
q = source.loc[source["panel"].eq("b")].sort_values("x_order")
bars = b.bar(
    [0, 1],
    q["estimate"],
    color=[NAVY, CORAL],
    width=0.58,
)
b.set_xticks([0, 1])
b.set_xticklabels(q["category"].tolist())
for bar, value in zip(bars, q["estimate"]):
    b.text(
        bar.get_x() + bar.get_width() / 2,
        float(value) + max(q["estimate"]) * 0.025,
        f"{float(value):.1f}",
        ha="center", va="bottom",
        fontsize=8.0, color=GRAY,
    )
b.set_ylim(0, max(q["estimate"]) * 1.16)
b.set_ylabel("Recorded bill (RMB/month)")
heading(b, "b", "Complete-window within-household comparison")
style_axis(b)

# Panel c
forest(
    c,
    source.loc[source["panel"].eq("c")],
    "c",
    "Same-village calendar-matched comparison",
    "Change in bill (RMB/month)",
    ytick_fontsize=8.0,
    y_margin=0.18,
)

# Panel d
forest(
    d,
    source.loc[source["panel"].eq("d")],
    "d",
    "Burden effects by baseline income",
    "Effect (percentage points)",
    ytick_fontsize=8.0,
    y_margin=0.22,
)

a.legend(
    handles, labels,
    loc="lower left",
    bbox_to_anchor=(0.0, 1.18),
    ncol=1,
    frameon=False,
    fontsize=7.2,
    handlelength=2.0,
    labelspacing=0.35,
    borderaxespad=0.0,
)
fig.subplots_adjust(
    left=0.115,
    right=0.99,
    top=0.79,
    bottom=0.12,
    wspace=0.34,
    hspace=0.43,
)

save(fig, OUT_DIR, 21)
