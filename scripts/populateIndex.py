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
    logfile = options['logfile']
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
    notIndexed = []
    pastec = PastecConnection(pastecHost=pastecHost, pastecPort=pastecPort)
    for row in tqdm(newData):
        try:
            pastec.indexImageUrl(row['index'], row['image'] + '/full/800,/0/default.jpg')
        except:
            # If the image could not be indexed, it might be because it is too small.
            # This can happen if the image is a wide landscape format, which will not
            # be high enough if requested with a width of 800px.
            # Therefore, we will try again and request the image with a height of 800px instead.
            try:
                pastec.indexImageUrl(row['index'], row['image'] + '/full/,800/0/default.jpg')
            except:
                # If we still fail to index the image, it is added to the list of images that could not be indexed.
                notIndexed.append(row)

    # Store data
    with open(datafile, 'w') as f:
        headers = ['index', 'subject', 'image']
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    # Print information about images that could not be indexed
    if len(notIndexed) > 0:
        with open(logfile, 'a') as f:
            f.write("============================================================\n")
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            f.write("Indexing performed: " + dt_string + "\n")
            f.write("Could not index the following images:\n")
            for row in notIndexed:
                f.write(row['image'] + '\n')
        
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
    if not 'logfile' in options:
        options['logfile'] = 'log.txt'
    if performIndexing(options):
        print("OK")
    else:
        print("FAIL")