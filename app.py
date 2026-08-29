import html
import pickle

import requests
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="CineMatch",
    page_icon="CM",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
    :root {
        --bg: #07080d;
        --panel: rgba(20, 23, 33, 0.72);
        --panel-strong: rgba(29, 32, 44, 0.92);
        --line: rgba(255, 255, 255, 0.10);
        --text: #f7f2e8;
        --muted: #a9adba;
        --gold: #d8a84f;
        --gold-soft: #f3d98b;
        --rose: #b85560;
        --teal: #55b4a7;
    }

    .stApp {
        color: var(--text);
        background:
            radial-gradient(circle at 14% 12%, rgba(216, 168, 79, 0.18), transparent 27rem),
            radial-gradient(circle at 86% 7%, rgba(85, 180, 167, 0.14), transparent 26rem),
            linear-gradient(145deg, #07080d 0%, #11131d 46%, #08090f 100%);
    }

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        background-image:
            linear-gradient(rgba(255, 255, 255, 0.025) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.018) 1px, transparent 1px);
        background-size: 42px 42px;
        mask-image: linear-gradient(to bottom, black, transparent 75%);
    }

    .block-container {
        max-width: 1240px;
        padding-top: 2.1rem;
        padding-bottom: 2.8rem;
    }

    [data-testid="stHeader"],
    [data-testid="stToolbar"] {
        background: transparent;
    }

    .hero {
        position: relative;
        overflow: hidden;
        border: 1px solid var(--line);
        border-radius: 26px;
        padding: clamp(2rem, 5vw, 4.6rem);
        margin-bottom: 1.8rem;
        background:
            linear-gradient(115deg, rgba(9, 10, 16, 0.96) 0%, rgba(15, 17, 27, 0.82) 52%, rgba(63, 42, 36, 0.48) 100%),
            url("https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1800&q=80");
        background-size: cover;
        background-position: center;
        box-shadow: 0 28px 85px rgba(0, 0, 0, 0.42);
    }

    .hero::after {
        content: "";
        position: absolute;
        inset: auto 2rem 0 2rem;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(243, 217, 139, 0.55), transparent);
    }

    .kicker {
        display: inline-flex;
        align-items: center;
        gap: 0.55rem;
        padding: 0.42rem 0.72rem;
        border: 1px solid rgba(243, 217, 139, 0.34);
        border-radius: 999px;
        color: var(--gold-soft);
        background: rgba(7, 8, 13, 0.54);
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .hero-title {
        max-width: 780px;
        margin: 1.1rem 0 0.8rem;
        font-size: clamp(3.2rem, 7vw, 6.4rem);
        line-height: 0.92;
        font-weight: 850;
        letter-spacing: 0;
        color: var(--text);
    }

    .hero-copy {
        max-width: 620px;
        color: #d8d7d2;
        font-size: 1.08rem;
        line-height: 1.7;
        margin: 0;
    }

    .hero-stats {
        display: flex;
        flex-wrap: wrap;
        gap: 0.9rem;
        margin-top: 1.6rem;
    }

    .stat {
        min-width: 136px;
        padding: 0.86rem 1rem;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(12px);
    }

    .stat-value {
        display: block;
        color: var(--gold-soft);
        font-size: 1.35rem;
        font-weight: 800;
    }

    .stat-label {
        color: var(--muted);
        font-size: 0.8rem;
    }

    .selector-panel {
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 1.3rem;
        background: var(--panel);
        box-shadow: 0 18px 55px rgba(0, 0, 0, 0.26);
    }

    .panel-label {
        color: var(--gold-soft);
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 0.55rem;
    }

    .section-title {
        margin: 2.3rem 0 1.2rem;
        color: var(--text);
        font-size: clamp(1.65rem, 3vw, 2.3rem);
        font-weight: 820;
        letter-spacing: 0;
    }

    .section-subtitle {
        margin-top: -0.8rem;
        margin-bottom: 1.2rem;
        color: var(--muted);
    }

    div[data-baseweb="select"] > div {
        min-height: 54px;
        border: 1px solid rgba(255, 255, 255, 0.13);
        border-radius: 14px;
        background: rgba(255, 255, 255, 0.07);
        color: var(--text);
        box-shadow: none;
    }

    div[data-baseweb="select"] span {
        color: var(--text);
    }

    .stButton > button {
        width: 100%;
        min-height: 54px;
        border: 0;
        border-radius: 14px;
        color: #161108;
        background: linear-gradient(135deg, var(--gold-soft), var(--gold) 55%, #b97835);
        box-shadow: 0 14px 34px rgba(216, 168, 79, 0.22);
        font-size: 1rem;
        font-weight: 850;
        transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;
    }

    .stButton > button:hover {
        color: #161108;
        transform: translateY(-2px);
        filter: brightness(1.05);
        box-shadow: 0 18px 45px rgba(216, 168, 79, 0.32);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    [data-testid="stImage"] img {
        border-radius: 18px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: 0 20px 46px rgba(0, 0, 0, 0.38);
        aspect-ratio: 2 / 3;
        object-fit: cover;
    }

    .movie-rank {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 2.2rem;
        height: 2.2rem;
        margin-top: 0.86rem;
        border-radius: 999px;
        color: #161108;
        background: var(--gold-soft);
        font-weight: 850;
        font-size: 0.84rem;
    }

    .movie-title {
        min-height: 3.6rem;
        margin-top: 0.58rem;
        color: var(--text);
        font-size: 0.98rem;
        line-height: 1.35;
        font-weight: 720;
    }

    .poster-fallback {
        height: 100%;
        min-height: 330px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--muted);
        background:
            linear-gradient(145deg, rgba(216, 168, 79, 0.12), transparent),
            var(--panel-strong);
        text-align: center;
        font-weight: 700;
    }

    .info-card {
        min-height: 180px;
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 1.25rem;
        background: rgba(255, 255, 255, 0.055);
        box-shadow: 0 14px 38px rgba(0, 0, 0, 0.20);
    }

    .info-card h3 {
        margin: 0 0 0.55rem;
        color: var(--text);
        font-size: 1.05rem;
        letter-spacing: 0;
    }

    .info-card p {
        margin: 0;
        color: var(--muted);
        line-height: 1.65;
        font-size: 0.94rem;
    }

    .footer {
        margin-top: 3rem;
        padding-top: 1.3rem;
        border-top: 1px solid var(--line);
        color: #858999;
        text-align: center;
        font-size: 0.88rem;
    }

    @media (max-width: 760px) {
        .block-container {
            padding-top: 1rem;
        }

        .hero,
        .selector-panel {
            border-radius: 18px;
        }

        .hero {
            padding: 1.45rem;
        }

        .hero-title {
            font-size: 3rem;
        }

        .stat {
            flex: 1 1 120px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD SAVED MODEL
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
# TMDB API KEY
# ============================================================

TMDB_API_KEY = st.secrets["TMDB_API_KEY"]


# ============================================================
# FETCH MOVIE POSTER
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
# RECOMMENDATION FUNCTION
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
        poster = fetch_poster(movie_id)

        recommendations.append(
            {
                "title": movie_title,
                "poster": poster,
            }
        )

    return recommendations


# ============================================================
# HEADER
# ============================================================

movie_count = movies["title"].dropna().nunique()

st.markdown(
    f"""
    <section class="hero">
        <div class="kicker">Premium movie discovery</div>
        <h1 class="hero-title">CineMatch</h1>
        <p class="hero-copy">
            Choose a film you already love and get a refined shortlist of
            similar picks, tuned by content signals and cinematic taste.
        </p>
        <div class="hero-stats">
            <div class="stat">
                <span class="stat-value">{movie_count:,}</span>
                <span class="stat-label">movies indexed</span>
            </div>
            <div class="stat">
                <span class="stat-value">5</span>
                <span class="stat-label">curated matches</span>
            </div>
            <div class="stat">
                <span class="stat-value">TMDB</span>
                <span class="stat-label">poster artwork</span>
            </div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MOVIE SELECTION
# ============================================================

left, center, right = st.columns([0.7, 2, 0.7])

with center:
    st.markdown('<div class="selector-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-label">Start with a favorite</div>', unsafe_allow_html=True)

    movie_titles = sorted(movies["title"].dropna().unique().tolist())

    selected_movie = st.selectbox(
        "Select Movie",
        movie_titles,
        label_visibility="collapsed",
    )

    recommend_button = st.button("Find premium matches")
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# RECOMMENDATIONS
# ============================================================

if recommend_button:
    with st.spinner("Curating your watchlist..."):
        recommendations = recommend(selected_movie)

    if recommendations:
        st.markdown(
            """
            <div class="section-title">Recommended For You</div>
            <div class="section-subtitle">
                Five films with the closest content profile to your selection.
            </div>
            """,
            unsafe_allow_html=True,
        )

        columns = st.columns(5)

        for number, (column, movie) in enumerate(zip(columns, recommendations), start=1):
            with column:
                if movie["poster"]:
                    st.image(movie["poster"], use_container_width=True)
                else:
                    st.markdown(
                        """
                        <div class="poster-fallback">
                            No poster available
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                safe_title = html.escape(str(movie["title"]))

                st.markdown(
                    f"""
                    <div class="movie-rank">#{number}</div>
                    <div class="movie-title">{safe_title}</div>
                    """,
                    unsafe_allow_html=True,
                )

    else:
        st.error("Sorry, we couldn't find recommendations for that movie.")


# ============================================================
# INFORMATION SECTION
# ============================================================

st.markdown(
    """
    <div class="section-title">How It Works</div>
    <div class="section-subtitle">
        A simple recommendation engine with a more polished viewing experience.
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="info-card">
            <h3>Content Signals</h3>
            <p>
                The system reads movie metadata such as genres, keywords,
                cast, and overview details.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="info-card">
            <h3>Similarity Scoring</h3>
            <p>
                Films are compared with cosine similarity to surface the
                nearest matches in the catalog.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="info-card">
            <h3>Curated Output</h3>
            <p>
                You get a focused list of five recommendations with clean
                poster artwork and ranking.
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
        Built with Python, Pandas, Scikit-learn, Streamlit, and TMDB.
        <br>
        CineMatch
    </div>
    """,
    unsafe_allow_html=True,
)
