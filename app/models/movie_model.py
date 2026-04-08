import os
import pandas as pd


class MovieModel:
    def __init__(self):
        self.movies_df = pd.read_csv('app/data/movies_processed.csv')
        self.ratings_df = pd.read_csv('app/data/ratings_processed.csv')

        reviews_path = 'app/data/reviews.csv'
        if os.path.exists(reviews_path):
            self.reviews_df = pd.read_csv(reviews_path)
        else:
            self.reviews_df = pd.DataFrame(columns=['movieId', 'userId', 'rating', 'review'])

    def search_movies(self, query, limit=20):
        """Search movies by title."""
        if not query:
            return []

        matches = self.movies_df[self.movies_df['title'].str.contains(query, case=False, na=False, regex=False)]
        return matches.head(limit).to_dict('records')

    def get_movie_by_id(self, movie_id):
        movie = self.movies_df[self.movies_df['id'] == movie_id]
        if not movie.empty:
            return movie.iloc[0].to_dict()
        return None

    def add_review(self, movie_id, rating, review):
        new_review = pd.DataFrame({
            'movieId': [movie_id],
            'userId': ['user_1'],
            'rating': [rating],
            'review': [review]
        })
        self.reviews_df = pd.concat([self.reviews_df, new_review], ignore_index=True)
        self.reviews_df.to_csv('app/data/reviews.csv', index=False)
        return True

    def get_movie_reviews(self, movie_id):
        return self.reviews_df[self.reviews_df['movieId'] == movie_id].to_dict('records')

