import json,subprocess,sys,urllib.parse,time
Q={
'peaks':"""SELECT ?m ?mLabel ?coord ?prom ?elev ?sl ?volc WHERE {
 ?m p:P2660/psn:P2660/wikibase:quantityAmount ?prom . FILTER(?prom >= 1000)
 ?m wdt:P625 ?coord . ?m wikibase:sitelinks ?sl .
 OPTIONAL { ?m p:P2044/psn:P2044/wikibase:quantityAmount ?elev }
 BIND(EXISTS { ?m wdt:P31/wdt:P279* wd:Q8072 } AS ?volc)
 SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }""",
'volcanoes':"""SELECT ?m ?mLabel ?coord ?sl ?elev ?prom WHERE {
 ?m wdt:P31/wdt:P279* wd:Q8072 . ?m wdt:P625 ?coord . ?m wikibase:sitelinks ?sl . FILTER(?sl >= 15)
 OPTIONAL { ?m p:P2044/psn:P2044/wikibase:quantityAmount ?elev } OPTIONAL { ?m p:P2660/psn:P2660/wikibase:quantityAmount ?prom }
 SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }""",
'parks':"""SELECT ?m ?mLabel ?coord ?sl WHERE {
 ?m wdt:P31 wd:Q46169 . ?m wdt:P625 ?coord . ?m wikibase:sitelinks ?sl . FILTER(?sl >= 15)
 SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }""",
'lakes':"""SELECT ?m ?mLabel ?coord ?area ?sl WHERE {
 ?m wdt:P31/wdt:P279* wd:Q23397 . ?m p:P2046/psn:P2046/wikibase:quantityAmount ?area . FILTER(?area >= 3e8)
 FILTER NOT EXISTS { ?m wdt:P576 ?gone } FILTER NOT EXISTS { ?m wdt:P31 wd:Q188025 } FILTER NOT EXISTS { ?m wdt:P31 wd:Q1321084 }
 ?m wdt:P625 ?coord . ?m wikibase:sitelinks ?sl .
 SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }""",
'glaciers':"""SELECT ?m ?mLabel ?coord ?area ?sl WHERE {
 ?m wdt:P31/wdt:P279* wd:Q35666 . ?m wdt:P625 ?coord . ?m wikibase:sitelinks ?sl .
 OPTIONAL { ?m p:P2046/psn:P2046/wikibase:quantityAmount ?area }
 FILTER(?sl >= 8 || (BOUND(?area) && ?area >= 5e7))
 SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }""",
'canyons':"""SELECT ?m ?mLabel ?coord ?sl ?kind WHERE {
 VALUES ?t { wd:Q150784 wd:Q45776 } ?m wdt:P31 ?t . ?m wdt:P625 ?coord . ?m wikibase:sitelinks ?sl . FILTER(?sl >= 8)
 BIND(?t AS ?kind) SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }""",
}
for k,q in Q.items():
    if len(sys.argv)>1 and k not in sys.argv[1:]: continue
    t=time.time()
    r=subprocess.run(['curl','-s','-m','120','-G','https://query.wikidata.org/sparql','--data-urlencode','query='+q,'-H','Accept: application/sparql-results+json','-H','User-Agent: window-sights/1.0 (github.com/rrwhite/window-sights)'],capture_output=True,text=True)
    try:
        d=json.loads(r.stdout); rows=d['results']['bindings']; json.dump(rows,open(f'wd/{k}.json','w'))
        print(k,len(rows),round(time.time()-t,1))
    except Exception as e: print(k,'FAIL',r.stdout[:300])
