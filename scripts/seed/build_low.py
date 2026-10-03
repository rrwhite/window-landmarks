# Build low-altitude sights + more cities from Wikidata dumps (stadiums/cities/airports/low/ind .json).
import json, csv, math, re, sys
sys.path.insert(0, '/home/claude/build')
W = '/home/claude/build/'
def pt(x):
    m = re.match(r'Point\(([-\d.eE]+) ([-\d.eE]+)\)', x['c']['value']); return float(m.group(2)), float(m.group(1))
def num(x, k):
    try: return float(x[k]['value'])
    except Exception: return None
def qid(x): return x['i']['value'].rsplit('/', 1)[1]
def T(x): return x['t']['value'].rsplit('/', 1)[1] if 't' in x else None
rows = {}  # qid -> [name, lat, lon, kind, rating, max_alt, sl]
GONE = set(json.load(open(W + 'gone.json')))
def add(x, kind, rating, cap):
    if rating is None or rating < 1: return
    if x['c']['value'].startswith('<'): return  # another planet
    q = qid(x); la, lo = pt(x); n = x['l']['value']; sl = int(x['sl']['value'])
    if re.match(r'^Q\d+$', n) or q in GONE or re.search(r'(?i)\b(proposed|planned|former|demolished|under construction)\b', n): return
    if q in rows and rows[q][4] >= rating: return
    rows[q] = [n, round(la, 4), round(lo, 4), kind, int(rating), cap, sl]

# stadiums: by capacity
for x in json.load(open(W + 'stadiums.json')):
    cap = num(x, 'cap'); sl = int(x['sl']['value'])
    if sl < 8 and cap < 60000: continue
    r = 5 if cap >= 70000 else 4 if cap >= 50000 else 3
    if sl >= 60: r += 1
    add(x, 'stadium', min(r, 6), 15000)
# airports: busy ones show planes moving
for x in json.load(open(W + 'airports.json')):
    sl = int(x['sl']['value']); r = 5 if sl >= 90 else 4 if sl >= 55 else 3
    add(x, 'airport', r, 15000)
UNI = {'Q3918', 'Q875538', 'Q902104'}; BR = {'Q12280', 'Q12570', 'Q158218', 'Q537127', 'Q158555'}
LOWJ = json.load(open(W + 'low.json'))
MINH = {}  # heights come in mixed units (m and ft); the smallest value is the metres one
for x in LOWJ:
    h = num(x, 'h')
    if h: MINH[qid(x)] = min(h, MINH.get(qid(x), 1e9))
for x in LOWJ:
    t = T(x); sl = int(x['sl']['value']); h = MINH.get(qid(x))
    if t in UNI:
        if sl >= 70: add(x, 'campus', 4 if sl >= 160 else 3, 10000)
    elif t in BR:
        if sl >= 15: add(x, 'bridge', 6 if sl >= 70 else 5 if sl >= 45 else 4 if sl >= 25 else 3, 15000)
    elif t == 'Q11303':  # skyscraper
        if h and h >= 200: add(x, 'tower', 5 if h >= 400 and sl >= 40 else 4 if h >= 300 and sl >= 20 else 3, 15000)
    elif t in ('Q12518', 'Q11166728'):
        if sl >= 30 or (h and h >= 250): add(x, 'tower', 5 if (h or 0) >= 450 and sl >= 40 else 4 if (h or 0) >= 300 and sl >= 20 else 3, 15000)
    elif t == 'Q12323':
        if sl >= 12: add(x, 'dam', 5 if sl >= 45 else 4 if sl >= 22 else 3, 20000)
    elif t == 'Q44782':
        if sl >= 15: add(x, 'port', 4 if sl >= 35 else 3, 15000)
    elif t in ('Q194195', 'Q2416723'):
        if sl >= 15: add(x, 'themepark', 4 if sl >= 40 else 3, 12000)
    elif t in ('Q1777138', 'Q2338524'):
        if sl >= 18: add(x, 'racetrack', 4 if sl >= 40 else 3, 12000)
    elif t == 'Q194356':
        add(x, 'windfarm', 4, 20000)
for x in json.load(open(W + 'ind.json')):
    t = T(x); sl = int(x['sl']['value'])
    if t == 'Q194356': add(x, 'windfarm', 5 if sl >= 8 else 4, 20000)
    elif t == 'Q820477' and sl >= 8: add(x, 'mine', 5 if sl >= 20 else 4, 20000)
    elif t == 'Q188040' and sl >= 4: add(x, 'mine', 3, 15000)
for x in json.load(open(W + 'extra.json')):
    t = T(x); sl = int(x['sl']['value'])
    if t in ('Q1440300', 'Q1068842'): add(x, 'tower', 5 if sl >= 60 else 4, 15000)
    elif t in ('Q179700', 'Q4989906'): add(x, 'landmark', 5 if sl >= 80 else 4, 12000)
    elif t == 'Q641226': add(x, 'stadium', 3, 15000)
    elif t in ('Q16560', 'Q23413'): add(x, 'landmark', 4 if sl >= 80 else 3, 10000)
low = list(rows.values())

# cities: population tiers; bigger ones already in the set keep their rating
cities = {}
for x in json.load(open(W + 'cities.json')):
    q = qid(x); pop = num(x, 'pop') or 0; la, lo = pt(x); n = x['l']['value']
    if q in cities and cities[q][6] >= pop: continue
    r = 5 if pop >= 1e6 else 4 if pop >= 4e5 else 3  # by size only; skyline ratings stay hand-made
    cities[q] = [n, round(la, 4), round(lo, 4), 'city', r, 0 if pop >= 1e6 else 25000, pop]
json.dump({'low': low, 'cities': list(cities.values())}, open(W + 'new_raw.json', 'w'))
print(len(low), 'low;', len(cities), 'cities')
import collections; print(collections.Counter(r[3] for r in low))
