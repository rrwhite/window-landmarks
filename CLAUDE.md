# Maintaining Window Landmarks

Instructions for the agent that owns this dataset. README.md and CONTRIBUTING.md describe the columns and the rating scale; read both first. This file covers how the data is used, the rules that decide what shows in the app, and the current work.

## Who does what

- **This repo (you):** `data/landmarks.csv` and everything under `scripts/`. Push to `main`; CI runs `scripts/validate.py`.
- **The app (another agent):** Window Seat, repo `rrwhite/window-seat`, site rrw-seat.netlify.app. It compiles this CSV into `netlify/functions/plan/data/landmarks.mjs` with `tools/build_landmarks.py` and deploys. You never edit or deploy the app.
- **Handoff:** when a batch is pushed, tell Rich in one line what landed (commit, rows added/removed/changed). The app agent rebuilds and deploys in batches, so several small dataset commits per app deploy is normal.
- Talk to Rich tersely. No em-dashes.

## Night scores

`data/night.csv` (from `scripts/night.py`, NASA Black Marble 2025) has columns name, region, lat,
lon, kind, radiance_sum, night, night_only. Join to landmarks.csv on name, region, lat, lon.
Rules for the app on segments flown in darkness:
- **Cities** score from `night` instead of `rating`, and ignore `max_alt` (city lights are visible
  from cruise even when the skyline isn't). Every city row has a night score. City night scores cap at 8
  (`round(1.8 log10(sum) - 2.7)`, 2 to 8): a bright city is not a Rainier. Only unique night
  sights go above 8, set by hand with Rich's sign-off.
- **Low landmarks** count only if they have a night.csv row (lit airports, ports, bridges, towers,
  landmarks, theme parks, racetracks with night >= 4), using `night` for points and their usual
  `max_alt` and size test. Everything else low is invisible at night. Stadiums have no night row:
  their lights are on only for night games.
- **night_only = 1** rows (gas flares, lit greenhouses, the Nile ribbon, the India-Pakistan border)
  are not in landmarks.csv. Treat them as scenery that exists only at night.
- **Other scenery** (peaks, lakes, coasts, glaciers): proposed moonlight rule, for the app agent to
  decide: count it only when the moon is up and at least half full, at `rating - 2`.
When you add or move a city or a lit low landmark, rerun the script (needs an Earthdata token from
Rich); a row missing from night.csv simply has no night score.

## Blurbs

`data/blurbs.csv` (name, region, lat, lon, blurb) is the card text the app shows instead of Wikipedia
extracts. Style is in CONTRIBUTING.md ("Blurbs"); Rich chose feet only and a "Look for" cue. validate.py
fails if any landmark or night_only row lacks a blurb, a blurb has no landmark, or the style lint trips.
When you add, rename, move or remove a row, update its blurb in the same commit. Facts must be ones you
would bet on; check numbers for anything rated 6+ before writing them.

## Before every push

```
python3 scripts/validate.py     # header, kinds, ratings, max_alt, size_m, duplicates
python3 scripts/geojson.py      # keeps data/landmarks.geojson in sync with the CSV
```

Keep the CSV's column order and `\n` line endings. Write it with `csv.DictWriter(..., lineterminator='\n')` using the existing header so diffs stay small.

## How the app decides what you see

**Scenery** (peaks, volcanoes, lakes, parks, cities, coasts; rows with blank `max_alt`): counts within a range that grows with the rating, up to the horizon. Rating is what matters.

**Low landmarks** (rows with `max_alt`): count only while the plane is below `max_alt`, and only while the thing *looks big enough* from the window:

```
apparent = size_m * sqrt(sin(look-down angle)) / slant distance      (flat things)
apparent = size_m / slant distance                                    (towers: size_m is height)
counts when apparent >= 25 mrad (1.4 degrees, about three full moons side by side)
```

Flat things shrink fast at shallow angles. Rough reach at 5,000 ft: a 250 m stadium about 3 mi, an 800 m campus about 7 mi, a 2.5 km airport about 15 mi.

Blank `size_m` uses the kind default: stadium 250, campus 800, office 800, airport 2500, bridge 1200, tower 200 (height), port 1500, themepark 500, racetrack 1000, landmark 300, windfarm 4000, mine 1500, dam 400.

**Set `size_m` for how big it reads, not its survey footprint.** Raise it for high contrast (an island in open water, white buildings on a dark hillside, a sign facing the approach). Lower it for things that blend in (a beige campus in beige suburbs, a low stadium hidden by trees). Current overrides: Alcatraz 800, Hollywood Sign 900, Griffith Observatory 700, Getty Center 500, Googleplex 600.

Ratings set points; `size_m` sets visibility. If something is clearly visible from farther than the rule allows, raise `size_m`, not the rating.

## Current job: metro curation pass

The seed came from Wikidata, which ranks low landmarks by how widely they are documented. That missed things people actually photograph from the window (the Hollywood Sign, Griffith Observatory, the Getty) and kept things invisible from the air (the Hollywood Walk of Fame, a sidewalk).

Done (Oct 2026): SFO, OAK, SJC, LAX, SEA, YVR, NYC (JFK/LGA/EWR), DEN, YYC, BOS, CHI (ORD/MDW),
MIA/FLL, ATL, DFW, IAH/HOU, PHX, LAS, MSP, DTW, PHL, WAS (IAD/DCA), LHR, CDG/ORY, FRA, AMS, NRT/HND,
SAN, PDX, SLC, CLT, MCO, YYZ, YUL, MEX, MAD, BCN, MUC, ZRH, FCO, IST, DXB, SIN, HKG, ICN, SYD.
Also done: global stadium sweep, district-as-city sweep, and AUS BNA RDU TPA PIT STL MCI SAT SMF
HNL ANC YEG YOW DUB EDI MAN CPH OSL ARN HEL VIE PRG LIS ATH DOH DEL BOM BKK KUL TPE PEK PVG MEL
AKL GRU EZE BOG LIM SCL CUN JNB CPT CAI.
Airport coverage check done: every airport with 5M+ passengers a year (Wikidata P3872) is in.
Known-issues sweep done (Oct 2026): underground and invisible mines, small monuments, towns
filed as mines or ports, demolished parks and dams, old road circuits, old-town universities,
label typos. Scenery pass and mid-size hubs pass also done (KIX/ITM FUK CTS OKA PUS CJU KHH
CTU CKG CAN XIY HGH WUH MNL CGK SGN HAN RUH JED AUH TLV MOW LED WAW BUD BRU GVA MIL VCE NCE BER HAM
DUS/CGN GDL MTY RIO BSB CLE MSY CVG IND CMH OGG BNE PER). Next: open; ask Rich.

For each metro, within about 30 miles of the airport:

1. **Candidates from what people see.** List what passengers notice and photograph on the climb out and approach: signs, observatories, museums on hills, piers, islands, distinctive buildings, big stadiums, harbors, bridges, racetracks. Use your knowledge and window-seat photo write-ups. Expect 15 to 30 candidates.
2. **Check every existing low row in the area.** Remove what can't be seen from the air: sidewalks, interiors, underground sites, demolished buildings, plaques. Fix wrong kinds and coordinates.
3. **Verify on satellite.** Esri World Imagery tiles: `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}` (zoom 14 to 16). Judge size and contrast as seen from about 5,000 ft, slanted. Put lat/lon on the thing itself, not its street address.
4. **Fill the row:**
   - `kind`: from the README list. `office` is for corporate campuses, `campus` for universities.
   - `rating`: per CONTRIBUTING, mostly 3 to 6 for low landmarks.
   - `max_alt`: per CONTRIBUTING.
   - `short`: the shortest name people still recognize.
   - `size_m`: only when the kind default is wrong.
   **Only unique things.** A low landmark earns a row when it is distinctive in itself, something a passenger would point at by name: a sign, an observatory, a giant accelerator, colored salt ponds, a theme park, a famous campus. Skip:
   - Single downtown towers. The skyline is the `city` row. Exception: a short list of icons whose silhouette people know from the window (Empire State, Willis, Transamerica, Space Needle, CN Tower, Burj Khalifa, Eiffel, Taipei 101, Oriental Pearl). Add to it rarely. Bare radio masts never.
   - Generic islands, parks and green space with nothing distinctive to see (Treasure Island, Angel Island, Golden Gate Park). Alcatraz stays because the prison is the point.
5. **Check thinning.** `scripts/thin.py` never removes low landmarks, so don't run it to clean a metro. Use judgment on crowding instead: within one approach, keep the few that stand out.
6. **Commit one metro at a time.** The message lists rows added, removed, and changed, with a reason for each removal.

## What qualifies

**Stadiums and arenas.** Keep one when either:
- a team in a top professional league plays there: NFL, MLB, NBA, NHL, MLS, WNBA, CFL; the
  top flight of football in Europe (Premier League, La Liga, Bundesliga, Serie A, Ligue 1, and
  the top league of other countries) and the equivalent top leagues elsewhere (NPB, J1, KBO,
  Liga MX, Argentine Primera, A-League, AFL, NRL, IPL grounds); or
- the venue is famous or a unique structure in its own right: SoFi, the Rose Bowl, Wembley,
  Olympic stadiums, the Kia Forum, a World Cup final ground.
College stadiums qualify only when they are the giants of college football: roughly 80,000+
seats or a name everyone knows (Michigan Stadium, Ohio Stadium, Bryant-Denny, Beaver Stadium,
Neyland, Kyle Field, Tiger Stadium, the Rose Bowl). Smaller college grounds do not.

**Campuses.** Famous universities with a look you can pick out (Stanford's red roofs, Berkeley's
Sather Tower, MIT's dome on the Charles), or a campus that is visually unique wherever it is
(Pepperdine on its bare hillside). Not every large university.

## How to find candidates

1. Pull every row within 30 miles of the airport and judge each against the rules above.
2. List candidates from: pro team venues in the metro; observatories, signs, theme parks, piers,
   ships, salt ponds, accelerators and other one-offs passengers photograph; distinctive
   bridges and harbors; famous campuses. Your own knowledge first; window-seat photo
   write-ups to confirm what people actually notice.
3. Satellite check each one: `python3 scripts/sat.py NAME LAT LON ZOOM`, then look at
   `sat/NAME.jpg`. Move the point onto the object. Drop it if it is hidden in trees, the same
   color as its surroundings, or smaller than about 100 m with no contrast.
4. Fill the row (kind, rating, max_alt, short, size_m) and commit the metro.

## Known data issues to sweep while you're there

- Kind mistakes: an airport was filed as a racetrack (Galeao, fixed), Nalanda Mahavihara was filed as a campus (fixed). Look for more, especially in `racetrack`, `landmark` and `campus`.
- Typos and odd capitalisation from Wikidata labels (fixed: Cofre de Perote, Imam Reza Stadium).
- Low `landmark` rows that are not visible objects (streets, districts, events).

## Roadmap (on hold until Rich says go)

- **Game-day flags.** `data/venues.csv`: each kept stadium with its tenant teams, league, and
  schedule-source IDs (MLB StatsAPI venue/team, NHL, NBA, ESPN for NFL/MLS, football-data.org
  for top European leagues, TheSportsDB fallback). Seed from the Wikidata tenant matches made in
  the stadium sweep; recheck each stadium sweep. App side, flights within ~2 months: flag a game
  near pass time ("Giants vs Dodgers at Oracle Park, 7:05"); at night a game means lights on,
  night score ~6. Note MLB and ESPN terms are personal/non-commercial.

## Rules

- The data is CC BY 4.0 (see LICENSE). Allowed sources: Wikidata (CC0), Natural Earth (public domain), NASA, USGS and NOAA (public domain), GeoNames (CC BY, credit it in README), satellite imagery for checking positions, and your own knowledge. Never OpenStreetMap: its ODbL share-alike license conflicts with CC BY. Don't copy text or lists from sources that don't allow it.
- Never remove a row only because it is unlikely to show. The app's rules handle visibility; remove only what truly can't be seen from the air.
