import os
import json
from flask import Flask, request
import requests

import model
import server
import utils

# context = SSL.Context(SSL.PROTOCOL_TLSv1_2)
# context.use_privatekey_file('server.key')
# context.use_certificate_file('server.crt')

app = Flask(__name__)

@app.route("/signup/", methods=['GET', 'POST'])
def signup():
    """
    Accept json={username:username, password:encrypted}
    Store user in db2

    Return verification
    """

    data = request.get_json()
    print(data)
    uname, enc_pass = data['username'], data['password']

    user_id = server.register_user(uname, enc_pass)
    if user_id == "username_exists":
        status = 902
    else:
        status = 900

    data = {'username': uname, 'responsecode': status}
    print(data)
    data = json.dumps(data)
    return data


@app.route("/verify/", methods=['POST'])
def verify_login():
    """
    Accept json={username:username, password:encrypted}
    Check from db2

    Return status (verified-1, not-verified-0)
    """

    data = request.get_json()
    print(data)
    uname, enc_pass = data['username'], data['password']

    matched = server.verify_user(uname, enc_pass)
    if matched is True:
        status = 900
        response = "ok"
    elif matched is False:
        status = 901
        response = "Username or Password Incorrect"
    else:
        status = 903
        response = "Username doesn't exist"

    data = {'username': uname, 'responsecode': status,
        'responsemessage': response}
    print(data)
    data = json.dumps(data)
    return data


@app.route("/register_movies/", methods=['POST'])
def register_movies():
    """
    Accept json={username:username, movies:json_array of imdb ids}
    	Create user in db1 and add movies
    Return status (ok-200, error-903)
    """

    data = request.get_json()
    print(data)
    uname, tmdb_ids = data['username'], data['tmdb_ids']
    ratings = data['ratings']

    check = server.check_user(uname)
    if not check:
        status = 903
        responsemessage = "Username doesn't exist"
    else:
        server.add_user_movies(uname, tmdb_ids, ratings)
        status = 200
        responsemessage = "ok"

    data = {'responsecode': status, 'responsemessage': responsemessage}
    print(data)
    data = json.dumps(data)
    return data


@app.route("/get_user_movies/", methods=['POST'])
def get_user_movies():
    """
    Accept json={username:username}
    Return num movie ids json_array / error code 703-for no history, 903-for username provided 
    """

    data = request.get_json()
    print(data)
    uname = data['username']

    check = server.check_user(uname)
    if not check:
        status = 903
        responsemessage = "Username doesn't exist"
        tmdb_ids, movie_names, ratings = [], [], []
    else:
        try:
            tmdb_ids, ratings = server.get_user_movies_n_ratings(uname)
            movie_ids = server.get_movie_ids(tmdb_ids)
            movie_names = server.get_movie_names(movie_ids)

            status = 200
            responsemessage = "ok"
        except ValueError:
            tmdb_ids, movie_names, ratings = [], [], []
            status = 703
            responsemessage = "History not available"

    data = {'responsecode': status, 'responsemessage': responsemessage,
        'tmdb_ids': tmdb_ids, 'names': movie_names, 'ratings': ratings}
    print(data)
    data = json.dumps(data)
    return data


@app.route("/get_popular_movies/", methods=['POST'])
def get_popular_movies():
    """
    Accept json={num_movies:num, genre:null/genre}
    Return num movie ids json_array
    """

    data = request.get_json()
    print(data)
    num_movies = data['num_movies']
    try:
        genre = data['genre']
    except KeyError:
        genre = None

    try:
        query = data['query']
    except KeyError:
        query = None

    assert genre is None or genre in model.GENRES

    movie_ids = model.get_popular_movies(num_movies, genre, query)
    tmdb_ids = server.get_tmdb_ids(movie_ids)
    movie_names = server.get_movie_names(movie_ids)

    data = {'responsecode': 200, 'responsemessage': "ok",
        'tmdb_ids': tmdb_ids, 'names': movie_names}
    print(data)
    data = json.dumps(data)
    return data


@app.route("/movies_similar_to/", methods=['POST'])
def movies_similar_to():
    """
    Accept json={movie_array:imdb ids json_array, num_result:num}
    Return num movie ids json_array
    """

    data = request.get_json()
    print(data)
    tmdb_ids, num_rec = data['tmdb_ids'], data['num_result']

    movie_ids = server.get_movie_ids(tmdb_ids)
    recc_movie_ids = model.get_recommendations(movie_ids)

    if type(recc_movie_ids) is str:
        return "insufficient_ratings"

    recc_tmdb_ids = server.get_tmdb_ids(recc_movie_ids)
    recc_movie_names = server.get_movie_names(recc_movie_ids)

    data = {'tmdb_ids': recc_tmdb_ids, 'names': recc_movie_names}
    print(data)
    data = json.dumps(data)
    return data


