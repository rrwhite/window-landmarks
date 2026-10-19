# Contributing

## The rating scale

The question is always: **how good is this from a passenger window at cruising altitude or on approach?** Not how famous it is, and not how good it is from the ground.

| rating | meaning | examples |
| --- | --- | --- |
| 10 | Unmistakable and breathtaking. People photograph it through the window. | Grand Canyon, Denali, Matterhorn, Mount Fuji, Hong Kong, New York City |
| 9 | A headline landmark for its region. Worth switching seats for. | Mount Shasta, Crater Lake, Yosemite Valley, Dolomites, Chicago, San Francisco |
| 8 | Clearly striking, easy to pick out. | Lake Tahoe, Monument Valley, Mount Baker, Bosphorus |
| 7 | Very nice if you're on that side. | Bryce Canyon, Mono Lake, Golden Gate Bridge, Beijing |
| 6 | Good. Worth a look. | Amalfi Coast, Annapurna II |
| 5 | Pleasant. | |
| 3 to 4 | Minor. Fine to glance at. | |
| 1 to 2 | Not worth listing. Leave it out. | |

Rules of thumb:
- **Relief beats fame.** A low, eroded volcano reads as forested hills from the air. Low volcanoes (under about 1,000 m) are rated 3.
- **Cities are rated by skyline**, not population. A city of 5 million with no towers is a 4 at most, for its lights at night.
- **Canyons and fjords top out at 5** unless they're truly exceptional (the Grand Canyon is a 10).
- **Nothing underwater.** Seamounts and submarine volcanoes don't belong here.
- **Low-altitude landmarks** (stadiums, bridges, airports, campuses, offices, towers, wind farms, quarries) are rated for how they look on the climb or approach, mostly 3 to 6, and carry a `max_alt` in feet: 20,000 for stadiums, bridges and ports, 25,000 for airports, campuses, offices, wind farms, mines and dams, 15,000 for single towers and monuments. Cities with no real skyline only belong if they are large (400,000+ people), and get a ceiling of 25,000 ft unless over a million.
- **No crowding.** Within any 50 km, a minor landmark (1 to 4) only stays if nothing else is kept nearby, and a 5 to 7 only stays if fewer than two others are. 8+ and cities always stay. `scripts/thin.py` applies this; run it after adding landmarks.

## How far away a low landmark counts

A low landmark counts while it looks at least 1.4 degrees across from the window (about three full moons side by side). Flat things shrink when seen at a shallow angle, so the app uses `size_m × √sin(look-down angle) ÷ distance`; towers use their height with no shrinking. A 250 m stadium counts out to about 3 miles at 5,000 ft. If something is clearly visible from farther away than that, raise its `size_m` rather than its rating.

## Short names

`short` is the label on the map, where space is tight. Make it as short as people would still recognize: drop the city on a bridge (`Bay Bridge`), the country on a peak, and words like International or Hydroelectric Power Station (`Bratsk Dam`). Use NP, NM, SP, Mt., St. and Ft. Airports get their IATA code. Leave it blank if the full name is already short.

## Blurbs

Every landmark has a card blurb in `data/blurbs.csv`. The card shows when a passenger can see the thing, so write what makes someone look twice:

- One or two sentences, about 20 to 45 words (55 at most).
- Lead with the jaw-drop fact: height, depth, size, age, a record, a story. Then, when there's an honest one, a spotting cue starting "Look for": a shape, color or contrast you can see from a plane.
- Feet, miles, acres and square miles only. No dashes as punctuation, no exclamation marks, no hype words (stunning, majestic, iconic, nestled).
- Don't open with the name or "X is a ...": the card already shows it.
- Only facts you're sure of. A true description of what it looks like beats a guessed number. Say "one of the largest" unless it's provably the largest.

Example: *At 1,943 ft, the deepest lake in the US. It fills the hole left when Mount Mazama blew apart about 7,700 years ago. Look for Wizard Island, a cinder cone near the west rim.*

## Making a change

1. Edit `data/landmarks.csv`. Keep one landmark per row and the same nine columns (`short`, `max_alt` and `size_m` can be blank). Add, rename, move or delete the matching row in `data/blurbs.csv` too: the two files must line up on name, region, lat and lon.
2. Run `python3 scripts/validate.py`, then `python3 scripts/geojson.py`.
3. Open a pull request saying what you changed and why. For a new landmark, a link (Wikipedia, Wikidata or a photo from a plane window) helps.

Contributions are licensed under CC BY 4.0, the same as the data. Please don't copy data from sources that don't allow it. Wikidata, Natural Earth, NASA, USGS, NOAA and your own knowledge are fine. Don't use OpenStreetMap: its share-alike license conflicts with CC BY.
