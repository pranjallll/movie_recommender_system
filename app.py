import streamlit as st
import pickle
import pandas as pd
import requests

# Function to fetch poster
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=0598b99ea1b962c37acf13e95966b1ea&language=en-US"
    response = requests.get(url)
    data = response.json()
    return "http://image.tmdb.org/t/p/w500/" + data['poster_path']

# Load data
movies_dict = pickle.load(open('movies_dict_small.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

with open('similarity_small.pkl', 'rb') as f:
    similarity = pickle.load(f)

# Title-based Recommendation
def recommend_by_title(movie_title):
    movie_index = movies[movies['title'] == movie_title].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters

# Search by Director or Actor (returns top 5 matching movies)
def search_by_person(query):
    query = query.lower().replace(" ", "")  # remove spaces for comparison

    # Ensure 'cast' and 'crew' are strings, replace missing values
    movies['cast'] = movies['cast'].astype(str).fillna('')
    movies['crew'] = movies['crew'].astype(str).fillna('')

    # Remove spaces from cast and crew for matching
    cast_no_space = movies['cast'].str.replace(" ", "", regex=False).str.lower()
    crew_no_space = movies['crew'].str.replace(" ", "", regex=False).str.lower()

    filtered = movies[
        cast_no_space.str.contains(query, na=False) |
        crew_no_space.str.contains(query, na=False)
    ].head(5)

    recommended_movies = filtered['title'].tolist()
    recommended_posters = []

    for idx in filtered.index:
        movie_id = movies.iloc[idx].movie_id
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters




# Streamlit UI
st.title('🎬 Movie Recommender System')

search_option = st.radio('Search by:', ('Title', 'Director/Actor'))

if search_option == 'Title':
    selected_movie_name = st.selectbox('Select a movie:', movies['title'].values)

    if st.button('Recommend by Title'):
        names, posters = recommend_by_title(selected_movie_name)
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            with col:
                st.text(names[idx])
                st.image(posters[idx])

elif search_option == 'Director/Actor':
    query = st.text_input('Type Director or Actor Name:')
    if st.button('Search'):
        names, posters = search_by_person(query)
        if names:
            cols = st.columns(5)
            for idx, col in enumerate(cols):
                with col:
                    st.text(names[idx])
                    st.image(posters[idx])
        else:
            st.warning('No matches found.')
