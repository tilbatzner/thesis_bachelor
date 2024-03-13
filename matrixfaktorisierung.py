import pandas as pd
import numpy as np
from scipy.sparse.linalg import svds
from scipy.sparse import csr_matrix

# Laden der Daten
movies = pd.read_csv('ml-latest-small/movies.csv')
ratings = pd.read_csv('ml-latest-small/ratings.csv')

# Vorbereiten der Daten
movie_ratings = pd.merge(movies, ratings, on='movieId')
user_movie_matrix = movie_ratings.pivot_table(index='userId', columns='title', values='rating').fillna(0)

# Konvertierung in eine Sparse-Matrix
user_movie_sparse = csr_matrix(user_movie_matrix.values)

# Durchführen der SVD
U, sigma, Vt = svds(user_movie_sparse, k=50) # k ist die Anzahl der zu extrahierenden Faktoren

# Konvertierung von Sigma in eine Diagonalmatrix
sigma = np.diag(sigma)

# Vorhersagen der Nutzerbewertungen
predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_movie_matrix.mean(axis=1).values.reshape(-1, 1)

# Konvertierung der Vorhersagen zurück in ein DataFrame
preds_df = pd.DataFrame(predicted_ratings, columns=user_movie_matrix.columns)

def recommend_movies(preds_df, userID, movies_df, original_ratings_df, num_recommendations=5):
    # Index des Nutzers abrufen
    user_idx = userID - 1 # UserID beginnt bei 1, Python-Index bei 0

    # Die Vorhersagen für diesen Nutzer abrufen und in ein DataFrame umwandeln
    sorted_user_predictions = preds_df.iloc[user_idx].sort_values(ascending=False).reset_index()

    # Informationen über die vom Nutzer bereits bewerteten Filme holen
    user_data = original_ratings_df[original_ratings_df.userId == (userID)]
    user_full = (user_data.merge(movies_df, how='left', left_on='movieId', right_on='movieId').
                 sort_values(['rating'], ascending=False))

    # Empfehlungen, die der Nutzer noch nicht gesehen hat, empfehlen
    recommendations = (movies_df[~movies_df['movieId'].isin(user_full['movieId'])].
                       merge(pd.DataFrame(sorted_user_predictions).rename(columns={user_idx: 'Predictions'}),
                             how='left',
                             left_on='title',
                             right_on='title').
                       sort_values('Predictions', ascending=False).
                       iloc[:num_recommendations, :-1])

    return user_full, recommendations

# Beispiel für die Nutzung der Empfehlungsfunktion für einen Nutzer mit ID 1
already_rated, predictions = recommend_movies(preds_df, 611, movies, ratings, 5)

# Ausgabe der bereits bewerteten Filme des Nutzers
print("Bereits bewertete Filme von Nutzer 1:")
print(already_rated)

# Ausgabe der Filmempfehlungen für den Nutzer
print("\nEmpfohlene Filme für Nutzer 1:")
print(predictions)
# Extraktion der Movie IDs aus den Empfehlungen
recommended_movie_ids = predictions['movieId'].tolist()

# Umwandlung in einen kommagetrennten String
recommended_movie_ids_str = ', '.join(map(str, recommended_movie_ids))

print("Empfohlene Movie IDs für Nutzer 611:")
print(recommended_movie_ids_str)
