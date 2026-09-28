import json,subprocess
q="""SELECT ?b ?coord ?h WHERE {
 ?b wdt:P31/wdt:P279* wd:Q11303 . ?b wdt:P625 ?coord .
 OPTIONAL { ?b p:P2048/psn:P2048/wikibase:quantityAmount ?h }
 FILTER NOT EXISTS { ?b wdt:P576 ?x } }"""
r=subprocess.run(['curl','-s','-m','180','-G','https://query.wikidata.org/sparql','--data-urlencode','query='+q,'-H','Accept: application/sparql-results+json','-H','User-Agent: window-sights/1.0 (github.com/rrwhite/window-sights)'],capture_output=True,text=True)
rows=json.loads(r.stdout)['results']['bindings']; json.dump(rows,open('wd/sky_all.json','w')); print(len(rows))
