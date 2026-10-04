"""Figure 5 plotting helpers.
Numerical input for panels a-d, h and i is provided in the aggregate source CSV.
Panel g is supplied separately in figure5_panel_g.csv.
"""
from pathlib import Path
import gc
import os
import tempfile
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "solar_matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
CORAL="#E76F51"
NAVY="#264653"
ORANGE="#F4A261"
TEAL="#2A9D8F"
BLUE="#4C83A5"
DEEP_BLUE="#005A9C"
GRAY="#5A5A5A"
LIGHT_GRAY="#D9D9D9"
FONT_TITLE=13.5
FONT_LABEL=11.5
FONT_TICK=11.0
FONT_SMALL=10.5
FONT_PANEL=15.0


def set_style():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Nimbus Sans", "DejaVu Sans"],
        "font.size": FONT_TICK,
        "axes.titlesize": FONT_TITLE,
        "axes.labelsize": FONT_LABEL,
        "xtick.labelsize": FONT_TICK,
        "ytick.labelsize": FONT_TICK,
        "legend.fontsize": FONT_SMALL,
        "text.color": "#171717",
        "axes.labelcolor": "#171717",
        "xtick.color": "#171717",
        "ytick.color": "#171717",
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
        fontsize=FONT_PANEL, fontweight="bold",
        clip_on=False,
    )
    ax.set_title(title, loc="center", pad=pad, fontsize=FONT_TITLE, fontweight="normal")

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
    baseline = x == -1
    ax.plot(x[baseline], y[baseline], linestyle="none", marker="o",
            markerfacecolor="white", markeredgecolor=TEAL,
            markeredgewidth=.8, markersize=3.1, zorder=4)
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
        baseline = x == -1
        ax.plot(x[baseline], est[baseline], linestyle="none", marker="o",
                markerfacecolor="white", markeredgecolor=colour,
                markeredgewidth=.8, markersize=3.1, zorder=4)
        series[outcome] = data

    vals = pd.concat(
        [series[k][["estimate"]] for k in series], ignore_index=True
    )["estimate"].astype(float)
    y_min = float(vals.min())
    y_max = float(vals.max())
    y_range = max(y_max-y_min, 1.0)

    ax.text(23.5, y_max-0.24*y_range, "Total use",
            color=CORAL, fontsize=FONT_SMALL, ha="right", va="center")
    ax.text(23.5, y_min+0.44*y_range, "Grid purchases",
            color=NAVY, fontsize=FONT_SMALL, ha="right", va="center")

    heading(ax, "c", "Total electricity use\nand grid purchases")
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
            "Income incl. PV\nrevenue, net of\nelectricity bill",
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
    ax.set_xlabel("Post-grid-connection\nchange (US$/month)")
    heading(ax, "d", "Household income and\nelectricity expenditure")
    style_axis(ax)

def panel_f(ax, source):
    """Monthly 5% incidence effects overall and by pre-adoption income."""
    labels = ['All households', 'Lower income', 'Higher income']
    required = {'group', 'threshold_pct', 'estimate', 'conf_low', 'conf_high'}
    if not required.issubset(source.columns):
        raise ValueError('Panel f requires the income-group source CSV. Use the accompanying Figure5_panel_f_source_data.csv.')
    if len(source) != 3 or set(source['group']) != set(labels) or not source.threshold_pct.eq(5).all():
        raise ValueError('Panel f requires three income-group rows at the 5% threshold.')
    plot = source.set_index('group').loc[labels]
    est = plot['estimate'].to_numpy(float)
    lo = plot['conf_low'].to_numpy(float)
    hi = plot['conf_high'].to_numpy(float)
    if not np.isfinite([est, lo, hi]).all() or (lo > est).any() or (hi < est).any():
        raise ValueError('Panel f has invalid point estimates or confidence intervals.')
    ax.axvline(0, linestyle='--', linewidth=.75, color=GRAY)
    ax.errorbar(est, [2, 1, 0], xerr=[est-lo, hi-est], fmt='o',
                color=TEAL, ecolor=GRAY, markersize=4.0, capsize=2.1, linewidth=.9)
    ax.set_yticks([2, 1, 0], labels)
    ax.set_ylim(-.60, 2.60)
    lower = min(-30, 5 * np.floor((lo.min() - 1) / 5))
    upper = max(1, 5 * np.ceil((hi.max() + 1) / 5))
    ax.set_xlim(lower, upper)
    ax.set_xticks(np.arange(10 * np.ceil(lower / 10), upper + .1, 10))
    ax.set_xlabel('Effect on probability\n(percentage points)')
    heading(ax, 'f', 'Energy-poverty incidence\n(5% threshold)')
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
    labels = {1:"<1 hour",2:"1–3 hours",3:"3–6 hours",4:">6 hours"}
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
            ha="left", va="center", color="#424242", fontsize=FONT_SMALL
        )
    ax.set_yticks(y)
    ax.set_yticklabels([str(label).replace('Basic services maintained','Basic services\nmaintained').replace('Appliance support','Appliance\nsupport') for label in plot['label']])
    ax.invert_yaxis()
    ax.set_xlim(0,108)
    ax.set_xticks([0,20,40,60,80,100])
    ax.set_xlabel(xlabel)
    heading(ax, letter, title)
    style_axis(ax)

