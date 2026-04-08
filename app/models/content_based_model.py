import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.movie_model import MovieModel


class ContentBasedModel:
    def __init__(self, movie_model=None):
        self.movie_model = movie_model or MovieModel()
        self.tfidf_matrix = None
        self.movie_similarity = None
        self.movies_df = pd.DataFrame()
        self._build_model()

    def _build_model(self):
        """Build TF-IDF and movie similarity matrix."""
        try:
            movies_path = 'app/data/movies_processed.csv'
            if not os.path.exists(movies_path):
                raise FileNotFoundError('movies_processed.csv not found in app/data/')

            self.movies_df = pd.read_csv(movies_path)
            required_columns = ['id', 'title', 'overview', 'genres']
            missing_columns = [col for col in required_columns if col not in self.movies_df.columns]
            if missing_columns:
                raise ValueError(f'Missing required columns in movies_processed.csv: {missing_columns}')

            self.movies_df['content'] = self.movies_df['overview'].fillna('') + ' ' + self.movies_df['genres'].fillna('')

            tfidf = TfidfVectorizer(stop_words='english')
            self.tfidf_matrix = tfidf.fit_transform(self.movies_df['content'])
            self.movie_similarity = cosine_similarity(self.tfidf_matrix)
        except Exception as e:
            print(f'Error building content-based model: {str(e)}')
            self.tfidf_matrix = None
            self.movie_similarity = None
            self.movies_df = pd.DataFrame()

    def get_recommendations(self, movie_id=None, n_recommendations=10):
        """Return recommendations using content-based filtering."""
        if self.movie_similarity is None or self.movies_df.empty:
            return []

        if movie_id is None:
            movie_id = self.movie_model.ratings_df.groupby('movieId')['rating'].mean().idxmax()

        if movie_id not in set(self.movies_df['id']):
            movie_id = self.movies_df.iloc[0]['id']

        movie_idx = self.movies_df[self.movies_df['id'] == movie_id].index[0]
        movie_similarities = self.movie_similarity[movie_idx]

        similar_movie_indices = movie_similarities.argsort()[::-1][1:n_recommendations + 1]
        similar_movies = self.movies_df.iloc[similar_movie_indices]

        recommendations = []
        for idx, movie in similar_movies.iterrows():
            movie_dict = movie.to_dict()
            movie_dict['similarity_score'] = float(movie_similarities[idx])
            recommendations.append(movie_dict)

        return recommendations

