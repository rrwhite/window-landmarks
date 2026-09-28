import json,re,math,geonamescache
from landmarks_src import L as CUR
def ll(r):
    m=re.match(r'Point\(([-\d.eE]+) ([-\d.eE]+)\)',r['coord']['value']); return (float(m[2]),float(m[1])) if m else None
def hav(a,b):
    p1,p2=math.radians(a[0]),math.radians(b[0]); dl=math.radians(b[1]-a[1]); dp=p2-p1
    x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2; return 6371*2*math.asin(min(1,math.sqrt(x)))
TEN={"Grand Canyon":10,"Mount Rainier":10,"Denali":10,"Mount Everest":10,"Matterhorn":10,"Mont Blanc":10,"Greenland ice sheet (east coast)":10,"Greenland ice sheet (west coast)":10,"Mount Fuji":10,"Kilimanjaro":10,"K2":10,"Kangchenjunga":10,"Mount Logan":10,
"Hubbard Glacier":9,"Malaspina Glacier":9,"Yosemite Valley / Half Dome":9,"Mount Shasta":9,"Mount Hood":9,"Crater Lake":9,"Aconcagua":9,"Mount Cook / Southern Alps":9,"Eiger / Jungfrau":9,"Aletsch Glacier":9,"Dolomites":9,"Vatnajokull":9,"Norwegian fjords (Sognefjord)":9,"Mount St. Helens":9,"Mount Robson":9,"Columbia Icefield":9,"Lake Louise / Banff peaks":9,"Grand Teton":9,"Kluane Icefields":9,"Mount Saint Elias":9,"Baffin Island fjords":9,"Popocatepetl":9,"Pico de Orizaba":9,"Mount Etna":9,"Mount Ararat":9,"Mount Elbrus":9,"Kamchatka volcanoes":9,"Nanga Parbat":9,
"Lake Tahoe":8,"Manhattan skyline":8,"Uluru":8,"Monument Valley":8,"Mount Baker":8,"Lake Powell":8,"Glacier National Park":8,"Teide":8,"Santorini caldera":8,"Ha Long Bay":8,"Great Barrier Reef":8,"Manicouagan Crater":8,"Mauna Kea":8,"Haleakala":8,"Na Pali Coast":8,"Bahamas banks":8,"Mount Adams":8,"Lofoten":8,"Mount Whitney":8,"Mount Waddington":8,"Mount Assiniboine":8,
"Golden Gate Bridge":7,"Great Salt Lake":7,"Death Valley":7,"Yellowstone Lake":7,"Hong Kong harbor":7,"Sydney Harbour":7,"Niagara Falls":7,"Florida Keys":7,"Mount Jefferson":7,"Three Sisters":7,"Mono Lake":7,"Bryce Canyon":7,"Zion Canyon":7,"Canyonlands":7,
"Palm Jumeirah":6,"Diamond Head / Waikiki":6,"Everglades":5}
OLD={3:8,2:6,1:4}
out=[]
for n,la,lo,k,v in CUR:
    if n.startswith('Crater of Mt Shasta'): n='Medicine Lake Volcano'
    out.append([n,la,lo,k,TEN.get(n,OLD[v])])
cur=list(out)
STOP={'mount','mountain','national','park','lake','glacier','range','the','peak','volcano','canyon','island','islands','river','coast','sound','bay'}
def words(s): return {w for w in re.findall(r'[a-z]+',s.lower()) if len(w)>=4 and w not in STOP}
def near_cur(n,p):
    for c in cur:
        d=hav(p,(c[1],c[2]))
        if d<12 or (d<60 and words(n)&words(c[0])): return True
    return False
wd=[]
def add(n,p,k,r):
    if re.fullmatch(r'Q\d+',n) or r<3 or re.search(r'(?i)paleo|prehistoric|Lake (Bonneville|Lahontan|Missoula|Agassiz|Manly)',n): return
    wd.append([n,round(p[0],4),round(p[1],4),k,min(10,r)])
seen={}
def best(rows,key):
    b={}
    for r in rows:
        q=r['m']['value']; v=float(r[key]['value']) if key in r else 0
        if q not in b or v>b[q][0]: b[q]=(v,r)
    return [x[1] for x in b.values()]
for r in best(json.load(open('wd/peaks.json')),'prom'):
    p=ll(r); 
    if not p: continue
    pr=float(r['prom']['value']); sl=int(r['sl']['value']); vol=r['volc']['value']=='true'
    base=9 if pr>=4000 else 8 if pr>=3000 else 7 if pr>=2500 else 6 if pr>=2000 else 4 if pr>=1500 else 3
    base+= 2 if sl>=100 else 1 if sl>=60 else 0
    if vol: base+=1
    add(r['mLabel']['value'],p,'volcano' if vol else 'peak',base)
for r in best(json.load(open('wd/volcanoes.json')),'sl'):
    p=ll(r); sl=int(r['sl']['value'])
    # fame sets the rating, but a low eroded volcano (Vogelsberg, 773 m) reads as forested hills from the air
    base=7 if sl>=60 else 6 if sl>=30 else 5
    if 'elev' in r and float(r['elev']['value'])<1000: base=3
    if p: add(r['mLabel']['value'],p,'volcano',base)
