from flask import Flask, Response, request

"""
PREFIX pastec: <http://service.swissartresearch.net/pastec/> 
SELECT * WHERE 
{ <http://image.org> pastec:hasSimilarImage ?candidate }
"""

app = Flask(__name__)

def getDataFromSparqlQuery(payload):
    from rdflib.plugins.sparql.parser import parseQuery
    q = parseQuery(payload)
    return q

@app.route('/')
def index():
  return 'Server Works!'
  
@app.route('/sparql', methods=['GET', 'POST'])
def sparql():
    """
    Listens for SPARQL Update requests and processes them.
    """
    if request.args:
        query = request.args.get('query')
        data = getDataFromSparqlQuery(query)
        app.logger.info(data)
    return Response("OK", mimetype='application/json')
