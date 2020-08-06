import os.path
from random import randrange
import numpy as np
import pandas as pd
import nltk
from nltk.corpus import wordnet as wn

from sqlalchemy import create_engine
import pymysql


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

def generate_explanations(profile_itens: pd.DataFrame, top_item: int, movie_data_info: pd.DataFrame):
    # i = 0
    columns = ['aspect', 'score']
    filename_rec = "../results/movie_" + str(top_item) + ".csv"

    db_connection_str = 'mysql+pymysql://root:root@localhost/worec'
    db_connection = create_engine(db_connection_str)
    df = pd.read_sql('SELECT aspect, score FROM ASPECT WHERE movie_id = %s' % top_item, con=db_connection).sort_values('score', ascending=False)
    print(df)
    if os.path.isfile(filename_rec):
        aspects_rec_movie = pd.read_csv(filename_rec, usecols=columns).sort_values('score', ascending=False)
        top_rec_aspects = get_n_aspects(5, aspects_rec_movie)
        max = 0
        word_p = ""
        word_r = ""
        movie_pro = 0
        while profile_itens.iloc[i] >= 4:
            p_movie = profile_itens.index[i]
            filename_profile = "../results/movie_" + str(p_movie) + ".csv"
            if os.path.isfile(filename_profile):
                aspects_profile_movie = pd.read_csv(filename_profile, usecols=columns).sort_values('score',
                                                                                                   ascending=False)
                top_profile_aspects = get_n_aspects(5, aspects_profile_movie)

                for p_aspects in top_profile_aspects:
                    for r_aspects in top_rec_aspects:
                        sim = wn.wup_similarity(p_aspects, r_aspects)
                        if sim is not None and sim > max: # TODO sim != 1
                            max = sim
                            movie_pro = p_movie
                            word_p = p_aspects.name().split('.')[0]
                            word_r = r_aspects.name().split('.')[0]

            i = i + 1

    else:
        return "Because you rated well the movie \"" + movie_data_info.loc[top_item][0] + "\" watch \"" + \
               movie_data_info.loc[profile_itens.index[0]][0] + "\""

    movie_pro_name = movie_data_info.loc[movie_pro][0]
    movie_rec_name = movie_data_info.loc[top_item][0]
    print(movie_pro_name)
    print(movie_rec_name)

    if word_p != word_r:
        sentence = "Because you rated well the movie \"" + movie_pro_name + "\" described as \"" \
                   + word_p + "\" watch \"" + movie_rec_name + "\" described with the similar word \"" + word_r + "\""
    else:
        sentence = "Because you rated well the movie \"" + movie_pro_name + "\" described as \"" \
                   + word_p + "\" watch \"" + movie_rec_name + "\" described with the same word"

    return sentence

def generate_explanations(profile_itens: list, top_item: int):
    nltk.download('wordnet')

    db_connection_str = 'mysql+pymysql://root:root@localhost/worec'
    db_connection = create_engine(db_connection_str)

    aspects_rec_movie = pd.read_sql('SELECT aspect, score FROM ASPECT WHERE movie_id = %s' % top_item, con=db_connection).sort_values('score', ascending=False)
    top_rec_aspects = get_n_aspects(5, aspects_rec_movie)
    max = 0
    word_p = ""
    word_r = ""
    movie_pro = 0

    for p_movie in profile_itens:
        aspects_profile_movie = pd.read_sql('SELECT aspect, score FROM aspect WHERE movie_id = %s' % p_movie, con=db_connection).sort_values('score', ascending=False)
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
        mv_data = pd.read_sql('SELECT movie_id, title FROM movie WHERE movie_id in (%s, %s)' % (profile_itens[0], top_item), con=db_connection, index_col='movie_id')
        return "Because you rated well the movie \"" + mv_data['title'][top_item] + "\" watch \"" + \
               mv_data['title'][profile_itens[0]] + "\""

    mv_data = pd.read_sql('SELECT movie_id, title FROM movie WHERE movie_id in (%s, %s)' % (movie_pro, top_item), con=db_connection, index_col='movie_id')

    movie_pro_name = mv_data['title'][movie_pro]
    movie_rec_name = mv_data['title'][top_item]

    if word_p != word_r:
        sentence = "Because you rated well the movie \"" + movie_pro_name + "\" described as \"" \
                   + word_p + "\" watch \"" + movie_rec_name + "\" described with the similar word \"" + word_r + "\""
    else:
        sentence = "Because you rated well the movie \"" + movie_pro_name + "\" described as \"" \
                   + word_p + "\" watch \"" + movie_rec_name + "\" described with the same word"

    return sentence

# nltk.download('wordnet')

# used_columns = ['user_id', 'movie_id', 'rating']

# train_data = pd.read_csv("datasets/train.csv", usecols=used_columns)

# # generate user/item matrix and mean item and transform it into interactions
# user_item = train_data.pivot(index="user_id", columns="movie_id", values="rating")

# rated = user_item.loc[8194].dropna().sort_values(ascending=False)

# # user_item[user_item >= 0] = 1
# # user_item[user_item.isna()] = 0

# # semantic_sim = pd.read_csv("datasets/sim_matrix.csv", header=None)
# # semantic_sim.index = user_item.columns
# # semantic_sim.columns = user_item.columns

# # response, teste = rec.generate_map(3, 5, user_item.loc[8194], semantic_sim)

# data_cols = ['movie_id', 'title']
# movie_data = pd.read_csv("datasets/movies_data.csv", usecols=data_cols)
# movie_data.set_index('movie_id', inplace=True)

# explanation = generate_explanations(rated, 5735, movie_data)
# print(explanation)