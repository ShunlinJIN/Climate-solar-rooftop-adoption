# Source data

The CSV files contain non-identifying plotting coordinates, regression summaries, distributions and table entries used by the public reproduction workflow. All input files required for a run are included.

## Field conventions

- `estimate` gives the coefficient or summary statistic in the stated `unit`.
- `std_error` (or `se`) gives the reported standard error. Confidence-limit columns use the supplied lower and upper endpoints.
- `panel`, `row_order` and `column_order` identify the position within multipart outputs. `display_value` preserves the table's displayed value and significance marks.
- A blank cell denotes an omitted, inapplicable or unreported statistic. A reference category is marked explicitly where applicable; its omitted uncertainty is not a zero-width confidence interval.
- A reported percentage and a percentage-point difference are distinguished in the unit fields. Probabilities and percentage points are not interchangeable.
- Files may retain more precision than the printed manuscript. `source_precision` identifies entries supplied at the precision of the reported table. A value such as `<0.001` is stored as a display string rather than an invented exact p value.

## Main figures

Figures 1–4 and 6 use their corresponding `figureN_plot_data.csv`. Figure 5 uses `figure5_plot_data.csv` together with the panel-specific source files listed in `OUTPUT_INDEX.md`.

Figure 4c uses county-income deciles for RRPV-only households; Figure 4d uses county-income tertiles for RRPV-BS households. The income ranking uses 2017 county rural per-capita disposable income.

Figure 5 displays monetary amounts in US dollars at RMB 6.8 per US$1. Source estimates for electricity expenditure and income retain their RMB units. Panel e displays electricity quantities in kWh/day and expenditure in US$/day. Panel f reports changes in the probability of electricity burdens meeting the 5% and 10% thresholds, in percentage points. Panel g displays electricity quantities in units of 10 kWh/month, with labels showing kWh/month; monetary amounts are in US$/month. The Supplementary Tables retain their stated RMB units.

## Supplementary tables

`supp_table01.csv` through `supp_table35.csv` hold the table entries. Table 3 uses `supp_table03_panelA.csv` and `supp_table03_panelB.csv`. The export script checks all table numbers and required panels and writes the corresponding `Supplementary_Table_*.csv` files.

`supplementary_table_notes.json` supplies final table titles and notes. These are exported together as `Supplementary_Table_Notes.md`. The notes define the samples, controls, fixed effects, clustering and inference methods for each analysis.

For Supplementary Table 32D, the Cragg–Donald Wald F statistic and the village-clustered first-stage Wald F statistic are separate diagnostics. Their values are 25.33 and 28.23, respectively, for the full sample of 96,702 household-months.
