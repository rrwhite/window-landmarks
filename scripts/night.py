"""Night brightness for city rows from NASA Black Marble (VNP46A4, yearly composite).

    EARTHDATA_TOKEN=... python3 scripts/night.py [year]     # default 2025
    pip install h5py fsspec aiohttp numpy

Reads only the pixels around each city straight from LAADS with HTTP range requests (no full
tile downloads). For every `city` row it sums snow-free all-angle radiance (nW/cm2/sr) inside a
15 km radius and writes data/night.csv: name, region, lat, lon, radiance_sum, night (1 to 10).

night = clamp(round(3 * log10(radiance_sum) - 7), 1, 10). Fixed formula, not a percentile, so
scores don't shift when rows are added. Black Marble is NASA data: public domain.
"""
import csv, json, math, os, pathlib, sys, threading, urllib.request
from concurrent.futures import ThreadPoolExecutor
import numpy as np, fsspec, h5py

ROOT = pathlib.Path(__file__).resolve().parent.parent
YEAR = sys.argv[1] if len(sys.argv) > 1 else '2025'
TOK = os.environ['EARTHDATA_TOKEN']
H = {'Authorization': 'Bearer ' + TOK}
DS = 'HDFEOS/GRIDS/VIIRS_Grid_DNB_2d/Data Fields/AllAngle_Composite_Snow_Free'
R_KM = 15
PX = 240  # pixels per degree (15 arc-seconds)

listing = json.load(urllib.request.urlopen(urllib.request.Request(
    f'https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/5200/VNP46A4/{YEAR}/001.json', headers=H)))
links = {x['name'].split('.')[2]: x['downloadsLink'] for x in listing['content']}
fs = fsspec.filesystem('https', headers=H, block_size=2**18)
cache, lock = {}, threading.Lock()

def tile(hv):
    with lock:
        if hv not in cache:
            cache[hv] = h5py.File(fs.open(links[hv], 'rb'), 'r')[DS] if hv in links else None
        return cache[hv]

def radiance(lat, lon):
    h, v = int((lon + 180) // 10), int((90 - lat) // 10)
    ds = tile(f'h{h:02d}v{v:02d}')
    if ds is None: return 0.0
    r0, c0 = (90 - v * 10 - lat) * PX, (lon - (h * 10 - 180)) * PX
    dr = R_KM / 111.32 * PX; dc = dr / max(math.cos(math.radians(lat)), 0.1)
    rs, re_ = max(0, int(r0 - dr)), min(2400, int(r0 + dr) + 1)
    cs, ce = max(0, int(c0 - dc)), min(2400, int(c0 + dc) + 1)
    a = ds[rs:re_, cs:ce].astype('float64'); a[a < 0] = 0
    yy, xx = np.mgrid[rs:re_, cs:ce]
    a[((yy - r0) / dr) ** 2 + ((xx - c0) / dc) ** 2 > 1] = 0
    return float(a.sum())

def score(s): return max(1, min(10, round(3 * math.log10(s) - 7))) if s > 0 else 1

rows = [r for r in csv.DictReader(open(ROOT / 'data' / 'landmarks.csv', newline='', encoding='utf-8')) if r['kind'] == 'city']
with ThreadPoolExecutor(8) as ex:
    sums = list(ex.map(lambda r: radiance(float(r['lat']), float(r['lon'])), rows))
with open(ROOT / 'data' / 'night.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f, lineterminator='\n'); w.writerow(['name', 'region', 'lat', 'lon', 'radiance_sum', 'night'])
    for r, s in zip(rows, sums): w.writerow([r['name'], r['region'], r['lat'], r['lon'], round(s), score(s)])
print(len(rows), 'cities ->', ROOT / 'data' / 'night.csv')
