#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


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
source = read_csv(DATA_DIR / "supp_fig23_source.csv")

fig, axes = plt.subplots(
    3, 2,
    figsize=(10.8, 9.6),
    gridspec_kw={"height_ratios": [0.92, 1.16, 1.04]},
)
a, b, c, d, e, f = axes.ravel()

# Panels a and b
for ax, panel, letter, title, xlabel in [
    (a, "a", "a", "Recorded bill across specifications",
     "Effect (RMB/month)"),
    (b, "b", "b", "Grid purchases across specifications",
     "Effect (kWh/month)"),
]:
    forest(
        ax,
        source.loc[source["panel"].eq(panel)],
        letter,
        title,
        xlabel,
        wrap_width=26,
        ytick_fontsize=7.5,
        y_margin=0.10,
    )

# The two panels use identical specification rows; suppress duplicates on b.
b.set_yticklabels([])
b.tick_params(axis="y", length=0)

# Panel c
forest(
    c,
    source.loc[source["panel"].eq("c")],
    "c",
    "Fake grid-connection dates",
    "Placebo effect (% of main-effect magnitude)",
    wrap_width=22,
    ytick_fontsize=7.4,
    y_margin=0.09,
)

# Panel d
q = (
    source.loc[source["panel"].eq("d")]
    .sort_values("x_order")
    .iloc[::-1]
    .reset_index(drop=True)
)
y = np.arange(len(q))
d.axvline(0.05, color=GRAY, linestyle="--", linewidth=0.65)
d.scatter(q["estimate"], y, color=TEAL, s=24)
d.set_yticks(y)
d.set_yticklabels(q["category"], fontsize=7.4)
d.set_xlabel("Joint-test P value")
d.margins(y=0.09)
heading(d, "d", "Pre-connection joint tests")
style_axis(d)

# Panel e
forest(
    e,
    source.loc[source["panel"].eq("e")],
    "e",
    "Alternative control groups",
    "Magnitude relative to not-yet-treated control (%)",
    wrap_width=23,
    ytick_fontsize=7.4,
    y_margin=0.09,
)

# Panel f
q = source.loc[source["panel"].eq("f")].sort_values("x_order")
f.fill_between(
    q["x_order"],
    q["conf_low"],
    q["conf_high"],
    color=TEAL,
    alpha=0.20,
)
f.plot(q["x_order"], q["conf_low"], color=TEAL, linewidth=0.85)
f.plot(q["x_order"], q["conf_high"], color=TEAL, linewidth=0.85)
f.axhline(0, color=GRAY, linestyle="--", linewidth=0.65)
f.set_xlabel("Relative-magnitude bound M")
f.set_ylabel("Robust 95% CI (RMB/month)")
heading(f, "f", "Official HonestDiD sensitivity")
style_axis(f)

fig.subplots_adjust(
    left=0.17,
    right=0.99,
    top=0.975,
    bottom=0.08,
    wspace=0.48,
    hspace=0.50,
)

save(fig, OUT_DIR, 23)
