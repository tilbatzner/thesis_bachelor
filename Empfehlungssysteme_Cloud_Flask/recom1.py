import pandas as pd
import numpy as np
from scipy.sparse.linalg import svds
from scipy.sparse import csr_matrix

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

