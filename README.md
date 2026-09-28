# Movie Recommendation System — CineMatch

A hybrid Machine Learning & Deep Learning movie recommendation system powered by **TF-IDF lexical matching**, **Sentence-BERT semantic transformer embeddings**, and an interactive **Streamlit** discovery interface enriched with real-time **TMDB artwork**.

---

## 📌 Project Overview

**CineMatch** is an end-to-end intelligent movie recommendation platform. Rather than relying on simple keyword lookups, CineMatch utilizes a **hybrid recommendation architecture** that fuses classical Natural Language Processing (NLP) with state-of-the-art Deep Learning (Sentence Transformers).

When a user selects a film they enjoy, CineMatch analyzes semantic context, genre interactions, franchise associations, release eras, and community acclaim profiles to surface the top 5 most relevant films, accompanied by high-resolution posters retrieved via the TMDB REST API.

---

## ✨ Key Features

- **Hybrid Recommendation Architecture**: Fuses classical ML cosine similarity with dense neural semantic embeddings for optimal precision and semantic generalization.
- **Classical ML Engine**: Multi-token sublinear TF-IDF representation capturing exact franchise names, keywords, and domain-specific tokens.
- **Deep Learning Semantic Engine**: Pretrained Sentence Transformer (`all-MiniLM-L6-v2`) mapping movie metadata into a 384-dimensional dense semantic space.
- **Composite Metadata Engineering**: Custom metadata "soup" combining normalized titles, franchise tokens, genre pairs, release decades, and Bayesian community rating signals.
- **Quantitative & Reproducible Evaluation**: Real evaluation on 500 test queries measuring Precision@5, Recall@5, Hit Rate@5, Jaccard Index, and Intra-List Diversity (ILD).
- **Interactive Streamlit Web Frontend**: Glassmorphism UI with dark mode aesthetics, curated shortlist rankings, and dynamic poster retrieval.
- **TMDB API Integration**: Real-time poster artwork and backdrop fetching using TMDB movie ID mapping.
- **Optimized Storage & Low-Latency Inference**: Sub-millisecond similarity lookups with compressed matrices for seamless Streamlit performance.

---

## 🏗 System Architecture

```
                                  ┌─────────────────────────────┐
                                  │   MovieLens 25M Dataset     │
                                  │ (movies.csv & ratings.csv)  │
                                  └──────────────┬──────────────┘
                                                 │
                                                 ▼
                                  ┌─────────────────────────────┐
                                  │ Data Preprocessing & Links  │
                                  │ (Deduplication + TMDB IDs)  │
                                  └──────────────┬──────────────┘
                                                 │
                                                 ▼
                                  ┌─────────────────────────────┐
                                  │     Feature Engineering     │
                                  │   (Composite Metadata Soup) │
                                  └──────────────┬──────────────┘
                                                 │
                        ┌────────────────────────┴────────────────────────┐
                        ▼                                                 ▼
        ┌───────────────────────────────┐                 ┌───────────────────────────────┐
        │     Classical ML Component    │                 │    Deep Learning Component    │
        │   TF-IDF Vectorizer (1-2 gram)│                 │   Sentence-BERT (MiniLM-L6)   │
        └───────────────┬───────────────┘                 └───────────────┬───────────────┘
                        │                                                 │
                        ▼                                                 ▼
        ┌───────────────────────────────┐                 ┌───────────────────────────────┐
        │      ML Cosine Similarity     │                 │     DL Cosine Similarity      │
        │         Matrix S_ML           │                 │         Matrix S_DL           │
        └───────────────┬───────────────┘                 └───────────────┬───────────────┘
                        │                                                 │
                        └────────────────────────┬────────────────────────┘
                                                 │
                                                 ▼
                                  ┌─────────────────────────────┐
                                  │  Hybrid Similarity Engine   │
                                  │  S_hyb = α*S_ML + (1-α)*S_DL│
                                  └──────────────┬──────────────┘
                                                 │
                                                 ▼
                                  ┌─────────────────────────────┐
                                  │   Model Evaluation Bench    │
                                  │ (Precision, Recall, HitRate)│
                                  └──────────────┬──────────────┘
                                                 │
                                                 ▼
                                  ┌─────────────────────────────┐
                                  │      Streamlit Frontend     │
                                  │ (Top 5 Matches + TMDB API)  │
                                  └─────────────────────────────┘
```

---

## 🧠 Machine Learning & Deep Learning Concepts

### 1. Classical Machine Learning Component
- **NLP Text Normalization**: Punctuation stripping, lowercasing, article re-ordering (`"Matrix, The"` $\to$ `"The Matrix"`), and stopword elimination.
- **Sublinear Term Frequency–Inverse Document Frequency (TF-IDF)**:
  $$\text{TF-IDF}(t, d) = (1 + \log(\text{TF}(t, d))) \times \log\left(\frac{1 + N}{1 + \text{DF}(t)}\right)$$
  Captures rare, highly discriminative tokens (such as specific franchise identifiers like `franchise_toy_story` and release decade tags).
- **Cosine Similarity**:
  $$S_{\text{ML}}(i, j) = \frac{\mathbf{v}_i \cdot \mathbf{v}_j}{\|\mathbf{v}_i\| \|\mathbf{v}_j\|}$$

