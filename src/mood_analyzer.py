import pandas as pd
import requests
from datetime import datetime
import os
from dotenv import load_dotenv
import logging
from typing import Dict, List, Optional
import json
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

    def get_weather_data(self, timestamp: datetime) -> Optional[Dict]:
        """Get weather data for a specific location and time"""
        from datetime import timezone
        try:
            #Convert local time to UTC first as OWA uses UTC
            utc_time = timestamp.astimezone(timezone.utc)
            #UTC --> Unix
            unix_timestamp = int(utc_time.timestamp())
            url = f"{self.base_url}/onecall/timemachine"
            params = {
                'lat': self.lat,
                'lon': self.lon,
                'dt': unix_timestamp, 
                'appid': self.api_key,
                'units': 'imperial'
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
        
    def predict_mood_with_llm(self, tracks_data: Dict) -> Dict:
        """Use LLM to predict mood based on multiple tracks, weather, and time data"""
        try:
            track_summary = []
            weather_summary = []
            time_summary = []
            weather_data_collection = {}
            
            for track_number, track_info in tracks_data.items():
                weather_data = self.weather_fetcher.get_weather_data(track_info['played_at'])
                if not weather_data:
                    raise ValueError(f"Failed to fetch weather data for track {track_number}")
                    
                hour = track_info["played_at"].hour
                time_of_day = "morning" if 5 <= hour < 12 else "afternoon" if 12 <= hour < 17 else "evening" if 17 <= hour < 22 else "night"
 
                track_summary.append(f"{track_info['track_name']} by {track_info['artist_name']}")
                weather_summary.append(f"{weather_data['temperature']}°F, {weather_data['type_of_weather']}")
                time_summary.append(f"{time_of_day} ({track_info['played_at'].strftime('%I:%M %p')})")
                
                weather_data_collection[track_number] = weather_data
                
            prompt = f"""Based on the following information about multiple tracks played in sequence, describe the likely overall mood or emotional state:
            
            Time Periods:
            {', '.join(time_summary)}
            
            Weather Conditions:
            {', '.join(weather_summary)}
            
            Music Played:
            {', '.join(track_summary)}
            
            Consider how these factors together might influence someone's mood. ONLY Provide your single emotion prediction 
            for the user's mental state: only use happy, angry, sad, or energized. No other response."""

            client = OpenAI(api_key=self.openrouter_api_key, base_url=self.openrouter_url)
            response = client.chat.completions.create(
                model="google/gemini-2.5-flash-lite",
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                'mood': response.choices[0].message.content.strip(),
                'weather_data': weather_data_collection,
                'llm_success': True,
                'weather_success': True
            }
            
        except ValueError as e:
            #Weather call failed
            logger.error(f"Weather data collection failed: {e}")
            return {
                'mood': "Unable to predict mood - weather data unavailable",
                'weather_data': {},
                'llm_success': False,
                'weather_success': False
            }
        except Exception as e:
            #LLM call failed but weather worked
            logger.error(f"Error predicting mood with LLM: {e}")
            return {
                'mood': "Unable to predict mood - LLM service unavailable",
                'weather_data': weather_data_collection,
                'llm_success': False,
                'weather_success': True
            }

    def analyze_mood_history(self, tracks_data: Dict) -> Dict:
        """Analyze mood for multiple tracks based on music and weather data"""
        #Get mood and weather
        prediction_result = self.predict_mood_with_llm(tracks_data)
        overall_mood = prediction_result['mood']
        weather_data_collection = prediction_result['weather_data']
        llm_success = prediction_result['llm_success']
        weather_success = prediction_result['weather_success']
        
        analyzed_tracks = {}
        for track_number, track_info in tracks_data.items():
            if not weather_success:
                #Weather failed - still return track info
                analyzed_tracks[track_number] = {
                    'track_name': track_info['track_name'],
                    'artist_name': track_info['artist_name'],
                    'played_at': track_info["played_at"].strftime('%I:%M %p'),
                    'temperature': 'Weather data unavailable',
                    'type_of_weather': 'Weather data unavailable',
                    'predicted_mood': 'Mood prediction unavailable'
                }
            elif not llm_success:
                #LLM failed but weather succeeded - include weather data still tho
                weather_data = weather_data_collection.get(track_number)
                analyzed_tracks[track_number] = {
                    'track_name': track_info['track_name'],
                    'artist_name': track_info['artist_name'],
                    'played_at': track_info["played_at"].strftime('%I:%M %p'),
                    'temperature': weather_data['temperature'],
                    'type_of_weather': weather_data['type_of_weather'],
                    'predicted_mood': 'Mood prediction unavailable'
                }
            else:
                #Both succeeded - include both
                weather_data = weather_data_collection.get(track_number)
                analyzed_tracks[track_number] = {
                    'track_name': track_info['track_name'],
                    'artist_name': track_info['artist_name'],
                    'played_at': track_info["played_at"].strftime('%I:%M %p'),
                    'temperature': weather_data['temperature'],
                    'type_of_weather': weather_data['type_of_weather'],
                    'predicted_mood': overall_mood 
                }
        
        return analyzed_tracks