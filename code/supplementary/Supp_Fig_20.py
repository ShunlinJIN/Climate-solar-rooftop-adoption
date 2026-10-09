# Supplementary Figure 20: figure-specific functions are included below.
import csv
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# Local functions and setup
# -----------------------------------------------------------------------------
from pathlib import Path
def package_paths(script_file):
    code_dir = Path(script_file).resolve().parent
    root = code_dir.parent
    data_dir = root / "data"
    output_dir = root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return root, data_dir, output_dir

# -----------------------------------------------------------------------------
# Data, panels and export
# -----------------------------------------------------------------------------
ROOT, DATA, OUT = package_paths(__file__)
with open(DATA/"supp_fig20_complete_event_time.csv",encoding="utf-8-sig",newline="") as f: rows=list(csv.DictReader(f))
order=[("electricity_bill_rmb","Recorded electricity expenditure","RMB/month"),
("bill_income_ratio_current_pct","Electricity-bill-to-income ratio","Percentage points"),
("total_electricity_consumption_kwh","Total household electricity use","kWh/month"),
("grid_import_kwh","Public-grid purchases","kWh/month")]
fig,axs=plt.subplots(2,2,figsize=(12,8))
for ax,(outcome,title,ylabel),tag in zip(axs.flat,order,"abcd"):
    d=[r for r in rows if r["outcome"]==outcome]; d.sort(key=lambda r: float(r["event_time_month"]))
    x=[float(r["event_time_month"]) for r in d]; y=[float(r["estimate"]) for r in d]; lo=[float(r["conf_low"]) for r in d]; hi=[float(r["conf_high"]) for r in d]
    ax.fill_between(x,lo,hi,alpha=.18); ax.plot(x,y,marker="o",markersize=3); ax.axhline(0,linestyle="--",linewidth=.8); ax.axvline(0,linestyle=":",linewidth=.8)
    ax.set_title(title); ax.set_xlabel("Months relative to grid connection"); ax.set_ylabel(ylabel); ax.text(-.11,1.03,tag,transform=ax.transAxes,fontweight="bold",fontsize=14)
fig.tight_layout(); fig.savefig(OUT/"Supplementary_Fig_20.png",dpi=300,bbox_inches="tight"); fig.savefig(OUT/"Supplementary_Fig_20.pdf",bbox_inches="tight"); plt.close(fig)
print("Supplementary Fig. 20 reproduced.")
