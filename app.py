import requests
import streamlit as st
import pickle
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------------------- PAGE STYLE --------------------
st.markdown(
    """
    <style>
    .stApp { background-color: #0b1d3a; }
    h1 { color: #ffffff !important; font-weight: 700; }
    h2, h3, h4, h5, h6, p, label, span { color: #e6e6e6 !important; }
    .stSelectbox div[data-baseweb="select"] > div { color: black; }
    .stButton > button {
        background-color: #1f3c88;
        color: white;
        border-radius: 8px;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------- POSTER FETCH --------------------
@st.cache_data(show_spinner=False)
def fetch_poster(movie_title):
    try:
        url = "https://api.themoviedb.org/3/search/movie"
        params = {
            "api_key": "0d13addf1717f446ffa74e88b73ba51b",
            "query": movie_title,
            "include_adult": False
        }
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        for result in data.get("results", []):
            if result.get("poster_path"):
                return "https://image.tmdb.org/t/p/w500/" + result["poster_path"]

        return "https://via.placeholder.com/300x450?text=No+Poster"

    except:
        return "https://via.placeholder.com/300x450?text=API+Error"

# -------------------- LOAD MOVIES --------------------
@st.cache_resource
def load_movies():
    movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
    return pd.DataFrame(movies_dict)

movies = load_movies()

# -------------------- COMPUTE SIMILARITY --------------------
@st.cache_resource
def compute_similarity(movies):
    cv = CountVectorizer(max_features=5000, stop_words="english")
    vectors = cv.fit_transform(movies["tags"]).toarray()
    return cosine_similarity(vectors)

similarity = compute_similarity(movies)

# -------------------- RECOMMENDER --------------------
def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        title = movies.iloc[i[0]].title
        recommended_movies.append(title)
        recommended_posters.append(fetch_poster(title))

    return recommended_movies, recommended_posters

# -------------------- UI --------------------
st.title("🎬 Movie Recommendation System")

option = st.selectbox(
    "Select a movie",
    movies["title"].values
)

st.write("You selected:", option)

if st.button("Recommend"):
    names, posters = recommend(option)
    cols = st.columns(5)

    for col, name, poster in zip(cols, names, posters):
        with col:
            st.text(name)
            st.image(poster)
