#!/usr/bin/env python3
"""Render Figure 5 from its source estimates and descriptive statistics."""
from pathlib import Path
import argparse
import gc
import os
import tempfile

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "solar_matplotlib"))

for thread_key in ("OPENBLAS_NUM_THREADS", "OPENBLAS_DEFAULT_NUM_THREADS",
                   "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[thread_key] = "1"

import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter
from figure5_helpers import *


PANEL_E_CAPTION = (
    "Panel e reports the post-adoption change in the slope of daily electricity use "
    "with respect to temperature above 30°C, estimated using a continuous piecewise-linear "
    "specification and expressed in kWh per day per °C. Both estimates use the same sample "
    "and include household fixed effects. The baseline specification includes village-by-date "
    "fixed effects; the alternative includes village-by-year-month fixed effects. "
    "Horizontal error bars indicate 95% confidence intervals (Supplementary Note 25)."
)

PANEL_F_CAPTION = (
    "Panel f reports estimated changes in the monthly probability that electricity expenditure "
    "is at or above 5% of fixed pre-adoption household income, for all households and by "
    "pre-adoption per-capita household income. Effects are averaged over months +1 to +12 "
    "after grid connection and expressed in percentage points. Lower- and higher-income groups "
    "fall below and at or above RMB 1,220 per capita per month, respectively (Supplementary Note 25)."
)

CAPTION = (
    "Fig. 5 | Alleviation of rural household energy poverty.\n"
    "Notes: This figure shows how rooftop solar and battery storage alleviate household energy poverty. "
    "Panel a shows monthly changes in recorded electricity expenditure around PV grid connection; "
    "panel b shows changes in the electricity-bill-to-income ratio; and panel c shows changes in total "
    "household electricity use and public-grid purchases. Panels a–c report event-study estimates. "
    "They compare each adopter’s outcomes with a no-connection counterfactual constructed from "
    "households that never connect and future adopters observed before connection. Event time is "
    "defined by the household’s PV grid-connection month. Month −1 is the reference period. Shaded "
    "bands indicate 95% confidence intervals. Panel d reports changes in non-PV income, PV export "
    "revenue, total income including PV revenue, and income including PV revenue net of electricity bill. "
    + PANEL_E_CAPTION + " "
    + PANEL_F_CAPTION + " "
    "Panel g reports 2SLS estimates linking extreme "
    "heat, RRPV adoption and household energy poverty, with bars showing coefficient estimates. "
    "Electricity expenditure is displayed in US$ per month, the electricity-bill-to-income ratio "
    "in percentage points, and total electricity use and public-grid purchases in units of 10 kWh "
    "per month; bar labels give coefficients in US$, percentage points and kWh. Panel h reports "
    "battery-supply outcomes among the respondents who experienced a recent outage. Panel i reports "
    "battery backup duration. Monetary values are converted at RMB 6.8 per US$1. Error bars in "
    "panels d–g indicate 95% confidence intervals for estimated effects.\n"
)


def read_slope_data(path):
    source = pd.read_csv(path)
    needed = {"household_fixed_effects", "time_fixed_effects", "temperature_range", "estimate",
              "conf_low", "conf_high", "observations", "households", "adopters", "clusters"}
    if not needed.issubset(source.columns):
        raise ValueError(f"Missing slope fields: {sorted(needed - set(source.columns))}")
    if len(source) != 2 or set(source.time_fixed_effects) != {"village_date", "village_year_month"}:
        raise ValueError("Panel e requires exactly one estimate for each fixed-effects specification.")
    if not source.household_fixed_effects.eq("Yes").all() or not source.temperature_range.eq(">30 C").all():
        raise ValueError("Both estimates must include household fixed effects and refer to temperatures above 30°C.")
    for name in ("observations", "households", "adopters", "clusters"):
        if source[name].nunique() != 1:
            raise ValueError(f"The two specifications must use the same sample: {name} differs.")
    vals = source[["estimate", "conf_low", "conf_high"]].to_numpy(float)
    if not np.isfinite(vals).all() or not ((vals[:, 1] <= vals[:, 0]) & (vals[:, 0] <= vals[:, 2])).all():
        raise ValueError("Invalid point estimates or confidence limits in panel e.")
    return source


def panel_e(ax, source):
    frame = source.set_index("time_fixed_effects").loc[["village_date", "village_year_month"]]
    est, lo, hi = [frame[column].to_numpy(float) for column in ("estimate", "conf_low", "conf_high")]
    ax.axvline(0, color=GRAY, ls="--", lw=0.75, zorder=1)
    ax.errorbar(est, [1, 0], xerr=[est - lo, hi - est], fmt="o",
                color=TEAL, markerfacecolor=TEAL, markeredgecolor=TEAL,
                markeredgewidth=0.9, ecolor=GRAY, markersize=4,
                capsize=2.1, linewidth=0.9, zorder=3)
    ax.set_yticks([1, 0], ["Household FE +\nvillage × date FE",
                          "Household FE +\nvillage × year-month FE"])
    ax.set_ylim(-0.55, 1.55)
    ax.set_xlim(-0.025, 0.265)
    ax.set_xticks([0, 0.05, 0.10, 0.15, 0.20, 0.25])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: "0" if abs(x) < 1e-10 else f"{x:.2f}"))
    ax.set_xlabel("Post-adoption slope change\n(kWh/day/°C)")
    heading(ax, "e", "Electricity-use response\nabove 30°C")
    style_axis(ax)


