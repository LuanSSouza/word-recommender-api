import requests
import os
import json

def omdb(title):
    payload = { 'apikey': os.environ['API_KEY'], 'type': 'movie', 's': title }
    r = requests.get("http://www.omdbapi.com/", params=payload)
    return r.json()

def omdbById(imdbID):
    payload = { 'apikey': os.environ['API_KEY'], 'type': 'movie', 'i': imdbID }
    r = requests.get("http://www.omdbapi.com/", params=payload)
    return r.json()