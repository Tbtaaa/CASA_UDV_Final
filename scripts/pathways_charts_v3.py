"""
Pathways to Progress — Chart Generation  v2
=============================================
Merged with GLA boundary clipping and selective-school exclusion,
matching exactly the filtering logic in review-traveltimematrix-code-2.py.

Requirements:
    pip install pyarrow pandas geopandas matplotlib numpy shapely

File layout expected (edit PATHS block below if yours differ):
    data/
        england_secondary_schools.parquet
        lsoa_travel_times.parquet
        gla_boundary.geojson          ← or .gpkg / .shp

Outputs → paths['outputs']  (set in PATHS block above)
    chart2_schools_per_borough.png   Section 3 — schools per borough + Ofsted overlay
    chart2b_utilisation.png          Section 3 — pupil-place utilisation by borough
    chart3_mode_times_borough.png    Section 3 — borough median travel times by mode
    chart4_borough_p8_table.png      Section 4 — borough P8 access table (fills empty table)
    chart5_quality_penalty.png       Section 4 — extra minutes to reach a P8 school
    chart6_mode_gap_matrix.png       Section 4 — walk vs transit gap by borough
    chart10_imd_vs_p8_transit.png    Section 5 — IMD vs P8 transit scatter (fills placeholder)
    chart11_ofsted_by_imd.png        Section 5 — Ofsted grade by IMD quintile
    borough_ranking.csv              Ready to pipe into the page's interactive borough table
"""

import os
import warnings
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from shapely.geometry import Point

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════════════
# PATHS — single source of truth for all input/output locations
# ══════════════════════════════════════════════════════════════════════════════
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

paths = {
    "schools":    os.path.join(root, "england_secondary_schools.parquet"),
    "travel_time":os.path.join(root, "data", "lsoa_travel_times.parquet"),
    "nts_9908":   os.path.join(root, "data", "nts9908.ods"),
    "nts_0613":   os.path.join(root, "data", "nts0613.ods"),
    "output":     os.path.join(root, "outputs", "commuter_behavior_report.csv"),
    "gla":        os.path.join(root, "data", "London_GLA_Boundary.shp"),
    "outputs":    os.path.join(root, "outputs"),
}

os.makedirs(paths["outputs"], exist_ok=True)

# Admissions policies to exclude (mirrors review-traveltimematrix-code-2.py)
EXCLUDE_ADMISSIONS = {"Selective", "selective"}

SCHOOLS_CRS = "EPSG:27700"  # British National Grid


# ══════════════════════════════════════════════════════════════════════════════
# COLOUR PALETTE  (matches page aesthetic)
# ══════════════════════════════════════════════════════════════════════════════
BLUE   = "#378ADD"
TEAL   = "#1D9E75"
AMBER  = "#BA7517"
CORAL  = "#D85A30"
RED    = "#E24B4A"
PURPLE = "#7F77DD"
GRAY   = "#888780"
LGRAY  = "#D3D1C7"

OFSTED_COLORS = {
    "Outstanding":          "#1D9E75",
    "Good":                 "#378ADD",
    "Requires improvement": "#BA7517",
    "Inadequate":           "#E24B4A",
    "Not yet inspected":    "#D3D1C7",
}

plt.rcParams.update({
    "font.family":        "sans-serif",
    "font.size":          11,
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.spines.left":   False,
    "axes.grid":          True,
    "axes.grid.axis":     "x",
    "grid.color":         "#E8E6DF",
    "grid.linewidth":     0.5,
    "figure.dpi":         150,
    "savefig.dpi":        150,
    "savefig.bbox":       "tight",
    "savefig.facecolor":  "white",
})


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — Load raw data
# ══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("Loading data...")

schools_raw = pd.read_parquet(paths["schools"])
travel      = pd.read_parquet(paths["travel_time"])

print(f"  {len(schools_raw):,} schools in England (all statuses)")
print(f"  {len(travel):,} LSOA rows in travel times file")


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Load GLA boundary
# ══════════════════════════════════════════════════════════════════════════════
print("\nLoading GLA boundary...")

gla = gpd.read_file(paths["gla"]).to_crs(SCHOOLS_CRS)
gla_union = gla.union_all() if hasattr(gla, "union_all") else gla.unary_union
print(f"  GLA boundary loaded from: {paths['gla']}")


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — Spatial clip: keep only schools inside GLA boundary
#           Mirrors: "500 schools within GLA boundary" from the matrix script
# ══════════════════════════════════════════════════════════════════════════════
print("\nClipping schools to GLA boundary...")

