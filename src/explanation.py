import numpy as np
import pandas as pd
import nltk
from nltk.corpus import wordnet as wn
import os

from src.connection import db_connection

def get_aspects(conn, mov_id):
    return pd.read_sql('SELECT aspect, score FROM ASPECT WHERE movie_id = %s' % mov_id, con=conn)

def get_title(conn, mov_prof, mov_rec):
    return pd.read_sql('SELECT movie_id, title FROM MOVIE WHERE movie_id in (%s, %s)' % (mov_prof, mov_rec), con=conn, index_col='movie_id')

def get_movies(conn, user_id):
    stmt = 'SELECT movie_id FROM USERMOVIE WHERE user_id = {0}'.format(user_id)
    return pd.read_sql(stmt, con=conn)

# get n (number) aspects most important to the movie that
# has a meaning on wordnet
def get_n_aspects(number: int, aspects_movie: pd.DataFrame):
    n = 0
    index = 0
    output = []
    while n < number:
        syns = wn.synsets(aspects_movie.iloc[index][0])
        if len(syns) > 0:
            output.append(syns[0])
            n = n + 1
        index = index + 1

    return output

def generate_explanations(profile_itens: list, top_item: int):
    # nltk.download('wordnet')
    
    nltk.data.path.append("/tmp")

    nltk.download("wordnet", download_dir = "/tmp")

    aspects_rec_movie = get_aspects(db_connection, top_item).sort_values('score', ascending=False)

    top_rec_aspects = get_n_aspects(5, aspects_rec_movie)
    max = 0
    word_p = ""
    word_r = ""
    movie_pro = 0

    for p_movie in profile_itens:
        aspects_profile_movie = get_aspects(db_connection, p_movie).sort_values('score', ascending=False)

        top_profile_aspects = get_n_aspects(5, aspects_profile_movie)
        for p_aspects in top_profile_aspects:
            for r_aspects in top_rec_aspects:
                sim = wn.wup_similarity(p_aspects, r_aspects)
                if sim is not None and sim > max and sim != 1: # TODO sim != 1
                    max = sim
                    movie_pro = p_movie
                    word_p = p_aspects.name().split('.')[0]
                    word_r = r_aspects.name().split('.')[0]

    if movie_pro == 0:
        mv_data = get_title(db_connection, profile_itens[0], top_item)
        return "Because you rated well the movie \"" + mv_data['title'][top_item] + "\" watch \"" + \
               mv_data['title'][profile_itens[0]] + "\""

    mv_data = get_title(db_connection, movie_pro, top_item)

    movie_pro_name = mv_data['title'][movie_pro]
    movie_rec_name = mv_data['title'][top_item]

    if word_p != word_r:
        sentence = "Because you rated well the movie \"" + movie_pro_name + "\" described as \"" \
                   + word_p + "\" watch \"" + movie_rec_name + "\" described with the similar word \"" + word_r + "\""
    else:
        sentence = "Because you rated well the movie \"" + movie_pro_name + "\" described as \"" \
                   + word_p + "\" watch \"" + movie_rec_name + "\" described with the same word"

    return sentence

def generate_explanations_compare(profile_itens: list, top_item: int):
    # nltk.download('wordnet')
    
    nltk.data.path.append("/tmp")

    nltk.download("wordnet", download_dir = "/tmp")

    aspects_rec_movie = get_aspects(db_connection, top_item).sort_values('score', ascending=False)

    if aspects_rec_movie.empty:
        top_rec_aspects = []
    else:
        top_rec_aspects = get_n_aspects(5, aspects_rec_movie)
    max = 0
    word_p = ""
    word_r = ""
    movie_pro = 0

    for p_movie in profile_itens:
        aspects_profile_movie = get_aspects(db_connection, p_movie).sort_values('score', ascending=False)
        if aspects_profile_movie.empty:
            break

        top_profile_aspects = get_n_aspects(5, aspects_profile_movie)
        for p_aspects in top_profile_aspects:
            for r_aspects in top_rec_aspects:
                sim = wn.wup_similarity(p_aspects, r_aspects)
                if sim is not None and sim > max and sim != 1: # TODO sim != 1
                    max = sim
                    movie_pro = p_movie
                    word_p = p_aspects.name().split('.')[0]
                    word_r = r_aspects.name().split('.')[0]

    if movie_pro == 0:
        mv_data = get_title(db_connection, profile_itens[0], top_item)
        return "Because you rated well the movie \"" + mv_data['title'][top_item] + "\" watch \"" + \
               mv_data['title'][profile_itens[0]] + "\"", mv_data['title'][top_item], mv_data['title'][profile_itens[0]]

    mv_data = get_title(db_connection, movie_pro, top_item)

    movie_pro_name = mv_data['title'][movie_pro]
    movie_rec_name = mv_data['title'][top_item]

    if word_p != word_r:
        sentence = "Because you rated well the movie \"" + movie_pro_name + "\" described as \"" \
                   + word_p + "\" watch \"" + movie_rec_name + "\" described with the similar word \"" + word_r + "\""
    else:
        sentence = "Because you rated well the movie \"" + movie_pro_name + "\" described as \"" \
                   + word_p + "\" watch \"" + movie_rec_name + "\" described with the same word"

    return sentence, movie_pro_name, movie_rec_name

def generate_explanations_AB(user_id: int, movies: list):
    movies = pd.DataFrame(movies)
    movies["justA"] = ""
    movies["justB"] = ""
    profile_itens = get_movies(db_connection, user_id)["movie_id"].tolist()
    print(profile_itens)
    for index, row in movies.iterrows():
        sentence, m_p, m_r = generate_explanations_compare(profile_itens, row["movie_id"])
        movies["justA"][index] = sentence
        movies["justB"][index] = "Because you rated well the movie \"" + m_p + "\" watch \"" + m_r + "\""
    
    return movies.to_json(orient="records")

