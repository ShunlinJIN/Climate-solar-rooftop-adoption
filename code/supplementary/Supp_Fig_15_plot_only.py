from _supp_fig15_common import *

d = pd.read_csv(DATA_DIR / "supp_fig15_plot_coordinates.csv")

fig, axes = plt.subplots(1, 2, figsize=(10, 4.0))
configs = [
    ("a", "RRPV-only", axes[0]),
    ("b", "RRPV-BS", axes[1]),
]

for panel, system, ax in configs:
    q = d.loc[d["panel"].eq(panel)].copy()
    bars = q.loc[q["component"].eq("histogram")]
    kde = q.loc[q["component"].eq("kde")].sort_values("x")

    for _, r in bars.iterrows():
        ax.bar(
            (r["xmin"] + r["xmax"]) / 2,
            r["y"],
            width=(r["xmax"] - r["xmin"]),
            align="center",
            color="lightblue",
            edgecolor="black",
            linewidth=0.55,
            alpha=0.7,
        )

    ax.plot(
        kde["x"],
        kde["y"],
        color="darkblue",
        linewidth=1.5,
    )
    ax.axvline(
        1,
        color="red",
        linestyle=(0, (5, 5)),
        linewidth=1.4,
    )

    if system == "RRPV-only":
        ax.set_xlim(-0.6, 30.6)
        ax.set_ylim(0, 0.34)
        ax.set_xticks([0, 10, 20, 30])
        ax.set_yticks([0, 0.1, 0.2, 0.3])
        ax.text(
            2.2,
            0.27,
            "Generation = Consumption",
            color="red",
            fontweight="bold",
            fontsize=9.5,
        )
        ax.set_xlabel(
            "Generation/Consumption Ratio (RRPV-only adopters)",
            fontsize=10.5,
        )
    else:
        ax.set_xlim(0.85, 4.15)
        ax.set_ylim(0, 1.75)
        ax.set_xticks([1, 2, 3, 4])
        ax.set_yticks([0, 0.5, 1.0, 1.5])
        ax.text(
            1.12,
            0.52,
            "Generation = Consumption",
            color="red",
            fontweight="bold",
            fontsize=9.5,
        )
        ax.set_xlabel(
            "Generation/Consumption Ratio (RRPV-BS adopters)",
            fontsize=10.5,
        )

    ax.set_ylabel("Density", fontsize=10.5)
    ax.tick_params(labelsize=9)
    clean_axis(ax)
    ax.text(
        -0.12,
        1.02,
        panel,
        transform=ax.transAxes,
        fontsize=15,
        fontweight="bold",
        ha="left",
        va="bottom",
    )

fig.tight_layout(w_pad=2.2)
fig.savefig(
    OUT_DIR / "Supplementary_Fig_15.png",
    dpi=600,
    bbox_inches="tight",
    pad_inches=0.05,
)
fig.savefig(
    OUT_DIR / "Supplementary_Fig_15.pdf",
    bbox_inches="tight",
    pad_inches=0.05,
)
plt.close(fig)
print("Supplementary Fig. 15 reproduced.")
