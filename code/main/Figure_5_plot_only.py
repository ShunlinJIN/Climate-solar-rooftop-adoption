#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone reproduction code for Main Figure 5.

PUBLIC-PLOTTING NOTE
----------------------
The household-, installation-, and provider-level microdata used to estimate
the results plotted in this figure are subject to data-use restrictions
and cannot be publicly released.

This script reproduces the published figure from the non-identifying aggregate
plotting inputs supplied in ../data/figure5_plot_data.csv. It does NOT
re-estimate the underlying statistical models from restricted-source microdata.

The plotting logic matches the final August 20, 2026 Figure 5 workflow:
- panels a-c unchanged from the frozen high-resolution source;
- panel d uses "Post-grid-connection change";
- panel e uses daily mean temperature >30C and separate non-extreme/extreme
  state-specific post-grid-connection effects;
- panel f uses "Adopter vs non-adopter difference";
- panels g-i unchanged.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CORAL = "#E76F51"
NAVY = "#264653"
ORANGE = "#F4A261"
TEAL = "#2A9D8F"
BLUE = "#4C83A5"
DEEP_BLUE = "#005A9C"
GRAY = "#5A5A5A"
LIGHT_GRAY = "#D9D9D9"


def set_style():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "DejaVu Sans"],
        "font.size": 7.5,
        "axes.titlesize": 8.6,
        "axes.labelsize": 7.4,
        "xtick.labelsize": 6.6,
        "ytick.labelsize": 6.6,
        "legend.fontsize": 6.2,
        "axes.linewidth": 0.75,
        "xtick.major.width": 0.75,
        "ytick.major.width": 0.75,
        "xtick.major.size": 3.0,
        "ytick.major.size": 3.0,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })


