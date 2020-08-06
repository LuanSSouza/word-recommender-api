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
    used_columns = ['user_id', 'movie_id', 'rating']

    train_data = pd.read_csv("datasets/train.csv", usecols=used_columns)

    # generate user/item matrix and mean item and transform it into interactions
    user_item = train_data.pivot(index="user_id", columns="movie_id", values="rating")
    user_item[user_item >= 0] = 1
    user_item[user_item.isna()] = 0
    print(user_item.columns)

    semantic_sim = pd.read_csv("datasets/sim_matrix.csv", header=None)
    semantic_sim.index = user_item.columns
    semantic_sim.columns = user_item.columns

    response, teste = rec.generate_rec(3, 5, user_item.loc[8194], semantic_sim)
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