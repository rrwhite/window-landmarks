"""Build data/coasts.json: dramatic coasts as areas, like mountain ranges (Rich, 2026-10-31, on
LH458: Greenland's coast is the sight, not one fjord point, and the white interior is not).

Dramatic coast = coast where mountains meet the sea. Coastline: Natural Earth 10m coastline (public domain),
github.com/nvkelso/natural-earth-vector geojson/ne_10m_coastline.geojson. Elevation: AWS Terrain Tiles (terrarium,
zoom 6), cached in /tmp/terrain, the same source as tools/build_range_cores.py (credited on /credits). No OpenStreetMap.
Names, ratings, boxes (or an outline, `area`, where boxes would overlap) and the single-point sights each coast
replaces: data/coasts.csv (ours). The app (rrwhite/window-seat) imports data/coasts.json with tools/build_areas.py.

Inside each box, a coastline point is dramatic when the land within ~12 km rises to RISE m or more. Dramatic stretches
are buffered BAND km each way (land and sea: from the plane the coast is both), gaps under ~25 km closed, pieces under
MIN_KM2 dropped, holes kept (a band all the way round an island must not cover its interior), simplified to ~2 km.

    python3 scripts/build_coasts.py /path/to/ne_10m_coastline.geojson   (after scripts/build_range_cores.py: families)
Record: [name, region, rating, family, [w, s, e, n], replaces[], polys] where polys = [[outer, hole, ...], ...], each
ring flat [lon, lat, ...]. family: a coast whose band mostly lies in a scored range's core joins that range's family,
so a route counts the coast or the range on a side, not both (the Coast Mountains are the Inside Passage's coast).
"""
import csv, json, math, os, pathlib, sys, urllib.request
import numpy as np
from PIL import Image
from scipy import ndimage
from shapely.geometry import LineString, Polygon, MultiPolygon, box, Point
import warnings; warnings.filterwarnings("ignore")
from shapely.ops import unary_union, transform

RISE, BAND, MIN_KM2 = 700, 10, 600
Z, CACHE = 6, '/tmp/terrain'
os.makedirs(CACHE, exist_ok=True)
root = pathlib.Path(__file__).resolve().parent.parent

def tile(x, y):
    p = f'{CACHE}/{Z}_{x}_{y}.png'
    if not os.path.exists(p):
        u = f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{Z}/{x}/{y}.png'
        open(p, 'wb').write(urllib.request.urlopen(u, timeout=60).read())
    a = np.asarray(Image.open(p).convert('RGB')).astype(np.float32)
    return a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768
def txy(lon, lat):
    n = 2 ** Z; lat = max(-85, min(85, lat))
    return (lon + 180) / 360 * n, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n

def grid(w, s, e, n):
    x0, y0 = txy(w, n); x1, y1 = txy(e, s)
    X0, Y0, X1, Y1 = int(x0), int(y0), int(x1), int(y1)
    G = np.zeros(((Y1 - Y0 + 1) * 256, (X1 - X0 + 1) * 256), np.float32)
    for ty in range(Y0, Y1 + 1):
        for tx in range(X0, X1 + 1):
            G[(ty - Y0) * 256:(ty - Y0 + 1) * 256, (tx - X0) * 256:(tx - X0 + 1) * 256] = tile(tx % 2 ** Z, ty)
    return G, X0, Y0

