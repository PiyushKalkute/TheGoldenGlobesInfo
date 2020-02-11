import pickle
from pathlib import Path

import requests
import unidecode as unidecode


class WikidataConnector:

    def __init__(self):
        self.queries = {"actors": """SELECT DISTINCT ?actorLabel WHERE {
  ?actor wdt:P31 wd:Q5;
         wdt:P106 wd:Q10800557;
         wdt:P21 wd:Q6581097.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
} ORDER BY ?actorLabel""",
                        "actresses": """SELECT DISTINCT ?actorLabel WHERE {
  ?actor wdt:P31 wd:Q5;
         wdt:P106 wd:Q10800557;
         wdt:P21 wd:Q6581072.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
} ORDER BY ?actorLabel""",
                        "films": """SELECT DISTINCT ?filmLabel WHERE {{
  ?film wdt:P31 wd:Q11424;
        wdt:P345 ?id;
        wdt:P577 ?date.
  FILTER (?date > "{0}-01-01"^^xsd:dateTime && ?date < "{1}-12-31"^^xsd:dateTime)
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
}} ORDER BY ?filmLabel""",
                        "directors": """SELECT DISTINCT ?directorLabel WHERE {
  ?director wdt:P31 wd:Q5;
         wdt:P106 wd:Q2526255.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
} ORDER BY ?directorLabel""",
                        "series": """SELECT DISTINCT ?seriesLabel WHERE {
  ?series wdt:P31 wd:Q5398426;
        wdt:P345 ?id;
        wdt:P580 ?date.
  FILTER (?date > "2000-01-01"^^xsd:dateTime && ?date < NOW())
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
} ORDER BY ?seriesLabel"""}
        self.results = {}

    def call_wikidate(self, query, field_name, year1="", year2=""):
        if not str(query + year2) in self.results.keys():
            file = Path("wikidata_" + query + ".txt")
            if file.exists():
                with open("wikidata_" + query + year2 + ".txt", 'rb') as f:
                    self.results[str(query + year2)] = pickle.load(f)
            else:
                url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql'
                if year2 == "":
                    dataform = str(self.queries[query]).strip("'<>() ").replace('\'', '\"')
                    json = requests.get(url, params={'query': dataform, 'format': 'json'}).json()
                else:
                    dataform = str(self.queries[query].format(year1, year2))
                    # print(dataform)
                    json = requests.get(url.strip("'<>() ").replace('\'', '\"'), params={'query': dataform, 'format': 'json'}).json()
                self.results[str(query + year2)] = self.parse_json(json, field_name)
                with open("wikidata_" + query + year2 + ".txt", 'wb') as f:
                    pickle.dump(self.results[str(query + year2)], f)
        return self.results[str(query + year2)]

    def parse_json(self, json, field_name):
        entities = []
        for item in json['results']['bindings']:
            name = item[field_name]['value']
            name = name.replace('-', ' ')
            name = name.replace(' of ', ' ')
            name = unidecode.unidecode(name)
            entities.append(name)
        entities.sort(key=len, reverse=True)
        return entities
