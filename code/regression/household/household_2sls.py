"""Household-month 2SLS regressions, manuscript Eqs. (7)-(8)."""
from __future__ import annotations

import argparse
import json
from numbers import Number
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import linalg, stats

OUTCOMES = (
    "followup_electricity_bill_rmb",
    "followup_bill_income_ratio_pct",
    "followup_total_electricity_kwh",
    "followup_grid_import_kwh",
)
ENDOGENOUS = "adoption_event"
INSTRUMENT = "heat_days_lag1"
NONREFERENCE_BINS = ("le_m5", "m5_0", "0_5", "5_10", "10_15", "20_25", "25_30", "gt30")
BASELINE_CONTROLS = tuple("lag_bin_" + b for b in NONREFERENCE_BINS if b != "gt30") + tuple(
    "followup_bin_" + b for b in NONREFERENCE_BINS
)
MONTHLY_OUTCOMES = (
    "electricity_bill_rmb", "bill_income_ratio_current_pct",
    "total_electricity_consumption_kwh", "grid_import_kwh",
)


def month_dates(values, name, allow_missing=False):
    values = values.copy() if isinstance(values, pd.Series) else pd.Series(values)
    if values.dropna().map(lambda value: isinstance(value, Number)).any():
        raise ValueError(f"{name} must use calendar dates, not numerical timestamps.")
    parsed = pd.to_datetime(values, errors="raise")
    if parsed.dt.tz is not None:
        raise ValueError(f"{name} must use timezone-naive calendar months.")
    if (
        (not allow_missing and parsed.isna().any())
        or parsed.dropna().dt.day.ne(1).any()
        or parsed.dropna().ne(parsed.dropna().dt.normalize()).any()
    ):
        raise ValueError(f"{name} must contain first-of-month dates at midnight.")
    return parsed


def validate_risk_set(frame):
    work = frame.copy()
    work["month"] = month_dates(work["month"], "month")
    work["ordinary_adoption_month"] = month_dates(
        work["ordinary_adoption_month"], "ordinary_adoption_month", allow_missing=True
    )
    if work.groupby("household_id").ordinary_adoption_month.nunique(dropna=False).gt(1).any():
        raise ValueError("Grid-connection month must be constant within household.")
    later = work.ordinary_adoption_month.notna() & work.month.gt(work.ordinary_adoption_month)
    if later.any():
        raise ValueError("The 2SLS analysis input includes post-connection risk-set observations.")
    expected = work.month.eq(work.ordinary_adoption_month).astype(int)
    if not np.array_equal(pd.to_numeric(work[ENDOGENOUS], errors="raise"), expected):
        raise ValueError("adoption_event is inconsistent with first grid-connection month.")
    return work


