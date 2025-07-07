import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from datetime import datetime
import time
import os
from dotenv import load_dotenv
import pytz
#from deezer_data_fetcher import DeezerDataFetcher

load_dotenv()

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError("Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri='http://127.0.0.1:8000/callback',
    scope='user-read-recently-played user-read-private user-read-email user-top-read',
    cache_path=None 
))

def convert_to_local_time(utc_time_str: str) -> datetime:
    """Convert UTC timestamp to local timezone"""
    try:
        utc_time = datetime.fromisoformat(utc_time_str.replace('Z', '+00:00'))
        user_timezone = os.getenv('TIMEZONE', 'America/Los_Angeles')
        local_tz = pytz.timezone(user_timezone)
        local_time = utc_time.astimezone(local_tz)
        return local_time
    except Exception as e:
        print(f"Error converting time: {e}")
        return utc_time

def fetch_recently_played():
    """Fetch recently played tracks with timestamps"""
    recently_played = sp.current_user_recently_played(limit=5)
    track_data = {}
    counter = 1 
    for item in recently_played['items']:
        track_name = item['track']['name']  
        artist_name = item['track']['artists'][0]['name']
        played_at = item['played_at']
        
        local_time = convert_to_local_time(played_at)
        
        track_data[counter] = {
            'track_name': track_name, 
            'artist_name': artist_name, 
            'played_at': local_time
        }
        counter += 1
        time.sleep(0.1)
    #fetcher = DeezerDataFetcher()
    #processed_tracks = fetcher.process_track(track_data)
    processed_tracks = track_data
    return processed_tracks