### 2. Deep Learning Semantic Component
- **Pretrained Sentence Transformer (`all-MiniLM-L6-v2`)**:
  A 6-layer MiniLM transformer with 384-dimensional dense output embeddings trained on over 1 billion sentence pairs for contrastive semantic similarity.
- **Dense Embedding Dot Product**:
  Since embeddings are $L_2$-normalized ($\|\mathbf{e}\| = 1$), the cosine similarity simplifies to:
  $$S_{\text{DL}}(i, j) = \mathbf{e}_i \cdot \mathbf{e}_j$$
- **Why Deep Learning?**
  Unlike TF-IDF which requires exact word overlaps, Sentence-BERT captures thematic and conceptual proximity (e.g. recognizing that *space exploration*, *quantum physics*, and *interstellar voyage* share strong semantic affinity).

### 3. Hybrid Synthesis Engine
The hybrid engine blends lexical precision and semantic generalization:
$$S_{\text{Hybrid}}(i, j) = \alpha \cdot S_{\text{ML}}(i, j) + (1 - \alpha) \cdot S_{\text{DL}}(i, j)$$
Where $\alpha = 0.50$ provides the ideal balance between exact franchise/keyword fidelity and thematic discovery.

---

## 📊 Evaluation & Benchmark Results

The models were quantitatively evaluated across **500 sample query movies** using top-$5$ recommendations ($K=5$):

| Model Architecture | Precision@5 | Recall@5 | Hit Rate@5 | Jaccard@5 | Diversity (ILD@5) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **TF-IDF (Classical ML)** | 0.9002 | 0.9988 | 1.0000 | 0.8690 | 0.5213 |
| **Sentence-BERT (DL)** | 0.7177 | 0.9747 | 1.0000 | 0.6045 | 0.3113 |
| **Hybrid Recommender** | **0.8854** | **0.9986** | **1.0000** | **0.8433** | **0.4720** |

### Qualitative Verification Examples

- **Toy Story (1995)** $\to$ `Toy Story 2 (1999)`, `Toy Story 4 (2019)`, `Toy Story 3 (2010)`, `Monsters, Inc. (2001)`, `Antz (1998)`
- **The Godfather (1972)** $\to$ `The Godfather: Part II (1974)`, `The Godfather: Part III (1990)`, `Goodfellas (1990)`, `American History X (1998)`, `Serpico (1973)`
- **The Dark Knight (2008)** $\to$ `The Dark Knight Rises (2012)`, `Need for Speed (2014)`, `Batman Begins (2005)`, `First Knight (1995)`, `Inception (2010)`
- **Interstellar (2014)** $\to$ `Gravity (2013)`, `Transcendence (2014)`, `Prometheus (2012)`, `Contagion (2011)`, `Edge of Tomorrow (2014)`

---

## 📁 Project Structure

```
movie-recommendation-system/
├── app.py                      # Main Streamlit web application frontend
├── train.py                    # End-to-end ML/DL training & artifact generation pipeline
├── requirements.txt            # Project dependencies
├── README.md                   # Comprehensive project documentation
├── .gitignore                  # Git ignore rules for secrets and large artifacts
├── data/
│   └── links.csv               # MovieLens to TMDB ID cross-reference table
├── models/
│   ├── movies.pkl              # Cleaned movie catalog dataframe
│   ├── similarity.pkl          # Precomputed hybrid similarity matrix
│   ├── tfidf_vectorizer.pkl    # Fitted TF-IDF model
│   ├── dl_embeddings.npy       # 384-D dense Sentence-BERT embeddings
│   ├── evaluation_report.json  # Quantitative benchmark results
│   └── metadata.json           # Model configuration & training metadata
├── notebooks/
│   └── model_experiment.ipynb  # Interactive Jupyter notebook for exploration & experiments
└── .streamlit/
    └── secrets.toml            # Streamlit secrets (TMDB API key configuration)
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/AnishRai54/movie_recommend.git
cd movie_recommend
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure TMDB API Key
Create a `.streamlit/secrets.toml` file with your free API key from [The Movie Database (TMDB)](https://www.themoviedb.org/documentation/api):

```toml
TMDB_API_KEY = "YOUR_ACTUAL_TMDB_API_KEY"
```

> **Note**: Never commit `.streamlit/secrets.toml` to version control. It is protected by `.gitignore`.

---

## 🚀 Training & Running the Application

### 1. Run the Training Pipeline
To process the dataset, engineer features, compute TF-IDF & DL embeddings, evaluate models, and generate production artifacts:

```bash
python train.py
```

### 2. Launch the Streamlit Web Application
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501` to use the interactive application.

---

## 🔮 Future Enhancements

- **Collaborative Filtering**: Integration of Matrix Factorization (SVD / ALS) and Neural Collaborative Filtering (NCF) on user rating histories.
- **ANN Vector Indexing**: Implementation of FAISS or ScaNN for approximate nearest neighbor retrieval scaling to millions of items.
- **Dynamic User Profiling**: Real-time session-based recommendations based on user watch history and implicit click signals.
- **Hybrid Collaborative + Content Fusion**: Blending content metadata embeddings with collaborative latent vectors.
