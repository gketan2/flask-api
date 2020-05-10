import pandas as pd
ratings = pd.read_csv('dataset/ratings.csv')
movies = pd.read_csv('dataset/movies.csv')
links = pd.read_csv('dataset/links.csv')
ratings = pd.merge(movies,ratings).drop(['timestamp'],axis=1)

userRatings2=ratings.drop("userId",axis=1)
userRatings2=userRatings2.groupby(['movieId','genres']).sum().reset_index()
userRatings2=userRatings2.sort_values('rating',ascending=False)
userRatings2=userRatings2.drop(["rating"],axis=1)
userRatings2.to_csv("dataset/popularity.csv")
