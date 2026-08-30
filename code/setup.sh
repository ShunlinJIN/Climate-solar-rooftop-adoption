#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 -m pip install --upgrade pip
python3 -m pip install -r "$ROOT/code/requirements.txt"

Rscript "$ROOT/code/setup.R"

echo "Environment setup complete."