def iv_display_data(source, rmb_per_usd):
    source = source.copy()
    money = source.outcome.eq("bill_rmb")
    source["display_divisor"] = source.display_divisor.astype(float)
    source.loc[money, "display_divisor"] = rmb_per_usd
    for native, shown in [("estimate", "display_estimate"), ("std_error", "display_std_error"),
                          ("ci_low", "display_ci_low"), ("ci_high", "display_ci_high")]:
        source[shown] = source[native] / source.display_divisor
    source["display_unit"] = np.select(
        [money, source.outcome.eq("bill_income_pp")],
        ["US$/month", "percentage points"], default="10 kWh/month")
    return source


def main():
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=root / "data")
    parser.add_argument("--output", type=Path, default=root)
    parser.add_argument("--rmb-per-usd", type=float, default=6.8)
    parser.add_argument("--png-dpi", "--dpi", dest="png_dpi", type=png_dpi_value, default=300)
    parser.add_argument("--panels-only", action="store_true", help="Render only panel e and the d–f comparison.")
    args = parser.parse_args()
    if not np.isfinite(args.rmb_per_usd) or args.rmb_per_usd <= 0:
        raise ValueError("Currency conversion must be positive and finite.")
    args.output.mkdir(parents=True, exist_ok=True)
    data = load_final_data(args.data_dir / "figure5_plot_data.csv")
    e = read_slope_data(args.data_dir / "figure5_panel_e_slopes.csv")
    burden = pd.read_csv(args.data_dir / "Figure5_panel_f_source_data.csv")
    set_style()
    if not args.panels_only:
        g = iv_display_data(pd.read_csv(args.data_dir / "figure5_panel_g.csv"), args.rmb_per_usd)
        fig, axes = plt.subplots(3, 3, figsize=(12.3, 11.2))
        a, b, c, d, ee, f, gg, h, i = axes.ravel()
        fig.subplots_adjust(left=.175, right=.98, top=.94, bottom=.075, wspace=.75, hspace=.70)
        event_panel(a, data["monthly_dynamic"], "electricity_bill_rmb", "a", "Electricity expenditure",
                    "Effect (US$/month)", scale=args.rmb_per_usd)
        event_panel(b, data["monthly_dynamic"], "bill_income_ratio_current_pct", "b",
                    "Electricity-bill-to-income\nratio", "Effect (percentage points)")
        panel_c(c, data["monthly_dynamic"])
        panel_d(d, data["income_static"], args.rmb_per_usd)
        panel_e(ee, e)
        panel_f(f, burden)
        iv_panel(gg, g)
        bar_distribution(h, outage_summary(data["supply"]), "h", "Battery supply\nduring outages",
                         "Respondents (%)", [TEAL, ORANGE, NAVY])
        bar_distribution(i, duration_distribution(data["duration"]), "i", "Reported backup\nduration",
                         "Respondents (%)", [LIGHT_GRAY, BLUE, DEEP_BLUE, NAVY])
        save_formats(fig, args.output, "Figure_5", png_dpi=args.png_dpi)
        plt.close(fig)
        del fig, axes, a, b, c, d, ee, f, gg, h, i
        gc.collect()
    fig, axes = plt.subplots(1, 3, figsize=(12.3, 3.7))
    fig.subplots_adjust(left=.155, right=.985, top=.79, bottom=.22, wspace=.78)
    panel_d(axes[0], data["income_static"], args.rmb_per_usd)
    panel_e(axes[1], e)
    panel_f(axes[2], burden)
    save_formats(fig, args.output, "Figure_5_def_preview", png_dpi=args.png_dpi)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(5.2, 3.7))
    fig.subplots_adjust(left=.43, right=.965, top=.79, bottom=.22)
    panel_e(ax, e)
    save_formats(fig, args.output, "Figure_5e", png_dpi=args.png_dpi)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(5.2, 3.7))
    fig.subplots_adjust(left=.32, right=.965, top=.79, bottom=.22)
    panel_f(ax, burden)
    save_formats(fig, args.output, "Figure_5f", png_dpi=args.png_dpi)
    plt.close(fig)
    caption = CAPTION.replace("RMB 6.8 per US$1", f"RMB {args.rmb_per_usd:g} per US$1")
    (args.output / "Figure_5_caption.txt").write_text(caption, encoding="utf-8")
    (args.output / "Figure_5e_caption.txt").write_text(PANEL_E_CAPTION + "\n", encoding="utf-8")
    (args.output / "Figure_5f_caption.txt").write_text(PANEL_F_CAPTION + "\n", encoding="utf-8")
    print(f"Figures saved in: {args.output.resolve()}")


if __name__ == "__main__":
    main()