schools_gdf_all = gpd.GeoDataFrame(
    schools_raw,
    geometry=gpd.points_from_xy(schools_raw["easting"], schools_raw["northing"]),
    crs=SCHOOLS_CRS,
)

open_in_gla = gpd.clip(schools_gdf_all, gla_union)
open_in_gla = open_in_gla[open_in_gla["establishment_status"] == "Open"].copy()

print(f"  {len(open_in_gla):,} open schools within GLA boundary")


# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Exclude selective schools and those with unknown admissions policy
#           Mirrors: "475 schools remaining after excluding Selective/NA policies"
# ══════════════════════════════════════════════════════════════════════════════
print("\nExcluding selective and unknown-admissions schools...")

open_schools = open_in_gla[
    open_in_gla["admissions_policy"].notna() &
    ~open_in_gla["admissions_policy"].isin(EXCLUDE_ADMISSIONS)
].copy()

print(f"  {len(open_schools):,} schools remaining after excluding Selective/NA")

# ── P8 / Att8 thresholds (London schools only, non-selective)
p8_threshold   = open_schools["ks4_progress8"].quantile(0.75)
att8_threshold = open_schools["ks4_attainment8"].quantile(0.75)
n_outstanding  = (open_schools["ofsted_overall_label"] == "Outstanding").sum()
n_top25_att8   = (open_schools["ks4_attainment8"] >= att8_threshold).sum()
n_top25_p8     = (open_schools["ks4_progress8"]   >= p8_threshold).sum()

print(f"\n  Destination thresholds (London non-selective schools only):")
print(f"    Top 25% Attainment 8 cutoff : {att8_threshold:.1f}")
print(f"    Top 25% Progress 8 cutoff   : {p8_threshold:.2f}")
print(f"    Outstanding schools         : {n_outstanding}")
print(f"    Top 25% Att8                : {n_top25_att8}")
print(f"    Top 25% P8                  : {n_top25_p8}")


# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — Shared aggregations
# ══════════════════════════════════════════════════════════════════════════════
print("\nBuilding borough-level aggregations...")

# LA-level school stats
la_schools = (
    open_schools
    .groupby("la_name")
    .agg(
        school_count = ("URN",              "count"),
        total_places = ("school_capacity",  "sum"),
        total_pupils = ("number_of_pupils", "sum"),
        median_imd   = ("imd_score",        "median"),
    )
    .reset_index()
)
la_schools["utilisation_pct"] = (
    la_schools["total_pupils"] / la_schools["total_places"] * 100
).round(1)

