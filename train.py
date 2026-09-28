"""
CineMatch: Hybrid Movie Recommendation Training Pipeline
=========================================================
This script executes the end-to-end training and artifact generation pipeline:
1. Dataset ingestion (movies.csv, ratings.csv, data/links.csv)
2. Data cleaning, deduplication, and popularity aggregation
3. Feature engineering & metadata content soup synthesis
4. Classical NLP & TF-IDF ML representation + Cosine Similarity
5. Deep Learning Semantic Embedding (Pretrained Sentence Transformer: all-MiniLM-L6-v2)
6. Hybrid Similarity Engine synthesis (alpha * ML + (1 - alpha) * DL)
7. Quantitative & Qualitative Model Evaluation (Precision@5, Recall@5, HitRate@5, Diversity)
8. Artifact serialization (movies.pkl, similarity.pkl, embeddings, vectorizer, evaluation report)
"""

import os
import re
import json
import time
import pickle
import warnings
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

warnings.filterwarnings("ignore")

# Configuration constants
DATA_MOVIES_PATH = "movies.csv"
DATA_RATINGS_PATH = "ratings.csv"
DATA_LINKS_PATH = "data/links.csv"
OUTPUT_DIR = "models"
TOP_N_MOVIES = 6000
HYBRID_ALPHA = 0.50
EVAL_SAMPLE_SIZE = 500
TOP_K_EVAL = 5
RANDOM_SEED = 42


def load_and_inspect_dataset():
    """Load raw dataset files and inspect shapes, columns, and missing values."""
    print("Loading dataset...")
    if not os.path.exists(DATA_MOVIES_PATH):
        raise FileNotFoundError(f"Missing required dataset file: {DATA_MOVIES_PATH}")

    movies_df = pd.read_csv(DATA_MOVIES_PATH)
    print(f"  Loaded movies: {len(movies_df):,} rows, columns: {list(movies_df.columns)}")

    links_df = None
    if os.path.exists(DATA_LINKS_PATH):
        links_df = pd.read_csv(DATA_LINKS_PATH)
        print(f"  Loaded TMDB links: {len(links_df):,} entries")
    else:
        print("  Notice: data/links.csv not found; falling back to internal movie IDs.")

    return movies_df, links_df


def clean_and_aggregate_data(movies_df, links_df):
    """Aggregate rating volume and mean score from ratings.csv and filter top catalog."""
    print("Cleaning data...")
    t0 = time.time()

    # Fast chunked aggregation over ratings
    if os.path.exists(DATA_RATINGS_PATH):
        print("  Aggregating 25M+ rating signals from ratings.csv...")
        chunks = []
        for chunk in pd.read_csv(DATA_RATINGS_PATH, usecols=["movieId", "rating"], chunksize=5000000):
            agg = chunk.groupby("movieId").agg(count=("rating", "count"), sum=("rating", "sum")).reset_index()
            chunks.append(agg)
        all_agg = pd.concat(chunks).groupby("movieId").sum().reset_index()
        all_agg["rating_mean"] = (all_agg["sum"] / all_agg["count"]).round(2)
        movies_df = movies_df.merge(all_agg[["movieId", "count", "rating_mean"]], on="movieId", how="left")
        movies_df["rating_count"] = movies_df["count"].fillna(0).astype(int)
        movies_df["rating_mean"] = movies_df["rating_mean"].fillna(0.0)
        movies_df.drop(columns=["count"], inplace=True)
    else:
        print("  Notice: ratings.csv not found; defaulting rating statistics.")
        movies_df["rating_count"] = 100
        movies_df["rating_mean"] = 3.5

    # Merge TMDB IDs if available
    if links_df is not None and "movieId" in links_df.columns and "tmdbId" in links_df.columns:
        movies_df = movies_df.merge(links_df[["movieId", "tmdbId"]], on="movieId", how="left")
        movies_df["movie_id"] = movies_df["tmdbId"].fillna(movies_df["movieId"]).astype(int)
    else:
        movies_df["movie_id"] = movies_df["movieId"].astype(int)

    # Filter out entries with invalid/missing genres
    cleaned_df = movies_df[movies_df["genres"].notna() & (movies_df["genres"] != "(no genres listed)")].copy()

    # Sort by rating count and mean rating to prioritize popular and well-reviewed movies
    cleaned_df = cleaned_df.sort_values(by=["rating_count", "rating_mean"], ascending=[False, False])
    catalog_df = cleaned_df.head(TOP_N_MOVIES).copy().reset_index(drop=True)

    print(f"  Cleaned catalog: {len(catalog_df):,} movies indexed (min rating count: {catalog_df['rating_count'].min()}) in {time.time() - t0:.2f}s")
    return catalog_df