def build_sample(monthly, weather, controls):
    """Construct calendar-aligned risk-set rows and three-month follow-up means.

    The temperature-bin controls are constructed from monthly weather.
    Other named controls are supplied in the anchor-month input.
    """
    if not set(BASELINE_CONTROLS).issubset(controls):
        raise ValueError("The control list must include all baseline lag and follow-up temperature bins.")
    additional = [name for name in controls if name not in BASELINE_CONTROLS]
    p = monthly.copy()
    p["month"] = month_dates(p.month, "month")
    p["ordinary_adoption_month"] = month_dates(
        p.ordinary_adoption_month, "ordinary_adoption_month", allow_missing=True
    )
    if p.duplicated(["household_id", "month"]).any():
        raise ValueError("Duplicate household-month input.")
    if p.groupby("household_id").village_id.nunique().gt(1).any():
        raise ValueError("A household is assigned to multiple villages.")
    if p.groupby("household_id").ordinary_adoption_month.nunique(dropna=False).gt(1).any():
        raise ValueError("Grid-connection month varies within a household.")
    for name in list(MONTHLY_OUTCOMES) + additional:
        p[name] = pd.to_numeric(p[name], errors="raise")
    w = weather.copy()
    w["month"] = month_dates(w.month, "weather month")
    if w.duplicated(["village_id", "month"]).any():
        raise ValueError("Duplicate village-month weather input.")
    weather_columns = ["days_" + b for b in NONREFERENCE_BINS]
    for name in weather_columns:
        w[name] = pd.to_numeric(w[name], errors="raise")
    finite_w = np.isfinite(w[weather_columns].to_numpy())
    values = w[weather_columns].to_numpy()
    if ((values[finite_w] < 0) | (values[finite_w] > 31)).any():
        raise ValueError("Monthly temperature bins must be day counts.")
    keep = p.ordinary_adoption_month.isna() | p.month.le(p.ordinary_adoption_month)
    a = p.loc[keep, ["household_id", "village_id", "month", "ordinary_adoption_month"] + additional].copy()
    a[ENDOGENOUS] = a.month.eq(a.ordinary_adoption_month).astype(int)
    outcome_index = p.set_index(["household_id", "month"])
    weather_index = w.set_index(["village_id", "month"])
    future_y = np.zeros((len(a), len(OUTCOMES)))
    future_w = np.zeros((len(a), len(NONREFERENCE_BINS)))
    for lag in (1, 2, 3):
        target = (a.month.dt.to_period("M") + lag).dt.to_timestamp()
        yi = pd.MultiIndex.from_arrays([a.household_id, target])
        wi = pd.MultiIndex.from_arrays([a.village_id, target])
        future_y += outcome_index.reindex(yi)[list(MONTHLY_OUTCOMES)].to_numpy() / 3
        future_w += weather_index.reindex(wi)[weather_columns].to_numpy() / 3
    previous = (a.month.dt.to_period("M") - 1).dt.to_timestamp()
    wi = pd.MultiIndex.from_arrays([a.village_id, previous])
    previous_w = weather_index.reindex(wi)[weather_columns].to_numpy()
    for j, name in enumerate(OUTCOMES):
        a[name] = future_y[:, j]
    for j, bin_name in enumerate(NONREFERENCE_BINS):
        a["followup_bin_" + bin_name] = future_w[:, j]
        if bin_name != "gt30":
            a["lag_bin_" + bin_name] = previous_w[:, j]
    a[INSTRUMENT] = previous_w[:, -1]
    return validate_risk_set(a)



def absorb(values, groups, tolerance=1e-10, max_iterations=10000):
    """Remove additive fixed effects by alternating orthogonal projections."""
    work = np.asarray(values, dtype=float).copy()
    scale = np.maximum(np.max(np.abs(work), axis=0), 1.0)
    codes = [pd.factorize(g, sort=True)[0] for g in groups]
    if any((g < 0).any() for g in codes):
        raise ValueError("Fixed-effect identifiers must be nonmissing.")
    counts = [np.bincount(g) for g in codes]
    for iteration in range(max_iterations):
        change = 0.0
        for g, count in zip(codes, counts):
            sums = np.zeros((len(count), work.shape[1]))
            np.add.at(sums, g, work)
            means = sums / count[:, None]
            change = max(change, float(np.max(np.abs(means) / scale)))
            work -= means[g]
        if change < tolerance:
            return work, iteration + 1
    raise RuntimeError("Fixed-effect absorption did not converge.")


def fixed_effect_rank(first, second):
    """Rank of two sets of indicator columns, including disconnected components."""
    a = pd.factorize(first)[0]
    b = pd.factorize(second)[0]
    na, nb = int(a.max()) + 1, int(b.max()) + 1
    parent = np.arange(na + nb)

    def root(k):
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    for i, j in zip(a, b):
        ri, rj = root(i), root(na + j)
        if ri != rj:
            parent[ri] = rj
    return na + nb - len({int(root(i)) for i in range(na + nb)})


def cluster_sums(values, cluster, count):
    out = np.zeros((count, values.shape[1]))
    np.add.at(out, cluster, values)
    return out


def trim_singletons(frame):
    work = frame.copy()
    while len(work):
        keep = (
            work.groupby("household_id")["household_id"].transform("size").gt(1)
            & work.groupby("month")["month"].transform("size").gt(1)
        )
        if keep.all():
            return work
        work = work.loc[keep].copy()
    raise ValueError("No observations remain after fixed-effect singleton removal.")


