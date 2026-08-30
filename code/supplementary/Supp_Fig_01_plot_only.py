# -*- coding: utf-8 -*-
"""
Supplementary Fig. 1 鈥?PUBLIC plot-only version, SI-matched lighter blues.

Reads ONLY:
    data/supp_fig01_map_plot_data.csv

The CSV contains no real county names, IDs, administrative codes,
province names, original geographic coordinates, or exact installation counts.

Plot style:
- no county boundary strokes
- no province exterior outline strokes
- lighter SI-matched blue scale
- panels a-d
- vertical legend from 1000 to 1500
"""

from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap
from shapely import wkt


CODE_DIR = Path(__file__).resolve().parent
ROOT = CODE_DIR.parent
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "output"

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

INPUT = DATA_DIR / "supp_fig01_map_plot_data.csv"

if not INPUT.exists():
    raise FileNotFoundError(
        f"Missing anonymized Fig. 1 plotting CSV:\n{INPUT}\n\n"
        "The required public Fig. 1 plotting CSV is not present."
    )

d = pd.read_csv(
    INPUT,
    dtype={
        "panel": "string",
        "anon_unit": "string",
        "fill_hex": "string",
        "geometry_wkt": "string",
    },
)

required = {
    "panel",
    "anon_unit",
    "fill_hex",
    "geometry_wkt",
}

missing = required.difference(
    d.columns
)

if missing:
    raise ValueError(
        "Public Fig. 1 CSV is missing field(s): "
        + ", ".join(sorted(missing))
    )

for forbidden in [
    "county",
    "countyid",
    "adcode",
    "city",
    "province",
    "boundary_name",
    "total_installation_count",
]:
    if forbidden in d.columns:
        raise RuntimeError(
            f"Identifying/sensitive column found in public CSV: {forbidden}"
        )

d["geometry"] = d["geometry_wkt"].map(
    wkt.loads
)

gdf = gpd.GeoDataFrame(
    d.drop(
        columns="geometry_wkt"
    ),
    geometry="geometry",
    crs=None,
)

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": [
        "Arial",
        "DejaVu Sans",
    ],
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

# ---------------------------------------------------------------------
# Same SI-matched palette as the exporter
# ---------------------------------------------------------------------
VMIN = 1000
VMAX = 1500

TICKS = [
    1000,
    1100,
    1200,
    1300,
    1400,
    1500,
]

base_blues = mpl.colormaps["Blues"]

si_blues = LinearSegmentedColormap.from_list(
    "SI_Blues",
    [
        base_blues(0.02),
        base_blues(0.60),
    ],
    N=256,
)

norm = mpl.colors.Normalize(
    vmin=VMIN,
    vmax=VMAX,
    clip=True,
)

fig = plt.figure(
    figsize=(7.4, 4.8)
)

gs = fig.add_gridspec(
    2,
    3,
    width_ratios=[
        1.0,
        1.0,
        0.10,
    ],
    height_ratios=[
        1.0,
        1.0,
    ],
    left=0.045,
    right=0.955,
    bottom=0.055,
    top=0.965,
    wspace=0.07,
    hspace=0.06,
)

axes = {
    "a": fig.add_subplot(gs[0, 0]),
    "b": fig.add_subplot(gs[0, 1]),
    "c": fig.add_subplot(gs[1, 0]),
    "d": fig.add_subplot(gs[1, 1]),
}

legend_holder = fig.add_subplot(
    gs[:, 2]
)
legend_holder.set_axis_off()

holder = legend_holder.get_position()

cax = fig.add_axes([
    holder.x0 + 0.010,
    holder.y0 + 0.28 * holder.height,
    0.014,
    0.40 * holder.height,
])

for panel in [
    "a",
    "b",
    "c",
    "d",
]:
    ax = axes[panel]

    p = gdf.loc[
        gdf["panel"].eq(panel)
    ].copy()

    if p.empty:
        raise ValueError(
            f"No geometry for panel {panel}."
        )

    # No county or province outline strokes.
    p.plot(
        ax=ax,
        color=p["fill_hex"].tolist(),
        edgecolor="none",
        linewidth=0,
        antialiased=True,
    )

    ax.set_xlim(
        0,
        1,
    )
    ax.set_ylim(
        0,
        1,
    )
    ax.set_aspect(
        "equal"
    )
    ax.set_axis_off()

    ax.text(
        0.015,
        0.985,
        panel,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9,
        fontweight="normal",
    )

sm = mpl.cm.ScalarMappable(
    norm=norm,
    cmap=si_blues,
)
sm.set_array([])

cbar = fig.colorbar(
    sm,
    cax=cax,
    orientation="vertical",
    ticks=TICKS,
)

cbar.ax.tick_params(
    labelsize=7,
    length=2.0,
    width=0.6,
    pad=2,
)

cbar.outline.set_linewidth(
    0.6
)

cbar.ax.set_title(
    "Number of\ninstallation",
    fontsize=7,
    pad=4,
    loc="left",
)

png = (
    OUT_DIR
    / "Supplementary_Fig_01.png"
)

pdf = (
    OUT_DIR
    / "Supplementary_Fig_01.pdf"
)

fig.savefig(
    png,
    dpi=600,
    bbox_inches="tight",
    pad_inches=0.02,
)

fig.savefig(
    pdf,
    bbox_inches="tight",
    pad_inches=0.02,
)

plt.close(fig)

print(
    "Supplementary Fig. 1 reproduced "
    "from anonymized CSV with SI-matched lighter blues."
)
print(png)
print(pdf)
