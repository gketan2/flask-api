import sqlite3

import utils


conn = sqlite3.connect('database', check_same_thread=False)

def register_user(uname, enc_pass): 
    query = """INSERT INTO USERS (username, password)
        VALUES ('{}', '{}')""".format(uname, enc_pass)
    try:
        conn.execute(query)
    except sqlite3.IntegrityError:
        return "username_exists"
    conn.commit()


def verify_user(uname, enc_pass):
    query = """SELECT password
        FROM USERS
        WHERE username = '{}'""".format(uname)

    cursor = conn.execute(query)
    data = cursor.fetchall()

    try:
        password = data[0][0]
    except IndexError:
        return "username_do_not_exists"

    if password == enc_pass:
        return True
    return False


def check_user(uname):
    query = """SELECT *
        FROM USERS
        WHERE username = '{}'""".format(uname)

    cursor = conn.execute(query)
    data = cursor.fetchall()

    if len(data):
        return True
    return False


def add_user_movies(uname, tmdb_ids, ratings):
    assert len(tmdb_ids)==len(ratings)

    for tmdb_id, rating in utils.get_zipped(tmdb_ids, ratings):
        query = """INSERT INTO MOVIES (username, tmdb_id, rating)
        VALUES ('{}', {}, {})""".format(uname, tmdb_id, rating)
        conn.execute(query)

    conn.commit()


def get_user_movies_n_ratings(uname):
    query = """SELECT tmdb_id, rating
        FROM MOVIES
        WHERE username = '{}'""".format(uname)

    cursor = conn.execute(query)
    data = cursor.fetchall()
    return utils.get_unzipped(data)


def get_tmdb_ids(movie_ids):
    tmdb_ids = []
    for id in movie_ids:
        tmdb_ids.append(utils.get_tmdb_id(id))
    return tmdb_ids


def get_movie_ids(tmdb_ids):
    movie_ids = []
    for id in tmdb_ids:
        movie_ids.append(utils.get_movie_id(id))
    return movie_ids


def get_movie_names(movie_ids):
    movie_names = []
    for id in movie_ids:
        movie_names.append(utils.get_movie_name(id))
    return movie_names

