#!/usr/bin/env bash
set -euo pipefail
CODE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$CODE_DIR/.." && pwd)"
mkdir -p "$ROOT/output"

Rscript "$CODE_DIR/Figure_1_plot_only.R"
Rscript "$CODE_DIR/Figure_2_plot_only.R"
Rscript "$CODE_DIR/Figure_3_plot_only.R"
Rscript "$CODE_DIR/Figure_4_plot_only.R"
python "$CODE_DIR/Figure_5_plot_only.py"
Rscript "$CODE_DIR/Figure_6_plot_only.R"

echo "All Main Figures 1-6 completed."
echo "Outputs: $ROOT/output"
