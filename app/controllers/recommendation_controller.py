from app.models.movie_model import MovieModel
from app.models.collaborative_model import CollaborativeModel
from app.models.content_based_model import ContentBasedModel
from app.models.hybrid_model import HybridModel


class RecommendationController:
    def __init__(self):
        self.movie_model = MovieModel()
        self.collaborative_model = CollaborativeModel(movie_model=self.movie_model)
        self.content_based_model = ContentBasedModel(movie_model=self.movie_model)
        self.hybrid_model = HybridModel(
            collaborative_model=self.collaborative_model,
            content_based_model=self.content_based_model
        )

    def get_collaborative_recommendations(self, user_id=None, n_recommendations=10):
        return self.collaborative_model.get_recommendations(user_id, n_recommendations)

    def get_content_based_recommendations(self, movie_id=None, n_recommendations=10):
        return self.content_based_model.get_recommendations(movie_id, n_recommendations)

    def get_hybrid_recommendations(self, user_id=None, movie_id=None, n_recommendations=10):
        return self.hybrid_model.get_recommendations(user_id, movie_id, n_recommendations)

