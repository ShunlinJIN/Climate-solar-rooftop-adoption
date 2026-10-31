"""Monthly household event studies: manuscript equations (5)-(6), Fig. 5a-c."""


from dataclasses import dataclass
from typing import Dict, Optional
import math
import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
import argparse


@dataclass
class FEFit:
    unit_effect: np.ndarray
    time_effect: np.ndarray
    unit_codes: np.ndarray
    time_codes: np.ndarray
    supported: np.ndarray
    iterations: int
    converged: bool
    max_change: float
    fit_rows: int


@dataclass
class JKResult:
    estimate: float
    std_error: float
    conf_low: float
    conf_high: float
    p_value: float
    clusters: int
    observations: int
    loo: Dict[int, float]


def factorize(values: pd.Series) -> tuple[np.ndarray, int]:
    codes, levels = pd.factorize(values, sort=True)
    if (codes < 0).any():
        raise ValueError("Fixed-effect identifiers contain missing values.")
    return codes.astype("int32"), len(levels)


def group_mean(
    values: np.ndarray,
    codes: np.ndarray,
    group_count: int,
    mask: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    mask = np.asarray(mask, dtype=bool)
    selected = codes[mask]
    counts = np.bincount(selected, minlength=group_count).astype(float)
    sums = np.zeros(group_count, dtype=float)
    np.add.at(sums, selected, values[mask])
    means = np.zeros(group_count, dtype=float)
    positive = counts > 0
    means[positive] = sums[positive] / counts[positive]
    return means, counts


def fit_two_way(
    outcome: np.ndarray,
    unit_id: pd.Series,
    time_id: pd.Series,
    fit_mask: np.ndarray,
    *,
    tolerance: float = 1e-9,
    max_iter: int = 1000,
) -> FEFit:
    y = np.asarray(outcome, dtype=float)
    usable = np.asarray(fit_mask, dtype=bool) & np.isfinite(y)
    if not usable.any():
        raise ValueError("No untreated observations are available.")

    unit_codes, unit_count = factorize(unit_id)
    time_codes, time_count = factorize(time_id)
    unit_n = np.bincount(
        unit_codes[usable], minlength=unit_count
    ).astype(float)
    time_n = np.bincount(
        time_codes[usable], minlength=time_count
    ).astype(float)

    alpha = np.zeros(unit_count, dtype=float)
    lam = np.zeros(time_count, dtype=float)
    converged = False
    max_change = np.inf

    for iteration in range(1, max_iter + 1):
        old_alpha = alpha.copy()
        old_lam = lam.copy()
        alpha, _ = group_mean(
            y - lam[time_codes], unit_codes, unit_count, usable
        )
        lam, _ = group_mean(
            y - alpha[unit_codes], time_codes, time_count, usable
        )

        positive_time = time_n > 0
        positive_unit = unit_n > 0
        if positive_time.any():
            shift = np.average(
                lam[positive_time], weights=time_n[positive_time]
            )
            lam[positive_time] -= shift
            alpha[positive_unit] += shift

        max_change = max(
            float(np.max(np.abs(alpha - old_alpha))),
            float(np.max(np.abs(lam - old_lam))),
        )
        if max_change < tolerance:
            converged = True
            break

    supported = (
        (unit_n[unit_codes] > 0)
        & (time_n[time_codes] > 0)
    )
    return FEFit(
        unit_effect=alpha,
        time_effect=lam,
        unit_codes=unit_codes,
        time_codes=time_codes,
        supported=supported,
        iterations=iteration,
        converged=converged,
        max_change=max_change,
        fit_rows=int(usable.sum()),
    )


def impute_tau(
    frame: pd.DataFrame,
    outcome: str,
    *,
    unit_column: str,
    time_column: str,
    treatment_column: str,
    target: np.ndarray,
    excluded_from_fit: Optional[np.ndarray] = None,
) -> tuple[np.ndarray, np.ndarray, FEFit]:
    y = pd.to_numeric(frame[outcome], errors="coerce").to_numpy(dtype=float)
    treatment = pd.to_numeric(
        frame[treatment_column], errors="coerce"
    ).to_numpy(dtype=float)
    fit_mask = treatment == 0
    if excluded_from_fit is not None:
        fit_mask &= ~np.asarray(excluded_from_fit, dtype=bool)

    fit = fit_two_way(
        y,
        frame[unit_column],
        frame[time_column],
        fit_mask,
    )
    prediction = (
        fit.unit_effect[fit.unit_codes]
        + fit.time_effect[fit.time_codes]
    )
    tau = y - prediction
    valid = (
        np.asarray(target, dtype=bool)
        & np.isfinite(y)
        & fit.supported
    )
    return tau, valid.astype(bool), fit


def add_values(
    sums: Dict[int, float],
    counts: Dict[int, int],
    cluster: int,
    values: np.ndarray,
) -> None:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size:
        sums[cluster] = sums.get(cluster, 0.0) + float(values.sum())
        counts[cluster] = counts.get(cluster, 0) + int(values.size)


def jk_ratio(
    sums: Dict[int, float],
    counts: Dict[int, int],
) -> JKResult:
    clusters = sorted(
        cluster
        for cluster in set(sums) | set(counts)
        if counts.get(cluster, 0) > 0
    )
    total_count = int(sum(counts.get(c, 0) for c in clusters))
    total_sum = float(sum(sums.get(c, 0.0) for c in clusters))
    if total_count == 0:
        return JKResult(
            np.nan, np.nan, np.nan, np.nan, np.nan, 0, 0, {}
        )

    estimate = total_sum / total_count
    loo: Dict[int, float] = {}
    for cluster in clusters:
        denominator = total_count - counts.get(cluster, 0)
        if denominator > 0:
            loo[cluster] = (
                total_sum - sums.get(cluster, 0.0)
            ) / denominator

    values = np.asarray(list(loo.values()), dtype=float)
    g = len(values)
    if g < 2:
        return JKResult(
            estimate, np.nan, np.nan, np.nan, np.nan,
            g, total_count, loo,
        )

    variance = (g - 1) / g * np.sum((values - values.mean()) ** 2)
    se = math.sqrt(max(float(variance), 0.0))
    critical = stats.t.ppf(0.975, df=g - 1)
    p_value = (
        2 * stats.t.sf(abs(estimate / se), df=g - 1)
        if se > 0 else (0.0 if estimate != 0 else 1.0)
    )
    return JKResult(
        estimate=estimate,
        std_error=se,
        conf_low=estimate - critical * se,
        conf_high=estimate + critical * se,
        p_value=p_value,
        clusters=g,
        observations=total_count,
        loo=loo,
    )


def read_table(path):
    path = Path(path)
    if path.suffix.lower() == '.parquet':
        return pd.read_parquet(path)
    return pd.read_csv(path, dtype={'household_id': str, 'village_id': str})


def require(frame, names):
    missing = sorted(set(names) - set(frame.columns))
    if missing:
        raise ValueError(f'Missing input columns: {missing}')


def number(frame, names):
    for name in names:
        frame[name] = pd.to_numeric(frame[name], errors='raise')
        if np.isinf(frame[name].to_numpy(dtype=float)).any():
            raise ValueError(f'Infinite value in {name}')


def eligible(frame, time_column):
    require(frame, ['household_id', 'village_id', time_column,
                    'timing_class', 'main_causal_sample'])
    frame = frame.copy()
    if not frame.main_causal_sample.isin([0, 1]).all():
        raise ValueError('main_causal_sample must contain 0 or 1.')
    frame = frame.loc[frame.main_causal_sample.eq(1)].copy()
    if frame.empty:
        raise ValueError('No eligible observations.')
    if not frame.timing_class.isin(['within_panel_switcher', 'never_treated']).all():
        raise ValueError('Eligible observations must be switchers or never-treated households.')
    for col in ['household_id', 'village_id', time_column]:
        if frame[col].isna().any():
            raise ValueError(f'Missing identifier: {col}')
    for col in ['household_id', 'village_id']:
        frame[col] = frame[col].astype(str)
    if frame.duplicated(['household_id', time_column]).any():
        raise ValueError('Duplicate household-period observations.')
    for col in ['village_id', 'timing_class']:
        if frame.groupby('household_id')[col].nunique().gt(1).any():
            raise ValueError(f'{col} changes within household.')
    return frame.reset_index(drop=True)


def prepare_monthly(frame):
    require(frame, ['month', 'ordinary_adoption_month'])
    frame = frame.copy()
    frame['month'] = pd.to_datetime(frame.month, errors='raise')
    if frame.month.isna().any() or frame.month.dt.tz is not None:
        raise ValueError('month must contain timezone-free dates.')
    frame['month'] = frame.month.dt.to_period('M').dt.to_timestamp()
    frame['ordinary_adoption_month'] = pd.to_datetime(frame.ordinary_adoption_month, errors='raise')
    if frame.ordinary_adoption_month.dt.tz is not None:
        raise ValueError('Adoption dates must be timezone-free.')
    frame['ordinary_adoption_month'] = frame.ordinary_adoption_month.dt.to_period('M').dt.to_timestamp()
    frame = eligible(frame, 'month')
    dates = frame.groupby('household_id').ordinary_adoption_month
    if dates.nunique(dropna=False).gt(1).any():
        raise ValueError('Adoption month changes within household.')
    switch = frame.timing_class.eq('within_panel_switcher')
    if not frame.ordinary_adoption_month.notna().eq(switch).all():
        raise ValueError('Adoption month and timing_class disagree.')
    adoption = frame.ordinary_adoption_month
    event = (frame.month.dt.year-adoption.dt.year)*12 + frame.month.dt.month-adoption.dt.month
    post = (switch & event.ge(0)).astype(int)
    if 'post_adoption' in frame and not frame.post_adoption.eq(post).all():
        raise ValueError('post_adoption disagrees with grid-connection month.')
    frame['post_adoption'] = post
    frame['event_time_month'] = event
    return frame


def identified_predictions(fit, usable):
    """A prediction requires household and time effects in one fitted component."""
    u, t = fit.unit_codes, fit.time_codes
    n_u, n_t = len(fit.unit_effect), len(fit.time_effect)
    a, b = u[usable], n_u+t[usable]
    graph = coo_matrix((np.ones(2*len(a)),
                       (np.r_[a, b], np.r_[b, a])), shape=(n_u+n_t, n_u+n_t)).tocsr()
    _, labels = connected_components(graph, directed=False)
    return fit.supported & (labels[u] == labels[n_u+t])


def estimate(frame, outcome, time_column, treatment_column, targets, exclude=None):
    """Observation-weighted targets from one common untreated-outcome model.

    Household and village-period effects are nested within village. Removing a
    village does not alter other villages' fitted effects, so deleting village
    sufficient statistics equals refitting the entire model without that village.
    """
    require(frame, [outcome, time_column, treatment_column])
    number(frame, [outcome])
    if not frame[treatment_column].isin([0, 1]).all():
        raise ValueError('Treatment indicator must contain 0 or 1.')
    masks = {name: np.asarray(value, dtype=bool) for name, value in targets.items()}
    for name, mask in masks.items():
        if mask.shape != (len(frame),):
            raise ValueError(f'Invalid target mask: {name}')
    excluded = np.zeros(len(frame), bool) if exclude is None else np.asarray(exclude, bool)
    if excluded.shape != (len(frame),):
        raise ValueError('Invalid exclusion mask.')
    sums = {k: {} for k in masks}; counts = {k: {} for k in masks}
    households = {k: set() for k in masks}
    unsupported = {k: 0 for k in masks}
    union = np.logical_or.reduce(list(masks.values()))
    for village, indices in frame.groupby('village_id', sort=True).indices.items():
        part = frame.iloc[indices].reset_index(drop=True)
        target = union[indices] & part[outcome].notna().to_numpy()
        if not target.any():
            continue
        tau, valid, fit = impute_tau(part, outcome, unit_column='household_id',
                                    time_column=time_column, treatment_column=treatment_column,
                                    target=target, excluded_from_fit=excluded[indices])
        if not fit.converged:
            raise RuntimeError(f'Fixed effects failed to converge: {outcome}, {village}')
        usable = part[treatment_column].eq(0).to_numpy() & ~excluded[indices] & part[outcome].notna().to_numpy()
        connected = identified_predictions(fit, usable)
        if np.any(target & fit.supported & ~connected):
            raise ValueError(f'Disconnected fixed-effect support: {outcome}, village {village}')
        valid &= connected
        for name, mask in masks.items():
            selected = valid & mask[indices]
            unsupported[name] += int(np.sum(target & mask[indices] & ~fit.supported))
            add_values(sums[name], counts[name], village, tau[selected])
            households[name].update(part.loc[selected, 'household_id'])
    rows, results = [], {}
    for name in masks:
        result = jk_ratio(sums[name], counts[name])
        if result.clusters < 2 or not np.isfinite([result.estimate, result.std_error,
                                                   result.conf_low, result.conf_high]).all():
            raise ValueError(f'Insufficient village support for {outcome}, {name}.')
        results[name] = result
        rows.append(dict(outcome=outcome, estimand=name, estimate=result.estimate,
                         std_error=result.std_error, conf_low=result.conf_low,
                         conf_high=result.conf_high, p_value=result.p_value,
                         n_villages=result.clusters, df=result.clusters-1,
                         n_target_observations=result.observations,
                         n_target_without_prediction_support=unsupported[name],
                         n_target_households=len(households[name])))
    return pd.DataFrame(rows), results


def export(frame, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, float_format='%.17g')


OUTCOMES = {
    'electricity_bill_rmb': 'RMB/month',
    'bill_income_ratio_current_pct': 'percentage points',
    'total_electricity_consumption_kwh': 'kWh/month',
    'grid_import_kwh': 'kWh/month',
}


def run(input_path, output_path):
    frame = prepare_monthly(read_table(input_path))
    require(frame, OUTCOMES)
    frame = frame.loc[frame.month.between('2021-01-01', '2026-06-01')].reset_index(drop=True)
    number(frame, OUTCOMES)
    switch = frame.timing_class.eq('within_panel_switcher')
    event = frame.event_time_month
    post_targets = {f'event_{k}': (switch & event.eq(k)).to_numpy() for k in range(25)}
    post_targets['post_months_1_12'] = (switch & event.between(1, 12)).to_numpy()
    event_rows, average_rows = [], []
    for outcome, unit in OUTCOMES.items():
        result, _ = estimate(frame, outcome, 'month', 'post_adoption', post_targets)
        result['unit'] = unit
        average_rows.append(result.loc[result.estimand.eq('post_months_1_12')])
        result = result.loc[~result.estimand.eq('post_months_1_12')].copy()
        result['event_month'] = result.estimand.str.removeprefix('event_').astype(int)
        event_rows.append(result)
        for k in range(-12, -1):
            target = (switch & event.eq(k)).to_numpy()
            lead, _ = estimate(frame, outcome, 'month', 'post_adoption',
                               {f'event_{k}': target}, exclude=target)
            lead['event_month'], lead['unit'] = k, unit
            event_rows.append(lead)
        event_rows.append(pd.DataFrame([dict(outcome=outcome, estimand='reference',
                         event_month=-1, estimate=0.0, std_error=0.0, conf_low=0.0,
                         conf_high=0.0, p_value=np.nan, unit=unit)]))
    output_path = Path(output_path)
    dynamic = pd.concat(event_rows, ignore_index=True).sort_values(['outcome', 'event_month'])
    export(dynamic, output_path/'monthly_event_study.csv')
    export(pd.concat(average_rows, ignore_index=True), output_path/'monthly_average_effects.csv')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, default=Path('D:/household_survey/monthly_panel.parquet'))
    p.add_argument('--output', type=Path, default=Path('D:/solar_results/main_regressions/monthly'))
    a = p.parse_args()
    run(a.input, a.output)