for r in best(json.load(open('wd/parks.json')),'sl'):
    p=ll(r); sl=int(r['sl']['value'])
    if p: add(r['mLabel']['value'],p,'park',6 if sl>=60 else 5 if sl>=40 else 4 if sl>=25 else 3)
for r in best(json.load(open('wd/lakes.json')),'area'):
    p=ll(r); a=float(r['area']['value'])/1e6; sl=int(r['sl']['value'])
    if p: add(r['mLabel']['value'],p,'lake',(6 if a>=10000 else 5 if a>=1000 else 4)+(1 if sl>=60 else 0))
for r in best(json.load(open('wd/glaciers.json')),'sl'):
    p=ll(r); a=float(r['area']['value'])/1e6 if 'area' in r else 0; sl=int(r['sl']['value'])
    if p: add(r['mLabel']['value'],p,'glacier',8 if a>=1000 else 7 if a>=200 else 6 if a>=50 else 5 if sl>=15 else 4)
for r in best(json.load(open('wd/canyons.json')),'sl'):
    p=ll(r); sl=int(r['sl']['value']); fj='Q45776' in r.get('kind',{}).get('value','')
    if p: add(r['mLabel']['value'],p,'coast' if fj else 'canyon',5 if sl>=30 else 4)
wd=[w for w in wd if not near_cur(w[0],(w[1],w[2]))]
wd.sort(key=lambda x:-x[4]); keep=[]
# grid dedupe within 6 km
grid={}
for w in wd:
    g=(round(w[1]*10),round(w[2]*10)); dup=False
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            for o in grid.get((g[0]+dx,g[1]+dy),[]):
                if hav((w[1],w[2]),(o[1],o[2]))<6: dup=True
    if not dup: keep.append(w); grid.setdefault(g,[]).append(w)
out+=keep
# Cities: rated by skyline (count of 150m+ towers). Authoritative counts for the top 61 cities
# (Wikipedia list, >30 towers); others from Wikidata skyscraper counts scaled to 150m+ and capped under 30.
from sky_top import TOP
skyc={int(k):v for k,v in json.load(open('wd/skycount.json')).items()}
allc=[c for c in geonamescache.GeonamesCache().get_cities().values() if c['population']>=100000]
count={}
for c in allc:
    w=skyc.get(c['geonameid'],0)
    if w: count[c['geonameid']]=min(29,round(w*0.35))
for name,n in TOP.items():
    cand=[c for c in allc if c['name']==name or name in c.get('alternatenames',[])]
    if not cand: print('MISSING',name); continue
    c=max(cand,key=lambda c:c['population']); count[c['geonameid']]=n
# Iconic skylines and settings, rated by hand (beats the tower count)
CITY_OVR={'New York City':10,'Hong Kong':10,'Dubai':10,'San Francisco':9,'Chicago':9,'Tokyo':9,'Shanghai':9,'Singapore':9,'Sydney':9,'Rio de Janeiro':9,
 'Toronto':8,'London':8,'Paris':8,'Seattle':7,'Vancouver':7,'Los Angeles':7,'Miami':7,'Las Vegas':7,'Shenzhen':9,'Kuala Lumpur':8,'Panama City':7,'Doha':7}
CITY_OVR_MINPOP={'Panama City':300000}
def srate(n): return 10 if n>=300 else 9 if n>=150 else 8 if n>=80 else 7 if n>=40 else 6 if n>=20 else 5 if n>=10 else 4 if n>=5 else 3 if n>=2 else 0
for c in allc:
    r=srate(count.get(c['geonameid'],0))
    if r==0 and c['population']>=5e6: r=4   # megacity lights at night, even without towers
    r=CITY_OVR.get(c['name'],r) if c['population']>=CITY_OVR_MINPOP.get(c['name'],0) else r
    if r: out.append([c['name'],round(c['latitude'],3),round(c['longitude'],3),'city',r])
out=[o for o in out if o[0] not in ('Manhattan skyline','Chicago lakefront')]
MAN={'Golden Gate Bridge','Las Vegas Strip','Washington DC Mall','Gateway Arch','Mackinac Bridge','Chesapeake Bay Bridge','Lake Pontchartrain Causeway','Kennedy Space Center','Statue of Liberty / NY Harbor','Panama Canal','Palm Jumeirah','Hong Kong harbor','Sydney Harbour','Miami Beach','Hoover Dam / Lake Mead','Mount Rushmore / Black Hills','Taipei 101 / Yangmingshan','Venice lagoon','Gibraltar','Rio de Janeiro bays','Bosphorus','Nile Valley / Pyramids','Cancun / Riviera Maya','Waikiki'}
for o in out:
    if o[0] in MAN: o[3]='landmark'

open('../data/landmarks.json','w').write('export default '+json.dumps(out,separators=(',',':'),ensure_ascii=False)+';\n')
from collections import Counter
print(len(out),Counter(x[3] for x in out)); print(Counter(x[4] for x in out if x[3]!='city'))
for n in ['Mount Waddington','Mount Fairweather','Mount Blackburn','Monarch Mountain','Mount Hayes','Kluane National Park and Reserve','Banff National Park','Lake Superior','Sognefjord']:
    print(n,[x[4] for x in out if x[0]==n])

import subprocess; subprocess.run(['python3','add_region.py'])
