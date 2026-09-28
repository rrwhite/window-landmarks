import json
from shapely.geometry import shape, Point
from shapely.strtree import STRtree
SHORT={'United States of America':'USA','United Kingdom':'UK'}
def load(fn, keyf):
    fs=json.load(open(fn))['features']; geoms=[]; names=[]
    for f in fs:
        try: g=shape(f['geometry'])
        except Exception: continue
        geoms.append(g); names.append(keyf(f['properties']))
    return STRtree(geoms), geoms, names
adm=load('ne_10m_admin_1_states_provinces.geojson', lambda p:(p.get('adm0_a3'),p.get('name')))
cty=load('ne_50m_admin_0_countries.geojson', lambda p:p.get('NAME_LONG') or p.get('NAME'))
def hit(t,pt,maxd=0.0):
    tree,geoms,names=t
    for i in tree.query(pt):
        if geoms[i].contains(pt): return names[i]
    if maxd:
        i=tree.nearest(pt)
        if geoms[i].distance(pt)<maxd: return names[i]
    return None
def region(la,lo):
    pt=Point(lo,la)
    a=hit(adm,pt,0.3)
    if a and a[0] in ('USA','CAN','AUS','MEX','BRA','IND','CHN','RUS'): return a[1]
    c=hit(cty,pt,1.0)
    return SHORT.get(c,c) or ''
p='../data/landmarks.json'
d=json.loads(open(p).read()[15:-2])
for x in d: x[5:]=[region(x[1],x[2])]
open(p,'w').write('export default '+json.dumps(d,separators=(',',':'),ensure_ascii=False)+';\n')
for n in ['Wheeler Peak','Mount Rainier','Lake Tahoe','Chicago','Greenland ice sheet (east coast)','Matterhorn','Mount Robson','Mont Blanc','Florida Keys','Bahamas banks']:
    print(n,[x[5] for x in d if x[0]==n])
print(sum(1 for x in d if not x[5]),'blank of',len(d))
