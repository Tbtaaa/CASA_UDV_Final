"""
Calculate how many children (1 in X) live in these clusters and median travel time for each cluster.
Visualisation will allow the user to select between clusters to  see 
(a) how many children live in these clusters compared to total (brick composition diagram) and
(b) median transit time to Top 25% P8 school for cluster compared to London median transit time (simple bar chart). 
"""

# ---------------------------------------------------------------------------
# Libraries
# ---------------------------------------------------------------------------

import warnings
warnings.filterwarnings("ignore")

import os
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import libpysal

from esda.moran import Moran_Local_BV
from pyprojroot import here

# ---------------------------------------------------------------------------
# Define routes and read files
# ---------------------------------------------------------------------------

ROOT = here()
GPKG_PATH = ROOT / "data" / "london_lsoa_education_accessibility.gpkg"
INCOME_PATH = ROOT / "data" / "income_datasetfinal.xlsx"
OUTPUT_DIR = ROOT / "outputs" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

income = pd.read_excel(INCOME_PATH)
gdf = gpd.read_file(GPKG_PATH)

# Clean income file
income = pd.read_excel(
    INCOME_PATH,
    sheet_name="Net income after housing costs",
    header=3)

income = income[[
    "MSOA code",
    "MSOA name",
    "Region name",
    "Disposable (net) annual income after housing costs (£)"]].copy()

income = income.rename(columns={
    "MSOA code": "MSOA11CD",
    "MSOA name": "MSOA11NM",
    "Region name": "RegionName",
    "Disposable (net) annual income after housing costs (£)": "income_ahc"})

print("\nIncome preview:")
print(income.head())
print(f"\nIncome rows: {len(income):,}")

# keep only rows with geometry + deprivation
gdf_base = gdf.dropna(subset=["idaci_score", "geometry"]).copy()
gdf_base = gdf_base[~gdf_base.geometry.is_empty].reset_index(drop=True)

# ---------------------------------------------------------------------------
# Median travel for transit
# ---------------------------------------------------------------------------

TRAVEL_COL = "tt_transit_nearest_top25_p8"
if TRAVEL_COL not in gdf_base.columns:
    raise ValueError(f"{TRAVEL_COL} not found in gpkg.")

# ---------------------------------------------------------------------------
# Rebuild LISA [OLIVIA'S]
# ---------------------------------------------------------------------------

P_CUTOFF = 0.05
PENALTY_MINS = 120
Y_COL = "idaci_score"

QUADRANT_LABELS = {
    1: "High-High",
    2: "Low-High",
    3: "Low-Low",
    4: "High-Low",
}

print("Building KNN-8 spatial weights ...")
w = libpysal.weights.KNN.from_dataframe(gdf_base, k=8)
w.transform = "r"

def run_lisa(gdf_in, w, x_col, p_cutoff=P_CUTOFF, penalty=PENALTY_MINS):
    gdf_out = gdf_in.copy()
    gdf_out[x_col] = gdf_out[x_col].fillna(penalty)

    x = gdf_out[x_col].values
    y = gdf_out[Y_COL].values

    # Calculate Local Moran's for the clusters
    moran_local = Moran_Local_BV(x, y, w, permutations=999, seed=42)

    
    gdf_out["lisa_cluster"] = "Not Significant"
    sig_mask = moran_local.p_sim < p_cutoff
    for idx in gdf_out.index[sig_mask]:
        gdf_out.at[idx, "lisa_cluster"] = QUADRANT_LABELS[moran_local.q[idx]]
    return gdf_out

print("Running bivariate LISA...")
gdf_lisa = run_lisa(gdf_base, w, TRAVEL_COL)

print("\nCluster counts:")
print(gdf_lisa["lisa_cluster"].value_counts(dropna=False))

# keep only significant clusters
cluster_df = gdf_lisa[gdf_lisa["lisa_cluster"].isin([
    "High-High",
    "Low-High",
    "Low-Low",
    "High-Low"
])].copy()

print(f"\nRows in significant clusters only: {len(cluster_df):,}")
print(cluster_df["lisa_cluster"].value_counts())

# ------------------------------------------------------------------
# Merge income (MSOA → LSOA clusters)
# ------------------------------------------------------------------

cluster_income_df = cluster_df.merge(
    income[["MSOA11CD", "income_ahc"]],
    on="MSOA11CD",
    how="left"
)

print("\nMissing income values:")
print(cluster_income_df["income_ahc"].isna().sum())

# ------------------------------------------------------------------
# Point 2 and Point 3 summary
# ------------------------------------------------------------------

cluster_summary = (
    cluster_income_df
    .groupby("lisa_cluster")
    .agg(
        child_population=("child_population", "sum"),
        median_travel_time=(TRAVEL_COL, "median"),
        median_income=("income_ahc", "median"),    
        lsoa_count=("LSOA11CD", "count"),
    )
    .reset_index()
)

cluster_order = ["High-High", "Low-High", "Low-Low", "High-Low"]
cluster_summary["lisa_cluster"] = pd.Categorical(
    cluster_summary["lisa_cluster"],
    categories=cluster_order,
    ordered=True
)
cluster_summary = cluster_summary.sort_values("lisa_cluster").reset_index(drop=True)

# Calculate medians for point 2
london_median_travel = gdf_base["tt_transit_nearest_top25_p8"].median()
total_children_clusters = cluster_summary["child_population"].sum()

# London median income for point 3
london_median_income = income["income_ahc"].median()

cluster_summary["income_vs_london_diff"] = (
    cluster_summary["median_income"] - london_median_income
).round(0)

cluster_summary["child_share_pct"] = (
    cluster_summary["child_population"] / total_children_clusters * 100
).round(1)