def estimate(frame, controls, outcomes=OUTCOMES):
    """Estimate one endogenous variable using one excluded instrument.

    The same complete-case sample is used for all outcomes and both stages.
    Covariance uses observed adoption in the structural residual, village-level
    scores and the CR1 factor G/(G-1) * (N-1)/(N-K), including fixed-effect rank.
    """
    outcomes = list(outcomes)
    controls = list(controls)
    if len(set(controls)) != len(controls):
        raise ValueError("Control names must be unique.")
    if set(controls) & set(outcomes + [ENDOGENOUS, INSTRUMENT]):
        raise ValueError("An outcome, adoption, or excluded instrument cannot be a control.")
    names = outcomes + [ENDOGENOUS, INSTRUMENT] + controls
    required = ["household_id", "village_id", "month"] + names
    missing = sorted(set(required) - set(frame))
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))
    work = frame[required].copy()
    if work[["household_id", "village_id", "month"]].isna().any().any():
        raise ValueError("Identifiers and months must be nonmissing.")
    if work.duplicated(["household_id", "month"]).any():
        raise ValueError("Duplicate household-month observations.")
    if work.groupby("household_id").village_id.nunique().gt(1).any():
        raise ValueError("A household is assigned to multiple villages.")
    for name in names:
        work[name] = pd.to_numeric(work[name], errors="raise")
    finite = np.isfinite(work[names].to_numpy()).all(axis=1)
    complete = work.loc[finite].copy()
    if not complete[ENDOGENOUS].isin([0, 1]).all():
        raise ValueError("adoption_event must be binary.")
    if (complete[INSTRUMENT] < 0).any() or (complete[INSTRUMENT] > 31).any():
        raise ValueError("heat_days_lag1 must be a count between 0 and 31.")
    work = trim_singletons(complete)
    raw, iterations = absorb(work[names].to_numpy(), [work.household_id, work.month])
    ny = len(outcomes)
    base = raw[:, :ny + 2]
    c = raw[:, ny + 2:]
    selected = np.array([], dtype=int)
    if c.shape[1]:
        norms = np.linalg.norm(c, axis=0)
        eligible = np.flatnonzero(norms > 1e-8)
        if len(eligible):
            _, r, pivot = linalg.qr(c[:, eligible] / norms[eligible], mode="economic", pivoting=True)
            rank = int(np.sum(np.abs(np.diag(r)) > max(c.shape) * np.finfo(float).eps * abs(r[0, 0])))
            selected = eligible[pivot[:rank]]
            c = c[:, selected] / norms[selected]
            base = base - c @ np.linalg.lstsq(c, base, rcond=None)[0]
    y, d, z = base[:, :ny], base[:, ny], base[:, ny + 1]
    clusters = pd.factorize(work.village_id, sort=True)[0]
    g = int(clusters.max()) + 1
    n = len(work)
    k = fixed_effect_rank(work.household_id, work.month) + len(selected) + 1
    if g < 2 or n <= k:
        raise ValueError("Insufficient clusters or residual degrees of freedom.")
    zz, zd = float(z @ z), float(z @ d)
    if zz <= 1e-12 or abs(zd) <= 1e-12 * max(np.linalg.norm(z) * np.linalg.norm(d), 1.0):
        raise ValueError("Excluded instrument has no identifying variation.")
    correction = g / (g - 1) * (n - 1) / (n - k)
    critical = stats.t.ppf(0.975, g - 1)
    first = zd / zz
    first_residual = d - first * z
    first_scores = cluster_sums((z * first_residual)[:, None], clusters, g)
    first_variance = float(correction * (first_scores.T @ first_scores)[0, 0] / zz**2)
    first_se = np.sqrt(first_variance)
    first_hom_var = float(first_residual @ first_residual / (n - k) / zz)
    beta = (z @ y) / zd
    structural_residual = y - d[:, None] * beta
    scores = cluster_sums(z[:, None] * structural_residual, clusters, g)
    covariance = correction * scores.T @ scores / zd**2
    reduced = z @ y / zz
    reduced_scores = cluster_sums(z[:, None] * (y - z[:, None] * reduced), clusters, g)
    reduced_covariance = correction * reduced_scores.T @ reduced_scores / zz**2
    rows = []
    for j, name in enumerate(outcomes):
        se = float(np.sqrt(covariance[j, j]))
        rse = float(np.sqrt(reduced_covariance[j, j]))
        rows.append({
            "outcome": name, "estimate": float(beta[j]), "standard_error": se,
            "ci_lower": float(beta[j] - critical * se), "ci_upper": float(beta[j] + critical * se),
            "t_statistic": float(beta[j] / se), "p_value": float(2 * stats.t.sf(abs(beta[j] / se), g - 1)),
            "degrees_of_freedom": g - 1, "observations": n,
            "households": work.household_id.nunique(), "villages": g,
            "reduced_form": float(reduced[j]), "reduced_form_standard_error": rse,
            "reduced_form_p_value": float(2 * stats.t.sf(abs(reduced[j] / rse), g - 1)),
        })
    diagnostic = {
        "input_rows": len(frame), "complete_case_rows": len(complete), "estimation_rows": n,
        "excluded_nonfinite_rows": int((~finite).sum()), "removed_singleton_rows": len(complete) - n,
        "households": int(work.household_id.nunique()), "villages": g,
        "first_stage_estimate": first, "first_stage_standard_error": float(first_se),
        "first_stage_p_value": float(2 * stats.t.sf(abs(first / first_se), g - 1)),
        "first_stage_cluster_robust_F": float(first**2 / first_variance),
        "first_stage_homoskedastic_F": float(first**2 / first_hom_var),
        "degrees_of_freedom": g - 1, "residual_degrees_of_freedom": n - k,
        "fixed_effect_rank": k - len(selected) - 1, "absorption_iterations": iterations,
        "controls_requested": controls,
        "controls_retained": [controls[j] for j in selected],
        "controls_absorbed_or_collinear": [v for j, v in enumerate(controls) if j not in selected],
    }
    return pd.DataFrame(rows), pd.DataFrame(covariance, index=outcomes, columns=outcomes), diagnostic


