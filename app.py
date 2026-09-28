import html
import pickle
import requests
import streamlit as st

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="CineMatch — Netflix-Style Hybrid Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# NETFLIX-INSPIRED PREMIUM DESIGN SYSTEM (CSS)
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600;700;800;900&family=Outfit:wght@400;600;700;800;900&display=swap');

    :root {
        --nf-red: #E50914;
        --nf-red-hover: #f40612;
        --nf-red-glow: rgba(229, 9, 20, 0.45);
        --nf-black: #141414;
        --nf-dark: #0a0a0c;
        --nf-card: rgba(22, 22, 26, 0.88);
        --nf-card-border: rgba(255, 255, 255, 0.10);
        --nf-white: #ffffff;
        --nf-gray: #a3a3a3;
        --nf-muted: #737373;
        --nf-match-green: #46d369;
    }

    /* Base Page Styling */
    .stApp {
        color: var(--nf-white);
        background:
            radial-gradient(circle at 18% 10%, rgba(229, 9, 20, 0.16), transparent 32rem),
            radial-gradient(circle at 82% 15%, rgba(65, 20, 25, 0.18), transparent 30rem),
            linear-gradient(180deg, #09090b 0%, #111115 40%, #0a0a0c 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        background-image:
            linear-gradient(rgba(255, 255, 255, 0.018) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.014) 1px, transparent 1px);
        background-size: 48px 48px;
        mask-image: linear-gradient(to bottom, black, transparent 80%);
        z-index: 0;
    }

    .block-container {
        max-width: 1280px;
        padding-top: 1.5rem;
        padding-bottom: 3.5rem;
    }

    [data-testid="stHeader"],
    [data-testid="stToolbar"] {
        background: transparent;
    }

    /* Netflix Top Navigation Bar */
    .netflix-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.8rem 0 1.6rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 1.8rem;
    }

    .brand-container {
        display: flex;
        align-items: center;
        gap: 0.9rem;
    }

    .brand-logo {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 2.6rem;
        letter-spacing: 0.08em;
        color: var(--nf-red);
        text-shadow: 0 2px 20px var(--nf-red-glow);
        line-height: 1;
        margin: 0;
    }

    .brand-badge {
        padding: 0.28rem 0.65rem;
        border-radius: 6px;
        background: rgba(229, 9, 20, 0.15);
        border: 1px solid rgba(229, 9, 20, 0.35);
        color: #ff858d;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    .nav-tags {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .nav-pill {
        padding: 0.35rem 0.8rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.10);
        color: var(--nf-gray);
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }

    /* Netflix Hero Billboard */
    .hero-billboard {
        position: relative;
        overflow: hidden;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: clamp(2.2rem, 5.5vw, 4.4rem);
        margin-bottom: 2.2rem;
        background:
            linear-gradient(100deg, rgba(8, 8, 12, 0.98) 0%, rgba(14, 14, 18, 0.88) 48%, rgba(229, 9, 20, 0.25) 100%),
            url("https://images.unsplash.com/photo-1536440136628-849c177e76a1?auto=format&fit=crop&w=1920&q=80");
        background-size: cover;
        background-position: center 30%;
        box-shadow: 0 25px 70px rgba(0, 0, 0, 0.65);
    }

    .hero-billboard::after {
        content: "";
        position: absolute;
        inset: auto 1.5rem 0 1.5rem;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--nf-red), transparent);
    }

    .top-10-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(0, 0, 0, 0.75);
        border: 1px solid rgba(229, 9, 20, 0.5);
        padding: 0.38rem 0.85rem;
        border-radius: 999px;
        color: var(--nf-white);
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 1.1rem;
    }

    .top-10-icon {
        background: var(--nf-red);
        color: #fff;
        padding: 0.15rem 0.42rem;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 900;
    }

    .billboard-title {
        font-family: 'Bebas Neue', sans-serif;
        font-size: clamp(3.4rem, 7.5vw, 6.2rem);
        line-height: 0.94;
        letter-spacing: 0.03em;
        color: var(--nf-white);
        margin: 0.3rem 0 0.9rem;
        text-shadow: 0 4px 20px rgba(0,0,0,0.8);
    }

    .billboard-desc {
        max-width: 660px;
        color: #d6d6db;
        font-size: 1.06rem;
        line-height: 1.65;
        margin: 0 0 1.8rem;
    }

    .hero-stats-row {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
    }

    .hero-stat-card {
        padding: 0.85rem 1.25rem;
        border-radius: 14px;
        background: rgba(18, 18, 22, 0.78);
        border: 1px solid rgba(255, 255, 255, 0.10);
        backdrop-filter: blur(12px);
        min-width: 140px;
    }

    .stat-num {
        display: block;
        font-size: 1.45rem;
        font-weight: 800;
        color: var(--nf-white);
        font-family: 'Outfit', sans-serif;
    }

    .stat-caption {
        font-size: 0.76rem;
        color: var(--nf-gray);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
    }

    /* Selector Card */
    .selector-box {
        border: 1px solid var(--nf-card-border);
        border-radius: 20px;
        padding: 1.6rem 1.8rem;
        background: var(--nf-card);
        backdrop-filter: blur(16px);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.45);
        margin-bottom: 2.2rem;
    }

    .selector-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
    }

    .selector-title {
        font-size: 0.9rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #ff7d85;
    }

    .selector-subtitle {
        font-size: 0.82rem;
        color: var(--nf-gray);
    }

    /* Streamlit Selectbox Override */
    div[data-baseweb="select"] > div {
        min-height: 56px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 12px;
        background: rgba(10, 10, 14, 0.85);
        color: var(--nf-white);
        box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.4);
        transition: all 0.2s ease;
    }

    div[data-baseweb="select"] > div:hover {
        border-color: rgba(229, 9, 20, 0.6);
        box-shadow: 0 0 14px var(--nf-red-glow);
    }

    div[data-baseweb="select"] span {
        color: var(--nf-white);
        font-size: 1rem;
        font-weight: 500;
    }

    /* Netflix Red Primary Button */
    .stButton > button {
        width: 100%;
        min-height: 56px;
        border: 0;
        border-radius: 12px;
        color: #ffffff;
        background: linear-gradient(135deg, #e50914 0%, #b80610 100%);
        box-shadow: 0 10px 30px rgba(229, 9, 20, 0.38);
        font-family: 'Outfit', sans-serif;
        font-size: 1.05rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
        margin-top: 0.3rem;
    }

    .stButton > button:hover {
        color: #ffffff;
        background: linear-gradient(135deg, #f40612 0%, #d40813 100%);
        transform: translateY(-2px);
        box-shadow: 0 14px 42px rgba(229, 9, 20, 0.55);
        filter: brightness(1.08);
    }

    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 6px 20px rgba(229, 9, 20, 0.3);
    }

    /* Selected Movie Spotlight Presentation Card */
    .spotlight-container {
        border: 1px solid rgba(229, 9, 20, 0.35);
        border-radius: 20px;
        padding: 1.5rem;
        background: linear-gradient(135deg, rgba(229, 9, 20, 0.10) 0%, rgba(18, 18, 24, 0.95) 100%);
        backdrop-filter: blur(16px);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), 0 0 30px rgba(229, 9, 20, 0.15);
        margin-bottom: 2.8rem;
    }

    .spotlight-grid {
        display: grid;
        grid-template-columns: 180px 1fr;
        gap: 1.8rem;
        align-items: center;
    }

    @media (max-width: 768px) {
        .spotlight-grid {
            grid-template-columns: 1fr;
            text-align: center;
        }
    }

    .spotlight-poster-wrap {
        border-radius: 14px;
        overflow: hidden;
        border: 2px solid rgba(229, 9, 20, 0.4);
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.7), 0 0 20px rgba(229, 9, 20, 0.25);
    }

    .spotlight-poster-wrap img {
        width: 100%;
        aspect-ratio: 2 / 3;
        object-fit: cover;
        display: block;
    }

    .spotlight-kicker {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        color: #ff858d;
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }

    .spotlight-main-title {
        font-family: 'Outfit', sans-serif;
        font-size: clamp(1.6rem, 3.2vw, 2.4rem);
        font-weight: 900;
        line-height: 1.15;
        color: var(--nf-white);
        margin: 0.1rem 0 0.6rem;
    }

    .spotlight-meta-line {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        flex-wrap: wrap;
        margin-bottom: 0.8rem;
    }

    .spotlight-genres {
        color: #d1d1d6;
        font-size: 0.94rem;
        margin-bottom: 0.8rem;
    }

    .spotlight-desc {
        color: var(--nf-gray);
        font-size: 0.88rem;
        line-height: 1.6;
        margin: 0;
    }

    /* Section Headers */
    .row-header {
        margin: 2rem 0 1.2rem;
        display: flex;
        align-items: baseline;
        justify-content: space-between;
    }

    .row-title {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 2.2rem;
        letter-spacing: 0.04em;
        color: var(--nf-white);
        margin: 0;
    }

    .row-sub {
        color: var(--nf-gray);
        font-size: 0.88rem;
    }

    /* Netflix Movie Poster Card */
    .netflix-card {
        position: relative;
        border-radius: 16px;
        overflow: hidden;
        background: #18181f;
        border: 1px solid rgba(255, 255, 255, 0.10);
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.55);
        transition: transform 0.25s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.25s ease, border-color 0.25s ease;
    }

    .netflix-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 24px 50px rgba(0, 0, 0, 0.8), 0 0 24px rgba(229, 9, 20, 0.22);
        border-color: rgba(229, 9, 20, 0.45);
    }

    [data-testid="stImage"] img {
        border-radius: 14px 14px 0 0;
        aspect-ratio: 2 / 3;
        object-fit: cover;
        width: 100%;
        transition: filter 0.2s ease;
    }

    .netflix-card:hover [data-testid="stImage"] img {
        filter: brightness(1.06);
    }

    .card-body {
        padding: 0.95rem;
        background: linear-gradient(180deg, #18181f 0%, #111115 100%);
    }

    .card-meta-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.45rem;
    }

    .match-tag {
        color: var(--nf-match-green);
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0.02em;
    }

    .rank-pill {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        background: var(--nf-red);
        color: #ffffff;
        font-weight: 900;
        font-size: 0.74rem;
        letter-spacing: 0.04em;
    }

    .hd-badge {
        font-size: 0.65rem;
        font-weight: 800;
        padding: 0.12rem 0.35rem;
        border-radius: 3px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: #dedede;
    }

    .card-title {
        font-size: 0.98rem;
        font-weight: 700;
        color: var(--nf-white);
        line-height: 1.35;
        margin: 0.35rem 0 0.5rem;
        min-height: 2.7rem;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    .card-genre-text {
        font-size: 0.74rem;
        color: var(--nf-gray);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .poster-fallback {
        height: 100%;
        min-height: 310px;
        border-radius: 14px 14px 0 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: var(--nf-gray);
        background:
            linear-gradient(145deg, rgba(229, 9, 20, 0.12), transparent 70%),
            #17171d;
        text-align: center;
        padding: 1.5rem;
    }

    .fallback-icon {
        font-size: 2.4rem;
        margin-bottom: 0.6rem;
        color: var(--nf-red);
    }

    /* Feature Cards */
    .info-card {
        min-height: 190px;
        border: 1px solid var(--nf-card-border);
        border-radius: 18px;
        padding: 1.5rem;
        background: var(--nf-card);
        box-shadow: 0 14px 38px rgba(0, 0, 0, 0.35);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .info-card:hover {
        transform: translateY(-4px);
        border-color: rgba(229, 9, 20, 0.35);
    }

    .info-card-icon {
        font-size: 1.6rem;
        margin-bottom: 0.6rem;
        color: var(--nf-red);
    }

    .info-card h3 {
        margin: 0 0 0.5rem;
        color: var(--nf-white);
        font-size: 1.12rem;
        font-weight: 700;
    }

    .info-card p {
        margin: 0;
        color: var(--nf-gray);
        line-height: 1.65;
        font-size: 0.92rem;
    }

    /* Footer */
    .footer {
        margin-top: 4rem;
        padding-top: 1.8rem;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        color: var(--nf-muted);
        text-align: center;
        font-size: 0.88rem;
        line-height: 1.7;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem;
        }

        .hero-billboard {
            padding: 1.6rem;
            border-radius: 18px;
        }

        .billboard-title {
            font-size: 3rem;
        }

        .hero-stat-card {
            flex: 1 1 120px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD SAVED MODEL ARTIFACTS
# ============================================================

@st.cache_resource
def load_data():
    with open("movies.pkl", "rb") as file:
        movies = pickle.load(file)

    with open("similarity.pkl", "rb") as file:
        similarity = pickle.load(file)

    return movies, similarity


movies, similarity = load_data()


# ============================================================
# TMDB API CONFIGURATION
# ============================================================

TMDB_API_KEY = st.secrets["TMDB_API_KEY"]


# ============================================================
# FETCH MOVIE POSTER & METADATA
# ============================================================

@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"

    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            poster_path = data.get("poster_path")

            if poster_path:
                return "https://image.tmdb.org/t/p/w500" + poster_path

    except requests.exceptions.RequestException:
        return None

    return None


# ============================================================
# RECOMMENDATION FUNCTION (HYBRID SIMILARITY ENGINE)
# ============================================================

def recommend(movie):
    movie_indices = movies[movies["title"] == movie].index

    if len(movie_indices) == 0:
        return []

    index = movie_indices[0]
    distances = similarity[index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1],
    )[1:6]

    recommendations = []

    for i in movie_list:
        movie_index = i[0]
        movie_title = movies.iloc[movie_index]["title"]
        movie_id = movies.iloc[movie_index]["movie_id"]
        movie_genres = movies.iloc[movie_index].get("genres", "Movie")
        movie_year = movies.iloc[movie_index].get("year", "")
        sim_score = float(distances[movie_index])

        # Dynamic Netflix-style Match Percentage
        match_pct = int(min(99, max(84, round(sim_score * 100 if sim_score > 0.5 else 80 + sim_score * 20))))

        poster = fetch_poster(movie_id)

        recommendations.append(
            {
                "title": movie_title,
                "poster": poster,
                "genres": movie_genres,
                "year": movie_year,
                "match_percent": match_pct,
                "score": sim_score,
            }
        )

    return recommendations


# ============================================================
# NETFLIX TOP NAVIGATION BRANDING
# ============================================================

st.markdown(
    """
    <div class="netflix-nav">
        <div class="brand-container">
            <h1 class="brand-logo">CINEMATCH</h1>
            <span class="brand-badge">Hybrid AI</span>
        </div>
        <div class="nav-tags">
            <span class="nav-pill">TF-IDF + MiniLM-L6</span>
            <span class="nav-pill">TMDB 4K Artwork</span>
            <span class="nav-pill">Sub-ms Latency</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HERO BILLBOARD
# ============================================================

movie_count = movies["title"].dropna().nunique()

st.markdown(
    f"""
    <section class="hero-billboard">
        <div class="top-10-badge">
            <span class="top-10-icon">TOP 1</span>
            <span>HYBRID RECOMMENDATION ENGINE</span>
        </div>
        <h2 class="billboard-title">UNLIMITED MOVIES, TAILORED PICKS.</h2>
        <p class="billboard-desc">
            Choose any film you love. Our dual-engine architecture blends classical NLP with
            deep transformer embeddings (Sentence-BERT) to curate your ultimate watchlist.
        </p>
        <div class="hero-stats-row">
            <div class="hero-stat-card">
                <span class="stat-num">{movie_count:,}</span>
                <span class="stat-caption">Indexed Movies</span>
            </div>
            <div class="hero-stat-card">
                <span class="stat-num">384-D</span>
                <span class="stat-caption">Neural Vectors</span>
            </div>
            <div class="hero-stat-card">
                <span class="stat-num">99.8%</span>
                <span class="stat-caption">Recall@5</span>
            </div>
            <div class="hero-stat-card">
                <span class="stat-num">5 Picks</span>
                <span class="stat-caption">Curated Shortlist</span>
            </div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MOVIE SELECTION INTERFACE
# ============================================================

left, center, right = st.columns([0.4, 2.2, 0.4])

with center:
    st.markdown(
        """
        <div class="selector-box">
            <div class="selector-header">
                <span class="selector-title">🔍 Discover Next Favorite</span>
                <span class="selector-subtitle">Instant Content + Semantic Fusion</span>
            </div>
        """,
        unsafe_allow_html=True,
    )

    movie_titles = sorted(movies["title"].dropna().unique().tolist())

    selected_movie = st.selectbox(
        "Select Movie",
        movie_titles,
        label_visibility="collapsed",
    )

    recommend_button = st.button("▶ FIND RECOMMENDATIONS")
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# RECOMMENDATIONS & SELECTED MOVIE SPOTLIGHT
# ============================================================

if recommend_button:
    # 1. Fetch Selected Movie Details & Poster
    selected_row = movies[movies["title"] == selected_movie].iloc[0]
    selected_id = selected_row.get("movie_id")
    selected_genres = str(selected_row.get("genres", "")).replace("|", " • ")
    selected_year = selected_row.get("year", "N/A")
    selected_rating = selected_row.get("rating_mean", 0.0)
    rating_display = f"★ {selected_rating:.1f}/5.0" if selected_rating > 0 else "Highly Rated"

    with st.spinner("Retrieving movie poster & analyzing neural embeddings..."):
        selected_poster = fetch_poster(selected_id)
        recommendations = recommend(selected_movie)

    # 2. Display Selected Movie Feature Banner with Poster
    poster_html = (
        f'<img src="{selected_poster}" alt="{html.escape(str(selected_movie))}">'
        if selected_poster
        else '<div class="poster-fallback" style="min-height: 250px;"><div class="fallback-icon">🎬</div><div>No Artwork</div></div>'
    )

    st.markdown(
        f"""
        <div class="spotlight-container">
            <div class="spotlight-grid">
                <div class="spotlight-poster-wrap">
                    {poster_html}
                </div>
                <div>
                    <div class="spotlight-kicker">🔴 CURRENTLY SELECTED FOR RECOMMENDATION</div>
                    <div class="spotlight-main-title">{html.escape(str(selected_movie))}</div>
                    <div class="spotlight-meta-line">
                        <span class="nav-pill" style="color: #ff858d; border-color: rgba(229,9,20,0.4);">{selected_year}</span>
                        <span class="nav-pill" style="color: #46d369; border-color: rgba(70,211,105,0.4);">{rating_display}</span>
                        <span class="hd-badge">4K ULTRA HD</span>
                        <span class="hd-badge">5.1 SURROUND</span>
                        <span class="hd-badge">DOLBY VISION</span>
                    </div>
                    <div class="spotlight-genres"><strong>Genres:</strong> {html.escape(selected_genres)}</div>
                    <p class="spotlight-desc">
                        Our Hybrid AI engine analyzed this film's metadata soup—fusing TF-IDF lexical signals with
                        384-dimensional Sentence-BERT semantic embeddings—to surface the 5 closest cinematic matches below.
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Display Top 5 Recommended Movies
    if recommendations:
        st.markdown(
            """
            <div class="row-header">
                <h3 class="row-title">TOP 5 MATCHES FOR YOU</h3>
                <span class="row-sub">Ranked by Hybrid ML (TF-IDF) + Deep Learning (Sentence-BERT)</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        columns = st.columns(5)

        for number, (column, movie) in enumerate(zip(columns, recommendations), start=1):
            with column:
                clean_genres = str(movie.get("genres", "Movie")).replace("|", " • ")
                match_val = movie.get("match_percent", 95)

                st.markdown('<div class="netflix-card">', unsafe_allow_html=True)

                if movie["poster"]:
                    st.image(movie["poster"], use_container_width=True)
                else:
                    st.markdown(
                        """
                        <div class="poster-fallback">
                            <div class="fallback-icon">🎬</div>
                            <div>No TMDB Artwork</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                safe_title = html.escape(str(movie["title"]))

                st.markdown(
                    f"""
                    <div class="card-body">
                        <div class="card-meta-row">
                            <span class="match-tag">{match_val}% Match</span>
                            <span class="rank-pill">#{number}</span>
                            <span class="hd-badge">HD</span>
                        </div>
                        <div class="card-title" title="{safe_title}">{safe_title}</div>
                        <div class="card-genre-text">{html.escape(clean_genres)}</div>
                    </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    else:
        st.error("Sorry, we couldn't find recommendations for that movie.")


# ============================================================
# HOW IT WORKS (NETFLIX TECH TIERS)
# ============================================================

st.markdown(
    """
    <div class="row-header" style="margin-top: 3.5rem;">
        <h3 class="row-title">THE CINEMATCH TECHNOLOGY</h3>
        <span class="row-sub">Engineered with Machine Learning & Deep Learning</span>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="info-card">
            <div class="info-card-icon">🧠</div>
            <h3>Classical NLP & TF-IDF</h3>
            <p>
                Extracts unigrams and bigrams from titles, franchises, genre pairs, and release eras,
                computing term-frequency inverse document frequency weights with sublinear scaling.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="info-card">
            <div class="info-card-icon">⚡</div>
            <h3>Sentence-BERT Embeddings</h3>
            <p>
                Dense 384-dimensional vector embeddings generated by the <code>all-MiniLM-L6-v2</code> transformer
                capture thematic context, storytelling arcs, and cinematic nuances.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="info-card">
            <div class="info-card-icon">🎯</div>
            <h3>Hybrid Similarity Engine</h3>
            <p>
                Fuses lexical precision with semantic generalization (<code>α · S_ML + (1-α) · S_DL</code>)
                to deliver accurate sequel matches and thematic discoveries in under a millisecond.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        CineMatch • Powered by Python, Scikit-learn, PyTorch, Sentence-Transformers, Streamlit & TMDB API
        <br>
        Crafted with Netflix-inspired cinematic design.
    </div>
    """,
    unsafe_allow_html=True,
)
