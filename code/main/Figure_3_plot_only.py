#!/usr/bin/env python3
"""Plot Figure 3 from aggregate source data. Author: Shunlin Jin."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
# The master runner stages each section as code/, data/, output/.
STAGED_DATA = SCRIPT_DIR.parent / "data/figure3_plot_data.csv"
DEFAULT_DATA = STAGED_DATA if STAGED_DATA.is_file() else ROOT / "data/non-confidential/aggregate_main/figure3_plot_data.csv"
DEFAULT_OUTPUT = SCRIPT_DIR.parent / "output" if STAGED_DATA.is_file() else ROOT / "output/figures"
GREEN = "#00894d"
BAND = "#b7f1df"
CI_GREEN = "#65c5ad"
MOTIVE_LABELS = [
    "Past outages /\nunstable voltage",
    "Future outages /\nrationing in heat",
    "Grid-tied PV:\nno outage backup",
    "Maintain basic\nservices in outages",
    "Maintain AC\nin outages",
]


def numbers(rows, key):
    return np.array([float(row[key]) for row in rows], dtype=float)


def load_data(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"panel", "x_order", "x_label", "estimate", "ci_lower",
                    "ci_upper", "count", "denominator", "share_percent"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("The source CSV is missing required Figure 3 columns.")
        rows = list(reader)
    panels = {}
    for panel, expected in (("a", 9), ("b", 5), ("c", 23), ("d", 23)):
        selected = sorted((row for row in rows if row["panel"] == panel),
                          key=lambda row: int(row["x_order"]))
        if len(selected) != expected:
            raise ValueError(f"Panel {panel} requires {expected} source-data rows.")
        if [int(row["x_order"]) for row in selected] != list(range(1, expected + 1)):
            raise ValueError(f"Panel {panel} has missing or duplicated x positions.")
        key = "share_percent" if panel == "b" else "estimate"
        value, lower, upper = (numbers(selected, field)
                               for field in (key, "ci_lower", "ci_upper"))
        if not np.all(np.isfinite([value, lower, upper])):
            raise ValueError(f"Panel {panel} contains non-finite estimates or limits.")
        if np.any(lower > value) or np.any(value > upper):
            raise ValueError(f"Panel {panel} has an estimate outside its interval.")
        panels[panel] = selected
    b = panels["b"]
    if [row["x_label"] for row in b] != [label.replace("\n", " ") for label in MOTIVE_LABELS]:
        raise ValueError("Panel b labels/order do not match this plotting version.")
    if not np.allclose(numbers(b, "share_percent"),
                       100 * numbers(b, "count") / numbers(b, "denominator"),
                       rtol=0, atol=1e-9):
        raise ValueError("Panel b shares do not match counts and denominators.")
    return panels


def style_axis(ax):
    ax.spines[["right", "top"]].set_visible(False)
    # Separate the horizontal and vertical axes, matching the manuscript style.
    ax.spines["bottom"].set_position(("outward", 6))
    ax.tick_params(direction="out", width=0.7, length=4)


def coefficient_panel(ax, rows, panel, title):
    x = np.arange(len(rows))
    ax.fill_between(x, numbers(rows, "ci_lower"), numbers(rows, "ci_upper"),
                    color=BAND)
    ax.plot(x, numbers(rows, "estimate"), "o-", color=GREEN,
            lw=1.5, ms=3.5)
    ax.axhline(0, color="black", ls=(0, (3, 4)), lw=0.7)
    style_axis(ax)
    labels = [row["x_label"].replace("-", "−") for row in rows]
    ax.set_xticks(x, labels, fontsize=9)
    ax.set_ylim(-0.03, 0.07)
    ax.set_yticks([-0.03, 0, 0.03, 0.06])
    ax.set_ylabel("Estimated coefficients", fontsize=11)
    ax.set_title(title, pad=51, fontsize=12)
    ax.legend([Patch(color=BAND), Line2D([], [], color=GREEN, marker="o")],
              ["95% CI", "Estimated coefficients"], ncol=2,
              loc="upper center", bbox_to_anchor=(0.5, 1.18),
              frameon=False, fontsize=10)
    ax.set_xlabel("Temperature bins" if panel == "a" else
                  "Months before and after power rationing", fontsize=11)
    if panel != "a":
        reference = next(i for i, row in enumerate(rows) if row["x_label"] == "-1")
        ax.axvline(reference, color="black", ls=(0, (3, 4)), lw=0.7)
    ax.text(-0.1, 1.24, panel, transform=ax.transAxes,
            fontweight="bold", fontsize=15)


def create_figure(panels):
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 11,
        "axes.labelsize": 12, "axes.titlesize": 13,
        "svg.fonttype": "none", "pdf.fonttype": 42, "axes.linewidth": 0.7,
    })
    fig, axes = plt.subplots(2, 2, figsize=(13.7, 8.8))
    fig.subplots_adjust(left=0.065, right=0.99, top=0.9, bottom=0.08,
                        wspace=0.21, hspace=0.53)
    for ax, panel, title in (
        (axes[0, 0], "a", "RRPV-BS: temperature response"),
        (axes[1, 0], "c", "RRPV-BS: power-rationing response"),
        (axes[1, 1], "d", "RRPV-only: power-rationing response"),
    ):
        coefficient_panel(ax, panels[panel], panel, title)

    ax = axes[0, 1]
    rows = panels["b"]
    x, y = np.arange(5), numbers(rows, "share_percent")
    ax.errorbar(x, y,
                yerr=[y - numbers(rows, "ci_lower"), numbers(rows, "ci_upper") - y],
                fmt="o", mfc=GREEN, mec=GREEN, ecolor=CI_GREEN,
                capsize=5, lw=1.3, ms=4)
    style_axis(ax)
    ax.set_ylim(0, 50)
    ax.set_yticks(range(0, 51, 10), [f"{i}%" for i in range(0, 51, 10)])
    ax.set_xlim(-0.55, 4.55)
    ax.set_xticks(x, MOTIVE_LABELS, fontsize=8)
    ax.set_ylabel("Share ranking motive among top three (%)", fontsize=10)
    ax.set_title("RRPV-BS: reliability motives", pad=51, fontsize=12)
    ax.legend([Line2D([], [], color=CI_GREEN),
               Line2D([], [], color=GREEN, marker="o", ls="")],
              ["95% CI", "Ranked among top three"], ncol=2,
              loc="upper center", bbox_to_anchor=(0.5, 1.18),
              frameon=False, fontsize=10)
    ax.text(-0.1, 1.24, "b", transform=ax.transAxes,
            fontweight="bold", fontsize=15)
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path,
                        default=DEFAULT_DATA)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dpi", type=int, default=400)
    args = parser.parse_args()
    if args.dpi < 72:
        parser.error("--dpi must be at least 72.")
    panels = load_data(args.data)
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    fig = create_figure(panels)
    metadata = {
        "png": {"Author": "Shunlin Jin", "Title": "Figure 3"},
        "pdf": {"Author": "Shunlin Jin", "Title": "Figure 3",
                "Creator": "Shunlin Jin"},
        "svg": {"Creator": "Shunlin Jin", "Title": "Figure 3"},
    }
    for extension in ("png", "pdf", "svg"):
        path = output / f"Figure_3.{extension}"
        fig.savefig(path, dpi=args.dpi, facecolor="white", bbox_inches="tight",
                    pad_inches=0.12, metadata=metadata[extension])
        print(f"Saved: {path}")
    plt.close(fig)
    print("Figure 3 completed successfully.")


if __name__ == "__main__":
    main()