def engineer_movie_features(catalog_df):
    """Build rich metadata soup combining clean title tokens, franchises, genre pairs, decade/era, and audience ratings."""
    print("Building movie features...")

    def format_display_title(title):
        m = re.match(r"^(.*?),\s*(The|A|An)\s*(\(\d{4}\))?$", str(title).strip())
        if m:
            prefix = m.group(2)
            main = m.group(1)
            year = m.group(3) or ""
            return f"{prefix} {main} {year}".strip()
        return str(title).strip()

    def get_clean_title_name(title):
        t = re.sub(r"\s*\(\d{4}\)", "", str(title))
        m = re.match(r"^(.*?),\s*(The|A|An)$", t.strip())
        if m:
            t = f"{m.group(2)} {m.group(1)}"
        return t.strip()

    def extract_year(title):
        m = re.search(r"\((\d{4})\)", str(title))
        return int(m.group(1)) if m else 2000

    def extract_franchise(clean_name):
        parts = re.split(r"[:\-–]", clean_name)
        if len(parts) > 1 and len(parts[0].strip()) > 2:
            return "franchise_" + re.sub(r"[^a-zA-Z0-9]", "_", parts[0].strip().lower())
        return ""

    catalog_df["display_title"] = catalog_df["title"].apply(format_display_title)
    catalog_df["clean_name"] = catalog_df["title"].apply(get_clean_title_name)
    catalog_df["year"] = catalog_df["title"].apply(extract_year)
    catalog_df["decade"] = (catalog_df["year"] // 10 * 10).astype(str) + "s"
    catalog_df["franchise"] = catalog_df["clean_name"].apply(extract_franchise)

    feature_soups = []
    for _, row in catalog_df.iterrows():
        genres_list = [g.strip() for g in row["genres"].split("|") if g != "(no genres listed)"]
        genre_str = " ".join(genres_list).lower()

        # Genre cross-products (e.g. action_adventure, scifi_thriller)
        genre_pairs = []
        for i in range(len(genres_list)):
            for j in range(i + 1, len(genres_list)):
                genre_pairs.append(f"{genres_list[i].lower()}_{genres_list[j].lower()}")
        genre_pairs_str = " ".join(genre_pairs)

        clean_name_tokens = re.sub(r"[^a-zA-Z0-9\s]", " ", row["clean_name"]).lower()
        franchise_token = row["franchise"]
        decade_token = f"decade_{row['decade']}"
        year_token = f"year_{row['year']}"

        # Audience sentiment signals
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

        # Composite feature soup with lexical weighting
        soup = (
            f"{clean_name_tokens} {clean_name_tokens} {franchise_token} "
            f"{genre_str} {genre_str} {genre_pairs_str} "
            f"{decade_token} {year_token} {audience_str}"
        )
        feature_soups.append(soup)

    catalog_df["soup"] = feature_soups
    print("  Feature engineering complete. Sample soup created.")
    return catalog_df


def build_ml_representation(catalog_df):
    """Train TF-IDF vectorizer and compute classical ML cosine similarity matrix."""
    print("Generating TF-IDF representation...")
    t0 = time.time()
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=10000,
        sublinear_tf=True,
    )
    tfidf_matrix = vectorizer.fit_transform(catalog_df["soup"])
    ml_sim = cosine_similarity(tfidf_matrix, tfidf_matrix).astype(np.float32)
    print(f"  TF-IDF matrix shape: {tfidf_matrix.shape}, computed ML similarity in {time.time() - t0:.2f}s")
    return vectorizer, ml_sim


def build_dl_representation(catalog_df):
    """Generate dense semantic embeddings using pretrained Sentence Transformer model."""
    print("Generating semantic embeddings (all-MiniLM-L6-v2)...")
    t0 = time.time()
    model = SentenceTransformer("all-MiniLM-L6-v2")
    dl_embeddings = model.encode(
        catalog_df["soup"].tolist(),
        batch_size=128,
        show_progress_bar=False,
        normalize_embeddings=True,
    )
    dl_sim = np.dot(dl_embeddings, dl_embeddings.T).astype(np.float32)
    print(f"  DL embeddings shape: {dl_embeddings.shape}, computed DL similarity in {time.time() - t0:.2f}s")
    return dl_embeddings, dl_sim


def build_hybrid_similarity(ml_sim, dl_sim, alpha=HYBRID_ALPHA):
    """Synthesize hybrid similarity matrix combining lexical and semantic signals."""
    print(f"Calculating similarities (Hybrid alpha={alpha:.2f})...")
    hybrid_sim = (alpha * ml_sim + (1.0 - alpha) * dl_sim).astype(np.float32)
    return hybrid_sim


