from app.models.collaborative_model import CollaborativeModel
from app.models.content_based_model import ContentBasedModel


class HybridModel:
    def __init__(self, collaborative_model=None, content_based_model=None):
        self.collaborative_model = collaborative_model or CollaborativeModel()
        self.content_based_model = content_based_model or ContentBasedModel()

    def get_recommendations(self, user_id=None, movie_id=None, n_recommendations=10):
        """Return recommendations by combining collaborative and content-based outputs."""
        collab_recommendations = self.collaborative_model.get_recommendations(user_id, n_recommendations * 2)
        content_recommendations = self.content_based_model.get_recommendations(movie_id, n_recommendations * 2)

        collab_movie_ids = {movie['id'] for movie in collab_recommendations}
        content_movie_ids = {movie['id'] for movie in content_recommendations}
        common_movie_ids = collab_movie_ids.intersection(content_movie_ids)

        if len(common_movie_ids) < n_recommendations:
            movie_scores = {}

            for movie in collab_recommendations:
                movie_scores[movie['id']] = movie.get('predicted_rating', 0)

            for movie in content_recommendations:
                if movie['id'] in movie_scores:
                    movie_scores[movie['id']] += movie.get('similarity_score', 0)
                else:
                    movie_scores[movie['id']] = movie.get('similarity_score', 0)

            sorted_movies = sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)
            top_movie_ids = [mid for mid, _ in sorted_movies[:n_recommendations]]
        else:
            top_movie_ids = list(common_movie_ids)[:n_recommendations]

        final_recommendations = []
        for mid in top_movie_ids:
            movie_rows = self.content_based_model.movies_df[self.content_based_model.movies_df['id'] == mid]
            if not movie_rows.empty:
                final_recommendations.append(movie_rows.iloc[0].to_dict())

        return final_recommendations

