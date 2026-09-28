import os
import re
import time
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def run_experiment():
    print("Starting recommendation model experiment...")
    t_start = time.time()
    
    # 1. Load data
    print("Loading dataset...")
    movies = pd.read_csv("movies.csv")
    links_path = "data/links.csv"
    if os.path.exists(links_path):
        links = pd.read_csv(links_path)
    else:
        links = pd.DataFrame(columns=["movieId", "tmdbId"])

    print(f"Total raw movies: {len(movies)}")
    
    # Fast aggregation of ratings
    print("Aggregating ratings for popularity & Bayesian rating...")
    chunks = []
    for chunk in pd.read_csv("ratings.csv", usecols=["movieId", "rating"], chunksize=5000000):
        agg = chunk.groupby("movieId").agg(count=("rating", "count"), sum=("rating", "sum")).reset_index()
        chunks.append(agg)
    all_agg = pd.concat(chunks).groupby("movieId").sum().reset_index()
    all_agg["rating_mean"] = (all_agg["sum"] / all_agg["count"]).round(2)

    movies = movies.merge(all_agg[["movieId", "count", "rating_mean"]], on="movieId", how="left")
    movies["rating_count"] = movies["count"].fillna(0).astype(int)
    movies["rating_mean"] = movies["rating_mean"].fillna(0)
    movies = movies.merge(links[["movieId", "tmdbId"]], on="movieId", how="left")

    # Filter movies: valid genres and top 6000 by popularity + quality
    filtered = movies[movies["genres"] != "(no genres listed)"].copy()
    filtered = filtered.sort_values(by=["rating_count", "rating_mean"], ascending=[False, False])
    df = filtered.head(6000).copy().reset_index(drop=True)
    
    # Ensure movie_id column is present and properly mapped
    df["movie_id"] = df["tmdbId"].fillna(df["movieId"]).astype(int)

    print(f"Selected {len(df)} movies for indexing (min rating count: {df['rating_count'].min()})")

    # 2. Feature engineering
    print("Engineering features & metadata soup...")
    def format_title(title):
        m = re.match(r"^(.*?),\s*(The|A|An)\s*(\(\d{4}\))?$", str(title).strip())
        if m:
            prefix = m.group(2)
            main = m.group(1)
            year = m.group(3) or ""
            return f"{prefix} {main} {year}".strip()
        return str(title).strip()

    def get_clean_name(title):
        t = re.sub(r"\s*\(\d{4}\)", "", str(title))
        m = re.match(r"^(.*?),\s*(The|A|An)$", t.strip())
        if m:
            t = f"{m.group(2)} {m.group(1)}"
        return t.strip()

    def get_year(title):
        m = re.search(r"\((\d{4})\)", str(title))
        return int(m.group(1)) if m else 2000

    def get_franchise(clean_name):
        parts = re.split(r"[:\-–]", clean_name)
        if len(parts) > 1 and len(parts[0].strip()) > 2:
            return "franchise_" + re.sub(r"[^a-zA-Z0-9]", "_", parts[0].strip().lower())
        return ""

    df["display_title"] = df["title"].apply(format_title)
    df["clean_name"] = df["title"].apply(get_clean_name)
    df["year"] = df["title"].apply(get_year)
    df["decade"] = (df["year"] // 10 * 10).astype(str) + "s"
    df["franchise"] = df["clean_name"].apply(get_franchise)

    soups = []
    for idx, row in df.iterrows():
        genres_list = [g.strip() for g in row["genres"].split("|") if g != "(no genres listed)"]
        genre_str = " ".join(genres_list).lower()
        genre_pairs = []
        for i in range(len(genres_list)):
            for j in range(i + 1, len(genres_list)):
                genre_pairs.append(f"{genres_list[i].lower()}_{genres_list[j].lower()}")
        genre_pairs_str = " ".join(genre_pairs)

        clean_name_tokens = re.sub(r"[^a-zA-Z0-9\s]", " ", row["clean_name"]).lower()
        franchise_token = row["franchise"]
        decade_token = f"decade_{row['decade']}"
        year_token = f"year_{row['year']}"

        rating_tags = []
        if row.get("rating_mean", 0) >= 4.0:
            rating_tags.append("critically_acclaimed masterpiece top_rated")
        elif row.get("rating_mean", 0) >= 3.6:
            rating_tags.append("highly_rated popular_favorite")

        if row.get("rating_count", 0) >= 5000:
            rating_tags.append("mega_blockbuster timeless_classic")
        elif row.get("rating_count", 0) >= 1000:
            rating_tags.append("widely_watched blockbuster")

        audience_str = " ".join(rating_tags)
        soup = f"{clean_name_tokens} {clean_name_tokens} {franchise_token} {genre_str} {genre_str} {genre_pairs_str} {decade_token} {year_token} {audience_str}"
        soups.append(soup)

    df["soup"] = soups

    # 3. Classical ML Representation (TF-IDF)
    print("Building TF-IDF representation...")
    tfidf = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=10000, sublinear_tf=True)
    tfidf_matrix = tfidf.fit_transform(df["soup"])
    ml_sim = cosine_similarity(tfidf_matrix, tfidf_matrix).astype(np.float32)

    # 4. Deep Learning Semantic Representation
    print("Generating Deep Learning Semantic Embeddings (all-MiniLM-L6-v2)...")
    dl_model = SentenceTransformer("all-MiniLM-L6-v2")
    dl_embeddings = dl_model.encode(df["soup"].tolist(), batch_size=128, show_progress_bar=False, normalize_embeddings=True)
    dl_sim = np.dot(dl_embeddings, dl_embeddings.T).astype(np.float32)

    # 5. Hybrid Recommendation
    alpha = 0.50
    print(f"Constructing Hybrid Similarity Matrix (alpha={alpha})...")
    hybrid_sim = (alpha * ml_sim + (1.0 - alpha) * dl_sim).astype(np.float32)

    # 6. Evaluation
    print("Evaluating models on 500 random sample query movies (K=5)...")
    def evaluate(sim_matrix, K=5, num_queries=500):
        np.random.seed(42)
        sample_indices = np.random.choice(len(df), size=min(num_queries, len(df)), replace=False)
        precisions, recalls, hit_rates, jaccards, ild_scores = [], [], [], [], []
        genre_sets = [set(g.split("|")) for g in df["genres"]]

        for idx in sample_indices:
            q_genres = genre_sets[idx]
            if not q_genres:
                continue
            scores = sim_matrix[idx]
            top_k = np.argsort(scores)[::-1][1:K+1]

            k_precs = []
            recovered = set()
            hit = 0
            k_jacc = []

            for r_idx in top_k:
                r_g = genre_sets[r_idx]
                inter = q_genres.intersection(r_g)
                union = q_genres.union(r_g)
                k_precs.append(len(inter) / len(r_g) if r_g else 0.0)
                if inter:
                    hit += 1
                if union:
                    k_jacc.append(len(inter) / len(union))
                recovered.update(inter)

            # Intra-List Diversity (ILD)
            sub_matrix = sim_matrix[np.ix_(top_k, top_k)]
            # average pairwise similarity off-diagonal
            off_diag = sub_matrix[~np.eye(K, dtype=bool)]
            ild = 1.0 - float(np.mean(off_diag)) if len(off_diag) > 0 else 0.0

            precisions.append(np.mean(k_precs) if k_precs else 0.0)
            recalls.append(len(recovered) / len(q_genres) if q_genres else 0.0)
            hit_rates.append(1.0 if hit >= 1 else 0.0)
            jaccards.append(np.mean(k_jacc) if k_jacc else 0.0)
            ild_scores.append(ild)

        return {
            "Precision@5": np.mean(precisions),
            "Recall@5": np.mean(recalls),
            "Hit Rate@5": np.mean(hit_rates),
            "Jaccard@5": np.mean(jaccards),
            "Diversity (ILD@5)": np.mean(ild_scores)
        }

    res_ml = evaluate(ml_sim)
    res_dl = evaluate(dl_sim)
    res_hyb = evaluate(hybrid_sim)

    print("\n" + "=" * 80)
    print(f"{'Model Architecture':<22} | {'Precision@5':<12} | {'Recall@5':<10} | {'Hit Rate@5':<12} | {'ILD (Diversity)':<15}")
    print("-" * 80)
    print(f"{'TF-IDF (Classical ML)':<22} | {res_ml['Precision@5']:.4f}       | {res_ml['Recall@5']:.4f}     | {res_ml['Hit Rate@5']:.4f}       | {res_ml['Diversity (ILD@5)']:.4f}")
    print(f"{'Sentence-BERT (DL)':<22} | {res_dl['Precision@5']:.4f}       | {res_dl['Recall@5']:.4f}     | {res_dl['Hit Rate@5']:.4f}       | {res_dl['Diversity (ILD@5)']:.4f}")
    print(f"{'Hybrid Recommender':<22} | {res_hyb['Precision@5']:.4f}       | {res_hyb['Recall@5']:.4f}     | {res_hyb['Hit Rate@5']:.4f}       | {res_hyb['Diversity (ILD@5)']:.4f}")
    print("=" * 80)

    # 7. Sample Qualitative Checks
    test_queries = ["Toy Story (1995)", "Matrix, The (1999)", "Godfather, The (1972)", "Dark Knight, The (2008)", "Interstellar (2014)"]
    print("\nQualitative Recommendation Inspection:")
    for query in test_queries:
        m_match = df[df["title"] == query]
        if len(m_match) > 0:
            idx = m_match.index[0]
            scores = hybrid_sim[idx]
            top_5 = np.argsort(scores)[::-1][1:6]
            print(f"\nRecommendations for: {query} (Genres: {df.iloc[idx]['genres']})")
            for r_pos, rec_i in enumerate(top_5, 1):
                rec_title = df.iloc[rec_i]["title"]
                rec_genres = df.iloc[rec_i]["genres"]
                rec_score = hybrid_sim[idx, rec_i]
                print(f"  #{r_pos}: {rec_title} | Genres: {rec_genres} | Score: {rec_score:.4f}")

    print(f"\nExperiment finished successfully in {time.time() - t_start:.2f}s")

if __name__ == "__main__":
    run_experiment()
