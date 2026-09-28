# Contributing

## The rating scale

The question is always: **how good is this from a passenger window at cruising altitude or on approach?** Not how famous it is, and not how good it is from the ground.

| rating | meaning | examples |
| --- | --- | --- |
| 10 | Unmistakable and breathtaking. People photograph it through the window. | Grand Canyon, Denali, Matterhorn, Mount Fuji, Hong Kong, New York City |
| 9 | A headline sight for its region. Worth switching seats for. | Mount Shasta, Crater Lake, Yosemite Valley, Dolomites, Chicago, San Francisco |
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

## Making a change

1. Edit `data/sights.csv`. Keep one sight per row and the same six columns.
2. Run `python3 scripts/validate.py`.
3. Open a pull request saying what you changed and why. For a new sight, a link (Wikipedia, Wikidata or a photo from a plane window) helps.

Please don't copy data from sources that don't allow it. Wikidata, OpenStreetMap-derived facts and your own knowledge are fine.
