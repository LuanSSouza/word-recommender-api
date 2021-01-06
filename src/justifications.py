from src.connection import db_connection

def insert_rate(user_id, rates: dict):
    with db_connection.connect() as conn:
        with conn.begin():
            conn.execute(insert_rate_stmt(user_id,rates))

def insert_rate_stmt(user_id, rate):
    return "INSERT INTO RECCOMP (user_id, reclist1_id, reclist2_id, quality, diversity, serendipity, reclist1, reclist2) VALUES({0}, {1}, {2}, {3}, {4}, {5}, '{6}', '{7}')".format(user_id, rate['reclist1_id'],rate['reclist2_id'],rate['quality'],rate['diversity'],rate['serendipity'],rate['reclist1'],rate['reclist2'])

def insert_comp(user_id, comps: list):
    with db_connection.connect() as conn:
        with conn.begin():
            for comp in comps:
                conn.execute(insert_comp_stmt(user_id, comp))

def insert_comp_stmt(user_id, comp):
    return "INSERT INTO JUSTCOMP (user_id,movie_id,convincing,understood,discover,commentrec,commentjust) VALUES({0}, {1}, {2}, {3}, {4}, '{5}', '{6}')".format(user_id,comp['movie_id'],comp['convincing'],comp['understood'],comp['discover'],comp['commentrec'],comp['commentjust'])