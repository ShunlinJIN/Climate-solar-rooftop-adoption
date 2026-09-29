# Output index

The master workflow generates the following outputs. Input filenames below are relative to the indicated source-data directory.

## Main figures

Scripts: `code/main/`. Inputs: `data/non-confidential/aggregate_main/`.

| Output | Script | Source data |
| --- | --- | --- |
| Figure 1 | `Figure_1_plot_only.R` | `figure1_plot_data.csv` |
| Figure 2 | `Figure_2_plot_only.R` | `figure2_plot_data.csv`, `figure2_pairwise_tests.csv` |
| Figure 3 | `Figure_3_plot_only.R` | `figure3_plot_data.csv` |
| Figure 4 | `Figure_4_plot_only.R` | `figure4_plot_data.csv` |
| Figure 5 | `Figure_5_plot_only.py` | `figure5_plot_data.csv`, `figure5_panel_e.csv`, `Figure5_panel_f_source_data.csv`, `figure5_panel_g.csv` |
| Figure 6 | `Figure_6_plot_only.R` | `figure6_plot_data.csv` |

## Supplementary Figures

Scripts: `code/supplementary/`. Inputs: `data/non-confidential/aggregate_supplementary/`.

| Output | Script | Source data |
| --- | --- | --- |
| Supplementary Figure 1 | `Supp_Fig_01_plot_only.py` | `supp_fig01_map_plot_data.csv` |
| Supplementary Figure 2 | `Supp_Fig_02_plot_only.py` | `supp_fig02_distribution_data.csv` |
| Supplementary Figure 3 | `Supp_Fig_03_plot_only.py` | `supp_fig03_daily_flows.csv` |
| Supplementary Figure 4 | `Supp_Fig_04_plot_only.py` | `supp_fig04_battery_capacity_distribution.csv` |
| Supplementary Figure 5 | `Supp_Fig_05_plot_only.py` | `supp_fig05_monthly_flows.csv` |
| Supplementary Figure 6 | `Supp_Fig_06_plot_only.py` | `supp_fig06_survey_rounds.csv`, `supp_fig06_regional_cross_section.csv`, `supp_table03_panelA.csv` |
| Supplementary Figure 7 | `Supp_Fig_07_plot_only.R` | `supp_fig07_search_temperature.csv`, `supp_fig07_temperature_bin_estimates.csv` |
| Supplementary Figure 8 | `Supp_Fig_08_plot_only.py` | `supp_fig08_income_density.csv`, `supp_fig08_income_benchmark_shares.csv` |
| Supplementary Figure 9 | `Supp_Fig_09_plot_only.R` | `supp_fig09_timing_placebo.csv` |
| Supplementary Figure 10 | `Supp_Fig_10_plot_only.R` | `supp_fig10_cross_province_placebo.csv` |
| Supplementary Figure 11 | `Supp_Fig_11_plot_only.R` | `supp_fig11_oos_monthly.csv` |
| Supplementary Figure 12 | `Supp_Fig_12_plot_only.R` | `supp_fig12_annual_heat_effects.csv` |
| Supplementary Figure 13 | `Supp_Fig_13_plot_only.R` | `supp_fig13_observed_penetration.csv`, `supp_fig13_marginal_effect_curve.csv` |
| Supplementary Figure 14 | `Supp_Fig_14_plot_only.R` | `supp_fig14_projection.csv` |
| Supplementary Figure 15 | `Supp_Fig_15_plot_only.py` | `supp_fig15_plot_coordinates.csv` |
| Supplementary Figure 16 | `Supp_Fig_16_plot_only.R` | `supp_fig16_comparability_density.csv` |
| Supplementary Figure 17 | `Supp_Fig_17_plot_only.R` | `supp_fig26_hourly_flow_composition.csv` |
| Supplementary Figure 18 | `Supp_Fig_18_plot_only.R` | `supp_fig18_hourly_coefficients.csv`, `supp_fig18_window_coefficients.csv` |
| Supplementary Figure 19 | `Supp_Fig_19_plot_only.py` | `supp_fig19_propensity_density.csv` |
| Supplementary Figure 20 | `Supp_Fig_20_plot_only.py` | `supp_fig20_complete_event_time.csv` |
| Supplementary Figure 21 | `Supp_Fig_21_plot_only.py` | `supp_fig21_source.csv` |
| Supplementary Figure 22 | `Supp_Fig_22_plot_only.py` | `supp_fig22_source.csv` |
| Supplementary Figure 23 | `Supp_Fig_23_plot_only.py` | `supp_fig23_source.csv` |
| Supplementary Figure 24 | `Supp_Fig_24_plot_only.R` | `supp_fig24_daily_rrpv_only_plot.csv`, `supp_fig24_daily_rrpv_bs_plot.csv`, `supp_fig24_hourly_plot.csv`, `supp_fig24_validation_metrics.csv` |
| Supplementary Figure 25 | `Supp_Figs_25_26_plot_only.R` | `supp_fig25_hourly_load_plot.csv`, `supp_fig25_hourly_load_metrics.csv`, `supp_fig26_hourly_flow_composition.csv` |
| Supplementary Figure 26 | `Supp_Figs_25_26_plot_only.R` | `supp_fig26_hourly_flow_composition.csv`, `supp_fig25_hourly_load_plot.csv`, `supp_fig25_hourly_load_metrics.csv` |
| Supplementary Figure 27 | `Supp_Fig_27_plot_only.R` | `supp_fig27_battery_dispatch_plot.csv`, `supp_fig27_battery_dispatch_metrics.csv` |

