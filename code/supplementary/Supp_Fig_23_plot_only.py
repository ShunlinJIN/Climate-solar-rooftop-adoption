#!/usr/bin/env python
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _supp_fig21_23_common import (
    TEAL, GRAY,
    project_paths, read_csv, set_style, style_axis, heading,
    forest, wrap_text, save
)

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
