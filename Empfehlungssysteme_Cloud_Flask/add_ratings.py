import pandas as pd
from datetime import datetime


def add_ratings(user_ratings):
    """
    Erzeugt einen DataFrame mit neuen Bewertungen für einen neuen Benutzer.

    :param user_ratings: Eine Liste von Film-IDs, für die Bewertungen hinzugefügt werden sollen.
    :return: Eine Tuple bestehend aus der neuen Benutzer-ID und dem DataFrame mit den neuen Bewertungen.
    """

    new_user_id = 614  # Beispiel für eine neue Benutzer-ID

    # Standardbewertung und Zeitstempel
    default_rating = 5.0
    timestamp = int(datetime.now().timestamp())

    # Erstellen neuer Bewertungen für den neuen Benutzer
    new_ratings = []
    for movie_id in user_ratings:
        new_ratings.append([new_user_id, movie_id, default_rating, timestamp])

    # Erstellen eines DataFrames mit den neuen Bewertungen
    new_ratings_df = pd.DataFrame(new_ratings, columns=['userId', 'movieId', 'rating', 'timestamp'])
    return new_user_id, new_ratings_df

