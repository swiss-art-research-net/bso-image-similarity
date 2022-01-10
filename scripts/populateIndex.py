import csv
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

def performIndexing(options):
    datafile = options['datafile']
    sparqlEndpoint = options['endpoint']
    pastecHost = options['pastecHost']
    pastecPort = options['pastecPort']
    limit = options['limit'] if 'limit' in options else None
    
    # Retrieve existing data from file
    data = []

    if isfile(datafile):
        with open(datafile, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)

    # Retrieve new data from SPARQL endpoint
    imagesQuery = """
    PREFIX la: <https://linked.art/ns/terms/>
    PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX search: <https://platform.swissartresearch.net/search/>
    SELECT ?subject ?image WHERE {
    ?subject a search:Object ;
        crm:P128_carries/la:digitally_shown_by/la:digitally_available_via/la:access_point ?image 
    } 
    ORDER BY ?subject
    """
    if limit:
        imagesQuery += " LIMIT " + limit
    sparql = SPARQLWrapper(sparqlEndpoint, returnFormat=JSON)
    sparql.setQuery(imagesQuery)
    try:
        ret = sparql.query().convert()
    except:
        raise Exception("Could not execute query against endpoint", sparqlEndpoint)
    imageDataFromStore = sparqlResultToDict(ret)

    # Compoare data from store with data loaded from file
    irisInData = [d['subject'] for d in data]
    newData = []

    for row in imageDataFromStore:
        if row['subject'] not in irisInData:
            dataToAdd = {
                "index": len(data),
                "subject": row['subject'],
                "image": row['image']
            }
            data.append(dataToAdd)
            newData.append(dataToAdd)

    # Index data
    pastec = PastecConnection(pastecHost=pastecHost, pastecPort=pastecPort)
    for row in tqdm(newData):
        pastec.indexImageUrl(row['index'], row['image'] + '/full/800,/0/default.jpg')

    # Store data
    with open(datafile, 'w') as f:
        headers = ['index', 'subject', 'image']
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

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
    if performIndexing(options):
        echo("OK")
    else:
        echo("FAIL")