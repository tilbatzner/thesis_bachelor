from flask import Flask, request, jsonify
import pandas as pd
from scipy.sparse.linalg import svds
from scipy.sparse import csr_matrix
from add_ratings import add_ratings
from recom1 import recommend_movies
import pandas as pd
from datetime import datetime
import numpy as np
from combination import recommend_movies_combined

app = Flask(__name__)

# API-Key-Handling wurde vereinfacht, da es nur für wissenschaftliche Zwecke eingesetzt wird und nicht für operative Anwendung
API_KEY = "test"

def validate_api_key(key):
    return key == API_KEY

@app.route('/recommend', methods=['POST'])
def recommend():
    api_key = request.headers.get('API-Key')
    if not api_key or not validate_api_key(api_key):
        return jsonify({"error": "Ungültiger oder fehlender API-Schlüssel"}), 401

    data = request.json
    user_ratings = data.get('movie_ids')
    if not user_ratings:
        return jsonify({"error": "Keine Filme angegeben"}), 400

    # Übergeben Sie die Liste der Film-IDs
    new_user_id, new_ratings_df = add_ratings(user_ratings)

    # Laden und Vorbereiten der Daten
    movies = pd.read_csv('ml-latest-small/movies.csv')
    ratings = pd.read_csv('ml-latest-small/ratings.csv')

    # Anhängen der neuen Bewertungen an die ratings DataFrame
    ratings = pd.concat([ratings, new_ratings_df]).reset_index(drop=True)

    movie_ratings = pd.merge(movies, ratings, on='movieId')
    user_movie_matrix = movie_ratings.pivot_table(index='userId', columns='title', values='rating').fillna(0)

    user_movie_sparse = csr_matrix(user_movie_matrix.values)
    U, sigma, Vt = svds(user_movie_sparse, k=50)
    sigma = np.diag(sigma)

    predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_movie_matrix.mean(axis=1).values.reshape(-1, 1)
    preds_df = pd.DataFrame(predicted_ratings, columns=user_movie_matrix.columns)

    _, predictions = recommend_movies(preds_df, new_user_id, movies, ratings, 4)
    recommended_movie_ids = predictions['movieId'].tolist()
    recommended_movie_ids_str = ', '.join(map(str, recommended_movie_ids))

    return jsonify({"recommended_movie_ids": recommended_movie_ids_str})

@app.route('/recommend2', methods=['POST'])
def recommend2():
    api_key = request.headers.get('API-Key')
    if not api_key or not validate_api_key(api_key):
        return jsonify({"error": "Ungültiger oder fehlender API-Schlüssel"}), 401

    data = request.json
    user_ratings = data.get('movie_ids')
    if not user_ratings:
        return jsonify({"error": "Keine Filme angegeben"}), 400
    recomms = recommend_movies_combined(user_ratings,4)
    return jsonify({"recommended_movie_ids": recomms})

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)
