import pandas as pd
import requests
from datetime import datetime
import os
from dotenv import load_dotenv
import logging
from typing import Dict, List, Optional
import json
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class WeatherDataFetcher:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY not found in environment variables")
            
        self.lat = os.getenv('LATITUDE')
        self.lon = os.getenv('LONGITUDE')
        if not self.lat or not self.lon:
            raise ValueError("LATITUDE and LONGITUDE must be set in environment variables")
            
        self.base_url = "https://api.openweathermap.org/data/3.0"
        logger.info("WeatherDataFetcher initialized with API key and coordinates")
        #my city in .env
    def get_weather_data(self, timestamp: str) -> Optional[Dict]:
        """Get weather data for a specific location and time"""
        try:
            # Parse ISO 8601 timestamp to datetime
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            # Convert to Unix timestamp (seconds since epoch)
            unix_timestamp = int(dt.timestamp())
            url = f"{self.base_url}/onecall/timemachine"
            params = {
                'lat': self.lat,
                'lon': self.lon,
                'dt': unix_timestamp,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            weather_data = {
                'temperature': data['data'][0]['temp'],
                'type_of_weather': data['data'][0]['weather'][0]['main'],
            }
            return weather_data
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return None

class MoodAnalyzer:
    def __init__(self):
        self.weather_fetcher = WeatherDataFetcher()
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.openrouter_url = "https://openrouter.ai/api/v1"
        
    def predict_mood_with_llm(self, music_data: Dict, weather_data: Dict, timestamp: str) -> str:
        """Use LLM to predict mood based on music, weather, and time data"""
        try:
            # Parse ISO 8601 timestamp to datetime
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            # Format time of day
            hour = dt.hour
            time_of_day = "morning" if 5 <= hour < 12 else "afternoon" if 12 <= hour < 17 else "evening" if 17 <= hour < 22 else "night"
            
            # Create prompt for the LLM
            prompt = f"""Based on the following information, describe the likely mood or emotional state:
            
            Time: {time_of_day} ({dt.strftime('%I:%M %p')})
            Temperature: {weather_data['temperature']}°C, Weather Type: {weather_data['type_of_weather']}
            Music: {music_data['track_name']} by {music_data['artist_name']} (BPM: {music_data['bpm']})
            
            Keep in mind that the user is in PST timezone (7h ahead of UTC). So adjust the time of day accordingly
            Consider how these factors might influence someone's mood. ONLY Provide your single emotion prediction 
            for the user's mental state: only use happy, angry, sad, or energized. No other response."""

            client = OpenAI(api_key=self.openrouter_api_key, base_url=self.openrouter_url)
            response = client.chat.completions.create(
                model="google/gemini-2.5-flash-preview-05-20",
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error predicting mood with LLM: {e}")
            return "Unable to predict mood"

    def analyze_mood_history(self, tracks_data: Dict) -> Dict:
        """Analyze mood for multiple tracks based on music and weather data"""
        analyzed_tracks = {}
        
        for track_number, track_info in tracks_data.items():
            weather_data = self.weather_fetcher.get_weather_data(track_info['played_at'])
            if not weather_data:
                continue
            mood_prediction = self.predict_mood_with_llm(track_info, weather_data, track_info['played_at'])

            analyzed_tracks[track_number] = {
                'track_name': track_info['track_name'],
                'artist_name': track_info['artist_name'],
                'played_at': track_info['played_at'],
                'bpm': track_info['bpm'],
                'temperature': weather_data['temperature'],
                'type_of_weather': weather_data['type_of_weather'],
                'predicted_mood': mood_prediction
            }
            
        return analyzed_tracks