# Ofsted counts per LA
ofsted_order = ["Outstanding", "Good", "Requires improvement", "Inadequate"]
ofsted_la = (
    open_schools
    .assign(ofsted=lambda d: d["ofsted_overall_label"].fillna("Not yet inspected"))
    .groupby(["la_name", "ofsted"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)
for col in ofsted_order:
    if col not in ofsted_la.columns:
        ofsted_la[col] = 0

# Top-25% P8 schools per LA  (thresholds already computed above)
p8_schools_la = (
    open_schools[open_schools["ks4_progress8"] >= p8_threshold]
    .groupby("la_name")
    .size()
    .reset_index(name="p8_school_count")
)

# LSOA → LA lookup
lsoa_la = (
    open_schools[["lsoa_code", "la_name"]]
    .dropna(subset=["lsoa_code"])
    .drop_duplicates("lsoa_code")
)

# Travel times → LA medians
TRAVEL_COLS = {
    "Transit any":  "tt_transit_nearest_any",
    "Walk any":     "tt_walk_nearest_any",
    "Cycle any":    "tt_cycle_nearest_any",
    "Car any":      "tt_car_nearest_any",
    "Transit P8":   "tt_transit_nearest_top25_p8",
    "Walk P8":      "tt_walk_nearest_top25_p8",
    "Cycle P8":     "tt_cycle_nearest_top25_p8",
    "Car P8":       "tt_car_nearest_top25_p8",
}

travel_la_base = travel.merge(lsoa_la, left_on="lsoa_id", right_on="lsoa_code", how="inner")

travel_la = (
    travel_la_base
    .groupby("la_name")[list(TRAVEL_COLS.values())]
    .median()
    .reset_index()
)
travel_la.columns = ["la_name"] + list(TRAVEL_COLS.keys())

# Master LA table
la = (
    la_schools
    .merge(ofsted_la,     on="la_name", how="left")
    .merge(p8_schools_la, on="la_name", how="left")
    .merge(travel_la,     on="la_name", how="left")
)
la["p8_school_count"] = la["p8_school_count"].fillna(0).astype(int)
la["penalty_transit"] = la["Transit P8"] - la["Transit any"]
la["penalty_walk"]    = la["Walk P8"]    - la["Walk any"]
la["borough_short"]   = la["la_name"].str.replace(
    r"London Borough of |Royal Borough of |City of ", "", regex=True
)

print(f"  {len(la)} London boroughs")
print(f"  {len(travel_la_base):,} LSOAs matched to London LAs")
print("=" * 60)


# ══════════════════════════════════════════════════════════════════════════════
# CHART 1 — Schools per borough + Ofsted overlay
# ══════════════════════════════════════════════════════════════════════════════
print("\nChart 1 — Schools per borough + Ofsted overlay...")

df  = la.sort_values("school_count", ascending=True)
fig, ax = plt.subplots(figsize=(9, 10))
left = np.zeros(len(df))

for grade in ["Outstanding", "Good", "Requires improvement", "Inadequate", "Not yet inspected"]:
    if grade in df.columns:
        vals = df[grade].fillna(0).values
        ax.barh(df["borough_short"], vals, left=left,
                color=OFSTED_COLORS.get(grade, GRAY), label=grade, height=0.65)
        left += vals

ax.set_xlabel("Number of open, non-selective schools")
ax.set_title("Secondary schools per London borough\n(open, non-selective only — coloured by Ofsted rating)",
             fontsize=13, fontweight="bold", pad=12)
handles = [mpatches.Patch(color=OFSTED_COLORS[g], label=g) for g in ofsted_order]
ax.legend(handles=handles, fontsize=9, loc="lower right", frameon=False)
ax.tick_params(axis="y", labelsize=9)
plt.tight_layout()
plt.savefig(os.path.join(paths["outputs"], "chart2_schools_per_borough.png"))
plt.close()
print(f"    → {os.path.join(paths['outputs'], 'chart2_schools_per_borough.png')}")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 2 — Pupil-place utilisation by borough
# ══════════════════════════════════════════════════════════════════════════════
print("Chart 2 — Pupil-place utilisation by borough...")

df     = la.sort_values("utilisation_pct", ascending=True).dropna(subset=["utilisation_pct"])
colors = [RED if v > 100 else AMBER if v > 95 else BLUE for v in df["utilisation_pct"]]

fig, ax = plt.subplots(figsize=(9, 10))
ax.barh(df["borough_short"], df["utilisation_pct"], color=colors, height=0.65)
ax.axvline(100, color=RED,  linewidth=1.2, linestyle="--", alpha=0.7, label="100% — at capacity")
ax.axvline(90,  color=AMBER, linewidth=1,  linestyle=":",  alpha=0.6, label="90% — near capacity")
ax.set_xlabel("Utilisation (%)")
ax.set_title("School place utilisation by London borough\n(pupils on roll ÷ capacity, non-selective schools)",
             fontsize=13, fontweight="bold", pad=12)
ax.legend(fontsize=9, loc="lower right", frameon=False)
ax.tick_params(axis="y", labelsize=9)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x)}%"))
plt.tight_layout()
plt.savefig(os.path.join(paths["outputs"], "chart2b_utilisation.png"))
plt.close()
print(f"    → {os.path.join(paths['outputs'], 'chart2b_utilisation.png')}")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 3 — Median travel times by mode per borough (to nearest any school)
# ══════════════════════════════════════════════════════════════════════════════
print("Chart 3 — Travel times by mode per borough...")

modes        = ["Transit any", "Walk any", "Cycle any", "Car any"]
mode_colors  = [BLUE, TEAL, PURPLE, AMBER]
mode_labels  = ["Transit", "Walk", "Cycle", "Car"]

df = la.dropna(subset=["Transit any"]).sort_values("Transit any", ascending=True)
fig, ax = plt.subplots(figsize=(9, 10))
y       = np.arange(len(df))
offsets = np.linspace(-0.28, 0.28, len(modes))

for i, (mode, color, label) in enumerate(zip(modes, mode_colors, mode_labels)):
    ax.barh(y + offsets[i], df[mode].fillna(0),
            height=0.16, color=color, label=label)