def iv_panel(ax, estimates):
    """Horizontal bars on one visible pair of axes, with explicit display units.

    Expenditure is displayed in US$/month and electricity in 10 kWh/month;
    the ratio remains in percentage points. This is unit conversion only, not
    standardization or a comparison of welfare magnitudes across outcomes.
    Labels report coefficients in US$, percentage points or unscaled kWh.
    """
    heading(ax, "g", "2SLS estimates")
    layout = [
        ("bill_rmb", "Electricity expenditure\n(US$/month)", "US$", TEAL),
        ("bill_income_pp", "Bill-to-income ratio\n(percentage points)", "pp", TEAL),
        ("total_use_kwh", "Total electricity use\n(10 kWh/month)", "kWh", CORAL),
        ("grid_purchase_kwh", "Grid purchases\n(10 kWh/month)", "kWh", NAVY),
    ]
    frame = estimates.set_index("outcome")
    ys = np.arange(len(layout))
    lower, upper = -5.0, 5.5
    for index, (outcome, label, raw_unit, colour) in enumerate(layout):
        row = frame.loc[outcome]
        b, lo, hi = (float(row[k]) for k in
                     ["display_estimate", "display_ci_low", "display_ci_high"])
        lower = min(lower, lo-.6)
        upper = max(upper, hi+1.7)
        ax.barh(index, b, height=.47, color=colour, edgecolor="none", zorder=2)
        ax.errorbar(b, index, xerr=[[b-lo], [hi-b]], fmt="none",
                    ecolor="#303030", elinewidth=.85, capsize=2.5,
                    capthick=.85, zorder=4)
        raw = b if outcome == "bill_rmb" else float(row.estimate)
        number = f"{raw:+.2f}" if outcome == "bill_rmb" else f"{raw:+.3f}"
        number = number.replace("-", "−")
        # Keep the complete label on its own side of zero, separated from the
        # reference line by six points and above the bar/error bar. Stars stay
        # in the numerical CSV for tables; they are not printed in the figure.
        negative = raw < 0
        ax.annotate(f"{number} {raw_unit}",
                    xy=(0, index), xytext=(-6 if negative else 6, 11),
                    textcoords="offset points",
                    ha="right" if negative else "left", va="bottom",
                    fontsize=FONT_SMALL, color=colour,
                    annotation_clip=False)
    ax.axvline(0, color="#7A7A7A", linewidth=.65, zorder=1)
    ax.set_yticks(ys)
    ax.set_yticklabels([item[1] for item in layout], fontsize=FONT_TICK)
    ax.set_xlim(lower, upper)
    ax.set_ylim(-.72, len(layout)-.43)
    ax.invert_yaxis()
    ax.set_xticks([-4, -2, 0, 2, 4])
    ax.set_xlabel("Effect (units at left)")
    ax.tick_params(axis="y", length=3.0, pad=4.0)
    style_axis(ax)

def png_dpi_value(value):
    """Validate a bounded, positive PNG resolution for each command-line entry."""
    import argparse
    try:
        dpi = int(value)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError('PNG DPI must be an integer from 72 to 1200.')
    if not 72 <= dpi <= 1200:
        raise argparse.ArgumentTypeError('PNG DPI must be an integer from 72 to 1200.')
    return dpi


def save_formats(fig, out, name, png_dpi=300):
    """Save vectors first; retry only PNG memory failures at a lower resolution.

    Atomic replacement prevents incomplete exports from replacing valid files.
    If all PNG attempts fail, remove the stale PNG and report its absence while
    retaining the vector exports. The caller records the actual DPI/status.
    """
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    png_dpi = png_dpi_value(png_dpi)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    common = dict(bbox_inches="tight", pad_inches=.06, facecolor="white")

    def atomic_export(filename, fmt, **kwargs):
        fd, temporary = tempfile.mkstemp(prefix='.' + name + '_', suffix='.' + fmt, dir=out)
        os.close(fd)
        temporary = Path(temporary)
        try:
            fig.savefig(temporary, format=fmt, **common, **kwargs)
            os.replace(temporary, out / filename)
        finally:
            temporary.unlink(missing_ok=True)

    atomic_export(name + '.pdf', 'pdf', metadata={"Author": "Shunlin Jin", "CreationDate": None, "ModDate": None})
    with plt.rc_context({"svg.fonttype": "none", "svg.hashsalt": name}):
        atomic_export(name + '.svg', 'svg', metadata={"Creator": "Shunlin Jin", "Date": None})
    with plt.rc_context({"svg.fonttype": "path", "svg.hashsalt": name}):
        atomic_export(name + '_Word.svg', 'svg', metadata={"Creator": "Shunlin Jin", "Date": None})
    print(f'{name}: saved PDF, editable SVG and Word SVG.', flush=True)

    attempts = [png_dpi] + [dpi for dpi in (300, 200, 150, 100, 72) if dpi < png_dpi]
    status = dict(png_requested_dpi=png_dpi, png_dpi=None, png_written=False,
                  png_attempted_dpi=[], vector_files=[name + '.pdf', name + '.svg', name + '_Word.svg'])
    for dpi in attempts:
        status['png_attempted_dpi'].append(dpi)
        try:
            atomic_export(name + '.png', 'png', dpi=dpi, metadata={"Author": "Shunlin Jin"})
        except MemoryError:
            print(f'{name}: insufficient memory for {dpi} dpi PNG; trying a smaller canvas.', flush=True)
        else:
            status.update(png_dpi=dpi, png_written=True)
            print(f'{name}: saved PNG at {dpi} dpi.', flush=True)
        finally:
            # Discard the cached Agg renderer before a retry or the next figure.
            FigureCanvasAgg(fig)
            gc.collect()
        if status['png_written']:
            return status
    (out / (name + '.png')).unlink(missing_ok=True)
    print(f'WARNING: {name} PNG could not be exported. PDF/SVG and CSV outputs remain available.', flush=True)
    return status
