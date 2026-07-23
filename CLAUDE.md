# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A single self-contained HTML file (`europe_map.html`) — an interactive choropleth map of
Europe showing selectable social/economic indicators per country (murder rate, suicide
rate, median income, median wealth, life expectancy). There is no build system, package
manager, or test suite; it's plain HTML/CSS/vanilla JS with inline SVG.

## Running it

Open the file directly in a browser — no server or build step required:

```bash
open europe_map.html
```

There is no lint/build/test tooling in this repo. Do not invent npm scripts or a build
step; changes are made by editing `europe_map.html` in place.

## Architecture (single file, three logical parts)

`europe_map.html` is organized as one HTML document with all CSS and JS inlined. Internally
it has three parts that must stay in sync when editing:

1. **`const geo = {...}`** — a JSON blob of pre-computed SVG path data (`d` attributes) and
   label centroids (`cx`/`cy`) for ~41 European countries/territories, keyed by short display
   name (e.g. `'UK'`, `'Czechia'`, `'Bosnia'` — not always the official name). This was
   generated offline with a Python pipeline (geopandas + shapely), not something checked into
   the repo:
   - Source: a public domain world GeoJSON (`johan/world.geo.json` on GitHub).
   - Filtered to European countries, clipped to a lon/lat bounding box (`-25,34` to `45,71`)
     to cut off Russia's Siberian extent, then reprojected to **EPSG:3035** (ETRS89-LAEA
     Europe — equal-area, appropriate for a Europe-only map).
   - Converted to SVG path strings manually (flipping Y, scaling to a 1000-wide viewBox) —
     there is no d3/topojson dependency at runtime; the paths are static strings.
   - If the map geometry ever needs regenerating (new countries, different clip box, higher
     resolution), redo this pipeline rather than hand-editing path strings.

2. **`const countryData = {...}`** — the actual indicator values per country. Keys must match
   the short display names used in `geo.countries`. Field provenance (important — don't
   silently replace with different definitions):
   - `murder`, `suicide`, `lifeexp`: rough 2023/24 estimates, not tied to a single cited
     source.
   - `income`: **median** (not mean) equivalised net income, PPP-adjusted. For EU/EFTA
     countries this is Eurostat dataset `ilc_di03`, unit `PPS`, 2023. For UK/Iceland (whose
     Eurostat series are stale) the last available PPS figure was inflation-forwarded using
     World Bank CPI (`FP.CPI.TOTL`). For non-EU countries with no Eurostat series (Russia,
     Ukraine, Belarus, Moldova, Bosnia, Kosovo), income is *estimated* as `0.30 × GDP per
     capita PPP` (World Bank `NY.GDP.PCAP.PP.CD`), where 0.30 is the calibrated
     median-income/GDP-PPP ratio observed across the real Eurostat data points.
   - `wealth`: **median** wealth per adult, PPP-adjusted. Base figures are nominal-USD median
     wealth per adult from the UBS Global Wealth Report 2023 (scraped from Wikipedia's "List
     of countries by wealth per adult"), then multiplied by a per-country PPP factor
     (`GDP per capita PPP ÷ GDP per capita nominal`, both from World Bank) to convert to
     purchasing-power terms. Ukraine, North Macedonia, and Kosovo aren't in the UBS table;
     their nominal-USD wealth is a rough regional-comparable estimate before the same PPP
     factor is applied.
   - Units are labelled `PPP-$` in the UI, not literal USD — don't reformat them with a `$`
     currency symbol implying market exchange rates.

3. **Rendering/interaction JS** (bottom of the file) — `metricConfig` defines per-metric
   color scales (5-step for income/wealth/lifeexp: red→green; 4-step for murder/suicide:
   green→red, since low is good there) and min/max domains used to bucket colors. `drawMap()`
   renders one `<path>` per country from `geo`, colored via `getColor()`; a radio-button group
   switches `currentMetric` and re-renders. Small countries (Luxembourg, Malta, Kosovo, etc.)
   are excluded from label rendering to avoid overlap, but still get their own colored path.

## Editing conventions specific to this file

- Country keys in `countryData` and `geo.countries` must match exactly (short names, e.g.
  `Czechia` not `Czech Republic`, `UK` not `United Kingdom`, `Bosnia` not `Bosnia and
  Herzegovina`) — there's no lookup/alias table reconciling the two.
- When updating `min`/`max` in `metricConfig`, recompute from the actual data range in
  `countryData` — they're hand-set, not derived at runtime.
- Keep the German-language UI text (labels, tooltips, source note) consistent — the whole
  page is in German.
