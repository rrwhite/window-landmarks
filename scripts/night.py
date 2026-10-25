"""Night brightness from NASA Black Marble (VNP46A4 yearly composite) -> data/night.csv

    EARTHDATA_TOKEN=... python3 scripts/night.py [year]     # default 2025
    pip install h5py fsspec aiohttp numpy

Reads only the pixels it needs from LAADS with HTTP range requests. For each point it sums
snow-free all-angle radiance (nW/cm2/sr) inside a radius and turns the sum into a 1 to 10 score:

- city rows: 15 km radius, night = round(3 log10(sum) - 7), clamped 1 to 10
- lit low landmarks (airport, port, bridge, tower, landmark, themepark, racetrack): small radius
  (airport and port 3 km, others 1.5 km, towers 1 km), night = round(3 log10(sum) - 6), clamped
  1 to 8; written only when night >= 4, so dark castles and unlit bridges get no night score.
  At 500 m resolution this measures how lit the spot and its surroundings are, not the object.
- stadiums are skipped: their lights are on only during night games.
- NIGHT_ONLY: things you only notice at night (gas flares, lit greenhouses, the Nile ribbon).
  They are not in landmarks.csv; the app adds them as night scenery. Scored like cities.

Columns: name, region, lat, lon, kind, radiance_sum, night, night_only. Join to landmarks.csv on
name, region, lat, lon. Black Marble is NASA data, public domain. The ocean is masked in this
product, so fishing fleets can't be measured and aren't included.
"""
import csv, json, math, os, pathlib, sys, threading, urllib.request
from concurrent.futures import ThreadPoolExecutor
import numpy as np, fsspec, h5py

ROOT = pathlib.Path(__file__).resolve().parent.parent
YEAR = sys.argv[1] if len(sys.argv) > 1 else '2025'
H = {'Authorization': 'Bearer ' + os.environ['EARTHDATA_TOKEN']}
DS = 'HDFEOS/GRIDS/VIIRS_Grid_DNB_2d/Data Fields/AllAngle_Composite_Snow_Free'
PX = 240
RADIUS = {'city': 15, 'airport': 3, 'port': 3, 'bridge': 1.5, 'tower': 1, 'landmark': 1.5, 'themepark': 1.5, 'racetrack': 1.5}
NIGHT_ONLY = [  # name, region, lat, lon, kind, radius_km
    ('Permian Basin gas flares', 'Texas', 31.80, -103.60, 'feature', 25),
    ('Bakken gas flares', 'North Dakota', 47.90, -103.30, 'feature', 25),
    ('South Pars gas field flares', 'Iran', 27.48, 52.60, 'feature', 20),
    ('Niger Delta gas flares', 'Nigeria', 5.00, 6.50, 'feature', 25),
    ('Khanty-Mansiysk oil field flares', 'Khanty-Mansiy', 61.50, 73.50, 'feature', 25),
    ('Westland greenhouses', 'Netherlands', 52.00, 4.25, 'feature', 10),
    ('Nile Valley lights', 'Egypt', 26.50, 31.70, 'feature', 25),
    ('India-Pakistan border lights', 'Rajasthan', 29.50, 73.00, 'feature', 25),
]

listing = json.load(urllib.request.urlopen(urllib.request.Request(
    f'https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/5200/VNP46A4/{YEAR}/001.json', headers=H)))
links = {x['name'].split('.')[2]: x['downloadsLink'] for x in listing['content']}
fs = fsspec.filesystem('https', headers=H, block_size=2**18)
cache, lock = {}, threading.Lock()

def radiance(lat, lon, r_km):
    h, v = int((lon + 180) // 10), int((90 - lat) // 10)
    hv = f'h{h:02d}v{v:02d}'
    with lock:
        if hv not in cache: cache[hv] = h5py.File(fs.open(links[hv], 'rb'), 'r')[DS] if hv in links else None
        ds = cache[hv]
    if ds is None: return 0.0
    r0, c0 = (90 - v * 10 - lat) * PX, (lon - (h * 10 - 180)) * PX
    dr = r_km / 111.32 * PX; dc = dr / max(math.cos(math.radians(lat)), 0.1)
    rs, re_ = max(0, int(r0 - dr)), min(2400, int(r0 + dr) + 1)
    cs, ce = max(0, int(c0 - dc)), min(2400, int(c0 + dc) + 1)
    with lock: a = ds[rs:re_, cs:ce].astype('float64')
    a[a < 0] = 0
    yy, xx = np.mgrid[rs:re_, cs:ce]
    a[((yy - r0) / dr) ** 2 + ((xx - c0) / dc) ** 2 > 1] = 0
    return float(a.sum())

def score(s, kind):
    if s <= 0: return 1
    # Cities cap at 8: brightness is mostly sprawl, so only unique night sights go above (hand-set, see CLAUDE.md)
    if kind == 'city': return max(2, min(8, round(1.8 * math.log10(s) - 2.7)))
    if kind == 'night_only': return max(1, min(10, round(3 * math.log10(s) - 7)))
    return max(1, min(8, round(3 * math.log10(s) - 6)))

rows = [r for r in csv.DictReader(open(ROOT / 'data' / 'landmarks.csv', newline='', encoding='utf-8')) if r['kind'] in RADIUS]
pts = [(r['name'], r['region'], r['lat'], r['lon'], r['kind'], RADIUS[r['kind']], 0) for r in rows]
pts += [(n, g, str(la), str(lo), k, rk, 1) for n, g, la, lo, k, rk in NIGHT_ONLY]
with ThreadPoolExecutor(8) as ex:
    sums = list(ex.map(lambda p: radiance(float(p[2]), float(p[3]), p[5]), pts))
# Hand-set scores for unique night sights (Rich, Oct 2026). Only these go above 8; cities otherwise cap at 8.
OVERRIDE = {'South Pars gas field flares': 10,
    'Las Vegas Strip': 9,
    'Nile Valley lights': 9,
    'Sphere': 8,
    'Manhattan': 8,
    'Hong Kong': 8,
    'Permian Basin gas flares': 8,
    'Bakken gas flares': 8,
    'Khanty-Mansiysk oil field flares': 8,
    'Niger Delta gas flares': 8,
    'Westland greenhouses': 8,
    'India-Pakistan border lights': 8,
    'Palm Jumeirah': 8,
    'Burj Khalifa': 8,
    'Eiffel Tower': 8,
    'Christ the Redeemer': 8}
out = 0
with open(ROOT / 'data' / 'night.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f, lineterminator='\n')
    w.writerow(['name', 'region', 'lat', 'lon', 'kind', 'radiance_sum', 'night', 'night_only'])
    for (n, g, la, lo, k, rk, only), s in zip(pts, sums):
        sc = OVERRIDE.get(n, score(s, 'night_only' if only else k))
        if k != 'city' and not only and sc < 4: continue
        w.writerow([n, g, la, lo, k, round(s), sc, only]); out += 1
print(out, 'rows ->', ROOT / 'data' / 'night.csv')
