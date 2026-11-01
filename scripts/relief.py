"""Relief: how far each peak and range row rises above the land around it (Rich, 2026-11-01).
Writes data/relief.csv: name, region, lat, lon, summit_m, relief_m, for every row of kind peak or range.

summit_m = the highest point within 4 km of the row's point. relief_m = summit_m minus the 10th percentile of
elevation within 20 km (about 12 miles), sea level as the floor. It stands in for topographic prominence: it is what
you see from a plane, a mountain standing up out of its surroundings. Elevation: AWS Terrain Tiles (Mapzen terrarium),
zoom 10, about 150 m a pixel at the equator, cached in /tmp/terrain10. Rows past 84 degrees (beyond the tiles) are left blank: unknown. Sharp spires read low at that size (Fitz Roy
3,405 m measures about 2,840 m), so relief errs low: anything that passes really does stand out.

The app uses it for standalone peaks (README, "Judgment calls"): a peak or range row rated under 9 that no scored range
or coast covers counts only if relief_m >= 1500. Rerun after adding or moving a peak or range row:

    python3 scripts/relief.py
"""
import csv, math, os, pathlib, urllib.request, concurrent.futures as cf
from PIL import Image

Z, CACHE = 10, '/tmp/terrain10'
d = pathlib.Path(__file__).resolve().parent.parent / 'data'
os.makedirs(CACHE, exist_ok=True)

def tile(x, y):
    p = f'{CACHE}/{x}_{y}.png'
    for _ in range(3):
        if os.path.exists(p):
            try: return Image.open(p).convert('RGB').load()
            except Exception: os.remove(p)
        try: open(p, 'wb').write(urllib.request.urlopen(f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{Z}/{x}/{y}.png', timeout=30).read())
        except Exception: pass
    raise RuntimeError(f'tile {x},{y}')

def measure(r):
    lat, lon = float(r['lat']), float(r['lon'])
    blank = {'name': r['name'], 'region': r['region'], 'lat': r['lat'], 'lon': r['lon'], 'summit_m': '', 'relief_m': ''}
    if abs(lat) > 84: return blank   # past the tiles' edge (Mercator): unknown, which the app treats as passing
    n = 2 ** Z; mpp = 156543.03 * math.cos(math.radians(lat)) / n
    px = (lon + 180) / 360 * n * 256
    py = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n * 256
    rp = 20000 / mpp; T = {}; top = -1e9; ring = []
    for i in range(int(px - rp), int(px + rp) + 1):
        for j in range(int(py - rp), int(py + rp) + 1):
            dk = math.hypot(i - px, j - py) * mpp / 1000
            if dk > 20 or j < 0 or j >= n * 256: continue
            k = ((i // 256) % n, j // 256)
            if k not in T: T[k] = tile(*k)
            R, G, B = T[k][i % 256, j % 256]; e = R * 256 + G + B / 256 - 32768
            ring.append(e)
            if dk <= 4: top = max(top, e)
    if not ring or top < -1e8: return blank
    ring.sort(); base = max(0, ring[int(len(ring) * 0.1)])
    return {'name': r['name'], 'region': r['region'], 'lat': r['lat'], 'lon': r['lon'], 'summit_m': round(top), 'relief_m': round(top - base)}

rows = [r for r in csv.DictReader(open(d / 'landmarks.csv', encoding='utf-8')) if r['kind'] in ('peak', 'range')]
with cf.ThreadPoolExecutor(12) as ex: out = list(ex.map(measure, rows))
with open(d / 'relief.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['name', 'region', 'lat', 'lon', 'summit_m', 'relief_m'], lineterminator='\n')
    w.writeheader(); w.writerows(sorted(out, key=lambda x: (x['name'], x['region'])))
print(len(out), 'rows ->', d / 'relief.csv', '|', sum(1 for x in out if x['relief_m'] != '' and x['relief_m'] < 1500), 'under 1,500 m |', sum(1 for x in out if x['relief_m'] == ''), 'unknown')