def evaluate_recommendation_models(catalog_df, ml_sim, dl_sim, hybrid_sim, k=TOP_K_EVAL, num_queries=EVAL_SAMPLE_SIZE):
    """Perform quantitative validation across ML, DL, and Hybrid models."""
    print("Evaluating recommendation models...")
    np.random.seed(RANDOM_SEED)
    sample_indices = np.random.choice(len(catalog_df), size=min(num_queries, len(catalog_df)), replace=False)
    genre_sets = [set(g.split("|")) for g in catalog_df["genres"]]

    def evaluate_matrix(sim_matrix):
        precisions, recalls, hit_rates, jaccards, ild_scores = [], [], [], [], []

        for idx in sample_indices:
            q_genres = genre_sets[idx]
            if not q_genres:
                continue

            scores = sim_matrix[idx]
            top_k = np.argsort(scores)[::-1][1 : k + 1]

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
            off_diag = sub_matrix[~np.eye(k, dtype=bool)]
            ild = 1.0 - float(np.mean(off_diag)) if len(off_diag) > 0 else 0.0

            precisions.append(np.mean(k_precs) if k_precs else 0.0)
            recalls.append(len(recovered) / len(q_genres) if q_genres else 0.0)
            hit_rates.append(1.0 if hit >= 1 else 0.0)
            jaccards.append(np.mean(k_jacc) if k_jacc else 0.0)
            ild_scores.append(ild)

        return {
            f"Precision@{k}": float(np.mean(precisions)),
            f"Recall@{k}": float(np.mean(recalls)),
            f"Hit Rate@{k}": float(np.mean(hit_rates)),
            f"Jaccard@{k}": float(np.mean(jaccards)),
            f"ILD (Diversity)": float(np.mean(ild_scores)),
        }

    results = {
        "TF-IDF (Classical ML)": evaluate_matrix(ml_sim),
        "Sentence-BERT (DL)": evaluate_matrix(dl_sim),
        "Hybrid Recommender": evaluate_matrix(hybrid_sim),
    }

    # Display Report Table
    print("\n" + "=" * 82)
    print(f"{'Model Architecture':<24} | {f'Precision@{k}':<12} | {f'Recall@{k}':<10} | {f'Hit Rate@{k}':<12} | {'ILD (Diversity)':<15}")
    print("-" * 82)
    for model_name, metrics in results.items():
        print(
            f"{model_name:<24} | "
            f"{metrics[f'Precision@{k}']:.4f}       | "
            f"{metrics[f'Recall@{k}']:.4f}     | "
            f"{metrics[f'Hit Rate@{k}']:.4f}       | "
            f"{metrics['ILD (Diversity)']:.4f}"
        )
    print("=" * 82 + "\n")

    return results


def save_artifacts(catalog_df, hybrid_sim, vectorizer, dl_embeddings, eval_results):
    """Save trained artifacts for Streamlit app and production packaging."""
    print("Saving artifacts...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Primary Streamlit artifacts in root directory
    with open("movies.pkl", "wb") as f:
        pickle.dump(catalog_df, f)

    with open("similarity.pkl", "wb") as f:
        pickle.dump(hybrid_sim, f)

    # 2. Complete model artifacts in models/ directory
    with open(os.path.join(OUTPUT_DIR, "movies.pkl"), "wb") as f:
        pickle.dump(catalog_df, f)

    with open(os.path.join(OUTPUT_DIR, "similarity.pkl"), "wb") as f:
        pickle.dump(hybrid_sim, f)

    with open(os.path.join(OUTPUT_DIR, "tfidf_vectorizer.pkl"), "wb") as f:
        pickle.dump(vectorizer, f)

    np.save(os.path.join(OUTPUT_DIR, "dl_embeddings.npy"), dl_embeddings)

    with open(os.path.join(OUTPUT_DIR, "evaluation_report.json"), "w") as f:
        json.dump(eval_results, f, indent=4)

    metadata = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_movies": len(catalog_df),
        "embedding_dim": dl_embeddings.shape[1],
        "hybrid_alpha": HYBRID_ALPHA,
        "dl_model_name": "all-MiniLM-L6-v2",
        "vectorizer_max_features": 10000,
    }
    with open(os.path.join(OUTPUT_DIR, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4)

    print("  Saved root: movies.pkl, similarity.pkl")
    print("  Saved models/: movies.pkl, similarity.pkl, tfidf_vectorizer.pkl, dl_embeddings.npy, evaluation_report.json, metadata.json")


def main():
    print("============================================================")
    print("  CineMatch: Hybrid Movie Recommender Training Pipeline")
    print("============================================================")
    t_start = time.time()

    # Step 1: Load and inspect
    movies_df, links_df = load_and_inspect_dataset()

    # Step 2: Clean and aggregate
    catalog_df = clean_and_aggregate_data(movies_df, links_df)

    # Step 3: Feature engineering
    catalog_df = engineer_movie_features(catalog_df)

    # Step 4: ML representation
    vectorizer, ml_sim = build_ml_representation(catalog_df)

    # Step 5: DL embeddings
    dl_embeddings, dl_sim = build_dl_representation(catalog_df)

    # Step 6: Hybrid similarity
    hybrid_sim = build_hybrid_similarity(ml_sim, dl_sim, alpha=HYBRID_ALPHA)

    # Step 7: Model evaluation
    eval_results = evaluate_recommendation_models(catalog_df, ml_sim, dl_sim, hybrid_sim)

    # Step 8: Save artifacts
    save_artifacts(catalog_df, hybrid_sim, vectorizer, dl_embeddings, eval_results)

    print(f"Training completed successfully in {time.time() - t_start:.2f}s.")
    print("============================================================")


if __name__ == "__main__":
    main()
