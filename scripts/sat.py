"""Satellite check for a candidate. Run: python3 scripts/sat.py NAME LAT LON ZOOM [N]

Stitches an NxN block (default 3x3) of Esri World Imagery tiles around LAT,LON, draws a red
cross on the point and a yellow 1 km scale bar, and saves sat/NAME.jpg (gitignored).
Zoom 14 for ports and big features, 15 for campuses, 16 for buildings and stadiums.
Offset from the cross in pixels times the printed m/px gives the coordinate fix."""
import sys, math, io, os, urllib.request
from PIL import Image, ImageDraw
name, lat, lon, z = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4])
n = int(sys.argv[5]) if len(sys.argv) > 5 else 3
N = 2 ** z
fx = (lon + 180) / 360 * N
fy = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * N
cx, cy = int(fx), int(fy)
h = n // 2
img = Image.new('RGB', (256 * n, 256 * n))
for dx in range(-h, h + 1):
    for dy in range(-h, h + 1):
        u = f'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{cy+dy}/{cx+dx}'
        img.paste(Image.open(io.BytesIO(urllib.request.urlopen(u, timeout=30).read())), ((dx + h) * 256, (dy + h) * 256))
px, py = (fx - cx + h) * 256, (fy - cy + h) * 256
d = ImageDraw.Draw(img)
d.line([(px - 12, py), (px + 12, py)], fill='red', width=2); d.line([(px, py - 12), (px, py + 12)], fill='red', width=2)
mpp = 156543.03 * math.cos(math.radians(lat)) / N
d.line([(10, 256 * n - 15), (10 + 1000 / mpp, 256 * n - 15)], fill='yellow', width=3)  # 1 km scale bar
d = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sat'); os.makedirs(d, exist_ok=True)
out = os.path.join(d, f'{name}.jpg')
img.save(out, quality=80); print(out, f'{mpp:.1f} m/px')
