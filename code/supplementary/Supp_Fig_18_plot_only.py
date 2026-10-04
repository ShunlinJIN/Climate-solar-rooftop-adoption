"""Supplementary Fig. 18: survey scheduling and observed daytime consumption.

Run with Python 3.9+ and Matplotlib. Source paths are resolved relative to this
script, so execution does not depend on the current working directory.
"""
from __future__ import annotations

import argparse
import csv
import math
import os
from pathlib import Path
import tempfile

if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = str(Path(tempfile.gettempdir()) / "solar_matplotlib")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ACTIVITIES = [
    "Laundry",
    "Charging an electric vehicle or tricycle",
    "Heating water",
    "Water pump or agricultural appliance",
]
LABELS = ["Laundry", "EV / tricycle charging", "Water heating", "Water pump /\nagricultural appliance"]
RESPONSES = ["Never", "Rarely", "Sometimes", "Often", "Always"]
SURVEY_COLORS = ["#E5E7E9", "#C7DAE0", "#91BDCD", "#4D91AE", "#1D587C"]
SYSTEMS = ["RRPV-only", "RRPV-BS"]
SYSTEM_COLORS = ["#159D94", "#3F6FA6"]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_survey(data_dir):
    rows = read_csv(data_dir / "supp_fig18_survey_frequencies.csv")
    if len(rows) != 20:
        raise ValueError("Expected four activities and five response categories.")
    result = []
    for activity in ACTIVITIES:
        subset = [row for row in rows if row["activity"] == activity]
        if len(subset) != 5 or {r["response"] for r in subset} != set(RESPONSES):
            raise ValueError(f"Incomplete or duplicate responses for {activity}.")
        ns = {int(r["valid_n"]) for r in subset}
        if len(ns) != 1 or min(ns) <= 0:
            raise ValueError(f"Inconsistent denominator for {activity}.")
        n = ns.pop()
        counts = {r["response"]: int(r["count"]) for r in subset}
        if min(counts.values()) < 0 or sum(counts.values()) != n:
            raise ValueError(f"Response counts do not sum to valid N for {activity}.")
        result.append({"activity": activity, "valid_n": n,
                       "counts": [counts[r] for r in RESPONSES],
                       "percentages": [100 * counts[r] / n for r in RESPONSES],
                       "often_always_pct": 100 * (counts["Often"] + counts["Always"]) / n})
    return result


def load_hourly(data_dir):
    rows = read_csv(data_dir / "supp_fig18_hourly_profile_2020.csv")
    if len(rows) != 48 or {r["system"] for r in rows} != set(SYSTEMS):
        raise ValueError("Expected 24 clock-hour means for each system type.")
    result = []
    for system in SYSTEMS:
        subset = sorted([r for r in rows if r["system"] == system], key=lambda r: int(r["hour"]))
        if [int(r["hour"]) for r in subset] != list(range(24)):
            raise ValueError(f"Missing or duplicate clock hours for {system}.")
        years = {int(r["year"]) for r in subset}
        household_counts = {int(r["households"]) for r in subset}
        day_counts = {int(r["household_days"]) for r in subset}
        if years != {2020} or len(household_counts) != 1 or len(day_counts) != 1:
            raise ValueError(f"The figure requires balanced 2020 coverage for {system}.")
        households = household_counts.pop()
        household_days = day_counts.pop()
        if households <= 0 or household_days != households * 366:
            raise ValueError(f"Unexpected household-day coverage for {system}.")
        loads = [float(r["mean_total_load_kwh"]) for r in subset]
        if not all(math.isfinite(x) and x >= 0 for x in loads):
            raise ValueError(f"Invalid consumption values for {system}.")
        daytime = sum(loads[6:19])
        total = sum(loads)
        if total <= 0:
            raise ValueError(f"Nonpositive daily consumption for {system}.")
        result.append({"system": system, "year": 2020, "households": households,
                       "household_days": household_days, "household_hours": household_days * 24,
                       "daytime_kwh": daytime, "nighttime_kwh": total - daytime,
                       "total_kwh": total, "daytime_share_pct": 100 * daytime / total})
    return result