ax.set_yticks(y)
ax.set_yticklabels(df["borough_short"], fontsize=9)
ax.set_xlabel("Median travel time (minutes)")
ax.set_title("Median travel time to nearest secondary school\nby mode and borough (non-selective schools only)",
             fontsize=13, fontweight="bold", pad=12)
ax.legend(fontsize=9, loc="lower right", frameon=False)
plt.tight_layout()
plt.savefig(os.path.join(paths["outputs"], "chart3_mode_times_borough.png"))
plt.close()
print(f"    → {os.path.join(paths['outputs'], 'chart3_mode_times_borough.png')}")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 4 — Borough P8 access table (fills the empty table in Section 4)
# ══════════════════════════════════════════════════════════════════════════════
print("Chart 4 — Borough P8 access table...")

cols = ["borough_short", "p8_school_count", "Transit P8", "Walk P8", "Car P8"]
df   = (
    la[cols]
    .dropna(subset=["Transit P8"])
    .sort_values("Transit P8")
    .rename(columns={
        "borough_short":  "Borough",
        "p8_school_count":"Top-25% P8 schools",
        "Transit P8":     "Transit (min)",
        "Walk P8":        "Walk (min)",
        "Car P8":         "Car (min)",
    })
    .reset_index(drop=True)
)
df.index += 1
for col in ["Transit (min)", "Walk (min)", "Car (min)"]:
    df[col] = df[col].round(1)

fig, ax = plt.subplots(figsize=(10, len(df) * 0.32 + 1.2))
ax.axis("off")
tbl = ax.table(cellText=df.values, colLabels=df.columns,
               rowLabels=df.index, cellLoc="center", loc="center")
tbl.auto_set_font_size(False)
tbl.set_fontsize(9)
tbl.scale(1, 1.35)

for j in range(len(df.columns)):
    tbl[0, j].set_facecolor("#1A1A2E")
    tbl[0, j].set_text_props(color="white", fontweight="bold")

for i in range(1, len(df) + 1):
    if i % 2 == 0:
        for j in range(len(df.columns)):
            tbl[i, j].set_facecolor("#F5F4F0")
    transit_val = df.iloc[i - 1]["Transit (min)"]
    if transit_val > 30:
        tbl[i, 2].set_facecolor("#FCEBEB")
        tbl[i, 2].set_text_props(color=RED)
    elif transit_val > 22:
        tbl[i, 2].set_facecolor("#FAEEDA")
        tbl[i, 2].set_text_props(color=AMBER)

ax.set_title("Borough-level access to Top 25% P8 schools — ranked by transit time\n"
             f"(P8 cutoff: {p8_threshold:.2f}, non-selective schools only)",
             fontsize=12, fontweight="bold", pad=10, loc="left")
plt.tight_layout()
plt.savefig(os.path.join(paths["outputs"], "chart4_borough_p8_table.png"))
plt.close()
print(f"    → {os.path.join(paths['outputs'], 'chart4_borough_p8_table.png')}")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 5 — Quality penalty: extra minutes to reach a P8 school
# ══════════════════════════════════════════════════════════════════════════════
print("Chart 5 — Quality penalty chart...")

df         = la.dropna(subset=["penalty_transit"]).sort_values("penalty_transit", ascending=True)
bar_colors = [CORAL if v >= 10 else AMBER if v >= 6 else TEAL for v in df["penalty_transit"]]

fig, ax = plt.subplots(figsize=(9, 10))
ax.barh(df["borough_short"], df["penalty_transit"],
        color=bar_colors, height=0.65, label="Transit penalty")
ax.scatter(df["penalty_walk"], range(len(df)),
           color=PURPLE, s=25, zorder=5, marker="D", label="Walk penalty")
ax.axvline(0, color=GRAY, linewidth=0.8)
ax.set_xlabel("Additional minutes vs nearest any non-selective school")
ax.set_title("The quality penalty — extra travel time to reach\na Top 25% P8 school, by borough",
             fontsize=13, fontweight="bold", pad=12)
ax.legend(fontsize=9, loc="lower right", frameon=False)
ax.tick_params(axis="y", labelsize=9)
plt.tight_layout()
plt.savefig(os.path.join(paths["outputs"], "chart5_quality_penalty.png"))
plt.close()
print(f"    → {os.path.join(paths['outputs'], 'chart5_quality_penalty.png')}")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 6 — Mode gap matrix: transit vs walk time per borough
# ══════════════════════════════════════════════════════════════════════════════
print("Chart 6 — Mode gap (transit − walk) by borough...")

