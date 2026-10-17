"""Rebuild data/landmarks.geojson from data/landmarks.csv. Run: python3 scripts/geojson.py"""
import csv, json, pathlib
d = pathlib.Path(__file__).resolve().parent.parent / 'data'
rows = list(csv.DictReader(open(d / 'landmarks.csv', newline='', encoding='utf-8')))
feats = [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [round(float(r['lon']), 4), round(float(r['lat']), 4)]},
          'properties': {'name': r['name'], **({'short': r['short']} if r['short'] else {}), 'kind': r['kind'], 'rating': int(r['rating']),
                         'region': r['region'], **({'max_alt': int(r['max_alt'])} if r['max_alt'] else {}), **({'size_m': int(r['size_m'])} if r['size_m'] else {})}} for r in rows]
json.dump({'type': 'FeatureCollection', 'features': feats}, open(d / 'landmarks.geojson', 'w', encoding='utf-8'), ensure_ascii=False)
print(len(feats), 'landmarks ->', d / 'landmarks.geojson')
