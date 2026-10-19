"""Check data/landmarks.csv before it's merged. Run: python3 scripts/validate.py"""
import csv, sys, pathlib
KINDS = {'peak','range','volcano','glacier','lake','coast','canyon','island','park','desert','landmark','feature','city',
         'stadium','campus','office','airport','bridge','tower','port','themepark','racetrack','windfarm','mine','dam'}
HEAD = ['name','short','lat','lon','kind','rating','region','max_alt','size_m']
p = pathlib.Path(__file__).resolve().parent.parent / 'data' / 'landmarks.csv'
errs, seen = [], {}
with open(p, newline='', encoding='utf-8') as f:
    r = csv.DictReader(f)
    if r.fieldnames != HEAD: sys.exit(f'Header must be {",".join(HEAD)} (got {r.fieldnames})')
    for i, row in enumerate(r, start=2):
        n = row['name'].strip()
        if not n: errs.append(f'line {i}: empty name')
        s = row['short']
        if s and (s != s.strip() or len(s) >= len(n)): errs.append(f'line {i}: {n}: short must be shorter than name, no edge spaces')
        if row['kind'] == 'airport' and s and not (len(s) == 3 and s.isupper()) and s != s.title(): errs.append(f'line {i}: {n}: airport short should be its IATA code')
        try:
            la, lo = float(row['lat']), float(row['lon'])
            if not (-90 <= la <= 90 and -180 <= lo <= 180): errs.append(f'line {i}: {n}: lat/lon out of range')
        except ValueError: errs.append(f'line {i}: {n}: lat/lon not numbers'); continue
        if row['kind'] not in KINDS: errs.append(f'line {i}: {n}: kind "{row["kind"]}" not one of {sorted(KINDS)}')
        if not row['rating'].isdigit() or not 1 <= int(row['rating']) <= 10: errs.append(f'line {i}: {n}: rating must be a whole number 1 to 10')
        m = row['max_alt'].strip()
        if m and (not m.isdigit() or not 1000 <= int(m) <= 40000): errs.append(f'line {i}: {n}: max_alt must be blank or feet between 1000 and 40000')
        z = row['size_m'].strip()
        if z and (not z.isdigit() or not 20 <= int(z) <= 50000): errs.append(f'line {i}: {n}: size_m must be blank or meters between 20 and 50000')
        if z and not m: errs.append(f'line {i}: {n}: size_m only applies to low landmarks (rows with max_alt)')
        key = (n.lower(), round(la, 2), round(lo, 2))
        if key in seen: errs.append(f'line {i}: {n}: duplicate of line {seen[key]}')
        seen[key] = i
# data/blurbs.csv: one card blurb per landmark and per night_only row, keyed on name,region,lat,lon
import re
d = p.parent
keys = {(x['name'], x['region'], x['lat'], x['lon']) for x in csv.DictReader(open(d / 'landmarks.csv', encoding='utf-8'))}
keys |= {(x['name'], x['region'], x['lat'], x['lon']) for x in csv.DictReader(open(d / 'night.csv', encoding='utf-8')) if x['night_only'] == '1'}
METRIC = re.compile(r'\d\s*(m|km|meters?|metres?|kilometers?|kilometres?|km2|hectares?)\b')
nb = 0
with open(d / 'blurbs.csv', newline='', encoding='utf-8') as f:
    r = csv.DictReader(f)
    if r.fieldnames != ['name', 'region', 'lat', 'lon', 'blurb']: sys.exit('blurbs.csv header must be name,region,lat,lon,blurb')
    got = set()
    for i, row in enumerate(r, start=2):
        k = (row['name'], row['region'], row['lat'], row['lon']); t = row['blurb']; nb += 1
        if k not in keys: errs.append(f'blurbs line {i}: {k[0]}: no matching landmark (name,region,lat,lon must match exactly)')
        if k in got: errs.append(f'blurbs line {i}: {k[0]}: duplicate')
        got.add(k)
        w = len(t.split())
        if not 10 <= w <= 55: errs.append(f'blurbs line {i}: {k[0]}: {w} words (10 to 55)')
        if '\u2014' in t or '\u2013' in t or ' - ' in t: errs.append(f'blurbs line {i}: {k[0]}: no dashes as punctuation')
        if METRIC.search(t): errs.append(f'blurbs line {i}: {k[0]}: feet and miles only')
    for k in sorted(keys - got): errs.append(f'blurbs.csv: missing blurb for {k[0]} ({k[1]})')
if errs: print('\n'.join(errs)); sys.exit(1)
print(f'OK: {len(seen)} landmarks, {nb} blurbs')
