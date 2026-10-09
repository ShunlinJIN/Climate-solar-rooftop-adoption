# Source data

The CSV files contain non-identifying inputs for the manuscript figures and tables. `OUTPUT_INDEX.md` lists the files used by each output.

## Data locations

- `aggregate_main/` contains main-figure inputs.
- `aggregate_supplementary/` contains Supplementary Figure inputs, Supplementary Table entries and `supplementary_table_notes.json`.

Both directories are under `data/non-confidential/`.

## Fields and units

Estimates and standard errors are stored in `estimate` and `std_error` (or `se`). Confidence-limit columns hold the supplied interval endpoints, which plotting scripts use directly. `unit` identifies the measurement scale; percentages and percentage points are distinct. `panel`, ordering columns and group labels identify the corresponding figure or table section. `display_value` preserves reported precision and significance marks. Blank cells denote omitted, inapplicable or unreported values.

Figure 5 displays monetary effects in US dollars at RMB 6.8 per US$1. Its source estimates and the Supplementary Tables retain the indicated original units. Panel e reports post-adoption changes in the slope above 30°C under two fixed-effects specifications. Panel f reports changes in monthly incidence at the 5% electricity-burden threshold overall and by pre-adoption income.

Figure 4 income groups are county-income tertiles defined using rural per-capita disposable income in 2017, separately for the two system types. The full-sample and group confidence intervals are supplied in `figure4_plot_data.csv`.

Supplementary Figure 7 policy estimates are stored in `supp_fig07_policy_estimates.csv`; its search inputs are stored separately. Supplementary Figure 19 uses item-level response counts with valid-response denominators and observed clock-hour mean household consumption for the common calendar year 2020. Daytime comprises 06:00–18:59. Its daytime share is aggregate daytime consumption divided by aggregate 24-hour consumption, not an average of household-specific shares. The questionnaire and hourly-monitoring samples are separate.

In `supp_fig16_propensity_density.csv`, `stage` and `group` identify matching stage and treatment group; `propensity_score` and `density` are the stored horizontal and vertical curve coordinates.

Supplementary Table 31 uses long-format rows for questionnaire responses and the system-type comparison. Supplementary Table 32 distinguishes the village-clustered first-stage Wald F statistic (28.23) from the Cragg–Donald Wald F statistic (25.33). Its Panel G retains the 10% threshold sensitivity results alongside the 5% results and income-group comparisons.

Supplementary Table 12 uses panels A (historical temperature exposure and variability) and B (solar resources, terrain and county income); `dimension_id` identifies the seven comparisons A–G within these panels.

Supplementary Table 17 Panel F uses 989 adopters with a valid reported current annual per-capita household income excluding RRPV revenue. Lower income is strictly below the adopter median of RMB 15,960 per person per year (492 households); higher income is at or above it (497 households). The aggregate `financing_current_income_counts.csv` contains `users`, `households` and `use_percent = 100 × users / households`. `supp_table17.csv` retains full-precision percentages; display percentages are rounded to one decimal place. Each funding channel is non-exclusive. The 1,033-household totals in other financing panels are not restricted by the current-income grouping.

Data access and licensing are described in `DATA_AVAILABILITY.md` and `DATA_LICENSE.md`.
