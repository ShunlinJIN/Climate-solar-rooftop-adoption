#!/usr/bin/env bash
set -euo pipefail
CODE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python "$CODE_DIR/Supp_Fig_04_plot_only.py"
python "$CODE_DIR/Supp_Fig_06_plot_only.py"
python "$CODE_DIR/Supp_Fig_20_plot_only.py"
python "$CODE_DIR/reproduce_ready_tables.py"
echo "Current v1 supplementary package completed."

Rscript "$CODE_DIR/Supp_Fig_18_plot_only.R"
Rscript "$CODE_DIR/Supp_Fig_24_plot_only.R"
Rscript "$CODE_DIR/Supp_Figs_25_26_plot_only.R"
