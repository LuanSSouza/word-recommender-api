from flask import Flask, request
from flask_cors import CORS

import src.most_watched as most
import src.recommendation as rec
import src.justifications as just
import src.explanation as exp
import src.users as users
import src.omdb as omdbCtrl
import pandas as pd
import json

app = Flask(__name__)
CORS(app)

@app.route("/", methods = ['GET'])
def hello():
    return "Hello!"

@app.route("/omdb", methods = ['GET'])
def omdb():
    return omdbCtrl.omdb(request.args.get('title'), request.args.get('year'))

@app.route("/mostwatched", methods = ['GET'])
def mostwatched():
    return most.get_mostwatchedfromdb()

@app.route("/recommendation", methods = ['GET', 'POST'])
def recommendation():
    data = request.json
    if not data or "movies" not in data or not data['movies']:
        return 'bad request!', 400

    return rec.recommendation(data['user_id'], data['movies'])

@app.route("/baseline", methods = ['GET', 'POST'])
def baseline():
    data = request.json
    if not data or "movies" not in data or not data['movies']:
        return 'bad request!', 400

    return rec.baseline(data['user_id'], data['movies'])

@app.route("/explanation", methods = ['GET', 'POST'])
def explanation():
    data = request.json
    if not data or "movies" not in data or not data['movies']:
        return 'bad request!', 400
    
    return exp.generate_explanations_AB(data['user_id'], data['movies'])

@app.route("/user", methods = ['POST'])
def user():
    data = request.json
    return json.dumps(users.insert_user(data))

@app.route("/rate", methods = ['POST'])
def rate():
    data = request.json
    return json.dumps(just.insert_rate(data['user_id'], data['rates']))

@app.route("/compare", methods = ['POST'])
def compare():
    data = request.json
    return json.dumps(just.insert_comp(data['user_id'], data['compares']))

if __name__ == "__main__":
    app.run()