df          = la.dropna(subset=["Transit any", "Walk any"]).copy()
# compares to nearest P8 school
df["mode_gap"] = df["Transit P8"] - df["Walk P8"]
df          = df.sort_values("mode_gap", ascending=False)
y           = np.arange(len(df))
gap_colors  = [RED if v > 12 else AMBER if v > 7 else LGRAY for v in df["mode_gap"]]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 10), sharey=True)
ax1.barh(y - 0.18, df["Transit P8"], height=0.35, color=BLUE, label="Transit to P8 school")
ax1.barh(y + 0.18, df["Walk P8"],    height=0.35, color=TEAL, label="Walk to P8 school")
ax1.set_yticks(y)
ax1.set_yticklabels(df["borough_short"], fontsize=9)
ax1.set_xlabel("Median minutes to nearest school")
ax1.legend(fontsize=9, frameon=False)
ax1.set_title("Absolute travel times", fontsize=11)

ax2.barh(y, df["mode_gap"], color=gap_colors, height=0.65)
ax2.set_xlabel("Gap: transit − walk (minutes)")
ax2.set_title("Transit − walk gap\n(higher = worse transit coverage)", fontsize=11)
ax2.axvline(0, color=GRAY, linewidth=0.7)
fig.suptitle("Walk vs transit access to nearest school by London borough\n"
             "(sorted by transit − walk gap, largest first)",
             fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig(os.path.join(paths["outputs"], "chart6_mode_gap_matrix.png"))
plt.close()
print(f"    → {os.path.join(paths['outputs'], 'chart6_mode_gap_matrix.png')}")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 7 — IMD score vs P8 transit time scatter  (fills Chart 10 placeholder)
# ══════════════════════════════════════════════════════════════════════════════
print("Chart 7 — IMD vs P8 transit time scatter...")

lsoa_imd = (
    open_schools
    .groupby("lsoa_code")["imd_score"]
    .median()
    .reset_index(name="imd_score")
)
scatter_df = (
    travel
    .merge(lsoa_imd, left_on="lsoa_id", right_on="lsoa_code", how="inner")
    .merge(lsoa_la,  left_on="lsoa_id", right_on="lsoa_code", how="left")
    .dropna(subset=["imd_score", "tt_transit_nearest_top25_p8"])
)

# Use all London LSOAs (no sampling needed — usually ~4,994 rows)
print(f"    {len(scatter_df):,} LSOAs in scatter plot")

fig, ax = plt.subplots(figsize=(10, 7))
sc = ax.scatter(
    scatter_df["imd_score"],
    scatter_df["tt_transit_nearest_top25_p8"],
    alpha=0.25, s=8,
    c=scatter_df["imd_score"], cmap="RdYlGn_r", vmin=0, vmax=50,
)

# Trend line
mask = scatter_df[["imd_score", "tt_transit_nearest_top25_p8"]].notna().all(axis=1)
z    = np.polyfit(scatter_df.loc[mask, "imd_score"],
                  scatter_df.loc[mask, "tt_transit_nearest_top25_p8"], 1)
xln  = np.linspace(scatter_df["imd_score"].min(), scatter_df["imd_score"].max(), 200)
ax.plot(xln, np.poly1d(z)(xln), color=CORAL, linewidth=2, label="Trend")

# Quadrant reference lines + annotations
imd_med = scatter_df["imd_score"].median()
tt_med  = scatter_df["tt_transit_nearest_top25_p8"].median()
ax.axvline(imd_med, color=GRAY, linewidth=0.8, linestyle="--", alpha=0.5)
ax.axhline(tt_med,  color=GRAY, linewidth=0.8, linestyle="--", alpha=0.5)
ax.text(scatter_df["imd_score"].max() * 0.82, tt_med * 0.28,
        "More deprived\nBetter access", fontsize=8.5, color=TEAL,
        ha="center", style="italic")
ax.text(scatter_df["imd_score"].max() * 0.82, tt_med * 1.75,
        "More deprived\nWorse access\n(vulnerable)", fontsize=8.5, color=RED,
        ha="center", style="italic", fontweight="bold")

cbar = plt.colorbar(sc, ax=ax, shrink=0.6)
cbar.set_label("IMD score (higher = more deprived)", fontsize=9)
ax.set_xlabel("IMD score (LSOA level)")
ax.set_ylabel("Median transit time to nearest Top 25% P8 school (min)")
ax.set_title(f"Deprivation vs transit time to quality schools — each dot = one London LSOA\n"
             f"(P8 cutoff: {p8_threshold:.2f}, non-selective only)",
             fontsize=13, fontweight="bold", pad=12)
ax.legend(fontsize=9, frameon=False)
plt.tight_layout()
plt.savefig(os.path.join(paths["outputs"], "chart10_imd_vs_p8_transit.png"))
plt.close()
print(f"    → {os.path.join(paths['outputs'], 'chart10_imd_vs_p8_transit.png')}")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 8 — Ofsted grade distribution by IMD quintile
# ══════════════════════════════════════════════════════════════════════════════
print("Chart 8 — Ofsted grade by IMD quintile...")

df = open_schools.dropna(subset=["ofsted_overall_label", "imd_decile"]).copy()
df["ofsted"] = df["ofsted_overall_label"].where(
    df["ofsted_overall_label"].isin(ofsted_order), "Not yet inspected"
)
df["imd_quintile"] = pd.cut(
    df["imd_decile"], bins=[0, 2, 4, 6, 8, 10],
    labels=["Q1\n(most deprived)", "Q2", "Q3", "Q4", "Q5\n(least deprived)"]
)

pct = (
    df.groupby(["imd_quintile", "ofsted"], observed=True)
    .size()
    .unstack(fill_value=0)
    .apply(lambda r: r / r.sum() * 100, axis=1)
)
for col in ofsted_order:
    if col not in pct.columns:
        pct[col] = 0

fig, ax = plt.subplots(figsize=(10, 5))
bottom = np.zeros(len(pct))
for grade in ofsted_order:
    vals = pct[grade].values
    ax.bar(pct.index, vals, bottom=bottom,
           color=OFSTED_COLORS[grade], label=grade, width=0.6)
    for i, (v, b) in enumerate(zip(vals, bottom)):
        if v > 5:
            ax.text(i, b + v / 2, f"{v:.0f}%",
                    ha="center", va="center", fontsize=8,
                    color="white", fontweight="bold")
    bottom += vals

ax.set_ylim(0, 100)
ax.set_ylabel("% of schools")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x)}%"))
ax.set_title("Ofsted rating distribution by deprivation quintile\n"
             "Are outstanding schools concentrated in less-deprived areas? (non-selective only)",
             fontsize=13, fontweight="bold", pad=12)
