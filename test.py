import tmdbsimple as tmdb

tmdb.API_KEY = "0246f51251084309309901ae3bf1a0f2"  # Replace with your actual key


movie = tmdb.Movies(603)
response = movie.info()
print(movie.title)
