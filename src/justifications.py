from src.connection import db_connection

def insert_rate(rate):
    with db_connection.connect() as conn:
        with conn.begin():
           conn.execute(insert_rate_stmt(rate))

def insert_rate_stmt(rate):
    return "INSERT INTO RECJUST (user_id,movie_id,liked,understood,words,interested,confidence,discover) VALUES({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7})".format(rate['user_id'],rate['movie_id'],rate['liked'],rate['understood'],rate['words'],rate['interested'],rate['confidence'],rate['discover'])

def insert_comp(comp):
    with db_connection.connect() as conn:
        with conn.begin():
           conn.execute(insert_comp_stmt(comp))

def insert_comp_stmt(comp):
    return "INSERT INTO JUSTCOMP (user_id,movie_id,convincing,understood,discover,commentrec,commentjust) VALUES({0}, {1}, {2}, {3}, {4}, '{5}', '{6}')".format(comp['user_id'],comp['movie_id'],comp['convincing'],comp['understood'],comp['discover'],comp['commentrec'],comp['commentjust'])