handles = [mpatches.Patch(color=OFSTED_COLORS[g], label=g) for g in ofsted_order]
ax.legend(handles=handles, fontsize=9, loc="upper left",
          bbox_to_anchor=(1, 1), frameon=False)
ax.set_xlabel("IMD quintile (school's LSOA)")
ax.grid(axis="y", linewidth=0.4)
plt.tight_layout()
plt.savefig(os.path.join(paths["outputs"], "chart11_ofsted_by_imd.png"))
plt.close()
print(f"    → {os.path.join(paths['outputs'], 'chart11_ofsted_by_imd.png')}")


# ══════════════════════════════════════════════════════════════════════════════
# EXPORT — borough ranking CSV (for the page's interactive table)
# ══════════════════════════════════════════════════════════════════════════════
print("\nWriting borough_ranking.csv...")

export = (
    la.rename(columns={
        "la_name":         "Borough",
        "school_count":    "Schools",
        "p8_school_count": "Top-25% P8 schools",
        "total_pupils":    "Pupils",
        "utilisation_pct": "Utilisation (%)",
        "Transit any":     "Transit to any school (min)",
        "Transit P8":      "Transit to P8 school (min)",
        "penalty_transit": "Quality penalty — transit (min)",
        "Walk any":        "Walk to any school (min)",
        "Walk P8":         "Walk to P8 school (min)",
        "Car any":         "Car to any school (min)",
        "Car P8":          "Car to P8 school (min)",
    })
    .sort_values("Transit to P8 school (min)")
    .round(1)
)
export.to_csv(os.path.join(paths["outputs"], "borough_ranking.csv"), index=False)
print(f"    → {os.path.join(paths['outputs'], 'borough_ranking.csv')}")

print("\n" + "=" * 60)
print(f"All done. Charts saved to {paths['outputs']}")
print("=" * 60)
