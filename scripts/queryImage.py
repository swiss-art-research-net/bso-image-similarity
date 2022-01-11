import csv
import sys
from lib.PastecLib import PastecConnection

def loadImageData(datafile):
    data = []
    with open(datafile, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

def searchForImage(options, keys):
    pastecHost = options['pastecHost']
    pastecPort = options['pastecPort']
    datafile = options['datafile']
    imageUrl = options['imageUrl']

    pastec = PastecConnection(pastecHost, pastecPort)
    results = pastec.imageQueryUrl(imageUrl)

    resultIris = []
    for result in results:
        if str(result[0]) in keys:
            resultIris.append((keys[str(result[0])]['subject'], keys[str(result[0])]['image']))
        else:
            print("Could not find key for", result[0])

    return resultIris

if __name__ == "__main__":
    options = {}
    for i, arg in enumerate(sys.argv[1:]):
        if arg.startswith("--"):
            if not sys.argv[i + 2].startswith("--"):
                options[arg[2:]] = sys.argv[i + 2]
            else:
                print("Malformed arguments")
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
    if not 'imageUrl' in options:
        print("A URL for an image needs to be specified via the --imageUrl argument")
        sys.exit(1)

    data = loadImageData(options['datafile'])
    
    keys = {}
    for row in data:
        keys[row['index']] = row

    print(searchForImage(options, keys))

    