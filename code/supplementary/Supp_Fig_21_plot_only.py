#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from _supp_fig21_23_common import (
    CORAL, NAVY, GRAY,
    project_paths, read_csv, set_style, style_axis, heading, forest, save
)

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
