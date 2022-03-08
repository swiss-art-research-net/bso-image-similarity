
import sys
sys.path.insert(0, '/scripts/lib')

import csv
import json
from dotenv import load_dotenv

from flask import Flask, Response, request
from sariSparqlParser import parser
from rdflib.term import Variable, URIRef, Literal
from os import getenv
from PastecLib import PastecConnection
"""
PREFIX pastec: <http://service.swissartresearch.net/pastec/> 
SELECT ?candidate WHERE 
{ 
    <https://www.e-rara.ch/zuz/i3f/v20/17367106/98,116,9034,6658/300,/0/default.jpg> a pastec:Image ;
        pastec:hasSimilarImage ?candidate ;
        pastec:hasSimilarEntity ?entity .
}
"""

app = Flask(__name__)
load_dotenv()
DATAFILE = getenv('DATAFILE')
PASTEC_HOST = getenv('PASTEC_HOST')
PASTEC_PORT = getenv('PASTEC_PORT')


def createSparqlResponse(parsedQuery, processedRequests):

  def getDataTypeForValue(value):
      if isinstance(value, int):
          return "http://www.w3.org/2001/XMLSchema#integer"
      return "http://www.w3.org/2001/XMLSchema#string"

  response = {}
  response['head'] = {
      "vars": parsedQuery['select']
  }
  bindings = []
  for request in processedRequests:
    if parsedQuery['limitOffset']:
      offset = parsedQuery['limitOffset']['offset'] if 'offset' in parsedQuery['limitOffset'] else 0
      limit = parsedQuery['limitOffset']['limit'] if  'limit' in parsedQuery['limitOffset'] else len(request)
    else:
      offset = 0
      limit = len(request)
    for entry in request[offset:offset+limit]:
      row = {}
      for variable in parsedQuery['select']:
        if variable in entry:
          row[variable] = {
            "value": entry[variable],
            "type": "literal",
            "datatype": getDataTypeForValue(entry[variable])
          }
      bindings.append(row)
  response['results'] = {'bindings': bindings}
  return response


def extractRequestFromQueryData(data):
    pastecPrefix = 'http://service.swissartresearch.net/pastec/'
  
    def getAttribute(value):
        return value[len(pastecPrefix):]
        
    requests = []
    for triple in data['where']:
        if triple['s']['type'] == URIRef and triple['p']['value'] == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
            requests.append({
              "subject": triple['s']['value'],
              "retrieve": {},
              "send": {},
              "type": triple['o']['value']
            })
    for request in requests:
        for triple in data['where']:
          if triple['s']['type'] == URIRef and triple['s']['value'] == request['subject']:
              if getAttribute(triple['p']['value']).startswith('has'):
                  if triple['o']['type'] == Variable:
                      request['retrieve'][getAttribute(triple['p']['value'])] = triple['o']['value']
                  if triple['o']['type'] == Literal:
                      request['send'][getAttribute(triple['p']['value'])] = triple['o']['value']

    return requests


def getDataFromSparqlQuery(payload):
    from rdflib.plugins.sparql.parser import parseQuery
    q = parseQuery(payload)
    return q

def loadImageData(datafile):
    data = []
    with open(datafile, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

def processPastecApiRequests(requests):
    ret = []
    for request in requests:
        if  request['type'] == 'http://service.swissartresearch.net/pastec/Image':
            ret.append(requestSimilarImage(request))
    return ret


def processQuery(query):
    requests = extractRequestFromQueryData(query)
    processedRequests = processPastecApiRequests(requests)
    response = createSparqlResponse(query, processedRequests)
    return response

def requestSimilarImage(request):
    data = []
    
    pastec = PastecConnection(PASTEC_HOST, PASTEC_PORT)

    url = request['subject']
    url = 'https://www.e-rara.ch/zuz/i3f/v20/17367106/98,116,9034,6658/300,/0/default.jpg'
    requestResult = {
        'url': url,
        'results': []
    }
    results = pastec.imageQueryUrl(url)
    for result in results:
        if str(result[0]) in imageKeys:
            response = {
                "hasSimilarEntity": imageKeys[str(result[0])]['subject'],
                "hasSimilarImage": imageKeys[str(result[0])]['image']
            }
            row = {}
            for key, variable in request['retrieve'].items():
                row[variable] = response[key]
            data.append(row)
        else:
            print("Could not find key for", result[0])
    return data

@app.route('/')
def index():
  return 'Server Works!'
  
@app.route('/sparql', methods=['GET', 'POST'])
def sparql():
    """
    Listens for SPARQL Update requests and processes them.
    """
    if request.values:
        p = parser()
        if 'query' in request.values:
            query = p.parseQuery(request.values['query'])
            response = processQuery(query)
            return Response(json.dumps(response), mimetype='application/json')
    return Response("OK", mimetype='application/json')

imageData = loadImageData(DATAFILE)
imageKeys = {}
for row in imageData:
    imageKeys[row['index']] = row

REQUEST_SIMILAR_IMAGE = 'similarImage'