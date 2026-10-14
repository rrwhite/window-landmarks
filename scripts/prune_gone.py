"""Remove low-altitude sights that no longer exist or can't be seen from the air.

Built 2026-10-13 from Wikidata: every low sight's item checked for "dissolved, abolished or
demolished" (P576) or "state of use: demolished" (P5817 = Q56556915), then hand-reviewed.
Open-pit mines and Tempelhof (now a park, still an obvious airfield) are kept on purpose.
Underground sights (caves, cellars, deep mines) go regardless.

    python3 scripts/prune_gone.py
"""
import csv, pathlib, re
P = pathlib.Path(__file__).resolve().parent.parent / 'data' / 'sights.csv'
GONE = {
    'Arsenal Stadium', 'Ayresome Park', 'BJK İnönü Stadium', 'Boleyn Ground', 'Bökelbergstadion', 'Camp de Les Corts',
    'Central Dynamo Stadium', 'Charmilles Stadium', 'Estádio José Alvalade (1956)', 'Estádio das Antas', 'Ferenc Puskás Stadium',
    'Kirov Stadium', 'Lancaster Park', 'Maine Road', 'Manor Ground, Plumstead', 'RCA Dome', 'Stadio Partenopeo',
    'Stadion der Weltjugend', 'Stadionul Național', 'Station Road', 'Tehelné pole', 'Victoria Ground', 'Wankdorf Stadium',
    'White Hart Lane', 'Francis Scott Key Bridge', 'Polcevera Viaduct', 'Kakhovka Dam', 'Old Phu Quoc Airport',
    'Cuxhaven offshore wind turbine test site', 'Eemmeerdijk Wind Farm', 'Zelenogradsk wind farm',
    'Coal mine Arthur de Buyer', 'Kongsberg Silverworks', 'Ytterby mine', 'Cave di Cusa',
}
UNDERGROUND = re.compile(r'(?i)\b(caves?|cellars?|cellar system|grotto|catacombs?)\b')
rows = list(csv.DictReader(open(P, newline='', encoding='utf-8')))
keep = [r for r in rows if not (r['max_alt'] and (r['name'] in GONE or UNDERGROUND.search(r['name'])))]
for r in rows:
    if r not in keep: print('drop', r['name'], r['kind'], r['region'])
with open(P, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator='\n'); w.writeheader(); w.writerows(keep)
print(f'{len(rows)} -> {len(keep)} sights')
