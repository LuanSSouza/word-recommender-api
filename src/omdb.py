import requests
import os
import json
import numpy as np
import pandas as pd
from src.connection import db_connection

def get_movies_data(conn, imdb: list):
    imdb = [i[2:] for i in imdb]
    ids = ",".join(imdb)
    return pd.read_sql('SELECT * FROM MOVIE WHERE imdbID in ({0})'.format(ids), con=conn)

def omdb(title):
    payload = { 'apikey': os.environ['API_KEY'], 'type': 'movie', 's': title }
    r = requests.get("http://www.omdbapi.com/", params=payload)
    search = r.json()["Search"]
    imdbs = [s["imdbID"] for s in search]
    movies = get_movies_data(db_connection, imdbs)
    movies['imdbID'] = movies['imdbID'].map('tt{0:07d}'.format)
    for s in search:
        movies.loc[movies['imdbID'] == s["imdbID"], 'poster'] = s["Poster"]
    movies.columns = ["movie_id", "imdbID", "Title", "Year", "imdbURL", "Poster"]
    
    return { "Search": json.loads(movies.to_json(orient="records"))}

def omdbById(imdbID):
    payload = { 'apikey': os.environ['API_KEY'], 'type': 'movie', 'i': imdbID }
    r = requests.get("http://www.omdbapi.com/", params=payload)
    return r.json()