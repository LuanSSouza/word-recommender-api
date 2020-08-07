import numpy as np
import pandas as pd
from src.connection import db_connection

def get_movies(conn, imdb: list):
    imdb = [i[2:] for i in imdb]
    ids = ",".join(imdb)
    stmt = 'SELECT movie_id, imdbID FROM MOVIE WHERE imdbID in ({0})'.format(ids)
    return pd.read_sql(stmt, con=conn, index_col='movie_id')

def calculate_prediction(k, movie, profile, sim_m):
    n = 0
    i = 0
    total = 0

    sim = sim_m.loc[movie][:]
    sim.loc[movie] = 0
    sim = sim.sort_values(ascending=False)
    while n < k and i < len(sim) - 1:
        neig = sim.index[i]
        if neig in profile.index:
            total = total + sim.iloc[i]
            n = n + 1
        i = i + 1

    return total


def generate_rec(number, k, u_row: pd.Series, sim_m: pd.DataFrame):
    profile = u_row[u_row == 1]
    prediction = u_row[u_row == 0]
    for m in prediction.index:
        prediction.loc[m] = calculate_prediction(k, m, profile, sim_m)

    prediction = prediction.sort_values(ascending=False)
    return prediction[:number].tolist(), prediction[:number].index

def recommendation(movies):

    used_columns = ['user_id', 'movie_id', 'rating']

    cols = pd.read_csv("../datasets/user_rating.csv", usecols=used_columns)['movie_id'].unique()

    profile = pd.DataFrame(0, index=[1], columns=cols)

    movies = get_movies(db_connection, movies).index

    profile[movies] = 1

    semantic_sim = pd.read_csv("../datasets/sim_matrix.csv", header=None)
    semantic_sim.index = cols
    semantic_sim.columns = cols

    return generate_rec(3, 5, profile.loc[1], semantic_sim)