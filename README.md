# Window Landmarks

An open list of things worth seeing out of an airplane window: mountains, volcanoes, glaciers, lakes, canyons, coastlines, parks and skylines, plus the stadiums, bridges, airports, campuses and wind farms you only notice on the climb out and the approach. Each one is rated 1 to 10 for how good it looks from a passenger window.

It powers [Window Seat](https://windowseat.travel), an app that tells you which side of the plane to sit on.

## The data

`data/landmarks.csv` is the source of truth: 6,517 landmarks, one per row.

| column | meaning |
| --- | --- |
| `name` | Full name. Group a cluster as one landmark when you'd see it as one ("Eiger / Jungfrau"). |
| `short` | Optional map label, as short as it can be and still be recognized: `Bay Bridge`, `Mt. Fuji`, `Chitwan NP`. Airports use their IATA code (`LHR`). Blank means use `name`. |
| `lat`, `lon` | Decimal degrees, the point a passenger would look at. |
| `kind` | Scenery: `peak`, `range`, `volcano`, `glacier`, `lake`, `coast`, `canyon`, `island`, `park`, `desert`, `landmark`, `feature`, `city`. Low-altitude: `stadium`, `campus` (universities), `office` (corporate campuses), `airport`, `bridge`, `tower`, `port`, `themepark`, `racetrack`, `windfarm`, `mine`, `dam`. |
| `rating` | 1 to 10. See [CONTRIBUTING.md](CONTRIBUTING.md) for the scale. |
| `region` | US state, Canadian province, Australian state, or country. |
| `max_alt` | Optional ceiling in feet. The landmark only counts while the plane is below it (climb out and approach). Blank means visible from cruise. |
| `size_m` | Optional, low landmarks only. How big it reads from the air, in meters: footprint for flat things, height for towers. Blank uses the default for its kind (stadium 250, campus and office 800, airport 2,500, bridge 1,200, tower 200). Set it higher for things that stand out more than their size suggests, like an island in open water or white buildings on a dark hillside. |

`data/night.csv` scores what you can see on a night flight, from NASA's Black Marble yearly night-lights composite (VNP46A4, 2025). Every `city` row gets `night` from the total radiance within 15 km (`round(1.8 × log10(sum) − 2.7)`, capped at 8: Riyadh, Doha and Moscow are 8, New York 7, Pyongyang 5). Brightness mostly measures sprawl, so cities top out below the best scenery. Lit airports, ports, bridges, towers, landmarks, theme parks and racetracks get one from a small radius around the point when they score 4 or more. Eight `night_only` rows cover things you only notice in the dark: gas flares (Permian, Bakken, South Pars, Niger Delta, western Siberia), the Westland greenhouses, the Nile valley and the India–Pakistan border. Rebuild with `EARTHDATA_TOKEN=... python3 scripts/night.py`; details in the script.

`data/blurbs.csv` holds the text for each landmark's card: one or two sentences, in feet and miles, with the fact that makes you look twice and usually a "Look for" cue saying what to spot from the window. It has one row per landmark and per `night_only` row, joined on `name, region, lat, lon`. Written for this dataset and fact-checked against public sources; style rules are in CONTRIBUTING.md.

**Areas.** Mountain ranges and dramatic coasts are scored whole, once per side of the plane, not as points:
- `data/ranges.csv`: Natural Earth's named ranges (`ne_id`), with our name, region and rating (0 to 4 = not scored).
  `data/ranges.json` is built from it: `[name, region, rating, family, [w, s, e, n], outline rings, core rings]`. The
  core is where the mountains are, from elevation, not the whole outline (the Rockies outline covers half of Wyoming's
  basins). Ranges nested in one another share a `family`. Build: `node scripts/build_ranges.mjs
  ne_10m_geography_regions_polys.geojson && python3 scripts/build_range_cores.py`.
- `data/coasts.csv`: coasts where mountains meet the sea (Greenland, Norway, Big Sur...): name, region, rating, a box or
  an outline (`area`), an optional height bar (`rise`, meters) and the single-point rows each one `replaces` (exact
  names). `data/coasts.json` is built from it: `[name, region, rating, family, [w, s, e, n], replaces, polys]`, a band
  about 10 km each side of the coastline where the land within ~12 km rises past the bar (700 m by default), holes kept.
  Build: `python3 scripts/build_coasts.py ne_10m_coastline.geojson` (after the ranges).
Rings are flat `[lon, lat, lon, lat, ...]`. Points inside an area that it covers (peaks, fjords, parks rated under 9)
are kept here but not shown on their own by the app.

`data/relief.csv` (name, region, lat, lon, summit_m, relief_m) measures how far each peak and range row rises above the land within about 12 miles; see Judgment calls. Rebuild with `python3 scripts/relief.py` after adding or moving a peak or range row.

`data/landmarks.geojson` is the same list as points, rebuilt by `scripts/geojson.py`, so you can browse it on a map right here on GitHub.

## Judgment calls

How Window Seat turns this data into points, and why. These are choices, not facts: each says who decided and when, so
you can disagree with a specific one.

- **Famous means 9 or 10.** A rating of 9 or 10 is for sights people recognize by name from the air: the Matterhorn,
  Mont Blanc, Denali, Grand Teton, Rainier. Pikes Peak and Mount Diablo are well known locally but not famous in this
  sense. (Rich, 2026-10-31)
- **Ranges are scored whole.** A mountain range counts once per side of the plane, at its rating, scaled by how long it
  fills the window. Peaks, old single-point ranges and parks inside a scored range's core fold into it, unless rated 9
  or 10: Rocky Mountain National Park beside the Rockies is the same view twice. Ranges rated under 5 aren't scored:
  low, rolling ranges like the Pacific Coast Ranges and the Appalachians don't read as mountains from cruise.
  (Rich, 2026-10-31)
- **Volcanoes always stand alone.** Rainier, Shasta and Fuji rise on their own whatever range they sit in, so they
  never fold. Glaciers, lakes and canyons stay too: they look like something of their own. So does Yosemite Valley /
  Half Dome (a feature, 9). (Rich, 2026-10-31)
- **Dramatic coasts** (mountains meeting the sea: Greenland, Norway, Big Sur) are scored whole like ranges, and the
  fjord, peak and park points inside them fold in. (Rich, 2026-10-31)
- **A peak on its own has to stand up: 1,500 m of relief.** A peak or range row rated under 9 that no scored range or
  coast covers counts only if it rises at least 1,500 m (about 5,000 ft) above the land within about 12 miles
  (`relief_m` in `data/relief.csv`, from `scripts/relief.py`). From 35,000 ft a 1,000 m hill is a brown bump; a
  1,500 m rise reads as a mountain. (Rich, 2026-11-01, after Mount Diablo showed as a sight on San Francisco to Seattle.)
  Where it falls:

  | Peak | Summit | Relief | Counts |
  | --- | --- | --- | --- |
  | Mount Tamalpais | 781 m | 781 m | no |
  | Mount Diablo | 1,140 m | 1,119 m | no |
  | Katahdin | 1,574 m | 1,403 m | no |
  | Mount Mitchell | 2,015 m | 1,448 m | no |
  | Mount Washington | 1,904 m | 1,515 m | yes, just |
  | Mont Ventoux | 1,893 m | 1,630 m | yes |
  | Charleston Peak | 3,599 m | 2,227 m | yes |
  | San Jacinto Peak | 3,270 m | 3,045 m | yes |

  Measured on roughly 150 m elevation pixels, so sharp spires read low (Fitz Roy is 3,405 m and measures 2,840 m):
  errors only make a peak look smaller, so whatever passes really does stand out. Rows past 84 degrees of latitude, south
  of 56 degrees (beyond SRTM, where the tiles fall back to coarse ETOPO1 and Antarctic peaks measured up to 2 km low),
  and a short hand list whose narrow summits the tiles miss (MEASURED_LOW in relief.py) are unmeasured and count. Ratings stay as they are: the rating says how good the view is, relief says whether it
  stands out enough to be a view at all.

## Where it came from

- **Wikidata**: peaks ranked by prominence, volcanoes, national parks, large lakes, glaciers, canyons and fjords; cities over 400,000 people; stadiums by capacity; skyscrapers by height; airports, bridges, dams, ports, theme parks, race tracks, wind farms and mines by how widely they're documented. Wikidata is CC0.
- **NASA Black Marble** (VNP46A4): city brightness at night for `data/night.csv`. NASA data is public domain.
- **Natural Earth**: state and country boundaries for the `region` column, range outlines and coastlines for the areas. Public domain.
- **AWS Terrain Tiles** (Mapzen terrarium, zoom 6 and 10): elevation for range cores, dramatic coasts and `data/relief.csv`. Their sources ask for these credits:
  - ArcticDEM terrain data DEM(s) were created from DigitalGlobe, Inc., imagery and funded under National Science Foundation awards 1043681, 1559691, and 1542736
  - Australia terrain data © Commonwealth of Australia (Geoscience Australia) 2017
  - Austria terrain data © offene Daten Österreichs – Digitales Geländemodell (DGM) Österreich
  - Canada terrain data contains information licensed under the Open Government Licence – Canada
  - Europe terrain data produced using Copernicus data and information funded by the European Union - EU-DEM layers
  - Global ETOPO1 terrain data U.S. National Oceanic and Atmospheric Administration
  - Mexico terrain data source: INEGI, Continental relief, 2016
  - New Zealand terrain data Copyright 2011 Crown copyright (c) Land Information New Zealand and the New Zealand Government (All rights reserved)
  - Norway terrain data © Kartverket
  - United Kingdom terrain data © Environment Agency copyright and/or database right 2015. All rights reserved
  - United States 3DEP (formerly NED) and global GMTED2010 and SRTM terrain data courtesy of the U.S. Geological Survey
- **Short names**: seeded by rules (airports to IATA codes, "National Park" to NP, "Mount" to Mt., city prefixes off bridge names) plus a hand list, then edited by hand.
- **Hand curation**: a starter list of famous landmarks, skyline ratings for cities (by count of 150 m+ towers, not population), and many rating fixes.

`scripts/seed/` holds the scripts that built the first version from those sources. They're kept for reference. From here on, edit the CSV directly.

## Contributing

Pull requests welcome: new landmarks, better coordinates, rating changes with a reason. Every change runs `scripts/validate.py` automatically. Details in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

The data is licensed under [CC BY 4.0](LICENSE): use it for anything, including commercially, as long as you give credit. The scripts in `scripts/` are CC0.

### How to credit

> Data: [Window Seat](https://windowseat.travel)

A link to the app is welcome. If space is tight, "Data: Window Seat" is enough.
