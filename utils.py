import pandas as pd

from model import movies, links


def get_tmdb_id(movie_id):
	id = links[links.movieId==movie_id].tmdbId
	return int(id.item())


def get_movie_id(tmdb_id):
    id = links[links.tmdbId==int(tmdb_id)].movieId
    return int(id.item())


def get_movie_name(movie_id):
    id = movies[movies.movieId==movie_id].title
    return id.item()


def get_zipped(col1, col2):
    return zip(col1, col2)


def get_unzipped(zipped):
    return list((zip(*zipped)))