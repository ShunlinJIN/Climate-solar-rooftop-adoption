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
    args = parser.parse_args()
    if not np.isfinite(args.rmb_per_usd) or args.rmb_per_usd <= 0:
        raise ValueError("Currency conversion must be positive and finite.")
    args.output.mkdir(parents=True, exist_ok=True)
    data = load_final_data(args.data_dir / "figure5_plot_data.csv")
    e = read_slope_data(args.data_dir / "figure5_panel_e_slopes.csv")
    burden = pd.read_csv(args.data_dir / "Figure5_panel_f_source_data.csv")
    set_style()
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
    print(f"Figure saved in: {args.output.resolve()}")


if __name__ == "__main__":
    main()