@app.route("/recommend_movies_to_user/", methods=['POST'])
def recommend_movies_to_user():
    """
    Accept json={username:username, num_result:num}
    Return num movie ids json_array
    """

    data = request.get_json()
    print(data)
    uname = data['username']

    check = server.check_user(uname)
    if not check:
        status = 903
        responsemessage = "Username doesn't exist"
        recc_tmdb_ids, recc_movie_names = [], []
    else:
        try:
            tmdb_ids, ratings = server.get_user_movies_n_ratings(uname)
            movie_ids = server.get_movie_ids(tmdb_ids)
            recc_movie_ids = model.get_recommendations(utils.get_zipped(movie_ids, ratings))
            if type(recc_movie_ids) is str:  # KeyError
                status = 601
                responsemessage = "Insufficient Ratings"
                recc_tmdb_ids, recc_movie_names = [], []
            else:  # All OK
                status = 200
                responsemessage = "ok"
                recc_tmdb_ids = server.get_tmdb_ids(recc_movie_ids)
                recc_movie_names = server.get_movie_names(recc_movie_ids)
        except ValueError:  # User had not rated movies yet
            status = 703
            responsemessage = "History not available"
            recc_tmdb_ids, recc_movie_names = [], []

    data = {'responsecode': status, 'responsemessage': responsemessage,
        'tmdb_ids': recc_tmdb_ids, 'names': recc_movie_names}
    print(data)
    data = json.dumps(data)
    return data

@app.route("/search/person/", methods=['GET','POST'])
def search_person():
	"""
	Accept json={query="query string"}
	Return(json object) =
	{
		"page":1,
		"total_results":157,
		"total_pages":8,
		"results":{
			[                 # array of person
				"known_for_department":"Acting",
				"gender":1,
				"popularity":5.1,
				"id":7825,
				"name":"name"
				"known_for":[  # array of related movies
					{
					"title":"movie name",
					"id":45,   //tmdb_id
					"vote_average":5.2,
					"vote_count":5000,
					"release_date":"2011-07-22",
					"original_language":"en",
					"poster_path":"/6bA8p6O4s9uhmCYqat2obcpPHXr.jpg",
					"popularity":12.3 //popularity index (only for comparison)
					}
				]
			]
		 
	"""
	data = request.get_json()
	if data is None:
		return json.dumps('{error:bad argument}')
	if 'query' not in data:
		return json.dumps('{error:bad argument}')
	query_string = data['query']
	r = requests.get("https://api.themoviedb.org/3/search/person?api_key=f6f1784088c8c27e9fa707584a1a1d34&language=en-US&page=1&include_adult=false&query="+query_string)
	r = json.loads(r.text)
	for item in r["results"]:
		del item["adult"]
		for x in item["known_for"]:
			del x['genre_ids']
			del x['overview']
	return json.dumps(r)

@app.route("/search/movie/", methods = ['GET', 'POST'])
def search_movie():
	"""
	Accept json={query="query string"}
	Return(json object) =
	{
		"page":1,
		"total_results":157,
		"total_pages":8,
		"results":{
			[                 # array of movie details
				{
				"title":"movie name",
				"id":45,   //tmdb_id
				"vote_average":5.2,
				"vote_count":5000,
				"release_date":"2011-07-22",
				"original_language":"en",
				"poster_path":"/6bA8p6O4s9uhmCYqat2obcpPHXr.jpg",
				"popularity":12.3 //popularity index (only for comparison)
				}
			]
		}
	}
	"""
	data = request.get_json()
	if data is None:
		return json.dumps('{error:bad argument}')
	if 'query' not in data:
		return json.dumps('{error:bad argument}')
	query_string = data['query']
	r = requests.get("https://api.themoviedb.org/3/search/movie?api_key=f6f1784088c8c27e9fa707584a1a1d34&language=en-US&page=1&include_adult=false&query="+query_string)
	r = json.loads(r.text)
	for item in r["results"]:
		del item['overview']
		del item['genre_ids']
		del item['video']
		del item['backdrop_path']
	return json.dumps(r)

@app.route("/search/tv/", methods=['GET','POST'])
def search_tv():
	"""
	Accept json={query="query string"}
	Return(json object) =
	{
		"page":1,
		"total_results":157,
		"total_pages":8,
		"results":{
			[                 # array of movie details
				{
				"name":"tv name",
				"original_name":"name",
				"id":45,   //tmdb_id
				"vote_average":5.2,
				"vote_count":5000,
				"first_air_date":"2011-07-22",
				"original_language":"en",
				"poster_path":"/6bA8p6O4s9uhmCYqat2obcpPHXr.jpg",
				"popularity":12.3 //popularity index (only for comparison)
				}
			]
		}
	}
	"""
	data = request.get_json()
	if data is None:
		return json.dumps('{error:bad argument}')
	if 'query' not in data:
		return json.dumps('{error:bad argument}')
	query_string = data['query']
	r = requests.get("https://api.themoviedb.org/3/search/tv?api_key=f6f1784088c8c27e9fa707584a1a1d34&language=en-US&page=1&include_adult=false&query="+query_string)
	r = json.loads(r.text)
	for item in r["results"]:
		del item['overview']
		del item['genre_ids']
		del item['backdrop_path']
	return json.dumps(r)

@app.route("/")
def root():
    return "I'm gROOT"


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=False, ssl_context=('server.crt','server.key'))

    if 'popularity.csv' not in os.listdir('dataset/'):
        print('popularity.csv not present')