def style_axis(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def heading(ax, letter, title, pad=7.0):
    ax.text(
        -0.17, 1.045, letter,
        transform=ax.transAxes,
        ha="left", va="bottom",
        fontsize=9.3, fontweight="bold",
        clip_on=False,
    )
    ax.set_title(title, loc="center", pad=pad, fontsize=8.6, fontweight="normal")


def load_final_data(path):
    df = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
    required = {"figure_panel"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    return {
        "monthly_dynamic": df.loc[df["figure_panel"].astype(str).eq("a-c")].copy(),
        "income_static": df.loc[df["figure_panel"].astype(str).eq("d")].copy(),
        "hotday": df.loc[df["figure_panel"].astype(str).eq("e")].copy(),
        "cross": df.loc[df["figure_panel"].astype(str).eq("f")].copy(),
        "services": df.loc[df["figure_panel"].astype(str).eq("g")].copy(),
        "supply": df.loc[df["figure_panel"].astype(str).eq("h")].copy(),
        "duration": df.loc[df["figure_panel"].astype(str).eq("i")].copy(),
    }


def event_panel(ax, dynamic, outcome, letter, title, ylabel, scale=1.0):
    data = dynamic.loc[
        dynamic["specification"].eq("main")
        & dynamic["outcome"].eq(outcome)
    ].sort_values("event_time_month")

    if data.empty:
        raise ValueError(f"No event-study rows found for {outcome}")

    x = pd.to_numeric(data["event_time_month"]).to_numpy(float)
    y = pd.to_numeric(data["estimate"]).to_numpy(float) / scale
    low = pd.to_numeric(data["conf_low"]).to_numpy(float) / scale
    high = pd.to_numeric(data["conf_high"]).to_numpy(float) / scale

    ax.axhline(0, linestyle="--", linewidth=0.75, color=GRAY)
    ax.axvline(-1, linestyle=":", linewidth=0.75, color=GRAY)
    ax.fill_between(x, low, high, color=TEAL, alpha=0.14, linewidth=0)
    ax.plot(
        x, y, color=TEAL, marker="o",
        markerfacecolor=TEAL, markeredgecolor=TEAL,
        markeredgewidth=0.5, markersize=2.8, linewidth=1.0, zorder=3
    )
    heading(ax, letter, title)
    ax.set_xlabel("Months relative to\ngrid connection")
    ax.set_ylabel(ylabel)
    ax.set_xticks([-12, -6, -1, 6, 12, 18, 24])
    style_axis(ax)


def panel_c(ax, dynamic):
    ax.axhline(0, linestyle="--", linewidth=0.75, color=GRAY)
    ax.axvline(-1, linestyle=":", linewidth=0.75, color=GRAY)

    series = {}
    for outcome, colour in [
        ("total_electricity_consumption_kwh", CORAL),
        ("grid_import_kwh", NAVY),
    ]:
        data = dynamic.loc[
            dynamic["specification"].eq("main")
            & dynamic["outcome"].eq(outcome)
        ].sort_values("event_time_month")
        x = pd.to_numeric(data["event_time_month"]).to_numpy(float)
        est = pd.to_numeric(data["estimate"]).to_numpy(float)
        ax.fill_between(
            x,
            pd.to_numeric(data["conf_low"]).to_numpy(float),
            pd.to_numeric(data["conf_high"]).to_numpy(float),
            color=colour, alpha=0.10, linewidth=0,
        )
        ax.plot(
            x, est, color=colour, marker="o",
            markerfacecolor=colour, markeredgecolor=colour,
            markeredgewidth=0.4, markersize=2.7, linewidth=1.0, zorder=3
        )
        series[outcome] = data

    vals = pd.concat(
        [series[k][["estimate"]] for k in series], ignore_index=True
    )["estimate"].astype(float)
    y_min = float(vals.min())
    y_max = float(vals.max())
    y_range = max(y_max-y_min, 1.0)

    ax.text(15.0, y_max-0.24*y_range, "Total use",
            color=CORAL, fontsize=6.8, ha="left", va="center")
    ax.text(15.0, y_min+0.44*y_range, "Grid purchases",
            color=NAVY, fontsize=6.8, ha="left", va="center")

    heading(ax, "c", "Total electricity use and grid purchase")
    ax.set_xlabel("Months relative to\ngrid connection")
    ax.set_ylabel("Effect (kWh/month)")
    ax.set_xticks([-12, -6, -1, 6, 12, 18, 24])
    style_axis(ax)


def panel_d(ax, income, rmb_per_usd):
    order = [
        "monthly_nonpv_income_rmb",
        "monthly_pv_revenue_rmb",
        "monthly_income_including_pv_rmb",
        "monthly_resources_after_electricity_rmb",
    ]
    labels = {
        "monthly_nonpv_income_rmb": "Non-PV income",
        "monthly_pv_revenue_rmb": "PV export revenue",
        "monthly_income_including_pv_rmb": "Total income incl.\nPV revenue",
        "monthly_resources_after_electricity_rmb":
            "Income incl. PV revenue,\nnet of electricity bill",
    }

    plot = income.set_index("outcome").loc[order].reset_index().iloc[::-1].reset_index(drop=True)
    for col in ["estimate", "conf_low", "conf_high"]:
        plot[col] = pd.to_numeric(plot[col]) / rmb_per_usd

    y = np.arange(len(plot))
    ax.axvline(0, linestyle="--", linewidth=0.75, color=GRAY)
    for idx, row in plot.iterrows():
        diagnostic = row["outcome"] == "monthly_nonpv_income_rmb"
        colour = BLUE if diagnostic else TEAL
        ax.errorbar(
            float(row["estimate"]), y[idx],
            xerr=[[float(row["estimate"])-float(row["conf_low"])],
                  [float(row["conf_high"])-float(row["estimate"])]],
            fmt="o", color=colour,
            markerfacecolor="white" if diagnostic else colour,
            markeredgecolor=colour, markeredgewidth=0.9,
            ecolor=GRAY, markersize=4.0, capsize=2.1, linewidth=0.9,
        )
    ax.set_yticks(y)
    ax.set_yticklabels([labels[x] for x in plot["outcome"]])
    ax.set_xlabel("Post-grid-connection change\n(US$/month)")
    heading(ax, "d", "Household income and electricity expenditure")
    style_axis(ax)


def panel_e(ax, hotday):
    y_map = {"Non-extreme days": 1.0, "Extreme-heat days": 0.0}
    outcomes = [
        ("total_electricity_consumption_kwh", "Total use", CORAL, -0.10),
        ("grid_import_kwh", "Grid purchases", NAVY, 0.10),
    ]

    plot = hotday.copy()
    plot["y_base"] = plot["heat_state"].map(y_map)

    ax.axvline(0, linestyle="--", linewidth=0.75, color=GRAY)
    for outcome, label, colour, offset in outcomes:
        subset = plot.loc[plot["outcome"].eq(outcome)].copy()
        subset["order"] = subset["heat_state"].map(
            {"Non-extreme days": 1, "Extreme-heat days": 0}
        )
        subset = subset.sort_values("order", ascending=False)

        est = pd.to_numeric(subset["estimate"])
        lo = pd.to_numeric(subset["conf_low"])
        hi = pd.to_numeric(subset["conf_high"])
        y = pd.to_numeric(subset["y_base"]) + offset

        ax.errorbar(
            est, y,
            xerr=[est-lo, hi-est],
            fmt="o", color=colour, ecolor=colour,
            markersize=3.8, capsize=2.0, linewidth=0.9,
            label=label,
        )

    ax.set_yticks([1.0, 0.0])
    ax.set_yticklabels(["Non-extreme days", "Extreme-heat days"])
    ax.set_ylim(-0.65, 1.70)
    ax.set_xlabel("Post-grid-connection effect\n(kWh/day)")
    ax.legend(
        frameon=False, loc="upper center",
        bbox_to_anchor=(0.56, 0.99), ncol=2,
        handlelength=1.6, columnspacing=1.05, borderaxespad=0.0
    )
    heading(ax, "e", "Electricity services by heat state", pad=10.5)
    style_axis(ax)


def panel_f(ax, cross):
    order = [
        "electricity_bill_pressure_code",
        "bill_impact_crowd_out_necessities",
        "heat_curtail_air_conditioner",
        "heat_curtail_reason_bill_cost",
    ]
    labels = {
        "electricity_bill_pressure_code": "Electricity-bill\npressure",
        "bill_impact_crowd_out_necessities":
            "Essential spending cut\nto pay electricity bills",
        "heat_curtail_air_conditioner":
            "Air-conditioner use limited\nduring hot weather",
        "heat_curtail_reason_bill_cost":
            "Electricity cost cited\nfor cooling limits",
    }

    plot = (
        cross.loc[
            cross["specification"].eq("main_adjusted")
            & cross["outcome"].isin(order)
        ]
        .set_index("outcome").loc[order].reset_index()
        .iloc[::-1].reset_index(drop=True)
    )

    est = pd.to_numeric(plot["standardized_difference"])
    lo = pd.to_numeric(plot["standardized_conf_low"])
    hi = pd.to_numeric(plot["standardized_conf_high"])
    y = np.arange(len(plot))

    ax.axvline(0, linestyle="--", linewidth=0.75, color=GRAY)
    ax.errorbar(
        est, y, xerr=[est-lo, hi-est],
        fmt="o", color=TEAL, ecolor=GRAY,
        markersize=4.0, capsize=2.1, linewidth=0.9,
    )
    ax.set_yticks(y)
    ax.set_yticklabels([labels[x] for x in plot["outcome"]])
    ax.set_xlabel("Adopter vs non-adopter difference")
    heading(ax, "f", "Electricity affordability")
    style_axis(ax)


def service_panel(ax, services):
    short = {
        "Lighting and phone charging": "Lighting/phone",
        "Electric fan": "Fan",
        "Refrigerator": "Refrigerator",
        "Air conditioner": "Air conditioner",
        "Cooking or hot water": "Cooking/hot water",
        "Water pump/agricultural equipment": "Agricultural\nequipment",
    }

    plot = services.copy()
    plot["short"] = plot["service"].map(short).fillna(plot["service"])
    plot = plot.sort_values("percentage", ascending=True)
    y = np.arange(len(plot))

    ax.barh(y, plot["percentage"], color=BLUE, height=0.50)
    ax.errorbar(
        plot["percentage"], y,
        xerr=[
            plot["percentage"] - plot["conf_low_percentage"],
            plot["conf_high_percentage"] - plot["percentage"],
        ],
        fmt="none", ecolor=GRAY, capsize=2.2,
        elinewidth=0.9, capthick=0.9, zorder=4,
    )
    for idx, row in plot.reset_index(drop=True).iterrows():
        value = float(row["percentage"])
        ci_right = float(row["conf_high_percentage"])
        ax.text(
            min(max(value, ci_right)+3.2, 112.0), idx,
            f"{value:.0f}%", ha="left", va="center",
            color=GRAY, fontsize=6.2
        )
    ax.set_yticks(y)
    ax.set_yticklabels(plot["short"])
    ax.set_xlim(0, 116)
    ax.set_xlabel("RRPV-BS respondents (%)")
    heading(ax, "g", "Storage-supported household services")
    style_axis(ax)


def outage_summary(frame):
    valid = frame.loc[frame["raw_code"].isin([2,3,4])].copy()
    denominator = int(valid["count"].sum())
    appliance = int(valid.loc[valid["raw_code"].eq(3), "count"].sum())
    basic = int(valid.loc[valid["raw_code"].eq(4), "count"].sum())
    supplied = appliance + basic
    return pd.DataFrame([
        {"label":"Battery supply","count":supplied,"denominator":denominator,
         "percentage":100*supplied/denominator},
        {"label":"Appliance support","count":appliance,"denominator":denominator,
         "percentage":100*appliance/denominator},
        {"label":"Basic services maintained","count":basic,"denominator":denominator,
         "percentage":100*basic/denominator},
    ])


def duration_distribution(frame):
    valid = frame.loc[frame["raw_code"].isin([1,2,3,4])].copy()
    denominator = int(valid["count"].sum())
    labels = {1:"<1 hour",2:"1\u20133 hours",3:"3\u20136 hours",4:">6 hours"}
    rows = []
    for code in [1,2,3,4]:
        c = int(valid.loc[valid["raw_code"].eq(code), "count"].sum())
        rows.append({
            "label": labels[code],
            "count": c,
            "denominator": denominator,
            "percentage": 100*c/denominator,
        })
    return pd.DataFrame(rows)


def bar_distribution(ax, data, letter, title, xlabel, colours):
    plot = data.copy()
    y = np.arange(len(plot))
    ax.barh(y, plot["percentage"], color=colours, height=0.50, zorder=2)
    for idx, row in plot.iterrows():
        ax.text(
            min(float(row["percentage"])+2.2,104.0), idx,
            f"{float(row['percentage']):.1f}%",
            ha="left", va="center", color=GRAY, fontsize=6.2
        )
    ax.set_yticks(y)
    ax.set_yticklabels(plot["label"])
    ax.invert_yaxis()
    ax.set_xlim(0,108)
    ax.set_xticks([0,20,40,60,80,100])
    ax.set_xlabel(xlabel)
    heading(ax, letter, title)
    style_axis(ax)


def build_figure(data, out, rmb_per_usd):
    set_style()
    fig, axes = plt.subplots(3,3,figsize=(10.4,7.8))
    ax_a,ax_b,ax_c,ax_d,ax_e,ax_f,ax_g,ax_h,ax_i = axes.ravel()

    event_panel(
        ax_a, data["monthly_dynamic"], "electricity_bill_rmb",
        "a", "Electricity expenditure", "Effect (US$/month)", scale=rmb_per_usd
    )
    event_panel(
        ax_b, data["monthly_dynamic"], "bill_income_ratio_current_pct",
        "b", "Electricity-bill-to-income ratio", "Effect (percentage points)"
    )
    panel_c(ax_c, data["monthly_dynamic"])
    panel_d(ax_d, data["income_static"], rmb_per_usd)
    panel_e(ax_e, data["hotday"])
    panel_f(ax_f, data["cross"])
    service_panel(ax_g, data["services"])

    bar_distribution(
        ax_h, outage_summary(data["supply"]), "h",
        "Battery supply during outages", "Respondents (%)",
        [TEAL, ORANGE, NAVY]
    )
    bar_distribution(
        ax_i, duration_distribution(data["duration"]), "i",
        "Reported backup duration", "Respondents (%)",
        [LIGHT_GRAY, BLUE, DEEP_BLUE, NAVY]
    )

    fig.subplots_adjust(
        left=0.125, right=0.985, top=0.96, bottom=0.085,
        wspace=0.70, hspace=0.58
    )

    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out/"Figure_5.pdf", bbox_inches="tight", pad_inches=0.04, facecolor="white")
    fig.savefig(out/"Figure_5.png", dpi=300, bbox_inches="tight", pad_inches=0.04, facecolor="white")
    plt.close(fig)


def main():
    script_dir = Path(__file__).resolve().parent
    capsule_root = script_dir.parent

    default_data = capsule_root/"data"/"figure5_plot_data.csv"
    if not default_data.exists():
        # Convenient fallback for the user's local staging structure:
        default_data = script_dir/"data"/"figure5_plot_data.csv"

    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=default_data)
    parser.add_argument("--output-dir", type=Path, default=capsule_root/"output")
    parser.add_argument("--rmb-per-usd", type=float, default=6.8)
    args = parser.parse_args()

    if not args.data.exists():
        raise FileNotFoundError(args.data)
    if not math.isfinite(args.rmb_per_usd) or args.rmb_per_usd <= 0:
        raise ValueError("Invalid RMB/USD conversion")

    data = load_final_data(args.data)
    build_figure(data, args.output_dir, args.rmb_per_usd)
    print("Figure 5 reproduced successfully.")
    print(args.output_dir/"Figure_5.pdf")
    print(args.output_dir/"Figure_5.png")


if __name__ == "__main__":
    main()

