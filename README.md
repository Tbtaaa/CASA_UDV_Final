# Pathways to Progress
Benjamin Tee, Tabata Paredes, Yujing (Olivia) Xing
22 April 2026

- [Overview](#overview)
- [Research Questions](#research-questions)
- [Datasets](#datasets)
- [Methodology](#methodology)
  - [1. School Database](#1-school-database)
  - [2. Travel Context](#2-travel-context)
  - [3. Travel Time Matrix](#3-travel-time-matrix)
  - [4. Isochrones](#4-isochrones)
  - [5. Spatial Layers and Processing](#5-spatial-layers-and-processing)
  - [6. Visualisation Stack](#6-visualisation-stack)
  - [7. Deprivation Data](#7-deprivation-data)
  - [8. Bivariate LISA Clustering](#8-bivariate-lisa-clustering)
  - [9. Income by Cluster](#9-income-by-cluster)
  - [10. Narrative and Interactivity](#10-narrative-and-interactivity)
- [Cartographic Design](#cartographic-design)
- [Webpage Architecture](#webpage-architecture)
- [References](#references)

------------------------------------------------------------------------

|                  |                                                    |
|------------------|----------------------------------------------------|
| **Contributors** | Benjamin Tee, Tabata Paredes, Yujing (Olivia) Xing |
| **Last Updated** | April 2026                                         |

------------------------------------------------------------------------

## Overview

This project examines how transport accessibility shapes access to
high-performing secondary schools across London, and whether spatial
disadvantage in school access reinforces broader patterns of
socio-economic inequality. The analysis is presented as an interactive
scrollytelling webpage — *Pathways to Progress* — combining travel time
modelling, deprivation analysis and spatial clustering, visualised
through Mapbox GL JS and Chart.js.

**Live site can be found
[here](https://benjamintee.github.io/CASA_UDV_Final/pathways_to_progress.html)**

------------------------------------------------------------------------

## Research Questions

**Main RQ:** How does accessibility to high-performing secondary schools
vary across London’s neighbourhoods, and to what extent does this
reflect patterns of socio-economic disadvantage?

**Sub-RQ 1 — Spatial Variation in Access:** How does travel time to
high-performing secondary schools vary across London by public transit,
walking, and cycling — and where are the greatest disparities
concentrated?

**Sub-RQ 2 — Deprivation and Vulnerability:** Is poor accessibility to
high-performing schools systematically associated with neighbourhood
deprivation, and where do pockets of compounded geographic and
socio-economic disadvantage exist?

------------------------------------------------------------------------

## Datasets

| Dataset | Source | Resolution | Use |
|----|----|----|----|
| Secondary school register | DfE Get Information About Schools | School | School locations, admissions policy, capacity |
| Ofsted inspection ratings | Ofsted | School | School quality classification |
| Key Stage 4 results | DfE National Statistics | School | Progress 8 and Attainment 8 scores |
| LSOA 2021 boundaries | ONS Open Geography Portal | LSOA | Geographic unit for travel time analysis |
| GTFS transit feeds | TfL, National Rail, DfT | Route/stop | Bus and rail schedules for transit routing |
| Index of Multiple Deprivation 2019 | MHCLG | LSOA | IDACI and overall deprivation scores |
| Median household income (AHC) | MHCLG / CACI | MSOA | Income estimates per neighbourhood cluster |
| National Travel Survey 2017–2024 | DfT | National/regional | Mode share patterns for school travel |
| School capacity data (SCAP 2024) | DfE | School/borough | Capacity utilisation by borough |
| OS Meridian 2 | Ordnance Survey | National | Urban area masking for map layers |
| ONS Population Estimates | ONS | LA | Secondary-age population by borough |

------------------------------------------------------------------------

## Methodology

### 1. School Database

A comprehensive database of London secondary schools was compiled from
the DfE’s Get Information About Schools register, supplemented with
Ofsted inspection records and KS4 performance data. Schools were
classified by admissions policy (selective vs. non-selective), Ofsted
rating (Outstanding, Good, Requires Improvement, Inadequate), and
performance quartile based on Progress 8 and Attainment 8 scores
relative to all London schools. Top 25% thresholds were computed from
this London-wide distribution to ensure comparability across boroughs.

### 2. Travel Context

Desktop research was conducted on school travel patterns for London
children, drawing on DfT’s National Travel Survey (2017–2024) and
published TfL school travel analyses. This established baseline mode
shares — walking/cycling (~54%), transit (~24%), car (~19%) — and
contextualised the policy landscape around school choice, travel
barriers, and the geography of oversubscription.

### 3. Travel Time Matrix

Transit feeds across London’s bus and rail network were compiled into an
integrated GTFS feed. Using **R5PY** (a Python interface to the R5
routing engine), a travel time matrix was computed from each LSOA 2021
population-weighted centroid to all destination schools, segmented by
school quality threshold (all schools, Ofsted Outstanding, Top 25% P8,
Top 25% Att8) and travel mode (walk, transit, car). A Tuesday morning
peak departure window (08:00–09:00) was used to reflect realistic school
commute conditions.

### 4. Isochrones

Comparative isochrones were generated in R5PY for two contrasting
locations — **Clapham North (Lambeth)** and **Harold Hill (Havering)** —
to illustrate the stark difference in catchment accessibility between a
well-connected inner London neighbourhood and a peripheral outer London
estate. Isochrones were computed at 15, 30, and 45-minute thresholds by
transit.

### 5. Spatial Layers and Processing

The travel time matrix was joined to the LSOA 2021 boundary layer. To
focus the analysis on human settlements, layers were masked using **OS
Meridian 2** built-up area data, following O’Brien & Cheshire (2016).
Boundaries were simplified using a 100-metre tolerance to balance visual
continuity with file efficiency. Final layers were reprojected to WGS84
(EPSG:4326) and converted to `.mbtiles` using **Tippecanoe**, ensuring
full geometric fidelity across all zoom levels for Mapbox integration.

### 6. Visualisation Stack

Maps were built in **Mapbox GL JS**, with dark-themed basemap styling
applied programmatically to improve luminosity and contrast of
choropleth layers and cluster boundaries. Charts were built in
**Chart.js**. A scrollytelling architecture using Intersection Observer
APIs drives map transitions, layer visibility, and stat counter
animations in response to the user’s scroll position.

### 7. Deprivation Data

The **Income Deprivation Affecting Children Index (IDACI)** and overall
IMD scores were extracted from MHCLG’s Index of Multiple Deprivation
(2019) and merged to the LSOA 2021 geographic layer. Median household
income after housing costs (AHC) was sourced at MSOA level and matched
to each LSOA as a supplementary socio-economic indicator.

### 8. Bivariate LISA Clustering

A **bivariate Local Indicators of Spatial Association (LISA)** analysis
was conducted using `esda.Moran_Local_BV` from the PySAL ecosystem, with
transit time to the nearest Top 25% P8 school as the focal variable (X)
and IDACI score as the spatial lag variable (Y). A **K-Nearest
Neighbours weight matrix (k=8)** was used in place of Queen contiguity
to avoid connectivity gaps introduced by the River Thames. LSOAs without
a reachable school within the routing window were assigned a penalty
travel time of 120 minutes. Statistical significance was assessed at p
\< 0.05 using 999 permutations. Clusters were classified into four
quadrants: High-High (high travel time, high deprivation — the primary
vulnerability indicator), Low-High, High-Low, and Low-Low.

### 9. Income by Cluster

Median household income after housing costs was matched from MSOA to
LSOA level and aggregated by LISA cluster to produce a comparative
income profile, contextualising the economic resources available to
families in each cluster type.

### 10. Narrative and Interactivity

Analysis outputs were compiled into five webpage sections following a
scroll-driven narrative structure. Interactive features — including
cluster selection buttons, map highlight synchronisation, borough hover
effects, and animated stat counters — were implemented using vanilla
JavaScript Intersection Observer APIs to maintain a single-file
architecture with no build step dependency.

------------------------------------------------------------------------

## Cartographic Design

Several cartographic principles guided the visual design of the webpage:

1.  **Dark basemap:** A custom dark Mapbox style reduces visual noise,
    allowing choropleth colours and cluster boundaries to dominate.
    Land, roads, and water were programmatically darkened to near-black
    to maximise luminance contrast with data layers.
2.  **Colour semantics:** Cluster colours follow an intuitive red-blue
    diverging scheme — red tones for high deprivation and high travel
    time (vulnerability), blue tones for low deprivation and low travel
    time (relative advantage), consistent with established cartographic
    conventions for disadvantage mapping.
3.  **Opacity as emphasis:** Layer opacity is used dynamically to direct
    attention: non-selected clusters dim to near-invisible when a
    cluster is chosen, focusing the reader’s eye on the highlighted
    group without removing spatial context entirely.
4.  **Progressive disclosure:** The scrollytelling format reveals
    complexity incrementally — beginning with city-wide patterns before
    zooming into specific clusters, boroughs, and household-level
    statistics — reducing cognitive load while building analytical
    depth.
5.  **Luminosity and contrast:** Off-white borough boundary outlines and
    bright cluster highlight borders provide high-contrast visual
    feedback on mouseover, supporting both aesthetic clarity and
    accessibility.

------------------------------------------------------------------------

## Webpage Architecture

The project is hosted as a **static site on GitHub Pages**. The entire
application is contained within a single `pathways_to_progress.html`
file, which embeds all CSS styling, JavaScript logic, chart data, and
scroll behaviour inline. Map tile layers are hosted on **Mapbox Studio**
as vector tilesets accessed via the Mapbox GL JS API at runtime.

This single-file architecture was a deliberate design choice. By
embedding chart data, CSS tokens, and interactive logic directly in the
HTML, the project eliminates build tooling, module bundlers, and
server-side dependencies allowing a fully portable, version-controllable
page that renders identically in any modern browser without a
development environment.

Map layers uploaded to Mapbox Studio include the LISA cluster fill
layer, cluster outline layer for hover highlighting, and the LSOA travel
time choropleth. Data for charts and summary statistics are embedded
directly within the HTML to avoid additional HTTP requests and ensure
the page loads as a single unit.

This approach achieves a practical balance between **reliability** — no
external data endpoints to fail — and **maintainability** — all logic
and content are co-located in one inspectable file, reducing the surface
area for deployment errors.

------------------------------------------------------------------------

## References

- Conway, M.W., Byrd, A. and van der Linden, M. (2017) “Evidence-Based
  Transit and Land Use Sketch Planning Using Interactive Accessibility
  Methods on Combined Schedule and Headway-Based Networks,”
  Transportation Research Record, 2653(1), pp. 45–53. Available at:
  https://doi.org/10.3141/2653-06.
- Fink, C. et al. (2022) “r5py: Rapid Realistic Routing with R5 in
  Python.” Zenodo. Available at: https://doi.org/10.5281/zenodo.7060438.
- O’Brien, O. and Cheshire, J. (2016) Full article: Interactive mapping
  for large, open demographic data sets using familiar geographical
  features. Journal of Maps. Available at:
  https://doi.org/doi:10.1080/17445647.2015.1060183.
- Smith, D. (2023) “R5R Accessibility Workshop,” CityGeographics.
  Available at: https://citygeographics.org/r5r-workshop/
- “tippecanoe: Builds vector tilesets from large (or small) collections
  of GeoJSON, FlatGeobuf, or CSV features” (no date). Available at:
  https://github.com/felt/tippecanoe