cluster_summary["travel_vs_london_diff"] = (
    cluster_summary["median_travel_time"] - london_median_travel
).round(1)

print("\nCluster summary:")
print(cluster_summary)
print(f"\nLondon median transit time: {london_median_travel:.1f} min")
print(f"London median income (AHC): £{london_median_income:,.0f}")

# ------------------------------------------------------------------
# Visual outputs
# ------------------------------------------------------------------

# Palette aligned with vulnerability section
CLUSTER_COLORS = {
    "High-High": "#D5605A",
    "Low-High": "#E3A7A4",
    "Low-Low": "#2D3D5E",
    "High-Low": "#5886C5",
}

# Short labels for charts
SHORT_LABELS = {
    "High-High": "HH",
    "Low-High": "LH",
    "Low-Low": "LL",
    "High-Low": "HL",
}

plot_df = cluster_summary.copy()
plot_df["cluster_short"] = plot_df["lisa_cluster"].map(SHORT_LABELS)
plot_df["color"] = plot_df["lisa_cluster"].map(CLUSTER_COLORS)

# ------------------------------------------------------------------
# Chart 1 — Brick composition diagram (children)
# ------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(10, 5), facecolor="white")

# 100 bricks total
n_bricks = 100
bricks_per_row = 10
plot_df["n_bricks"] = (plot_df["child_share_pct"]).round().astype(int)

# force total = 100 after rounding
diff = 100 - plot_df["n_bricks"].sum()
if diff != 0:
    max_idx = plot_df["n_bricks"].idxmax()
    plot_df.loc[max_idx, "n_bricks"] += diff

brick_colors = []
brick_labels = []

for _, row in plot_df.iterrows():
    brick_colors.extend([row["color"]] * row["n_bricks"])
    brick_labels.extend([row["cluster_short"]] * row["n_bricks"])

for i in range(n_bricks):
    col = i % bricks_per_row
    row = i // bricks_per_row
    x = col
    y = 9 - row
    ax.scatter(
        x, y,
        s=420,
        marker="s",
        color=brick_colors[i],
        edgecolor="white",
        linewidth=1
    )

ax.set_xlim(-0.8, 9.8)
ax.set_ylim(-0.8, 9.8)
ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)

ax.set_title(
    "Children living in significant LISA clusters\nBrick composition diagram (100 = all children in clustered LSOAs)",
    fontsize=13,
    fontweight="bold",
    pad=18
)

legend_handles = []
for _, row in plot_df.iterrows():
    label = f"{row['cluster_short']} — {row['child_share_pct']}% ({int(row['child_population']):,} children)"
    handle = plt.Line2D(
        [0], [0],
        marker='s',
        color='w',
        markerfacecolor=row["color"],
        markersize=12,
        label=label
    )
    legend_handles.append(handle)

ax.legend(
    handles=legend_handles,
    loc="center left",
    bbox_to_anchor=(1.02, 0.5),
    frameon=False,
    fontsize=10
)

brick_path = OUTPUT_DIR / "cluster_children_brick.png"
plt.tight_layout()
plt.savefig(brick_path, dpi=300, bbox_inches="tight")
plt.close()
print(f"Saved -> {brick_path}")

# ------------------------------------------------------------------
# Chart 2 — Median transit time by cluster vs London median
# ------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 5), facecolor="white")

bars = ax.bar(
    plot_df["cluster_short"],
    plot_df["median_travel_time"],
    color=plot_df["color"],
    width=0.65
)

ax.axhline(
    london_median_travel,
    color="black",
    linestyle="--",
    linewidth=1.2,
    label=f"London median = {london_median_travel:.1f} min"
)

for bar, value in zip(bars, plot_df["median_travel_time"]):
    ax.text(
        bar.get_x() + bar.get_width()/2,
        bar.get_height() + 0.6,
        f"{value:.1f}",
        ha="center",
        va="bottom",
        fontsize=10
    )

ax.set_title(
    "Median transit time to nearest Top 25% P8 school by cluster",
    fontsize=13,
    fontweight="bold",
    pad=12
)
ax.set_ylabel("Median transit time (minutes)")
ax.set_xlabel("Cluster")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(axis="y", linestyle="--", alpha=0.35)
ax.set_axisbelow(True)
ax.legend(frameon=False)

travel_path = OUTPUT_DIR / "cluster_travel_time_bar.png"
plt.tight_layout()
plt.savefig(travel_path, dpi=300, bbox_inches="tight")
plt.close()
print(f"Saved -> {travel_path}")

# ------------------------------------------------------------------
# Chart 3 — Median income by cluster vs London median
# ------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 5), facecolor="white")

bars = ax.bar(
    plot_df["cluster_short"],
    plot_df["median_income"],
    color=plot_df["color"],
    width=0.65
)

ax.axhline(
    london_median_income,
    color="black",
    linestyle="--",
    linewidth=1.2,
    label=f"London median = £{london_median_income:,.0f}"
)

for bar, value in zip(bars, plot_df["median_income"]):
    ax.text(
        bar.get_x() + bar.get_width()/2,
        bar.get_height() + 350,
        f"£{value:,.0f}",
        ha="center",
        va="bottom",
        fontsize=10
    )

ax.set_title(
    "Median income by cluster",
    fontsize=13,
    fontweight="bold",
    pad=12
)
ax.set_ylabel("Median income after housing costs (£)")
ax.set_xlabel("Cluster")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x:,.0f}"))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(axis="y", linestyle="--", alpha=0.35)
ax.set_axisbelow(True)
ax.legend(frameon=False)

income_path = OUTPUT_DIR / "cluster_income_bar.png"
plt.tight_layout()
plt.savefig(income_path, dpi=300, bbox_inches="tight")
plt.close()
print(f"Saved -> {income_path}")

