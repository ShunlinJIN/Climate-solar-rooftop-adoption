# Supplementary Figure 4: figure-specific functions are included below.
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
rows=[]
with open(DATA/"supp_fig04_battery_capacity_distribution.csv",encoding="utf-8-sig",newline="") as f:
    for r in csv.DictReader(f):
        rows.append((float(r["battery_capacity_kwh"]),int(r["households"]),float(r["percentage"])))
x=[a for a,_,_ in rows]; n=[b for _,b,_ in rows]; pct=[c for _,_,c in rows]
fig,ax=plt.subplots(figsize=(8.2,5.2))
ax.bar([str(v).rstrip("0").rstrip(".") for v in x],pct)
ax.set_xlabel("Battery Capacity (kWh)"); ax.set_ylabel("Percentage (%)")
ax.set_ylim(0,max(pct)*1.28)
for i,(p,nn) in enumerate(zip(pct,n)):
    ax.text(i,p+0.35,f"{p:.1f}%\n(n={nn})",ha="center",va="bottom",fontsize=8)
fig.tight_layout()
fig.savefig(OUT/"Supplementary_Fig_04.png",dpi=300,bbox_inches="tight")
fig.savefig(OUT/"Supplementary_Fig_04.pdf",bbox_inches="tight")
plt.close(fig)
print("Supplementary Fig. 4 reproduced.")
