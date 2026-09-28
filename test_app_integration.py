import pickle
import pandas as pd
import numpy as np

def test_integration():
    with open("movies.pkl", "rb") as f:
        movies = pickle.load(f)

    with open("similarity.pkl", "rb") as f:
        similarity = pickle.load(f)

    print("Movies type:", type(movies), "shape:", movies.shape)
    print("Movies columns:", list(movies.columns))
    print("Similarity type:", type(similarity), "shape:", similarity.shape)
    print("Null titles:", movies["title"].isnull().sum())
    print("Null movie_id:", movies["movie_id"].isnull().sum())

    def recommend(movie):
        movie_indices = movies[movies["title"] == movie].index
        if len(movie_indices) == 0:
            return []
        index = movie_indices[0]
        distances = similarity[index]
        movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        recommendations = []
        for i in movie_list:
            movie_index = i[0]
            movie_title = movies.iloc[movie_index]["title"]
            movie_id = movies.iloc[movie_index]["movie_id"]
            recommendations.append({
                "title": movie_title,
                "movie_id": movie_id,
                "score": distances[movie_index]
            })
        return recommendations

    test_movies = ["Toy Story (1995)", "Matrix, The (1999)", "Godfather, The (1972)", "Fight Club (1999)", "Inception (2010)"]
    for tm in test_movies:
        recs = recommend(tm)
        assert len(recs) == 5, f"Expected 5 recommendations, got {len(recs)}"
        assert all(r["title"] != tm for r in recs), "Self recommendation detected!"
        print(f"\nRecommendations for '{tm}':")
        for r in recs:
            print(f"  -> {r['title']} (ID: {r['movie_id']}, Score: {r['score']:.4f})")

    print("\nAll integration checks PASSED successfully!")

if __name__ == "__main__":
    test_integration()
