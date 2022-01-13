import csv
import datetime
import json
import sys
import uuid
from string import Template
from tqdm import tqdm

def generateRDF(options):
    inputfile = options['inputfile']
    outputfile = options['outputfile']
    
    with open(inputfile, 'r') as f:
        inputData = json.loads(f.read())

    dateTime = datetime.datetime.now()

    technique = 'https://github.com/swiss-art-research-net/bso-image-similarity'
    
    namespaces = """
@prefix crm: <http://www.cidoc-crm.org/cidoc-crm/>.
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
@prefix xsd: <http://www.w3.org/2001/XMLSchema#>.
    """
    
    classificationTemplate = Template("""
<$classification> a crm:E13_Attribute_Assignment .
<$classification> crm:P140_assigned_attribute_to <$subject> .
<$classification> crm:P141_assigned <$objectUri> .
<$classification> crm:P177_assigned_property_of_type crm:P130_shows_features_of .
<$classification> crm:P4_has_time-span <$classification/date> .
<$classification> crm:P33_used_specific_technique <$technique> .

<$classification/date> a crm:E52_Time-Span .
<$classification/date> crm:P82_at_some_time_within "$dateTime"^^xsd:dateTime .
    """)

    with open(outputfile, 'w') as f:
        f.write(namespaces)

    with open(outputfile, 'a') as f:
        for fromIri in tqdm(inputData.keys()):
            for toObject in inputData[fromIri]:
                classificationUri = 'https://resource.swissartresearch.net/classification/' + str(uuid.uuid4())
                subjectUri = fromIri
                objectUri = toObject['image']
                f.write(classificationTemplate.substitute(
                                            classification=classificationUri, 
                                            subject=subjectUri, 
                                            objectUri=objectUri,
                                            technique=technique,
                                            dateTime=dateTime.strftime("%Y-%m-%dT%H:%M:%S")))
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
    if not 'inputfile' in options:
        print("An input file in JSON format needs to be specified via the --inputfile argument")
        sys.exit(1)
    if not 'outputfile' in options:
        print("An output file in RDF/Turtle format needs to be specified via the --outputfile argument")
        sys.exit(1)
    
    if generateRDF(options):
        print("OK")
    else:
        print("FAIL")