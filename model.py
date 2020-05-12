import pandas as pd
import gc


ratings = pd.read_csv('dataset/ratings.csv')
movies = pd.read_csv('dataset/movies.csv')
links = pd.read_csv('dataset/links.csv')
f = pd.read_csv("dataset/popularity.csv")
ratings = pd.merge(movies,ratings).drop(['timestamp'],axis=1)

GENRES = ["Action","Adventure","Animation","Children's","Comedy","Crime","Documentary","Drama",
	"Fantasy","Film-Noir","Horror","Musical","Mystery","Romance","Sci-Fi","Thriller","War","Western"]

userRatings = ratings.pivot_table(index=['userId'],columns=['movieId'],values='rating')
userRatings = userRatings.dropna(thresh=10, axis=1).fillna(0,axis=1)
corrMatrix = userRatings.corr(method='pearson')

del ratings
gc.collect()


def get_similar(movieId,rating):
	similar_ratings = corrMatrix[movieId]*(rating-2.5)
	similar_ratings = similar_ratings.sort_values(ascending=False)
	return similar_ratings   


def get_recommendations(movie_list):
	similar_movies = pd.DataFrame()	
	ids=[]

	for Id,rating in movie_list:
		try:
			similar_movies = similar_movies.append(get_similar(Id,float(rating)),ignore_index = True)
			ids.append(Id)
		except KeyError:
			pass

	similar_movies=similar_movies.sum().sort_values(ascending=False)[0:10]
	sim=pd.DataFrame(similar_movies)
	sim.movie=sim.index
	sim.reset_index(level=0, inplace=True)
	sim=sim["index"]
	sim=set(sim.tolist())
	sim=sim-set(ids)

	if len(sim):
		return list(sim)
	return "insufficient_ratings"


def get_popular_movies(num_movies, genre=None, query=None, df=f):
	ids=[]
	if genre and query:
		f=df[(df["genres"].str.contains(genre)) & (df["title"].str.lower().str.contains(query.lower()))].reset_index()
	elif genre:
		f=df[df["genres"].str.contains(genre)].reset_index()
	elif query:
		f=df[df["title"].str.lower().str.contains(query.lower())].reset_index()
	else:
		f=df.reset_index()
	f=f.ix[0:num_movies,"movieId"]
	ids=f.tolist()
	return ids

if __name__=="__main__":
	def create_popularity_csv():
		userRatings2=ratings.drop("userId",axis=1)
		userRatings2=userRatings2.groupby(['movieId','genres']).sum().reset_index()
		userRatings2=userRatings2.sort_values('rating',ascending=False)
		userRatings2=userRatings2.drop(["rating"],axis=1)
		userRatings2.to_csv("dataset/popularity.csv")

	create_popularity_csv()

