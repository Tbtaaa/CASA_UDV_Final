"""
r5py isochrones — Clapham North vs Harold Hill
================================================
Generates 10, 20, 30-minute transit+walk isochrones from two contrasting
LSOA origins for the Motivation section map (S2).

Departure: Tuesday 17 March 2026, 08:30 
Output:    data/isochrones.geojson  (one feature per origin × time band)
"""

import r5py
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
from datetime import datetime
from alphashape import alphashape
import os

os.makedirs("data", exist_ok=True)

# ── Config ────────────────────────────────────────────────────────────────────

OSM_PATH = "large/greater-london-latest.osm.pbf"
GTFS_PATHS = [
    "large/itm_london_gtfs.zip",
    "large/national_rail_fixed_gtfs.zip",
]
DEPARTURE = datetime(2026, 3, 17, 8, 30)
PERCENTILE = 50

ORIGINS = [
    {
        "id":        "clapham",
        "label":     "Clapham North (Lambeth)",
        "geometry":  Point(-0.1323, 51.4627),
        "radius_km": 14,    # Zone 2 — transit fans out far
        "spacing_m": 100,
    },
    {
        "id":        "harold_hill",
        "label":     "Harold Hill (Havering)",
        "geometry":  Point(0.220865, 51.600122),
        "radius_km": 10,    # Bus-only — much tighter reach
        "spacing_m": 100,
    },
]

# ── Grid helper ───────────────────────────────────────────────────────────────


def make_local_grid(origin_point, radius_km, spacing_m):
    origin_gdf = gpd.GeoDataFrame(
        geometry=[origin_point], crs=4326).to_crs(27700)
    cx, cy = origin_gdf.geometry.x[0], origin_gdf.geometry.y[0]
    r = radius_km * 1000
    xs = np.arange(cx - r, cx + r, spacing_m)
    ys = np.arange(cy - r, cy + r, spacing_m)
    gx, gy = np.meshgrid(xs, ys)
    return gpd.GeoDataFrame(
        {"id": [f"g{i}" for i in range(gx.size)]},
        geometry=gpd.points_from_xy(gx.flatten(), gy.flatten()),
        crs=27700
    ).to_crs(4326)

# ── Build network ─────────────────────────────────────────────────────────────


print("Building transport network...")
network = r5py.TransportNetwork(OSM_PATH, GTFS_PATHS)
print("✓ Network built")

# ── Compute per origin ────────────────────────────────────────────────────────

for cfg in ORIGINS:

    origin_id = cfg["id"]
    print(f"\n── {cfg['label']} ──────────────────────────────────────")

    grid = make_local_grid(cfg["geometry"], cfg["radius_km"], cfg["spacing_m"])
    print(f"  Grid: {len(grid):,} points "
          f"({cfg['radius_km']}km radius, {cfg['spacing_m']}m spacing)")

    origin_gdf = gpd.GeoDataFrame(
        [{"id": origin_id, "geometry": cfg["geometry"]}], crs=4326
    )

    tt = r5py.TravelTimeMatrix(
        network,
        origins=origin_gdf,
        destinations=grid,
        departure=DEPARTURE,
        departure_time_window=pd.Timedelta(hours=1),
        max_time=pd.Timedelta(minutes=65),   # capture out to 60 min
        transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
        percentiles=[PERCENTILE],
    )

    # Merge back onto grid geometry
    merged = grid.merge(
        tt[["to_id", "travel_time"]],
        left_on="id", right_on="to_id", how="left"
    )

    # Keep only reachable points
    reachable = merged.dropna(subset=["travel_time"]).copy()
    reachable["travel_time"] = reachable["travel_time"].astype(int)
    reachable["origin_id"] = origin_id
    reachable["label"] = cfg["label"]

    total = len(merged)
    reach = len(reachable)
    print(f"  Reachable: {reach:,} / {total:,} ({reach/total*100:.1f}%)")
    print(reachable["travel_time"].describe().round(1))

    # Export — drop unnecessary columns to keep file size small
    out = reachable[["origin_id", "label", "travel_time", "geometry"]].copy()
    path = f"data/tt_grid_{origin_id}.geojson"
    out.to_file(path, driver="GeoJSON")
    print(f"  ✓ Saved → {path}  ({os.path.getsize(path)/1e6:.1f} MB)")
