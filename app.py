# app.py

from flask import Flask, request
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello():
    return "Hello!"

@app.route("/omdb", methods = ['GET'])
def omdb():
    payload = { 'apikey': os.environ['API_KEY'], 'type': 'movie', 's': request.args.get('title') }
    r = requests.get("http://www.omdbapi.com/", params=payload)
    return r.json()