# Window Landmarks

An open list of things worth seeing out of an airplane window: mountains, volcanoes, glaciers, lakes, canyons, coastlines, parks and skylines, plus the stadiums, bridges, airports, campuses and wind farms you only notice on the climb out and the approach. Each one is rated 1 to 10 for how good it looks from a passenger window.

It powers [Window Seat](https://rrw-seat.netlify.app), an app that tells you which side of the plane to sit on.

## The data

`data/landmarks.csv` is the source of truth: 6,305 landmarks, one per row.

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

`data/landmarks.geojson` is the same list as points, rebuilt by `scripts/geojson.py`, so you can browse it on a map right here on GitHub.

## Where it came from

- **Wikidata**: peaks ranked by prominence, volcanoes, national parks, large lakes, glaciers, canyons and fjords; cities over 400,000 people; stadiums by capacity; skyscrapers by height; airports, bridges, dams, ports, theme parks, race tracks, wind farms and mines by how widely they're documented. Wikidata is CC0.
- **NASA Black Marble** (VNP46A4): city brightness at night for `data/night.csv`. NASA data is public domain.
- **Natural Earth**: state and country boundaries for the `region` column. Public domain.
- **Short names**: seeded by rules (airports to IATA codes, "National Park" to NP, "Mount" to Mt., city prefixes off bridge names) plus a hand list, then edited by hand.
- **Hand curation**: a starter list of famous landmarks, skyline ratings for cities (by count of 150 m+ towers, not population), and many rating fixes.

`scripts/seed/` holds the scripts that built the first version from those sources. They're kept for reference. From here on, edit the CSV directly.

## Contributing

Pull requests welcome: new landmarks, better coordinates, rating changes with a reason. Every change runs `scripts/validate.py` automatically. Details in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

The data is licensed under [CC BY 4.0](LICENSE): use it for anything, including commercially, as long as you give credit. The scripts in `scripts/` are CC0.

### How to credit

> Data: [Window Seat](https://rrw-seat.netlify.app)

A link to the app is welcome. If space is tight, "Data: Window Seat" is enough.
