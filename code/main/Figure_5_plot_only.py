#!/usr/bin/env python3
"""Render Figure 5 from its accompanying source data."""
from pathlib import Path
import subprocess
import sys

code = Path(__file__).resolve().parent
root = code.parent
subprocess.run([
    sys.executable, str(code / "figure5_heat/plot_figure5.py"),
    "--data-dir", str(root / "data"),
    "--results", str(root / "data"),
    "--output", str(root / "output"),
], check=True)
