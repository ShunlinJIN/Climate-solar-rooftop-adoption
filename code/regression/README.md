# Rooftop solar responds to extreme heat and reduces energy poverty among rural households

Regression estimation code for the empirical models reported in the main text.

These scripts are provided for inspection and require the underlying analysis datasets. They are not called by the capsule's figure-and-table reproduction workflow, which runs through `/code/run`.

## County

| Script | Analysis | Main text location |
|---|---|---|
| `county/county_regressions.R` | County adoption, distributed lags, subgroup heterogeneity and the Liaoning rationing event study | Eqs. (1)-(3); selected regression results in Figs. 1-3 |

## Household

| Script | Analysis | Main text location |
|---|---|---|
| `household/household_monthly.py` | Monthly adoption effects on electricity bills, bill-to-income ratios, consumption and grid purchases | Eqs. (5)-(6); Fig. 5a-c |
| `household/household_income.py` | Adoption effects on non-PV income, PV revenue, total income and income net of electricity bills | Fig. 5d |
| `household/household_heat_slope.py` | Post-adoption changes in the temperature-consumption relationship | Fig. 5e |
| `household/household_energy_poverty.py` | Adoption effects on electricity-burden incidence at the 5% threshold and income-group differences | Fig. 5f |
| `household/household_2sls.py` | Two-stage least squares (2SLS) estimates of adoption effects on household electricity outcomes | Eqs. (7)-(8); Fig. 5g; Supplementary Table 32, Panel D |
| `household/household_daily_heat.py` | Daily adoption effects on extreme-heat and other days | Supplementary Note 12 |
| `household/household_motives.py` | Post-adoption electricity outcomes by reported heat-related bill-pressure motives | Supplementary Table 32, Panel E: primary top-three-motive comparison |

## Rebound

| Script | Analysis | Main text location |
|---|---|---|
| `rebound/rebound_regressions.R` | Daily generation-consumption relationships and income-group heterogeneity | Eq. (4); Fig. 4a-d |

R packages: `data.table`, `fixest`, `arrow`.

Python packages: `numpy`, `pandas`, `scipy`, `pyarrow`.
