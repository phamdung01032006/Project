import os
import sys
from pathlib import Path

import streamlit as st

# Add project root to PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.controllers.movie_controller import MovieController
from app.controllers.recommendation_controller import RecommendationController
import app.utils.youtube_utils as youtube_utils

st.set_page_config(page_title='Movie Recommender', layout='wide')


@st.cache_resource
def get_controllers():
    return MovieController(), RecommendationController()


@st.cache_data(ttl=3600)
def get_cached_video_url(movie_title):
    return youtube_utils.get_youtube_video(movie_title)


def inject_m3_style():
    css_path = Path(__file__).parent / "styles" / "material3.css"
    css_content = css_path.read_text(encoding="utf-8")
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def render_movie_block(movie, show_review_form=False):
    year = movie.get('year', 0)
    year_str = f' ({year})' if year and year > 0 else ''
    rating = movie.get('vote_average', 0)

    st.markdown(
        (
            f"<div class='m3-card'><strong>{movie.get('title', 'Unknown')}{year_str}</strong><br/>"
            f"<span class='m3-chip'>IMDb {rating}/10</span></div>"
        ),
        unsafe_allow_html=True,
    )

    with st.expander('Details'):
        st.write(movie.get('overview') or 'No overview available.')

        trailer_key = f"show_trailer_{movie['id']}"
        if st.button('Watch trailer', key=f"btn_{movie['id']}"):
            st.session_state[trailer_key] = True

        if st.session_state.get(trailer_key, False):
            with st.spinner('Loading trailer...'):
                video_url = get_cached_video_url(movie['title'])
            if video_url:
                st.video(video_url)
            else:
                st.info('Trailer not found or API quota exceeded.')

        if show_review_form:
            rating_input = st.slider('Rating', 1, 10, 7, key=f"rating_{movie['id']}")
            review = st.text_area('Review', key=f"review_{movie['id']}")
            if st.button('Submit review', key=f"submit_{movie['id']}"):
                movie_controller.add_review(movie['id'], rating_input, review)
                st.success('Review saved.')


inject_m3_style()
movie_controller, recommendation_controller = get_controllers()

# Top navigation bar
# st.markdown("<div class='top-nav-wrap'>", unsafe_allow_html=True)
nav_left, nav_center, nav_right = st.columns([1, 6, 1])
with nav_left:
    st.markdown("<div class='nav-dots'>::::</div>", unsafe_allow_html=True)
with nav_center:
    page = st.radio(
        "Navigation",
        ['Home', 'Movies', 'Recommendations'],
        horizontal=True,
        label_visibility="collapsed",
        key="top_nav_page"
    )
with nav_right:
    st.markdown("<div class='nav-brand'>Group</div>", unsafe_allow_html=True)

remaining_calls = youtube_utils.MAX_API_CALLS - youtube_utils.API_CALLS
st.caption(f'YouTube API remaining: {max(remaining_calls, 0)} calls')
if remaining_calls <= 20:
    st.warning('Trailer quota is running low. Avoid loading too many trailers at once.')

if page == 'Home':
    st.title('Movie Recommendation System')

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric('Movies', len(movie_controller.movie_model.movies_df))
    with col2:
        st.metric('Ratings', len(movie_controller.movie_model.ratings_df))
    with col3:
        st.metric('User reviews', len(movie_controller.movie_model.reviews_df))

    st.info('Tip: search in Movies, and only open trailers when needed for better performance.')

elif page == 'Movies':
    st.subheader('Search Movies')
    search_query = st.text_input('Enter movie title', placeholder='Example: Inception')

    if search_query:
        movies = movie_controller.search_movies(search_query)
        st.caption(f'Found {len(movies)} results (limited for faster performance).')
        for movie in movies:
            render_movie_block(movie, show_review_form=True)

elif page == 'Recommendations':
    st.subheader('Recommendations')

    rec_type = st.selectbox(
        'Recommendation type',
        ['Collaborative Filtering', 'Content-based Filtering', 'Hybrid Filtering']
    )
    top_n = st.slider('Number of recommendations', 5, 20, 10)

    with st.spinner('Generating recommendations...'):
        if rec_type == 'Collaborative Filtering':
            recommendations = recommendation_controller.get_collaborative_recommendations(n_recommendations=top_n)
        elif rec_type == 'Content-based Filtering':
            recommendations = recommendation_controller.get_content_based_recommendations(n_recommendations=top_n)
        else:
            recommendations = recommendation_controller.get_hybrid_recommendations(n_recommendations=top_n)

    if not recommendations:
        st.warning('No suitable recommendations found.')
    else:
        for movie in recommendations:
            render_movie_block(movie, show_review_form=False)