def main(src):
    coast = json.load(open(src))['features']
    rows = list(csv.DictReader(open(root / 'data' / 'coasts.csv')))
    # range cores, for families
    RG = json.loads((root / 'data' / 'ranges.json').read_text())
    rcores = []
    for r in RG:
        if r[2] < 5 or not (r[6] if len(r) > 6 else []): rcores.append(None); continue
        rcores.append(unary_union([Polygon([(rg[i], rg[i + 1]) for i in range(0, len(rg), 2)]).buffer(0) for rg in r[6]]))
    out = []
    for ci, row in enumerate(rows):
        w, s, e, n = (float(row[k]) for k in 'wsen')
        lat0, lon0 = (s + n) / 2, (w + e) / 2
        rise = float(row.get('rise') or RISE)   # a lower bar for short, steep coasts the zoom-6 tiles flatten (Faroes, Table Mountain)
        kx, ky = math.cos(math.radians(lat0)) * 111.32, 110.57   # km per degree, local
        fwd = lambda x, y, z=None: ((x - lon0) * kx, (y - lat0) * ky)
        back = lambda x, y, z=None: (x / kx + lon0, y / ky + lat0)
        G, X0, Y0 = grid(w - 0.5, s - 0.3, e + 0.5, n + 0.3)
        # land within ~12 km: max elevation, sea counted as 0. Pixel size varies with latitude; use the box's middle.
        px_km = 40075 * math.cos(math.radians(lat0)) / (2 ** Z * 256)
        k = max(3, int(round(12 / px_km)) | 1)
        top = ndimage.maximum_filter(np.maximum(G, 0), size=k)
        bb = box(w, s, e, n)
        if row.get('area'):   # an outline instead of the box, where boxes overlap (Greenland vs Baffin and Iceland)
            v = [float(x) for x in row['area'].split()]; bb = Polygon(list(zip(v[0::2], v[1::2])))
        keep = []
        for f in coast:
            ln = LineString(f['geometry']['coordinates'])
            if not ln.intersects(bb): continue
            part = ln.intersection(bb)
            parts = [part] if part.geom_type == 'LineString' else list(getattr(part, 'geoms', []))
            for p in parts:
                if p.geom_type != 'LineString' or p.length == 0: continue
                L = transform(fwd, p); steps = max(2, int(L.length / 2))
                run = []
                for j in range(steps + 1):
                    q = transform(back, L.interpolate(j / steps, normalized=True))
                    tx, ty = txy(q.x, q.y); px, py = int((tx - X0) * 256), int((ty - Y0) * 256)
                    hi = 0 <= py < top.shape[0] and 0 <= px < top.shape[1] and top[py, px] >= rise
                    if hi: run.append(transform(fwd, q))
                    elif len(run) > 1: keep.append(LineString([(a.x, a.y) for a in run])); run = []
                    else: run = []
                if len(run) > 1: keep.append(LineString([(a.x, a.y) for a in run]))
        if not keep: print(f'{row["name"]}: no dramatic coast'); continue
        band = unary_union([k.buffer(BAND + 12, resolution=4) for k in keep]).buffer(-12, resolution=4)   # close gaps
        polys = [band] if band.geom_type == 'Polygon' else list(band.geoms)
        mink = 150 if row.get('rise') else MIN_KM2   # short coasts: keep their small pieces
        polys = [p for p in polys if p.area >= mink]
        if not polys: print(f'{row["name"]}: dramatic stretches too small'); continue
        polys = [p.simplify(2, preserve_topology=True) for p in polys]
        polys = [Polygon(p.exterior, [h for h in p.interiors if Polygon(h).area >= mink]) for p in polys]
        area = sum(p.area for p in polys)
        ll = [transform(back, p) for p in polys]
        flat = lambda ring: [v for x, y in ring.coords for v in (round(x, 3), round(y, 3))]
        recs = [[flat(p.exterior)] + [flat(h) for h in p.interiors] for p in ll]
        xs = [c for p in ll for c in p.exterior.xy[0]]; ys = [c for p in ll for c in p.exterior.xy[1]]
        u = unary_union(ll)
        fam = 1000 + ci; why = ''
        for ri, rc in enumerate(rcores):
            if rc is None: continue
            if not rc.intersects(u): continue
            share = rc.intersection(u).area / u.area
            if share > 0.25: fam = RG[ri][3]; why = f' family of {RG[ri][0]} ({share:.0%} inside)'; break
        reps = [x.strip() for x in row['replaces'].split(';') if x.strip()]
        out.append([row['name'], row['region'], int(row['rating']), fam,
                    [round(min(xs), 3), round(min(ys), 3), round(max(xs), 3), round(max(ys), 3)], reps, recs])
        print(f'{row["name"]}: {len(recs)} pieces, {area:,.0f} km2, {sum(len(r) for p in recs for r in p) // 2} points{why}')
    dst = root / 'data' / 'coasts.json'
    dst.write_text(json.dumps(out, separators=(',', ':')) + '\n')
    print(dst, dst.stat().st_size, 'bytes')

main(sys.argv[1])
