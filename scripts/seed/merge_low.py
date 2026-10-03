import json, csv, math, re, sys
from shapely.geometry import shape, Point
from shapely.strtree import STRtree
W = '/home/claude/build/'; REPO = '/home/claude/window-sights/'
SHORT = {'United States of America': 'USA', 'United Kingdom': 'UK'}
def load(fn, keyf):
    fs = json.load(open(W + fn))['features']; g = []; n = []
    for f in fs:
        try: g.append(shape(f['geometry'])); n.append(keyf(f['properties']))
        except Exception: pass
    return STRtree(g), g, n
adm = load('ne_10m_admin_1_states_provinces.geojson', lambda p: (p.get('adm0_a3'), p.get('name')))
cty = load('ne_50m_admin_0_countries.geojson', lambda p: p.get('NAME_LONG') or p.get('NAME'))
def hit(t, pt, maxd=0.0):
    tree, geoms, names = t
    for i in tree.query(pt):
        if geoms[i].contains(pt): return names[i]
    if maxd:
        i = tree.nearest(pt)
        if geoms[i].distance(pt) < maxd: return names[i]
    return None
def region(la, lo):
    pt = Point(lo, la); a = hit(adm, pt, 0.3)
    if a and a[0] in ('USA', 'CAN', 'AUS', 'MEX', 'BRA', 'IND', 'CHN', 'RUS'): return a[1]
    c = hit(cty, pt, 1.0); return SHORT.get(c, c) or ''
def mi(a, b): return math.hypot((a[0] - b[0]) * 69, (a[1] - b[1]) * 69 * math.cos(math.radians(a[0])))
def norm(s): return re.sub(r'[^a-z0-9]', '', s.lower())

old = list(csv.DictReader(open(REPO + 'data/sights.csv', newline='', encoding='utf-8')))
old = [r for r in old]  # name,lat,lon,kind,rating,region(,max_alt)
out = [[r['name'], float(r['lat']), float(r['lon']), r['kind'], int(r['rating']), r['region'], int(r.get('max_alt') or 0)] for r in old]
names = {norm(r[0]) for r in out}
d = json.load(open(W + 'new_raw.json'))

# Hand list for routes Rich flies: (name, lat, lon, kind, rating, max_alt); rating 0 removes
HAND = [
 ('San Francisco-Oakland Bay Bridge', 37.7983, -122.3778, 'bridge', 6, 15000),
 ('San Mateo-Hayward Bridge', 37.585, -122.215, 'bridge', 4, 15000),
 ('Dumbarton Bridge', 37.505, -122.117, 'bridge', 3, 12000),
 ('Richmond-San Rafael Bridge', 37.935, -122.45, 'bridge', 4, 15000),
 ('Oakland Coliseum', 37.7516, -122.2005, 'stadium', 4, 15000),
 ('Chase Center', 37.768, -122.3877, 'stadium', 3, 12000),
 ('Apple Park', 37.3349, -122.009, 'campus', 5, 15000),
 ('Googleplex', 37.422, -122.0841, 'campus', 4, 12000),
 ('Moffett Field and Hangar One', 37.415, -122.049, 'airport', 5, 15000),
 ('Port of Oakland', 37.7955, -122.317, 'port', 4, 15000),
 ('San Jose International Airport', 37.3626, -121.929, 'airport', 3, 12000),
 ('Alcatraz Island', 37.8267, -122.423, 'landmark', 5, 15000),
 ('Stanford University', 37.4275, -122.1703, 'campus', 4, 12000),
 ('Big Bear Lake', 34.2439, -116.9114, 'lake', 5, 25000),
 ('Lake Arrowhead', 34.2486, -117.189, 'lake', 4, 25000),
 ('San Gorgonio Pass Wind Farm', 33.9, -116.583, 'windfarm', 6, 20000),
 ('Altamont Pass Wind Farm', 37.7347, -121.6522, 'windfarm', 5, 20000),
 ('Alta Wind Energy Center', 35.0211, -118.321, 'windfarm', 5, 20000),
 ('Candlestick Park', 0, 0, '', 0, 0), ('Oakland Ballpark', 0, 0, '', 0, 0), ('Kezar Stadium', 0, 0, '', 0, 0),
 ('Oakland', 37.8044, -122.2712, 'city', 6, 0),
]
drop = {norm(h[0]) for h in HAND}
low = [r for r in d['low'] if norm(r[0]) not in drop]
cities = [r for r in d['cities'] if norm(r[0]) not in drop]

# cities: skip ones the set already has (within 12 mi), and suburbs within 10 mi of a bigger new city
oldc = [(r[1], r[2]) for r in out if r[3] == 'city']
cities.sort(key=lambda r: -r[6]); keptc = []
for r in cities:
    p = (r[1], r[2])
    if norm(r[0]) in names or any(mi(p, q) < 12 for q in oldc) or any(mi(p, (k[1], k[2])) < 10 for k in keptc): continue
    keptc.append(r)
# low sights: skip names the set has, thin to one per 0.8 mi (best first)
oldp = [(r[1], r[2]) for r in out]
low.sort(key=lambda r: (-r[4], -r[6])); keptl = []
for r in low:
    p = (r[1], r[2])
    if norm(r[0]) in names: continue
    if any(mi(p, (k[1], k[2])) < 0.8 for k in keptl): continue
    keptl.append(r)
new = [[r[0], r[1], r[2], r[3], r[4], None, r[5]] for r in keptc + keptl]
for h in HAND:
    if h[4] == 0: continue
    k = norm(h[0]); ex = [r for r in out if norm(r[0]) == k]
    if ex: ex[0][3:5] = [h[3], h[4]]; ex[0][6] = h[5]; continue
    new.append([h[0], h[1], h[2], h[3], h[4], None, h[5]])
# ceilings by kind (ft): seen from the window up to ~20,000 ft on the climb, per Rich's OAK-PSP flight
CAP = {'stadium': 20000, 'campus': 25000, 'airport': 25000, 'bridge': 20000, 'port': 20000, 'themepark': 18000, 'racetrack': 18000,
       'tower': 15000, 'landmark': 15000, 'windfarm': 25000, 'mine': 25000, 'dam': 25000}
for r in new:
    if r[3] in CAP and r[6]: r[6] = CAP[r[3]]
for r in new: r[5] = region(r[1], r[2])
allr = out + new
print('old', len(out), 'new cities', len(keptc), 'new low', len(keptl), 'total', len(allr))
w = csv.writer(open(REPO + 'data/sights.csv', 'w', newline='', encoding='utf-8'), lineterminator='\n')
w.writerow(['name', 'lat', 'lon', 'kind', 'rating', 'region', 'max_alt'])
for r in allr: w.writerow([r[0], round(r[1], 4), round(r[2], 4), r[3], r[4], r[5], r[6] or ''])
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [round(r[2], 4), round(r[1], 4)]},
  'properties': {'name': r[0], 'kind': r[3], 'rating': r[4], 'region': r[5], **({'max_alt': r[6]} if r[6] else {})}} for r in allr]},
  open(REPO + 'data/sights.geojson', 'w'), ensure_ascii=False)
open(W + 'landmarks.mjs', 'w').write('export default ' + json.dumps([[r[0], round(r[1], 4), round(r[2], 4), r[3], r[4], r[5], r[6] or 0] for r in allr], separators=(',', ':'), ensure_ascii=False) + ';\n')
