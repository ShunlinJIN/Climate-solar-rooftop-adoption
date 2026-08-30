import csv
import matplotlib.pyplot as plt
from _paths import package_paths
ROOT, DATA, OUT = package_paths(__file__)
def read(name):
    with open(DATA/name,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
waves=read("supp_fig06_survey_rounds.csv")
reg=read("supp_fig06_regional_cross_section.csv")
cover=read("supp_table03_panelA.csv")
labels=[r["reference_period"].replace("January-June","Jan–Jun").replace("July-December","Jul–Dec") for r in waves]
ad=[int(r["rrpv_adopters"]) for r in waves]; non=[int(r["non_adopters"]) for r in waves]; tot=[int(r["completed_households"]) for r in waves]
regions=["Northern Jiangsu","Central Jiangsu","Southern Jiangsu"]
ad_r={r["region"]:int(r["rrpv_adopters"]) for r in cover if r["region"]!="Total"}
non_r={r["region"]:int(r["non_adopters"]) for r in cover if r["region"]!="Total"}
income={(r["region"],r["adoption_status"]):(float(r["mean_income_rmb"]),float(r["ci_low"]),float(r["ci_high"])) for r in reg}
fig,axs=plt.subplots(2,2,figsize=(12,8))
ax=axs[0,0]
ax.plot(labels,ad,marker="o",label="RRPV adopters"); ax.plot(labels,non,marker="o",label="Non-adopters"); ax.plot(labels,tot,linestyle="--",label="Total")
ax.set_title("Panel composition by survey round"); ax.set_ylabel("Completed households"); ax.tick_params(axis="x",rotation=45,labelsize=8); ax.legend(frameon=False,fontsize=8); ax.text(-.12,1.03,"a",transform=ax.transAxes,fontweight="bold",fontsize=14)
ax=axs[0,1]; xx=list(range(len(waves)-1)); w=.38
new=[int(r["new_entrants"]) for r in waves[1:]]
ex=[0 if r["permanent_exits_after_round"]=="" else int(r["permanent_exits_after_round"]) for r in waves[1:]]
ax.bar([i-w/2 for i in xx],new,w,label="New entrants"); ax.bar([i+w/2 for i in xx],ex,w,label="Permanent exits")
ax.set_xticks(xx); ax.set_xticklabels(labels[1:],rotation=45,ha="right",fontsize=8); ax.set_title("Post-baseline entry and permanent exit"); ax.set_ylabel("Households"); ax.legend(frameon=False,fontsize=8); ax.text(-.12,1.03,"b",transform=ax.transAxes,fontweight="bold",fontsize=14)
ax=axs[1,0]; xx=list(range(3)); w=.38
ax.bar([i-w/2 for i in xx],[ad_r[r] for r in regions],w,label="RRPV adopters"); ax.bar([i+w/2 for i in xx],[non_r[r] for r in regions],w,label="Non-adopters")
ax.set_xticks(xx); ax.set_xticklabels([r.replace(" ","\n",1) for r in regions],fontsize=9); ax.set_title("Regional composition, July 2026"); ax.set_ylabel("Households"); ax.legend(frameon=False,fontsize=8); ax.text(-.12,1.03,"c",transform=ax.transAxes,fontweight="bold",fontsize=14)
ax=axs[1,1]
for status,marker,off in [("RRPV adopters","o",-0.08),("Non-adopters","s",0.08)]:
    xs=[i+off for i in xx]; means=[]; lo=[]; hi=[]
    for r in regions:
        m,l,h=income[(r,status)]; means.append(m); lo.append(m-l); hi.append(h-m)
    ax.errorbar(xs,means,yerr=[lo,hi],fmt=marker,capsize=3,label=status)
ax.set_xticks(xx); ax.set_xticklabels([r.replace(" ","\n",1) for r in regions],fontsize=9); ax.set_title("Household income by region"); ax.set_ylabel("Monthly household income (RMB)"); ax.legend(frameon=False,fontsize=8); ax.text(-.12,1.03,"d",transform=ax.transAxes,fontweight="bold",fontsize=14)
fig.tight_layout(); fig.savefig(OUT/"Supplementary_Fig_06.png",dpi=300,bbox_inches="tight"); fig.savefig(OUT/"Supplementary_Fig_06.pdf",bbox_inches="tight"); plt.close(fig)
print("Supplementary Fig. 6 reproduced.")
