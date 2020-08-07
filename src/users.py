from src.connection import db_connection

def insert_user(user):
    result = None
    with db_connection.connect() as conn:
        with conn.begin():
            result = conn.execute(insert_user_stmt(user)).lastrowid
    return result

def insert_user_stmt(user):
    return "INSERT INTO USER (age,gender,education,usedRecSys,terms_accept) VALUES({0}, {1}, {2}, {3}, {4})".format(user['age'],user['gender'],user['education'],user['usedRecSys'],user['terms_accept'])

def insert_user(user_id, movie: list):
    with db_connection.connect() as conn:
        with conn.begin():
            for m in movie:
                conn.execute(insert_user_movie_stmt(user_id, m))

def insert_user_movie_stmt(user_id, movie_id):
    return "INSERT INTO USERMOVIE (user_id, movie_id) VALUES({0}, {1})".format(user_id, movie_id)