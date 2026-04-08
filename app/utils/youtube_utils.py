import os
from functools import lru_cache

from googleapiclient.discovery import build
try:
    from dotenv import load_dotenv
except ImportError:
    # Optional dependency: app can still run without loading .env automatically.
    def load_dotenv():
        return False

load_dotenv()

API_CALLS = 0
MAX_API_CALLS = 100


@lru_cache(maxsize=1)
def _get_youtube_client():
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        return None
    return build('youtube', 'v3', developerKey=api_key)


def get_youtube_video(movie_title):
    """Search trailer URL on YouTube."""
    global API_CALLS

    try:
        if API_CALLS >= MAX_API_CALLS:
            return None

        youtube = _get_youtube_client()
        if youtube is None:
            return None

        API_CALLS += 1

        search_query = f'{movie_title} official trailer HD'
        request = youtube.search().list(
            part='snippet',
            q=search_query,
            type='video',
            maxResults=1,
            videoDuration='short',
            relevanceLanguage='en',
            order='relevance'
        )
        response = request.execute()

        items = response.get('items', [])
        if items:
            video_id = items[0]['id']['videoId']
            return f'https://www.youtube.com/watch?v={video_id}'

        return None
    except Exception as e:
        if 'quotaExceeded' in str(e):
            return None
        print(f'Error searching YouTube: {str(e)}')
        return None