def read_frame(path):
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path, dtype={"household_id": str, "village_id": str})


def read_control_x(path):
    """Read the complete control vector, one input-column name per line."""
    if not path.is_file():
        raise FileNotFoundError(f"Control-vector file not found: {path}. Supply the complete W variable list.")
    control_x = [
        line.strip() for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not control_x:
        raise ValueError("control_x must explicitly name the analysis covariates.")
    if len(control_x) != len(set(control_x)):
        raise ValueError("control_x contains duplicate variable names.")
    if not set(BASELINE_CONTROLS).issubset(control_x):
        raise ValueError("control_x omits baseline lag or follow-up temperature bins.")
    if set(control_x) & set(OUTCOMES + (ENDOGENOUS, INSTRUMENT)):
        raise ValueError("An outcome, adoption, or excluded instrument cannot be a control.")
    return control_x


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("D:/household_survey/2sls_monthly.parquet"))
    parser.add_argument("--monthly", type=Path, help="Build the 2SLS sample from this household-month panel.")
    parser.add_argument("--weather", type=Path, default=Path("D:/household_survey/village_monthly_weather.parquet"))
    parser.add_argument("--controls", type=Path, default=Path("D:/household_survey/control_x.txt"),
                        help="Complete W control vector, one input-column name per line.")
    parser.add_argument("--output", type=Path, default=Path("D:/solar_results/main_regressions/2sls"))
    args = parser.parse_args()
    control_x = read_control_x(args.controls)
    if args.monthly:
        frame = build_sample(read_frame(args.monthly), read_frame(args.weather), control_x)
    else:
        frame = validate_risk_set(read_frame(args.input))
    results, covariance, diagnostics = estimate(frame, control_x)
    diagnostics["control_specification"] = "explicit_control_x"
    args.output.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.output / "2sls_results.csv", index=False)
    covariance.to_csv(args.output / "2sls_covariance.csv", index_label="outcome")
    (args.output / "2sls_diagnostics.json").write_text(json.dumps(diagnostics, indent=2, allow_nan=False), encoding="utf-8")
    print(f"Completed: {args.output}")


if __name__ == "__main__":
    main()
