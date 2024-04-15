import pandas as pd
from joblib import load

def recommend_movies_combined(movie_ids, num_recommendations=5):
    # Laden der vorverarbeiteten DatenFrames
    combined_sim = pd.read_pickle('combined_sim.pkl')

    sim_scores_combined_list = []  # Liste zum Sammeln der Serien
    for movie_id in movie_ids:
        if movie_id in combined_sim.index:
            sim_scores = combined_sim.loc[movie_id]
            sim_scores_combined_list.append(sim_scores)  # Füge die Serie zur Liste hinzu

    sim_scores_combined = pd.concat(sim_scores_combined_list, axis=1).mean(axis=1)  # Konkateniere und berechne den Mittelwert über die Spalten
    movie_indices = [idx for idx in movie_ids if idx in combined_sim.index]
    sim_scores_combined = sim_scores_combined.drop(movie_indices, errors='ignore')  # Entferne die ursprünglichen Film-IDs

    recommended_indices = sim_scores_combined.sort_values(ascending=False).head(num_recommendations).index
    recommended_movie_ids = recommended_indices.tolist()  # Konvertiere in Liste

    # Konvertiere die Liste der movieIds in einen kommagetrennten String
    recommended_movie_ids_str = ', '.join(map(str, recommended_movie_ids))

    return recommended_movie_ids_str

