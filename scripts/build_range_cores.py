"""Add each range's core to data/ranges.json: where its mountains actually are, not the whole
Natural Earth outline (Rich, 2026-10-31: "a really tight band only where there really are dramatic peaks"; the Rockies
outline covers half of Wyoming's basins).

Elevation: AWS Terrain Tiles (Mapzen terrarium, zoom 6, about 2.4 km a pixel at the equator), cached in /tmp/terrain.
Sources: USGS 3DEP and SRTM (public domain), GMTED2010, ETOPO1, Canadian CDEM (Open Government Licence - Canada),
EU-DEM, LINZ (CC BY 4.0) and others; credited on /credits. No OpenStreetMap data.

Inside a range's outline, a pixel is core when its smoothed summit elevation (max over ~7 km, then blurred) is in the
top 35% of that outline and its local relief (max minus min over ~17 km) is at least 600 m. Speckle is smoothed away,
blobs under ~150 km2 dropped, and the result traced to polygons, rounded and simplified to ~3 km.

    node scripts/build_ranges.mjs ne_10m_geography_regions_polys.geojson && python3 scripts/build_range_cores.py
Record gains index 6: core rings, flat [lon, lat, ...] like the outline. A range with no core keeps [] and is not scored.
"""
import json, math, os, pathlib, urllib.request
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.draw import polygon as skpoly
from skimage.measure import find_contours
from shapely.geometry import Polygon
from shapely.ops import unary_union

Z, CACHE = 6, '/tmp/terrain'
os.makedirs(CACHE, exist_ok=True)
root = pathlib.Path(__file__).resolve().parent.parent
dst = root / 'data' / 'ranges.json'
RG = json.loads(dst.read_text())

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
def lonlat(px, py, X0, Y0):
    n = 2 ** Z; x, y = X0 + px / 256, Y0 + py / 256
    return x / n * 360 - 180, math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))

for r in RG:
    name, region, rating, fam, bb, rings = r[:6]
    pad = 0.3
    x0, y0 = txy(bb[0] - pad, bb[3] + pad); x1, y1 = txy(bb[2] + pad, bb[1] - pad)
    X0, Y0, X1, Y1 = int(x0), int(y0), int(x1), int(y1)
    G = np.zeros(((Y1 - Y0 + 1) * 256, (X1 - X0 + 1) * 256), np.float32)
    for ty in range(Y0, Y1 + 1):
        for tx in range(X0, X1 + 1):
            G[(ty - Y0) * 256:(ty - Y0 + 1) * 256, (tx - X0) * 256:(tx - X0 + 1) * 256] = tile(tx % 2 ** Z, ty)
    M = np.zeros(G.shape, bool)
    for rg in rings:
        pts = [txy(rg[i], rg[i + 1]) for i in range(0, len(rg), 2)]
        rr, cc = skpoly([(p[1] - Y0) * 256 for p in pts], [(p[0] - X0) * 256 for p in pts], G.shape); M[rr, cc] = True
    if M.sum() < 20: r[5:] = [rings, []]; print(f'{name}: outline too small'); continue
    Es = ndimage.gaussian_filter(ndimage.maximum_filter(G, 3), 2)
    rel = ndimage.maximum_filter(G, 7) - ndimage.minimum_filter(G, 7)
    core = M & (Es >= np.percentile(Es[M], 65)) & (rel >= 600)
    core = ndimage.gaussian_filter(core.astype(np.float32), 2.2) > 0.42      # smooth the speckle into shapes
    core = ndimage.binary_fill_holes(core) & ndimage.binary_dilation(M, iterations=2)
    lab, k = ndimage.label(core)
    sizes = ndimage.sum(core, lab, range(1, k + 1)) if k else []
    px_km2 = (40075 / 2 ** Z / 256 * math.cos(math.radians((bb[1] + bb[3]) / 2))) ** 2
    keep = [i + 1 for i, s in enumerate(sizes) if s * px_km2 >= 150]
    polys = []
    for i in keep:
        m = np.pad(lab == i, 1)
        for c in find_contours(m.astype(np.float32), 0.5):
            if len(c) < 4: continue
            pg = Polygon([lonlat(x - 1, y - 1, X0, Y0) for y, x in c])
            if pg.is_valid and pg.area > 0: polys.append(pg)
    u = unary_union(polys).buffer(0.06).buffer(-0.06).simplify(0.03) if polys else None   # rounder, calmer edges
    out = []
    if u is not None and not u.is_empty:
        for g in getattr(u, 'geoms', [u]):
            if g.geom_type != 'Polygon' or g.area < 0.005: continue
            out.append([round(v, 3) for xy in g.exterior.coords for v in xy])
    r[5:] = [rings, out]
    print(f'{name} ({rating}): {len(out)} core shapes, {sum(len(o) for o in out) // 2} points')

dst.write_text(json.dumps(RG, separators=(',', ':')) + '\n')
print(f'{len(RG)} ranges, {dst.stat().st_size // 1024} KB')