def separate_axes(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("bottom", "left"):
        ax.spines[side].set_position(("outward", 6))
        ax.spines[side].set_linewidth(0.75)
        ax.spines[side].set_color("#222222")
    ax.tick_params(direction="out", length=3, width=0.7, colors="#222222", pad=5)
    ax.grid(False)


def make_figure(survey, hourly, output_dir, dpi):
    plt.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
        "font.size": 10, "axes.labelsize": 10.5, "axes.titlesize": 11,
        "xtick.labelsize": 9.5, "ytick.labelsize": 10, "text.color": "#222222",
        "axes.labelcolor": "#222222", "pdf.fonttype": 42, "ps.fonttype": 42,
        "svg.fonttype": "none", "savefig.facecolor": "white", "figure.facecolor": "white",
    })
    fig = plt.figure(figsize=(12, 4.6))
    ax_a = fig.add_axes([0.195, 0.245, 0.400, 0.600])
    ax_b = fig.add_axes([0.760, 0.245, 0.210, 0.600])
    y = list(range(len(survey)))
    left = [0.0] * len(survey)
    for j, response in enumerate(RESPONSES):
        widths = [row["percentages"][j] for row in survey]
        ax_a.barh(y, widths, left=left, height=0.58, color=SURVEY_COLORS[j],
                  edgecolor="white", linewidth=0.65, zorder=2)
        for i, width in enumerate(widths):
            ax_a.text(left[i] + width / 2, i, f"{width:.1f}", ha="center", va="center",
                      color="white" if j >= 3 else "#222222", fontsize=8.5)
            left[i] += width
    ax_a.set_xlim(0, 100)
    ax_a.set_ylim(3.55, -0.55)
    ax_a.set_xticks([0, 20, 40, 60, 80, 100])
    ax_a.set_yticks(y)
    ax_a.set_yticklabels([f"{label}\n(n = {row['valid_n']:,})" for label, row in zip(LABELS, survey)])
    ax_a.set_xlabel("Share of valid responses (%)", labelpad=10)
    separate_axes(ax_a)
    ax_a.spines["bottom"].set_bounds(0, 100)
    ax_a.spines["left"].set_bounds(0, 3)
    ax_a.tick_params(axis="y", length=0, pad=8)
    legend = [Patch(facecolor=c, edgecolor="none", label=r) for c, r in zip(SURVEY_COLORS, RESPONSES)]
    fig.legend(handles=legend, loc="lower center", bbox_to_anchor=(0.395, 0.030),
               ncol=5, frameon=False, fontsize=9, handlelength=1.25,
               handletextpad=0.45, columnspacing=0.9)

    values = [r["daytime_share_pct"] for r in hourly]
    ax_b.bar([0, 1], values, width=0.56, color=SYSTEM_COLORS, edgecolor="none", zorder=2)
    for i, value in enumerate(values):
        ax_b.text(i, value + 2.2, f"{value:.1f}%", ha="center", va="bottom", fontsize=11)
    ax_b.set_xlim(-0.65, 1.65)
    ax_b.set_ylim(0, 100)
    ax_b.set_xticks([0, 1])
    ax_b.set_xticklabels([f"{r['system']}\n(n = {r['households']:,})" for r in hourly])
    ax_b.set_yticks([0, 20, 40, 60, 80, 100])
    ax_b.set_ylabel("Daytime share of total consumption (%)", labelpad=11)
    separate_axes(ax_b)
    ax_b.spines["bottom"].set_bounds(-0.40, 1.40)
    ax_b.spines["left"].set_bounds(0, 100)
    ax_b.tick_params(axis="x", length=0, pad=8)

    fig.text(0.023, 0.943, "a", weight="bold", fontsize=14, va="center")
    fig.text(0.655, 0.943, "b", weight="bold", fontsize=14, va="center")
    fig.text(0.395, 0.944, "Scheduling flexible electricity use", ha="center", va="center", fontsize=11)
    fig.text(0.865, 0.944, "Daytime electricity consumption", ha="center", va="center", fontsize=11)
    fig.text(0.395, 0.892, "Sunny daytime hours", ha="center", va="center", fontsize=9.5, color="#555555")
    fig.text(0.865, 0.892, "06:00–18:59, 2020", ha="center", va="center", fontsize=9.5, color="#555555")
    stem = output_dir / "Supplementary_Fig_18"
    for suffix in ("svg", "pdf", "png"):
        metadata = {"Creator": "Shunlin Jin"} if suffix in ("svg", "pdf") else {"Author": "Shunlin Jin"}
        fig.savefig(stem.with_suffix("." + suffix), dpi=dpi, metadata=metadata)
    plt.close(fig)


def export_summaries(survey, hourly, output_dir):
    with (output_dir / "Supplementary_Fig_18_survey_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["activity", "valid_n", "often_or_always_n", "often_or_always_pct"])
        writer.writeheader()
        for row in survey:
            writer.writerow({"activity": row["activity"], "valid_n": row["valid_n"],
                             "often_or_always_n": sum(row["counts"][3:]),
                             "often_or_always_pct": row["often_always_pct"]})
    with (output_dir / "Supplementary_Fig_18_daytime_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(hourly[0]))
        writer.writeheader()
        writer.writerows(hourly)


def main():
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=root / "data")
    parser.add_argument("--output-dir", type=Path, default=root / "output")
    parser.add_argument("--dpi", type=int, default=600)
    args = parser.parse_args()
    if args.dpi < 150:
        parser.error("Use at least 150 dpi; the default is 600 dpi.")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    survey = load_survey(args.data_dir)
    hourly = load_hourly(args.data_dir)
    make_figure(survey, hourly, args.output_dir, args.dpi)
    export_summaries(survey, hourly, args.output_dir)
    for row in survey:
        print(f"{row['activity']}: often/always = {row['often_always_pct']:.1f}% (n = {row['valid_n']})")
    for row in hourly:
        print(f"{row['system']}: daytime share = {row['daytime_share_pct']:.4f}%")
    print(f"Output: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
