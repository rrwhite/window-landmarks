"""Check data/sights.csv before it's merged. Run: python3 scripts/validate.py"""
import csv, sys, pathlib
KINDS = {'peak','range','volcano','glacier','lake','coast','canyon','island','park','desert','landmark','feature','city',
         'stadium','campus','airport','bridge','tower','port','themepark','racetrack','windfarm','mine','dam'}
p = pathlib.Path(__file__).resolve().parent.parent / 'data' / 'sights.csv'
errs, seen = [], {}
with open(p, newline='', encoding='utf-8') as f:
    r = csv.DictReader(f)
    if r.fieldnames != ['name','lat','lon','kind','rating','region','max_alt']:
        sys.exit(f'Header must be name,lat,lon,kind,rating,region,max_alt (got {r.fieldnames})')
    for i, row in enumerate(r, start=2):
        n = row['name'].strip()
        if not n: errs.append(f'line {i}: empty name')
        try:
            la, lo = float(row['lat']), float(row['lon'])
            if not (-90 <= la <= 90 and -180 <= lo <= 180): errs.append(f'line {i}: {n}: lat/lon out of range')
        except ValueError: errs.append(f'line {i}: {n}: lat/lon not numbers'); continue
        if row['kind'] not in KINDS: errs.append(f'line {i}: {n}: kind "{row["kind"]}" not one of {sorted(KINDS)}')
        if not row['rating'].isdigit() or not 1 <= int(row['rating']) <= 10: errs.append(f'line {i}: {n}: rating must be a whole number 1 to 10')
        m = row['max_alt'].strip()
        if m and (not m.isdigit() or not 1000 <= int(m) <= 40000): errs.append(f'line {i}: {n}: max_alt must be blank or feet between 1000 and 40000')
        key = (n.lower(), round(la, 2), round(lo, 2))
        if key in seen: errs.append(f'line {i}: {n}: duplicate of line {seen[key]}')
        seen[key] = i
if errs: print('\n'.join(errs)); sys.exit(1)
print(f'OK: {len(seen)} sights')
