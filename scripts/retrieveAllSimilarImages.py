import csv
import json
import sys
from os.path import isfile
from lib.PastecLib import PastecConnection
from SPARQLWrapper import SPARQLWrapper, JSON
from tqdm import tqdm

def sparqlResultToDict(results):
    rows = []
    for result in results["results"]["bindings"]:
        row = {}
        for key in results["head"]["vars"]:
            if key in result:
                row[key] = result[key]["value"]
            else:
                row[key] = None
        rows.append(row)
    return rows

def loadImageData(datafile):
    data = []
    with open(datafile, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

def performRetrieval(options):
    datafile = options['datafile']
    sparqlEndpoint = options['endpoint']
    pastecHost = options['pastecHost']
    pastecPort = options['pastecPort']
    outputfile = options['outputfile']
    logfile = options['logfile']
    limit = options['limit'] if 'limit' in options else None

    # Retrieve new data from SPARQL endpoint
    imagesQuery = """
    PREFIX  search: <https://platform.swissartresearch.net/search/>
    PREFIX  la:   <https://linked.art/ns/terms/>
    PREFIX  crmdig: <http://www.ics.forth.gr/isl/CRMdig/>
    PREFIX  rso:  <http://www.researchspace.org/ontology/>
    PREFIX  crm:  <http://www.cidoc-crm.org/cidoc-crm/>

    SELECT  ?subject ?image ?crop
    WHERE
    { ?subject  a  search:Object .
        ?subject ((crm:P128_carries/la:digitally_shown_by)/la:digitally_available_via)/la:access_point ?image
        OPTIONAL
        { ?bbox ^rso:boundingBox/crmdig:L49_is_primary_area_of ?image }
        BIND(if(bound(?bbox), strafter(?bbox, "xywh="), "full") AS ?crop)
    }
    ORDER BY DESC(?subject)
    """
    if limit:
        imagesQuery += " LIMIT " + limit
    
    sparql = SPARQLWrapper(sparqlEndpoint, returnFormat=JSON)
    sparql.setQuery(imagesQuery)
    try:
        ret = sparql.query().convert()
    except:
        raise Exception("Could not execute query against endpoint", sparqlEndpoint)
    
    imagesToQuery = sparqlResultToDict(ret)

    # Load image data
    data = loadImageData(options['datafile'])
    
    keys = {}
    for row in data:
        keys[row['index']] = row

    # Retrieve similar images per image
    pastec = PastecConnection(pastecHost=pastecHost, pastecPort=pastecPort)
    
    output = {}
    for row in tqdm(imagesToQuery):
        urlLandscape = row['image'] + "/" + row['crop'] + "/800,/0/default.jpg"
        urlPortrait= row['image'] + "/" + row['crop'] + "/,800/0/default.jpg"
        try:
            results = pastec.imageQueryUrl(urlLandscape)
        except:
            try:
                results = pastec.imageQueryUrl(urlPortrait)
            except:
                continue
                
        output[row['image']] = []
        for result in results:
            if str(result[0]) in keys:
                objectIri = keys[str(result[0])]['subject']
                imageIri =  keys[str(result[0])]['image']
                if row['image'] not in imageIri:
                    output[row['image']].append({
                        "object": objectIri,
                        "image": imageIri
                    })
            else:
                print("Could not find key for", result[0])

    # DEBUG
    with open(outputfile, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)    
    
    return True

if __name__ == "__main__":
    options = {}
    for i, arg in enumerate(sys.argv[1:]):
        if arg.startswith("--"):
            if not sys.argv[i + 2].startswith("--"):
                options[arg[2:]] = sys.argv[i + 2]
            else:
                print("Malformed arguments")
                sys.exit(1)
    if not 'endpoint' in options:
        print("A SPARQL endpoint needs to be specified via the --endpoint argument")
        sys.exit(1)
    if not 'pastecHost' in options:
        print("A Pastec host needs to be specified via the --pastecHost argument")
        sys.exit(1)
    if not 'pastecPort' in options:
        print("A Pastec port needs to be specified via the --pastecPort argument")
        sys.exit(1)
    if not 'datafile' in options:
        print("A data file needs to be specified via the --datafile argument")
        sys.exit(1)
    if not 'outputfile' in options:
        print("An output file needs to be specified via the --outputfile argument")
        sys.exit(1)
    if not 'logfile' in options:
        options['logfile'] = 'log.txt'
    if performRetrieval(options):
        print("OK")
    else:
        print("FAIL")