import numpy as np
import pandas as pd
from src.connection import db_connection
from random import randrange
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
    df = pd.read_sql(most_watched_stmt(), con=db_connection)
    df['imdbID'] = df['imdbID'].map('tt{0:07d}'.format)
    return df.to_json(orient="records")

def most_watched_stmt():   
    
    
    top_m = ['120737', '167261', '167260', '126029', '172495', '378194', '209144', '325980', '145487', '181689', 
             '266543', '240772', '338013', '190332', '372784', '268978', '317705', '438488', '120903', '198781', 
             '317919', '211915', '258463', '335266', '401792', '234215', '264464', '190590', '246578', '121765', 
             '434409', '298148', '290334', '121766', '208092', '241527', '305357', '162222', '295297', '181865', 
             '372183', '212338', '381061', '319061', '310793', '242653', '407887', '375679', '217869', '180093', 
             '181875', '146882', '360717', '383574', '120630', '268380', '325710', '449059', '289043', '343818', 
             '212720', '330373', '195685', '286106', '265666', '407304', '405159', '361596', '203009', '413099', 
             '243155', '454848', '317740', '298130', '367594', '245429', '390521', '268126', '333766', '332379', 
             '405422', '365748', '443453', '482571', '375063', '120912', '457430', '259446', '363771', '416449', 
             '289879', '356910', '427944', '369339', '253474', '327056', '166924', '181852', '376994', '395169', 
             '299977', '187393', '308644', '396269', '314331', '358273', '257044', '276751', '265086', '468569', 
             '440963', '299658', '259711', '311113', '379786', '374900', '250494', '477348', '295178', '187078', 
             '217505', '388795', '349903', '278504', '146316', '382625', '175142', '258000', '286499', '212346', 
             '332452', '338751', '362270', '312004', '167190', '139654', '425112', '319262', '467406', '196229', 
             '408306', '362227', '213149', '462538', '399295', '382932', '207201', '177971', '443543', '337978']
    
    ids = ''
    n_shown = 50
    for i in range(n_shown):
        i_chosen = randrange(n_shown)
        if i != n_shown - 1:
            ids = ids + top_m[i_chosen] + ', '
        else:
            ids = ids + top_m[i_chosen]
    
    return 'SELECT movie_id, imdbID, title Title, year Year, poster Poster FROM MOVIE WHERE poster != \'N\' and imdbID in ({0}) order by rand()'.format(ids)