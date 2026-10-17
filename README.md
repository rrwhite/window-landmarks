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

`data/landmarks.geojson` is the same list as points, rebuilt by `scripts/geojson.py`, so you can browse it on a map right here on GitHub.

## Where it came from

- **Wikidata**: peaks ranked by prominence, volcanoes, national parks, large lakes, glaciers, canyons and fjords; cities over 400,000 people; stadiums by capacity; skyscrapers by height; airports, bridges, dams, ports, theme parks, race tracks, wind farms and mines by how widely they're documented. Wikidata is CC0.
- **Natural Earth**: state and country boundaries for the `region` column. Public domain.
- **Short names**: seeded by rules (airports to IATA codes, "National Park" to NP, "Mount" to Mt., city prefixes off bridge names) plus a hand list, then edited by hand.
- **Hand curation**: a starter list of famous landmarks, skyline ratings for cities (by count of 150 m+ towers, not population), and many rating fixes.

`scripts/seed/` holds the scripts that built the first version from those sources. They're kept for reference. From here on, edit the CSV directly.

## Contributing

Pull requests welcome: new landmarks, better coordinates, rating changes with a reason. Every change runs `scripts/validate.py` automatically. Details in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

The data is licensed under [CC BY 4.0](LICENSE): use it for anything, including commercially, as long as you give credit. The scripts in `scripts/` are CC0.
