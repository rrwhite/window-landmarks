"""Keep crowded areas from dominating. Run: python3 scripts/thin.py

Walking from the highest rating down, a sight is dropped when it is crowded
by sights already kept within 50 km:
  rated 1 to 4: dropped if any kept sight is within 50 km
  rated 5 to 7: dropped if two or more kept sights are within 50 km
  rated 8 to 10, and all cities: always kept
Low-altitude sights (rows with max_alt) sit inside cities by design and are never thinned here,
and neither they nor cities count as crowding.
"""
import csv, math, collections, pathlib
P = pathlib.Path(__file__).resolve().parent.parent / 'data' / 'sights.csv'
R_KM = 50
def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (float(a['lat']), float(a['lon']), float(b['lat']), float(b['lon'])))
    x = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(min(1, math.sqrt(x)))
rows = list(csv.DictReader(open(P, newline='', encoding='utf-8')))
kept, cell = [], collections.defaultdict(list)
for r in sorted(rows, key=lambda r: -int(r['rating'])):
    key = (int(float(r['lat']) // 1), int(float(r['lon']) // 1))
    near = [k for dx in (-1, 0, 1) for dy in (-1, 0, 1) for k in cell[(key[0] + dx, key[1] + dy)] if km(k, r) < R_KM]
    rating = int(r['rating'])
    if not r.get('max_alt') and r['kind'] != 'city' and rating < 8 and len(near) >= (1 if rating <= 4 else 2): continue
    kept.append(r)
    if not r.get('max_alt') and r['kind'] != 'city': cell[key].append(r)  # cities and low sights never crowd others out
keep = {id(r) for r in kept}
out = [r for r in rows if id(r) in keep]
with open(P, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['name', 'lat', 'lon', 'kind', 'rating', 'region', 'max_alt']); w.writeheader(); w.writerows(out)
print(f'{len(rows)} -> {len(out)} sights')