## Supplementary Tables

All tables are exported by `code/supplementary/reproduce_supplementary_tables.py`. Inputs are in `data/non-confidential/aggregate_supplementary/`. Final titles and notes are supplied in `supplementary_table_notes.json` and exported as `Supplementary_Table_Notes.md`.

| Table | Source file | Exported file |
| --- | --- | --- |
| 1 | `supp_table01.csv` | `Supplementary_Table_01.csv` |
| 2 | `supp_table02.csv` | `Supplementary_Table_02.csv` |
| 3 | `supp_table03_panelA.csv`, `supp_table03_panelB.csv` | `Supplementary_Table_03_panelA.csv`, `Supplementary_Table_03_panelB.csv` |
| 4 | `supp_table04.csv` | `Supplementary_Table_04.csv` |
| 5 | `supp_table05.csv` | `Supplementary_Table_05.csv` |
| 6 | `supp_table06.csv` | `Supplementary_Table_06.csv` |
| 7 | `supp_table07.csv` | `Supplementary_Table_07.csv` |
| 8 | `supp_table08.csv` | `Supplementary_Table_08.csv` |
| 9 | `supp_table09.csv` | `Supplementary_Table_09.csv` |
| 10 | `supp_table10.csv` | `Supplementary_Table_10.csv` |
| 11 | `supp_table11.csv` | `Supplementary_Table_11.csv` |
| 12 | `supp_table12.csv` | `Supplementary_Table_12.csv` |
| 13 | `supp_table13.csv` | `Supplementary_Table_13.csv` |
| 14 | `supp_table14.csv` | `Supplementary_Table_14.csv` |
| 15 | `supp_table15.csv` | `Supplementary_Table_15.csv` |
| 16 | `supp_table16.csv` | `Supplementary_Table_16.csv` |
| 17 | `supp_table17.csv` | `Supplementary_Table_17.csv` |
| 18 | `supp_table18.csv` | `Supplementary_Table_18.csv` |
| 19 | `supp_table19.csv` | `Supplementary_Table_19.csv` |
| 20 | `supp_table20.csv` | `Supplementary_Table_20.csv` |
| 21 | `supp_table21.csv` | `Supplementary_Table_21.csv` |
| 22 | `supp_table22.csv` | `Supplementary_Table_22.csv` |
| 23 | `supp_table23.csv` | `Supplementary_Table_23.csv` |
| 24 | `supp_table24.csv` | `Supplementary_Table_24.csv` |
| 25 | `supp_table25.csv` | `Supplementary_Table_25.csv` |
| 26 | `supp_table26.csv` | `Supplementary_Table_26.csv` |
| 27 | `supp_table27.csv` | `Supplementary_Table_27.csv` |
| 28 | `supp_table28.csv` | `Supplementary_Table_28.csv` |
| 29 | `supp_table29.csv` | `Supplementary_Table_29.csv` |
| 30 | `supp_table30.csv` | `Supplementary_Table_30.csv` |
| 31 | `supp_table31.csv` | `Supplementary_Table_31.csv` |
| 32 | `supp_table32.csv` | `Supplementary_Table_32.csv` |
| 33 | `supp_table33.csv` | `Supplementary_Table_33.csv` |
| 34 | `supp_table34.csv` | `Supplementary_Table_34.csv` |
| 35 | `supp_table35.csv` | `Supplementary_Table_35.csv` |
