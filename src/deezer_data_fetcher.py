#Commented out because Deezer API is not working properly in fetching bpm data
'''import requests
import pandas as pd
from datetime import datetime
import time
import os
from dotenv import load_dotenv
import logging
from typing import Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

class DeezerDataFetcher:
    def __init__(self):
        self.base_url = "https://api.deezer.com"
        self.rate_limit_delay = 1  #RL delay (seconds)

    def search_track(self, artist, title):
        """Search for a track on Deezer and return its ID and metadata"""
        try:
            query = f"{artist} {title}"
            encoded_query = requests.utils.quote(query)

            response = requests.get(f"{self.base_url}/search?q={encoded_query}")
            response.raise_for_status()
            data = response.json()
            
            if data.get('data') and len(data['data']) > 0:
                track = data['data'][0]
                return {
                    'id': track['id'],
                    'title': track['title'],
                    'artist': track['artist']['name'],
                }
            logger.warning(f"No results found for: {query}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching Deezer: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error searching Deezer: {e}")
            return None

    def get_track_features(self, track_id):
        """Get audio features for a track from Deezer"""
        try:
            response = requests.get(f"{self.base_url}/track/{track_id}")
            response.raise_for_status()
            data = response.json()
            if not data:
                return None
            features = {
                'bpm': data.get('bpm', "unknown"),
            }
            return features
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting Deezer features: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting Deezer features: {e}")
            return None

    def process_track(self, track_data: Dict) -> Dict:
        """Process multiple tracks and return their data"""
        processed_tracks = {}
        
        for track_number, track_info in track_data.items():
            track_metadata = self.search_track(track_info['artist_name'], track_info['track_name'])
            if not track_metadata:
                continue
            features = self.get_track_features(track_metadata['id'])
            if not features:
                continue
            processed_tracks[track_number] = {
                'track_name': track_info['track_name'],
                'artist_name': track_info['artist_name'],
                'played_at': track_info['played_at'],
                'bpm': features.get('bpm', "unknown")
            }
            # Respect rate limit of Deezer API
            time.sleep(self.rate_limit_delay)
            
        return processed_tracks
'''