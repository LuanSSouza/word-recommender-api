import numpy as np
import pandas as pd
from src.connection import db_connection
import src.users as users
import src.explanation as exp
import src.omdb as omdb

def get_movies(conn, imdb: list):
    imdb = [i[2:] for i in imdb]
    ids = ",".join(imdb)
    stmt = 'SELECT movie_id, imdbID FROM MOVIE WHERE imdbID in ({0})'.format(ids)
    return pd.read_sql(stmt, con=conn, index_col='movie_id')

def get_movies_data(conn, movie_id: list):
    ids = ",".join(str(i) for i in movie_id)
    return pd.read_sql('SELECT * FROM MOVIE WHERE movie_id in ({0})'.format(ids), con=conn)

def update_movie_poster(movie_id, poster):
    with db_connection.connect() as conn:
        with conn.begin():
            conn.execute(update_movie_poster_stmt(movie_id, poster))

def update_movie_poster_stmt(movie_id, poster):
    return "UPDATE MOVIE SET poster = '{0}' WHERE movie_id = {1}".format(poster, movie_id)

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

def recommendation(user_id, movies):

    used_columns = ['user_id', 'movie_id', 'rating']

    cols = pd.read_csv("../datasets/user_rating.csv", usecols=used_columns)['movie_id'].unique()

    profile = pd.DataFrame(0, index=[1], columns=cols)

    movies = get_movies(db_connection, movies).index
    
    users.insert_user_movie_stmt(user_id, movies.tolist())

    profile[movies] = 1

    semantic_sim = pd.read_csv("../datasets/sim_matrix.csv", header=None)
    semantic_sim.index = cols
    semantic_sim.columns = cols

    response, idx = generate_rec(3, 5, profile.loc[1], semantic_sim)

    rec = get_movies_data(db_connection, idx.tolist())
    rec["explanation"] = ""
    rec['imdbID'] = rec['imdbID'].map('tt{0:07d}'.format)

    for index, row in rec.iterrows():
        rec["explanation"][index] = exp.generate_explanations(movies.tolist(), row["movie_id"])
        if row["poster"] is None:
            poster = omdb.omdbById(row["imdbID"])["Poster"]
            update_movie_poster(row["movie_id"], poster)
            rec["poster"][index] = poster

    return rec.to_json(orient="records")