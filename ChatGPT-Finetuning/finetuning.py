import pandas as pd
import json
import random

def process_csv_to_jsonl(filename, output_filename, num_combinations=3):
    df = pd.read_csv(filename)

    with open(output_filename, 'w', encoding='utf-8') as f:
        for user_id, group in df.groupby('user_id'):
            all_movies = list(group['title'])
            genres_and_tags = {row['title']: (row['genre'], row['tags']) for _, row in group.iterrows()}

            for _ in range(num_combinations):
                if len(all_movies) < 10:
                    selected_movies = random.choices(all_movies, k=10) 
                else:
                    selected_movies = random.sample(all_movies, 10)  

                input_movies = selected_movies[:6]
                output_movies = selected_movies[6:10]

                input_formatted = "; ".join([
                    f"Title: {movie}; Genres: {genres_and_tags[movie][0]}" +
                    (f"; Tags: {genres_and_tags[movie][1]}" if pd.notna(genres_and_tags[movie][1]) else "")
                    for movie in input_movies
                ])
                
                output_formatted = "; ".join(output_movies)

                result = {
                    "messages": [
                        {
                            "role": "system",
                            "content": "This chatbot gives personalized movie recommendations based on users' favourite movies. The model outputs 4 different movie suggestions without further information separated by semicolon."
                        },
                        {
                            "role": "user",
                            "content": f"I like these movies the most: {input_formatted}"
                        },
                        {
                            "role": "assistant",
                            "content": output_formatted
                        }
                    ]
                }

                json.dump(result, f, ensure_ascii=False)
                f.write("\n")

process_csv_to_jsonl('ratings_combined.csv', 'data_finetuning.jsonl', num_combinations=5)
