"""Daily temperature-response regressions for Fig. 5e and Eq. (S12.3)."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


ARRAY_COLUMNS = (
    "household", "village", "date", "year_month", "post", "temperature",
    "total_use", "switcher",
)


def load_input(path: Path) -> dict[str, np.ndarray]:
    """Read an analysis panel, retaining the January 2021-June 2026 sample."""
    if path.suffix.lower() == ".npz":
        with np.load(path, allow_pickle=False) as archive:
            missing = set(ARRAY_COLUMNS) - set(archive.files)
            if missing:
                raise ValueError(f"Missing arrays: {sorted(missing)}")
            data = {k: archive[k].copy() for k in ARRAY_COLUMNS}
        lengths = {len(value) for value in data.values()}
        if len(lengths) != 1 or any(value.ndim != 1 for value in data.values()):
            raise ValueError("Input arrays must be one-dimensional and have equal lengths.")
        dates = pd.to_datetime(data["date"], unit="D", origin="unix")
        expected_month = 12 * dates.year + dates.month
        if not np.array_equal(data["year_month"], expected_month):
            raise ValueError("year_month must equal 12 * year + month.")
    else:
        frame = (pd.read_parquet(path) if path.suffix.lower() == ".parquet"
                 else pd.read_csv(path, dtype={"household_id": str, "village_id": str}))
        required = ["household_id", "village_id", "date", "timing_class",
                    "main_causal_sample", "post_adoption", "ordinary_adoption_date",
                    "temperature_mean_c", "total_electricity_consumption_kwh"]
        missing = set(required) - set(frame.columns)
        if missing:
            raise ValueError(f"Missing columns: {sorted(missing)}")
        frame = frame.loc[frame.main_causal_sample.eq(1)].copy()
        if not frame.timing_class.isin(["never_treated", "within_panel_switcher"]).all():
            raise ValueError("The analysis sample must contain never-treated and within-panel switcher households.")
        if frame[["household_id", "village_id", "date"]].isna().any().any():
            raise ValueError("Household identifiers, village identifiers and dates cannot be missing.")
        dates = pd.DatetimeIndex(pd.to_datetime(frame.date, errors="raise"))
        if dates.tz is not None or not (dates == dates.normalize()).all():
            raise ValueError("Dates must be timezone-free calendar dates.")
        adoption_date = pd.to_datetime(frame.ordinary_adoption_date, errors="raise")
        connection_dates = adoption_date.groupby(frame.household_id).nunique(dropna=False)
        if (connection_dates != 1).any():
            raise ValueError("Each household must have one recorded connection date, including consistent missingness.")
        implied_post = adoption_date.notna().to_numpy() & np.asarray(dates >= adoption_date)
        if not np.array_equal(implied_post, frame.post_adoption.eq(1).to_numpy()):
            raise ValueError("post_adoption does not match the recorded first connection date.")
        data = {
            "household": frame.household_id.to_numpy(),
            "village": frame.village_id.to_numpy(),
            "date": dates.to_numpy(dtype="datetime64[D]").astype("int64"),
            "year_month": np.asarray(12 * dates.year + dates.month),
            "post": frame.post_adoption.to_numpy(),
            "temperature": frame.temperature_mean_c.to_numpy(dtype=float),
            "total_use": frame.total_electricity_consumption_kwh.to_numpy(dtype=float),
            "switcher": frame.timing_class.eq("within_panel_switcher").to_numpy(dtype=int),
        }
    period = (dates >= "2021-01-01") & (dates <= "2026-06-30")
    data = {k: value[period] for k, value in data.items()}
    check_input(data)
    return data


def check_input(data: dict[str, np.ndarray]) -> None:
    if not len(data["post"]):
        raise ValueError("No observations in the analysis period.")
    frame = pd.DataFrame(data)
    if frame.isna().any().any():
        raise ValueError("Analysis variables must not contain missing values.")
    if frame.duplicated(["household", "date"]).any():
        raise ValueError("Household-date keys must be unique.")
    if not np.isfinite(frame[["temperature", "total_use"]].to_numpy()).all():
        raise ValueError("Temperature and electricity consumption must be finite.")
    if not frame.post.isin([0, 1]).all() or not frame.switcher.isin([0, 1]).all():
        raise ValueError("post and switcher must be binary.")
    metadata = frame.groupby("household")[["village", "switcher"]].nunique()
    if (metadata != 1).any().any():
        raise ValueError("Each household must have one village and one sample classification.")
    if (frame.loc[frame.switcher.eq(0), "post"] != 0).any():
        raise ValueError("Never-treated households must have post equal to zero.")
    ordered = frame.sort_values(["household", "date"])
    if (ordered.groupby("household").post.diff() < 0).any():
        raise ValueError("Post-connection status must be nondecreasing within each household.")
    observed_states = frame.loc[frame.switcher.eq(1)].groupby("household").post.nunique()
    if not len(observed_states) or (observed_states != 2).any():
        raise ValueError("Switcher households require observations before and after connection.")
    support = frame.groupby(["village", "date"]).temperature.agg(["min", "max"])
    if ((support["max"] - support["min"]) > 1e-7).any():
        raise ValueError("Temperature must be common within each village-date.")


def within(values: np.ndarray, groups: list[np.ndarray], tolerance: float = 1e-10,
           max_iterations: int = 3000) -> tuple[np.ndarray, int]:
    """Absorb the two fixed effects by alternating group-mean projections."""
    residual = np.asarray(values, dtype=float).copy()
    codes = [pd.factorize(group, sort=True)[0] for group in groups]
    counts = [np.bincount(group) for group in codes]
    for iteration in range(1, max_iterations + 1):
        change = 0.0
        for group, count in zip(codes, counts):
            for column in range(residual.shape[1]):
                mean = np.bincount(group, weights=residual[:, column], minlength=len(count)) / count
                change = max(change, float(np.max(np.abs(mean))))
                residual[:, column] -= mean[group]
        if change < tolerance:
            return residual, iteration
    raise RuntimeError(f"Fixed-effect absorption did not converge; last change={change:g}.")


def design(data: dict[str, np.ndarray], fixed_effects: str) -> tuple[np.ndarray, list[str]]:
    temperature = data["temperature"]
    post = data["post"].astype(float)
    basis = np.column_stack([temperature - 20, np.maximum(temperature - 25, 0),
                             np.maximum(temperature - 30, 0)])
    interactions = post[:, None] * np.column_stack([np.ones(len(post)), basis])
    interaction_names = ["post", "post_temp20", "post_temp25", "post_temp30"]
    if fixed_effects == "village_year_month":
        return np.column_stack([basis, interactions]), ["temp20", "temp25", "temp30"] + interaction_names
    if fixed_effects == "village_date":
        return interactions, interaction_names
    raise ValueError(f"Unknown fixed-effect specification: {fixed_effects}")


def solve_blocks(blocks: list[dict]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    xx = np.stack([block["xx"] for block in blocks])
    xy = np.stack([block["xy"] for block in blocks])
    total_xx, total_xy = xx.sum(axis=0), xy.sum(axis=0)
    if len(blocks) < 3:
        raise ValueError("At least three villages are required for delete-one-village inference.")
    if np.linalg.matrix_rank(total_xx) != len(total_xy):
        raise ValueError("The full-sample design is rank deficient.")
    beta = np.linalg.solve(total_xx, total_xy)
    replicates = []
    for index, (block_xx, block_xy) in enumerate(zip(xx, xy)):
        reduced_xx = total_xx - block_xx
        if np.linalg.matrix_rank(reduced_xx) != len(total_xy):
            raise ValueError(f"The design is rank deficient after excluding village {blocks[index]['village']}.")
        replicates.append(np.linalg.solve(reduced_xx, total_xy - block_xy))
    replicates = np.stack(replicates)
    centred = replicates - replicates.mean(axis=0)
    count = len(blocks)
    covariance = (count - 1) / count * (centred.T @ centred)
    return beta, covariance, replicates


def inference(beta: np.ndarray, covariance: np.ndarray, contrast: np.ndarray,
              degrees_freedom: int) -> dict:
    estimate = float(contrast @ beta)
    variance = float(contrast @ covariance @ contrast)
    if variance < -1e-12:
        raise ValueError("Negative variance for a linear contrast.")
    standard_error = float(np.sqrt(max(0.0, variance)))
    critical = float(stats.t.ppf(0.975, degrees_freedom))
    t_statistic = estimate / standard_error if standard_error > 0 else np.nan
    return {"estimate": estimate, "std_error": standard_error,
            "conf_low": estimate - critical * standard_error,
            "conf_high": estimate + critical * standard_error,
            "t_statistic": t_statistic, "df": degrees_freedom,
            "p_value": float(2 * stats.t.sf(abs(t_statistic), degrees_freedom))}


def estimate(data: dict[str, np.ndarray]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Fit both specifications and report the summed slope change above 30 C."""
    warm = data["temperature"] > 20
    sample = {key: value[warm] for key, value in data.items()}
    villages = np.unique(sample["village"])
    if len(villages) < 3:
        raise ValueError("The warm-day analysis sample must contain at least three villages.")
    estimates, coefficients, covariances = [], [], []
    for fixed_effects in ("village_date", "village_year_month"):
        blocks = []
        for village in villages:
            selected = sample["village"] == village
            local = {key: value[selected] for key, value in sample.items()}
            matrix, names = design(local, fixed_effects)
            time = local["date"] if fixed_effects == "village_date" else local["year_month"]
            residual, _ = within(np.column_stack([local["total_use"], matrix]),
                                 [local["household"], time])
            y, x = residual[:, 0], residual[:, 1:]
            blocks.append({"village": village, "xx": x.T @ x, "xy": x.T @ y})
        # Both absorbed fixed effects are nested in villages. Subtracting a
        # village's cross-products therefore gives its exact leave-one refit.
        beta, covariance, _ = solve_blocks(blocks)
        contrast = np.array([name.startswith("post_temp") for name in names], dtype=float)
        summary = {"fixed_effects": fixed_effects, "observations": len(sample["post"]),
                   "households": len(np.unique(sample["household"])),
                   "adopters": len(np.unique(sample["household"][sample["switcher"] == 1])),
                   "villages": len(villages)}
        estimates.append({**summary, "estimand": "slope_change_above_30",
                          "unit": "kWh/day/degree_C",
                          **inference(beta, covariance, contrast, len(villages) - 1)})
        for index, name in enumerate(names):
            coefficients.append({**summary, "term": name,
                                 **inference(beta, covariance, np.eye(len(names))[index], len(villages) - 1)})
            for other_index, other_name in enumerate(names):
                covariances.append({"fixed_effects": fixed_effects, "term1": name,
                                    "term2": other_name, "covariance": covariance[index, other_index]})
    return pd.DataFrame(estimates), pd.DataFrame(coefficients), pd.DataFrame(covariances)


def run(input_path: Path, output_dir: Path) -> pd.DataFrame:
    data = load_input(input_path)
    results, coefficients, covariance = estimate(data)
    output_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_dir / "heat_slope_estimates.csv", index=False, float_format="%.15g")
    coefficients.to_csv(output_dir / "heat_slope_coefficients.csv", index=False, float_format="%.15g")
    covariance.to_csv(output_dir / "heat_slope_covariance.csv", index=False, float_format="%.15g")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path,
                        default=Path("D:/household_survey/panel_e_daily_input.parquet"))
    parser.add_argument("--output", type=Path, default=Path("D:/solar_results/main_regressions/heat_slope"))
    args = parser.parse_args()
    print(run(args.input, args.output).to_string(index=False))


if __name__ == "__main__":
    main()
