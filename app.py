
import streamlit as st
import pandas as pd
import pickle
import requests
import time

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="CineSuggest",
    page_icon="🎬",
    layout="wide"
)

# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

* {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f0f17, #171725, #0d0d12);
    color: white;
}

/* HEADER */
.header {
    text-align: center;
    padding: 35px 15px 25px;
}

.header h1 {
    font-size: clamp(32px, 6vw, 48px);
    font-weight: 700;
    margin-bottom: 5px;
    background: linear-gradient(90deg, #ff416c, #ff8a5b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.header p {
    color: #b8b8c5;
    font-size: clamp(13px, 2vw, 17px);
}

/* MAIN CONTAINER */
.main-box {
    width: min(1200px, 94%);
    margin: auto;
}

/* SELECT BOX */
.stSelectbox label {
    color: white !important;
    font-size: 16px;
    font-weight: 600;
}

div[data-baseweb="select"] > div {
    background-color: #20202c;
    border: 1px solid #3a3a4a;
    border-radius: 12px;
}

/* BUTTON */
.stButton {
    text-align: center;
    margin-top: 25px;
}

.stButton > button {
    background: linear-gradient(90deg, #ff416c, #ff4b2b);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 35px;
    font-size: 16px;
    font-weight: 600;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(255, 65, 108, 0.35);
}

/* RECOMMENDATION TITLE */
.recommend-title {
    text-align: center;
    margin: 45px 0 25px;
    font-size: clamp(22px, 4vw, 28px);
    font-weight: 600;
}

/* RESPONSIVE MOVIE GRID */
.movie-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 20px;
    width: 100%;
}

/* MOVIE CARD */
.movie-card {
    background: linear-gradient(145deg, #20202c, #171720);
    border-radius: 16px;
    padding: 10px;
    text-align: center;
    box-shadow: 0 8px 25px rgba(0,0,0,0.35);
    transition: 0.3s;
    overflow: hidden;
}

.movie-card:hover {
    transform: translateY(-7px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.5);
}

.movie-card img {
    width: 100%;
    aspect-ratio: 2 / 3;
    object-fit: cover;
    border-radius: 12px;
}

.movie-title {
    color: white;
    font-size: 14px;
    font-weight: 600;
    margin-top: 11px;
    min-height: 42px;
    display: flex;
    justify-content: center;
    align-items: center;
}

/* MOVIE LINK */
.movie-link {
    text-decoration: none;
    color: white;
}

/* MOVIE LINK */
.movie-link,
.movie-link:hover,
.movie-link:focus,
.movie-link:active {
    text-decoration: none !important;
    color: white !important;
}

/* ABOUT SECTION */
.about {
    margin-top: 60px;
    padding: 30px;
    background: linear-gradient(145deg, #1c1c28, #15151e);
    border: 1px solid #30303d;
    border-radius: 18px;
    line-height: 1.8;
}

.about h2 {
    color: #ff6b6b;
    margin-bottom: 12px;
}

.about p {
    color: #c5c5d0;
    font-size: 15px;
}

.about strong {
    color: white;
}

/* FOOTER */
.footer {
    text-align: center;
    margin-top: 45px;
    padding: 20px;
    color: #777783;
    font-size: 13px;
}

/* TABLET */
@media (max-width: 900px) {
    .movie-grid {
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
    }
}

/* MOBILE */
@media (max-width: 600px) {

    .header {
        padding-top: 20px;
    }

    .main-box {
        width: 92%;
    }

    .movie-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
    }

    .movie-card {
        padding: 7px;
        border-radius: 12px;
    }

    .movie-title {
        font-size: 12px;
        min-height: 36px;
    }

    .about {
        padding: 20px;
        margin-top: 40px;
    }

    .about p {
        font-size: 13px;
    }
}

</style>
""", unsafe_allow_html=True)


# -------------------- HEADER --------------------
st.markdown("""
<div class="header">
    <h1>🎬 CineSuggest</h1>
    <p>Discover movies you'll love with intelligent recommendations</p>
</div>
""", unsafe_allow_html=True)


# -------------------- FETCH POSTER --------------------
def fetch_poster(movie_id):

    url = 'https://api.themoviedb.org/3/movie/{}'.format(movie_id)

    params = {
        'api_key': '879ae95d4a9ba9e383010fc84b77fe71',
        'language': 'en-US'
    }

    for attempt in range(3):

        try:

            response = requests.get(
                url,
                params=params,
                timeout=10
            )

            response.raise_for_status()

            data = response.json()

            if data.get('poster_path'):

                return 'https://image.tmdb.org/t/p/w500/' + data['poster_path']

            return None

        except requests.exceptions.ConnectionError:

            if attempt < 2:
                time.sleep(2)
            else:
                return None

        except requests.exceptions.RequestException:

            return None


# -------------------- LOAD DATA --------------------
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))


# -------------------- RECOMMENDATION FUNCTION --------------------
def recommend(movie):

    movie_index = movies[movies['title'] == movie].index[0]

    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movie_list:

        movie_id = movies.iloc[i[0]].movie_id

        recommended_movies.append(
            movies.iloc[i[0]].title
        )

        recommended_movies_posters.append(
            fetch_poster(movie_id)
        )

    return recommended_movies, recommended_movies_posters


# -------------------- MAIN UI --------------------
st.markdown('<div class="main-box">', unsafe_allow_html=True)

selected_movie_name = st.selectbox(
    "🎥 Choose a movie you like",
    movies['title'].values
)

if st.button("✨ Recommend Movies"):

    recommendations, posters = recommend(selected_movie_name)

    st.markdown(
        '<div class="recommend-title">🍿 Movies You May Like</div>',
        unsafe_allow_html=True
    )

    # Responsive grid
    st.markdown('<div class="movie-grid">', unsafe_allow_html=True)
    cards_html = '<div class="movie-grid">'
    for movie, poster in zip(recommendations, posters):

        # Find movie ID
        movie_id = movies[
            movies['title'] == movie
        ].iloc[0].movie_id

        # TMDB movie page
        movie_url = f"https://www.themoviedb.org/movie/{movie_id}"

        if poster:
            poster_element = f'<img src="{poster}">'
  
           

        else:
            poster_element = """
            <div style="
                aspect-ratio: 2/3;
                display: flex;
                align-items: center;
                justify-content: center;
                background: #292936;
                border-radius: 12px;
                font-size: 50px;">
                🎬
            </div>
            """

        cards_html += f"""<a href="{movie_url}" target="_blank" class="movie-link"><div class="movie-card">{poster_element}<div class="movie-title">{movie}</div></div></a>"""

    cards_html += '</div>'

    # Render entire grid block at once
    st.markdown(cards_html, unsafe_allow_html=True)

    


# -------------------- ABOUT MODEL --------------------
st.markdown("""
<div class="about">

<h2>🎬 About CineSuggest</h2>

<p>
<strong>CineSuggest</strong> is a movie recommendation system designed to
help users discover movies similar to the movie they already like.
</p>

<p>
The recommendation model is built using the
<strong>IMDb 5000 Movies Dataset</strong>. Movie information such as
genres, keywords, cast, crew and other relevant features are processed
to determine the similarity between movies.
</p>

<p>
When a user selects a movie, the system compares it with other movies
using a <strong>content-based recommendation approach</strong> and
identifies the <strong>top 5 most similar movies</strong>.
</p>

<p>
The movie posters are retrieved dynamically using the
<strong>TMDB API</strong>. Clicking on a recommended movie opens its
corresponding movie page on TMDB in a new tab.
</p>

<p>
<strong>How it works:</strong>
Select a movie → Calculate similarity → Find top 5 similar movies →
Display recommendations and posters.
</p>

</div>
""", unsafe_allow_html=True)


# -------------------- FOOTER --------------------
st.markdown("""
<div class="footer">
    🎬 CineSuggest • Movie Recommendation System
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

