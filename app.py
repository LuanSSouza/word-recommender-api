from flask import Flask, request
from flask_cors import CORS
import requests
import os
import json

import src.most_watched as most
import src.recommendation as rec
import src.explanation as exp
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route("/", methods = ['GET'])
def hello():
    return "Hello!"

@app.route("/omdb", methods = ['GET'])
def omdb():
    payload = { 'apikey': os.environ['API_KEY'], 'type': 'movie', 's': request.args.get('title') }
    r = requests.get("http://www.omdbapi.com/", params=payload)
    return r.json()

@app.route("/mostwatched", methods = ['GET'])
def mostwatched():
    return most.get_mostwatchedfromdb()

@app.route("/recommendation", methods = ['GET', 'POST'])
def recommendation():
    data = request.json
    if not data or "movies" not in data or not data['movies']:
        return 'bad request!', 400

    response, idx = rec.recommendation(data['movies'])
    return json.dumps(response)

@app.route("/explanation", methods = ['GET', 'POST'])
def explanation():
    data = request.json
    if not data or "movies" not in data or "recs" not in data or not data['movies'] or not data['recs']:
        return 'bad request!', 400
    
    rated = data['movies']
    recommendation = data['recs']

    explanation = exp.generate_explanations(rated, recommendation[0])
    return json.dumps({'explanation': explanation})

app.run()