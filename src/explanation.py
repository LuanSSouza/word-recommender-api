import os.path
from random import randrange
import numpy as np
import pandas as pd
import nltk
from nltk.corpus import wordnet as wn

from sqlalchemy import create_engine
import pymysql

def get_aspects(conn, mov_id):
    return pd.read_sql('SELECT aspect, score FROM aspect WHERE movie_id = %s' % mov_id, con=conn)

def get_title(conn, mov_prof, mov_rec):
    return pd.read_sql('SELECT movie_id, title FROM movie WHERE movie_id in (%s, %s)' % (mov_prof, mov_rec), con=conn, index_col='movie_id')

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
    nltk.download('wordnet')

    db_connection_str = 'mysql+pymysql://root:root@localhost/worec'
    db_connection = create_engine(db_connection_str)

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