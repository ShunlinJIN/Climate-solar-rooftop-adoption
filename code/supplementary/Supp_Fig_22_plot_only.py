#!/usr/bin/env python
# -*- coding: utf-8 -*-
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _supp_fig21_23_common import (
    TEAL, CORAL, NAVY, GRAY, LIGHT,
    project_paths, read_csv, set_style, style_axis, heading, save
)

DATA_DIR, OUT_DIR = project_paths(__file__)
set_style()
source = read_csv(DATA_DIR / "supp_fig22_source.csv")

fig, axes = plt.subplots(
    2, 2,
    figsize=(10.4, 6.7),
    gridspec_kw={"height_ratios": [1.02, 0.96]},
)
a, b, c, d = axes.ravel()

shared_handles = None
shared_labels = None

# Panels a and b
for ax, panel, letter, title, ylabel in [
    (a, "a", "a", "Recorded electricity bill", "Effect (RMB/month)"),
    (b, "b", "b", "Electricity-bill-to-income ratio",
     "Effect (percentage points)"),
]:
    q = source.loc[source["panel"].eq(panel)].copy()
    ax.axhline(0, color=GRAY, linestyle="--", linewidth=0.65)
    ax.axvline(-0.5, color=GRAY, linestyle=":", linewidth=0.65)

    for series, color in [
        ("BJS imputation", TEAL),
        ("Callaway–Sant'Anna", CORAL),
    ]:
        z = q.loc[q["series"].eq(series)].sort_values("x_order")
        ax.plot(
            z["x_order"],
            z["estimate"],
            "o-",
            color=color,
            markersize=2.8,
            linewidth=1.0,
            label=series,
        )

    ax.set_xticks([-12, -6, -1, 0, 6, 12, 18, 24])
    ax.set_xlabel("Months relative to grid connection")
    ax.set_ylabel(ylabel)
    heading(ax, letter, title)
    style_axis(ax)

    if shared_handles is None:
        shared_handles, shared_labels = ax.get_legend_handles_labels()

# Panel c
q = source.loc[source["panel"].eq("c")].copy()
outcome_order = ["Bill", "Burden", "Total use", "Grid purchases"]
display_labels = ["Bill", "Burden", "Total\nuse", "Grid\npurchases"]
estimators = ["BJS", "Callaway–Sant'Anna", "Sun–Abraham"]
colors = [TEAL, CORAL, NAVY]
x = np.arange(len(outcome_order))
width = 0.23

for index, (estimator, color) in enumerate(zip(estimators, colors)):
    z = (
        q.loc[q["series"].eq(estimator)]
        .set_index("category")
        .loc[outcome_order]
        .reset_index()
    )
    values = z["estimate"].to_numpy(float)
    bars = c.bar(
        x + (index - 1) * width,
        values,
        width=width,
        color=color,
        label=estimator,
    )
    for bar, value in zip(bars, values):
        c.text(
            bar.get_x() + bar.get_width() / 2,
            float(value) + 1.8,
            f"{float(value):.0f}",
            ha="center", va="bottom",
            fontsize=7.1, color=GRAY,
        )

c.axhline(100, color=GRAY, linestyle="--", linewidth=0.65)
c.set_xticks(x)
c.set_xticklabels(display_labels, rotation=0, ha="center", fontsize=7.5)
c.tick_params(axis="x", pad=4)
c.set_ylabel("Magnitude relative to BJS (%)")
c.set_ylim(0, 158)
c.legend(
    frameon=False,
    ncol=3,
    loc="upper center",
    bbox_to_anchor=(0.5, 0.99),
    fontsize=7.2,
    handlelength=1.4,
    columnspacing=1.0,
)
heading(c, "c", "Average effects across modern estimators")
style_axis(c)

# Panel d
q = source.loc[source["panel"].eq("d")].copy()
q["cohort_date"] = pd.to_datetime(q["category"])
large = q.loc[q["size_group"].eq("≥10 treated households")].copy()
small = q.loc[q["size_group"].eq("<10 treated households")].copy()

d.axhline(0, color=GRAY, linestyle="--", linewidth=0.65)
d.scatter(
    small["cohort_date"],
    small["estimate"],
    s=10,
    color=LIGHT,
    alpha=0.85,
)
d.errorbar(
    large["cohort_date"],
    large["estimate"],
    yerr=[
        large["estimate"] - large["conf_low"],
        large["conf_high"] - large["estimate"],
    ],
    fmt="o",
    color=TEAL,
    ecolor=GRAY,
    markersize=3.8,
    capsize=2.0,
    linewidth=0.9,
)
d.set_ylabel("Bill effect (RMB/month)")
d.set_xlabel("Grid-connection cohort")
d.xaxis.set_major_locator(mdates.MonthLocator(interval=12))
d.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
d.tick_params(axis="x", rotation=0, labelsize=6.4, pad=4)
for tick_label in d.get_xticklabels():
    tick_label.set_horizontalalignment("center")
d.margins(x=0.04)
heading(d, "d", "Cohort-specific bill effects", pad=15)
d.text(
    0.5, 1.01,
    "Gray: <10 treated households; teal: ≥10 treated households",
    transform=d.transAxes,
    ha="center", va="bottom",
    fontsize=7.0, color=GRAY,
    clip_on=False,
)
style_axis(d)

fig.legend(
    shared_handles,
    shared_labels,
    loc="upper center",
    bbox_to_anchor=(0.5, 0.985),
    ncol=2,
    frameon=False,
    fontsize=7.4,
    handlelength=2.0,
    columnspacing=1.8,
)
fig.subplots_adjust(
    left=0.10,
    right=0.99,
    top=0.86,
    bottom=0.13,
    wspace=0.32,
    hspace=0.44,
)

save(fig, OUT_DIR, 22)
