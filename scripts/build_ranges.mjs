// Build data/ranges.json: mountain ranges as areas (2026-10-31, Rich over the Canadian Rockies:
// "the range itself is the landmark", not a count of its peaks).
// Outlines: Natural Earth 10m geography regions, class Range/mtn (public domain), github.com/nvkelso/natural-earth-vector
// geojson/ne_10m_geography_regions_polys.geojson. Names, regions and ratings: data/ranges.csv (ours; rating 0-4 = not scored).
//   node scripts/build_ranges.mjs path/to/ne_10m_geography_regions_polys.geojson && python3 scripts/build_range_cores.py
// The app (rrwhite/window-seat) imports data/ranges.json with tools/build_areas.py.
// Record: [name, region, rating, family, [w, s, e, n], rings]. rings: outer rings as flat [lon, lat, lon, lat, ...] (holes
// dropped). family: ranges that sit inside one another share it, and a route counts only the best of a family per side.
import fs from 'fs';
import path from 'path';
const root = path.join(path.dirname(new URL(import.meta.url).pathname), '..');
const src = process.argv[2]; if (!src) { console.log('usage: node scripts/build_ranges.mjs ne_10m_geography_regions_polys.geojson'); process.exit(1); }
const csv = fs.readFileSync(path.join(root, 'data', 'ranges.csv'), 'utf8').trim().split('\n').slice(1).map((l) => {
  const out = []; let cur = '', q = false;
  for (const ch of l) { if (ch === '"') q = !q; else if (ch === ',' && !q) { out.push(cur); cur = ''; } else cur += ch; }
  out.push(cur); return out; });
const R = new Map(csv.map(([id, , name, region, rating]) => [id, { name, region, rating: +rating }]));
const g = JSON.parse(fs.readFileSync(src, 'utf8'));
const inRing = (x, y, r) => { let c = false; for (let i = 0, j = r.length - 2; i < r.length; j = i, i += 2) { const xi = r[i], yi = r[i + 1], xj = r[j], yj = r[j + 1]; if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) c = !c; } return c; };
const rows = [];
for (const f of g.features) {
  if (f.properties.FEATURECLA !== 'Range/mtn') continue;
  const r = R.get(String(f.properties.NE_ID)); if (!r) { console.log('not in data/ranges.csv: ' + f.properties.NAME); process.exit(1); }
  if (r.rating < 5) continue;
  const polys = f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates;
  const rings = polys.map((p) => p[0].flatMap(([x, y]) => [+x.toFixed(3), +y.toFixed(3)]));
  const xs = rings.flatMap((rg) => rg.filter((_, i) => i % 2 === 0)), ys = rings.flatMap((rg) => rg.filter((_, i) => i % 2 === 1));
  rows.push({ ...r, bbox: [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)].map((v) => +v.toFixed(3)), rings });
}
// families: a range with most of its outline inside another joins that one's family
const fam = rows.map((_, i) => i), find = (i) => (fam[i] === i ? i : (fam[i] = find(fam[i])));
for (let a = 0; a < rows.length; a++) for (let b = 0; b < rows.length; b++) {
  if (a === b) continue;
  const pts = rows[a].rings.flatMap((rg) => rg.flatMap((v, i) => (i % 2 ? [] : [[v, rg[i + 1]]])));
  const inside = pts.filter(([x, y]) => rows[b].rings.some((rg) => inRing(x, y, rg))).length;
  if (inside / pts.length > 0.5) { fam[find(a)] = find(b); console.log(`family: ${rows[a].name} inside ${rows[b].name}`); }
}
const out = rows.map((r, i) => [r.name, r.region, r.rating, find(i), r.bbox, r.rings]);
fs.writeFileSync(path.join(root, 'data', 'ranges.json'), JSON.stringify(out) + '\n');
