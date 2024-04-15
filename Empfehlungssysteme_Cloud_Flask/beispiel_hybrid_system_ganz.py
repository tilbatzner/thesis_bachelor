import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer


def recommend_movies_combined(movie_ids, num_recommendations=5):
    # Lade die Daten
    movies = pd.read_csv('ml-latest-small/movies.csv')
    ratings = pd.read_csv('ml-latest-small/ratings.csv')
    tags = pd.read_csv('ml-latest-small/tags.csv')

    # Bereinige die Tags-Daten
    tags_combined = tags.groupby('movieId')['tag'].apply(lambda x: ' '.join(x.astype(str))).reset_index()

    # Füge die zusammengefassten Tags zu den Filmdaten hinzu
    movies_with_tags = pd.merge(movies, tags_combined, on='movieId', how='left')
    movies_with_tags['tag'] = movies_with_tags['tag'].fillna('')

    # Verarbeite die Genres
    movies_with_tags['genres'] = movies_with_tags['genres'].str.replace('|', ' ')

    # Verwende TF-IDF für die Tags und Genres
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix_tags = tfidf.fit_transform(movies_with_tags['tag'])
    tfidf_matrix_genres = tfidf.fit_transform(movies_with_tags['genres'])

    # Berechne die Cosinus-Ähnlichkeit basierend auf den Tags
    cosine_sim_tags = linear_kernel(tfidf_matrix_tags, tfidf_matrix_tags)

    # Berechne die Cosinus-Ähnlichkeit basierend auf den Genres
    cosine_sim_genres = linear_kernel(tfidf_matrix_genres, tfidf_matrix_genres)

    # Erstelle eine Nutzer-Film-Bewertungsmatrix
    ratings_matrix = ratings.pivot_table(index='movieId', columns='userId', values='rating').fillna(0)
    movie_user_matrix_sparse = csr_matrix(ratings_matrix.values)

    # Berechne die Cosinus-Ähnlichkeit basierend auf den Bewertungen
    cosine_sim_ratings = cosine_similarity(movie_user_matrix_sparse, movie_user_matrix_sparse)

    # Erstelle DataFrame aus den Ähnlichkeitsmatrizen, um leichter zu kombinieren
    cosine_sim_tags_df = pd.DataFrame(cosine_sim_tags, index=movies_with_tags['movieId'], columns=movies_with_tags['movieId'])
    cosine_sim_genres_df = pd.DataFrame(cosine_sim_genres, index=movies_with_tags['movieId'], columns=movies_with_tags['movieId'])
    cosine_sim_ratings_df = pd.DataFrame(cosine_sim_ratings, index=ratings_matrix.index, columns=ratings_matrix.index)

    # Kombiniere die Ähnlichkeitsmatrizen mit gewichteten Summen
    weight_ratings = 0.50
    weight_genres = 0.30
    weight_tags = 0.20

    # Stelle sicher, dass alle Matrizen dieselben Indizes haben
    combined_index = cosine_sim_tags_df.index.intersection(cosine_sim_genres_df.index).intersection(cosine_sim_ratings_df.index)
    cosine_sim_tags_df = cosine_sim_tags_df.loc[combined_index, combined_index]
    cosine_sim_genres_df = cosine_sim_genres_df.loc[combined_index, combined_index]
    cosine_sim_ratings_df = cosine_sim_ratings_df.loc[combined_index, combined_index]

    combined_sim = (weight_tags * cosine_sim_tags_df) + (weight_genres * cosine_sim_genres_df) + (weight_ratings * cosine_sim_ratings_df)


    sim_scores_combined_list = []  
    for movie_id in movie_ids:
        if movie_id in combined_sim.index:
            sim_scores = combined_sim.loc[movie_id]
            sim_scores_combined_list.append(sim_scores)  

    sim_scores_combined = pd.concat(sim_scores_combined_list, axis=1).mean(axis=1) 
    movie_indices = [idx for idx in movie_ids if idx in combined_sim.index]
    sim_scores_combined = sim_scores_combined.drop(movie_indices, errors='ignore') 

    recommended_indices = sim_scores_combined.sort_values(ascending=False).head(num_recommendations).index
    recommended_movie_ids = recommended_indices.tolist()  

    # Konvertiere die Liste der movieIds in einen kommagetrennten String
    recommended_movie_ids_str = ', '.join(map(str, recommended_movie_ids))

    return recommended_movie_ids_str

# Beispiel: Empfehle Filme basierend auf diesen Film-IDs
example_movie_ids = [79132, 356, 109487, 53972, 114662, 65802]
recommended_movie_ids_str = recommend_movies_combined(example_movie_ids, 5)
print(recommended_movie_ids_str)