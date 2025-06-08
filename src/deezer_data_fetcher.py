import requests
import pandas as pd
from datetime import datetime
import time
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class DeezerDataFetcher:
    def __init__(self):
        self.base_url = "https://api.deezer.com"
        self.rate_limit_delay = 1  #RL delay (seconds)

    def search_track(self, artist, title):
        """Search for a track on Deezer and return its ID and metadata"""
        try:
            # Format the search query
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
                    'duration': track['duration'],
                    'preview': track['preview']
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
                
            # Extract and normalize features
            features = {
                'bpm': data.get('bpm', 0),
            }
            return features
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting Deezer features: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting Deezer features: {e}")
            return None

    def process_track(self, artist, title, timestamp=None):
        """Process a single track and return its data"""
        # Search for the track
        track_info = self.search_track(artist, title)
        if not track_info:
            return None

        # Get features
        features = self.get_track_features(track_info['id'])
        if not features:
            return None

        # Combine all data
        track_data = {
            **features  # Include all audio features
        }
        return track_data
