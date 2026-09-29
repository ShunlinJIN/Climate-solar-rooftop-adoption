# Source data

The included CSV files provide non-identifying inputs for reproducing the figures and tables. See `OUTPUT_INDEX.md` for the input files used by each output.

## Files

- `data/non-confidential/aggregate_main/` contains the main-figure inputs.
- `data/non-confidential/aggregate_supplementary/` contains the Supplementary Figure inputs and Supplementary Table entries.
- `supplementary_table_notes.json` contains table titles and notes.

## Fields and units

- `estimate` and `std_error` (or `se`) contain estimates and standard errors. Confidence-limit columns contain the supplied interval endpoints.
- `unit` identifies the measurement scale. Percentage points and percentages are distinct units.
- `panel`, `panel_label`, `row_order` and `column_order` identify table or figure sections and ordering. `display_value` retains the displayed value and significance marks.
- Blank cells indicate omitted, inapplicable or unreported values. Reference categories are labelled where applicable.
- Supplementary Table 12 and Panel B of Supplementary Table 29 use the precision reported in those tables. Values such as `<0.001` are stored as display strings.
- Figure 5 displays monetary amounts in US dollars at RMB 6.8 per US$1; the source expenditure and income estimates retain their RMB units. Supplementary Tables retain their stated units.
- In `supp_fig19_propensity_density.csv`, `stage` and `group` identify matching status and treatment group; `propensity_score` and `density` are the horizontal and vertical curve coordinates.

Data-access arrangements and licensing are described in `DATA_AVAILABILITY.md` and `DATA_LICENSE.md`.
