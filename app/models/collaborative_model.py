import pandas as pd
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity

from app.models.movie_model import MovieModel


class CollaborativeModel:
    def __init__(self, movie_model=None):
        self.movie_model = movie_model or MovieModel()
        self.ratings_matrix = None
        self.user_similarity = None
        self._build_model()

    def _build_model(self):
        """Build user-item matrix and user similarity matrix."""
        try:
            ratings_path = 'app/data/ratings_processed.csv'
            if not os.path.exists(ratings_path):
                raise FileNotFoundError('ratings_processed.csv not found in app/data/')

            ratings_df = pd.read_csv(ratings_path)
            required_columns = ['userId', 'movieId', 'rating']
            missing_columns = [col for col in required_columns if col not in ratings_df.columns]
            if missing_columns:
                raise ValueError(f'Missing required columns in ratings_processed.csv: {missing_columns}')

            self.ratings_matrix = ratings_df.pivot(
                index='userId',
                columns='movieId',
                values='rating'
            ).fillna(0)

            self.user_similarity = cosine_similarity(self.ratings_matrix)
        except Exception as e:
            print(f'Error building collaborative model: {str(e)}')
            self.ratings_matrix = pd.DataFrame()
            self.user_similarity = np.array([])

    def get_recommendations(self, user_id=None, n_recommendations=10):
        """Return recommendations using collaborative filtering."""
        if self.ratings_matrix is None or self.ratings_matrix.empty:
            return []

        if user_id is None or user_id not in self.ratings_matrix.index:
            user_id = self.ratings_matrix.sum(axis=1).idxmax()

        user_ratings = self.ratings_matrix.loc[user_id]
        unwatched_movies = user_ratings[user_ratings == 0].index

        user_idx = self.ratings_matrix.index.get_loc(user_id)
        user_similarities = self.user_similarity[user_idx]
        denominator = np.sum(np.abs(user_similarities))
        if denominator == 0:
            return []

        predictions = []
        for movie_id in unwatched_movies:
            movie_ratings = self.ratings_matrix[movie_id]
            pred_rating = np.sum(user_similarities * movie_ratings) / denominator
            predictions.append((movie_id, pred_rating))

        predictions.sort(key=lambda x: x[1], reverse=True)

        top_movies = []
        for movie_id, pred_rating in predictions[:n_recommendations]:
            movie_info = self.movie_model.get_movie_by_id(movie_id)
            if movie_info:
                movie_info['predicted_rating'] = float(pred_rating)
                top_movies.append(movie_info)

        return top_movies

