import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from datetime import datetime
import time
import os
from dotenv import load_dotenv

from deezer_data_fetcher import DeezerDataFetcher

# Load environment variables
load_dotenv()

# Spotify API credentials from environment variables
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError("Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables")

# Initialize Spotify client with necessary scopes
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri='http://127.0.0.1:8000/callback',
    scope='user-read-recently-played user-read-private user-read-email user-top-read',
    cache_path=None  # This will force a new token request
))

def fetch_recently_played():
    """Fetch recently played tracks with timestamps"""
    recently_played = sp.current_user_recently_played(limit=1)
    track_data = {}
    for item in recently_played['items']:
        track_name = item['track']['name']  
        artist_name = item['track']['artists'][0]['name']
        played_at = item['played_at']
        time.sleep(0.1)
    track_data = {
        'track_name': track_name,
        'artist_name': artist_name,
        'played_at': played_at
        #this is UTC timezone (7h ahead of PST after Spring Forward)
    }
    fetcher = DeezerDataFetcher()
    additional_data = fetcher.process_track(track_data['artist_name'], track_data['track_name'])
    track_data.update(additional_data)
    return track_data