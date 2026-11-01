"""List peak, range and park rows rated 5 to 8 that the app scores on their own: not inside any scored range core
(data/ranges.json, rating 5+) or coast band (data/coasts.json). Rows rated 9 or 10 always stand alone, so they are
skipped. For each, says why: inside a scored range's outline but outside its core, inside an unscored range (ranges.csv
rating 0 to 4, outline from Natural Earth), or not in any range. (2026-11-01, Rich: "fix Diablo and others like it".)

    python3 scripts/standalone.py ne_10m_geography_regions_polys.geojson > /tmp/standalone.tsv
Needs shapely. Output: name, kind, rating, region, lat, lon, why.
"""
import csv, json, sys, pathlib
from shapely.geometry import Polygon, Point, shape
from shapely.prepared import prep
from shapely.ops import unary_union

d = pathlib.Path(__file__).resolve().parent.parent / 'data'
def rings(flat):
    out = []
    for rg in flat:
        pts = [(rg[i], rg[i + 1]) for i in range(0, len(rg), 2)]
        if len(pts) >= 3: out.append(Polygon(pts).buffer(0))
    return out
R = [(r[0], r[2], [prep(p) for p in rings(r[6] if len(r) > 6 else [])], rings(r[5]))
     for r in json.loads((d / 'ranges.json').read_text())]
C = []
for c in json.loads((d / 'coasts.json').read_text()):
    for poly in c[6]:
        rs = rings(poly if poly and isinstance(poly[0], list) else [poly])
        if rs: C.append(prep(rs[0].difference(unary_union(rs[1:])) if len(rs) > 1 else rs[0]))
U = []
if len(sys.argv) > 1:
    rc = {r['ne_id']: r for r in csv.DictReader(open(d / 'ranges.csv', encoding='utf-8'))}
    for f in json.load(open(sys.argv[1], encoding='utf-8'))['features']:
        r = rc.get(str(f['properties'].get('NE_ID')))
        if f['properties'].get('FEATURECLA') == 'Range/mtn' and r and int(r['rating']) < 5:
            U.append((r['name'], r['rating'], prep(shape(f['geometry']).buffer(0))))
for x in csv.DictReader(open(d / 'landmarks.csv', encoding='utf-8')):
    if x['kind'] not in ('peak', 'range', 'park') or not 5 <= int(x['rating']) <= 8: continue
    pt = Point(float(x['lon']), float(x['lat']))
    if any(rr >= 5 and any(c.contains(pt) for c in cs) for _, rr, cs, _ in R) or any(c.contains(pt) for c in C): continue
    out = [f'{n} ({rr})' for n, rr, _, os in R if any(o.contains(pt) for o in os)]
    uns = [f'{n} ({rr})' for n, rr, g in U if g.contains(pt)]
    if out: why = 'in outline, outside core: ' + ', '.join(out)
    elif uns: why = 'in unscored range: ' + ', '.join(uns)
    else:
        n, rr, _, os = min(R, key=lambda r: min([o.distance(pt) for o in r[3]] or [999]))
        why = f'no range; nearest scored: {n} ({rr}) {min(o.distance(pt) for o in os) * 111:.0f} km'
    print('\t'.join([x['name'], x['kind'], x['rating'], x['region'], x['lat'], x['lon'], why]))
