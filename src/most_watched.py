import numpy as np
import pandas as pd
from src.connection import db_connection
import os

def get_mostwatched():
    train_data = pd.read_csv("datasets/ratings.dat", header=None, names=['user_id', 'movie_id', 'rating'], sep='\t')

    # dropping duplicate values 
    train_data = train_data.sort_values(by='rating').drop_duplicates(subset=['user_id', 'movie_id'])

    # generate user/item matrix and mean item and transform it into interactions
    user_item = train_data.pivot(index="user_id", columns="movie_id", values="rating")
    user_item[user_item >= 0] = 1
    user_item[user_item.isna()] = 0

    # return a data_frame with the number of times for each movie_id was interacted
    times_seen = user_item.sum(axis=0)
    times_seen = times_seen.sort_values(ascending=False)

    # topn is a np.arrray with the top n (number) most watched films 
    number = 10
    topn = np.array(times_seen.index[:number])

    # get data of all films and set index as movie id
    movie_data = pd.read_csv("datasets/movies_data.csv")
    movie_data.index = movie_data.movie_id

    # create imbs_id_vec that contains the ids of the most watched films
    # if imbd_id has len of 6 than add a zero to the start since imdb_id
    # has tt + 7 digits
    imdb_id_vec = []
    for m in topn:
        m_data = movie_data.loc[m]
        m_imbd = str(m_data['imdb_id'])
        if len(m_imbd) < 7:
            imbd_id_str = "tt0" + m_imbd
        else:
            imbd_id_str = "tt" + m_imbd
            
        imdb_id_vec.append(imbd_id_str)
    
    return imdb_id_vec

def get_mostwatchedfromdb():
    df = pd.read_sql('SELECT movie_id, imdbID, title Title, year Year, poster Poster FROM MOVIE WHERE poster IS NOT NULL', con=db_connection)
    df['imdbID'] = df['imdbID'].map('tt{0:07d}'.format)
    return df.to_json(orient="records")
