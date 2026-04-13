"""
lsoa_travel_times.py
====================
1. Load LSOA boundaries and clip to GLA boundary
2. Join with lsoa_travel_times.parquet on LSOA21CD / lsoa_id
3. Clip to dlua_region.shp polygons (Inner / Outer London regions)
4. Export to lsoa_travel_times.geojson for Mapbox upload

Run from the project root where your data files live.
"""

import geopandas as gpd
import pandas as pd
import os
import sys

# ── 0. Paths ──────────────────────────────────────────────────────────────────

LSOA_PATH = "large/Lower_layer_Super_Output_Areas_December_2021_BGC.gpkg"
GLA_PATH = "data/London_GLA_Boundary.shp"
PARQUET_PATH = "data/lsoa_travel_times.parquet"
DLUA_PATH = "large/dlua_region.shp"
OUTPUT_PATH = "data/lsoa_travel_times.geojson"

# Check all inputs exist before doing any work
for path in [LSOA_PATH, GLA_PATH, PARQUET_PATH, DLUA_PATH]:
    if not os.path.exists(path):
        print(f"✗ File not found: {path}")
        sys.exit(1)

print("All input files found.")

# ── 1. Load and clip LSOAs to GLA boundary ───────────────────────────────────

print("\nLoading GLA boundary...")
gla = gpd.read_file(GLA_PATH)
print(f"  CRS: {gla.crs}  |  Features: {len(gla)}")

print("Loading LSOA boundaries...")
lsoa = gpd.read_file(LSOA_PATH)
print(f"  CRS: {lsoa.crs}  |  Features: {len(lsoa)}")
print(f"  Columns: {lsoa.columns.tolist()}")

# Reproject to match if CRS differs
if lsoa.crs != gla.crs:
    print(f"  Reprojecting LSOAs from {lsoa.crs} to {gla.crs}...")
    lsoa = lsoa.to_crs(gla.crs)

print("Clipping LSOAs to GLA boundary...")
gla_union = gla.union_all() if hasattr(gla, 'union_all') else gla.unary_union
lsoa_clipped = lsoa.clip(gla_union)
print(f"  LSOAs after GLA clip: {len(lsoa_clipped)}")

# ── 2. Join with travel times parquet ────────────────────────────────────────

print("\nLoading travel times parquet...")
tt = pd.read_parquet(PARQUET_PATH)
print(f"  Shape: {tt.shape}")
print(f"  Columns: {tt.columns.tolist()}")

# Confirm join columns exist
if "LSOA21CD" not in lsoa_clipped.columns:
    print(
        f"✗ 'LSOA21CD' not found in LSOA layer. Available: {lsoa_clipped.columns.tolist()}")
    sys.exit(1)
if "lsoa_id" not in tt.columns:
    print(
        f"✗ 'lsoa_id' not found in parquet. Available: {tt.columns.tolist()}")
    sys.exit(1)

print("Joining travel times to LSOA boundaries...")
joined = lsoa_clipped.merge(
    tt,
    left_on="LSOA21CD",
    right_on="lsoa_id",
    how="left"
)
print(f"  Joined features: {len(joined)}")

# Report on unmatched LSOAs
unmatched = joined["lsoa_id"].isna().sum()
if unmatched > 0:
    print(
        f"  ⚠ {unmatched} LSOAs had no matching travel time record (left join — kept as NaN)")
else:
    print("  ✓ All LSOAs matched")

# ── 3. Clip to dlua_region polygons ──────────────────────────────────────────

print("Loading dlua_region boundaries...")
dlua = gpd.read_file(DLUA_PATH)

if joined.crs != dlua.crs:
    dlua = dlua.to_crs(joined.crs)

# Simplify dlua before clipping — much faster, minimal accuracy loss
# tolerance in CRS units (metres if EPSG:27700, degrees if EPSG:4326)
dlua_simplified = dlua.copy()
dlua_simplified['geometry'] = dlua.geometry.simplify(
    tolerance=50,              # 50 metres — adjust if needed
    preserve_topology=True
)

dlua_simplified = dlua_simplified.clip(gla_union)

dlua_union = dlua_simplified.union_all() \
    if hasattr(dlua_simplified, 'union_all') \
    else dlua_simplified.unary_union

print("Clipping to dlua_region...")
final = joined.clip(dlua_union)
print(f"  Features after dlua clip: {len(final)}")

# ── 4. Prepare for Mapbox export ──────────────────────────────────────────────

print("\nPreparing for export...")

# Reproject to WGS84 (required for GeoJSON / Mapbox)
if final.crs.to_epsg() != 4326:
    print(f"  Reprojecting from {final.crs} to EPSG:4326...")
    final = final.to_crs(4326)

# Drop duplicate join column to keep GeoJSON clean
if "lsoa_id" in final.columns:
    final = final.drop(columns=["lsoa_id"])

# Round float columns to 2dp to reduce file size
float_cols = final.select_dtypes(include="float").columns
final[float_cols] = final[float_cols].round(2)

# Report column summary
print(f"\nFinal GeoDataFrame:")
print(f"  Features : {len(final)}")
print(f"  Columns  : {final.columns.tolist()}")
print(f"\nTravel time column summary:")
tt_cols = [c for c in final.columns if "tt_" in c]
if tt_cols:
    print(final[tt_cols].describe().round(1).to_string())
else:
    print("  (no tt_ columns found — check parquet column names)")

# ── 5. Export ─────────────────────────────────────────────────────────────────

os.makedirs(os.path.dirname(OUTPUT_PATH) if os.path.dirname(
    OUTPUT_PATH) else ".", exist_ok=True)

print(f"\nWriting to {OUTPUT_PATH}...")
final.to_file(OUTPUT_PATH, driver="GeoJSON")

size_mb = os.path.getsize(OUTPUT_PATH) / 1e6
print(f"✓ Saved — {size_mb:.1f} MB")

if size_mb > 50:
    print(
        f"\n⚠ File is {size_mb:.0f} MB — Mapbox free tier limit is 50 MB per tileset.")
    print("  Consider simplifying geometries:")
    print(
        "    final['geometry'] = final.geometry.simplify(tolerance=0.0001, preserve_topology=True)")
    print("  Then re-run the export block.")
else:
    print("  File size is within Mapbox free tier limits (< 50 MB).")
