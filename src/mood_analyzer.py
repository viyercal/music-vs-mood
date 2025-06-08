import pandas as pd
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import logging
from typing import Dict, List, Optional
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class WeatherDataFetcher:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        if not self.api_key:
            raise ValueError("Please set OPENWEATHER_API_KEY environment variable")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
    def get_weather_data(self, lat: float, lon: float, timestamp: datetime) -> Optional[Dict]:
        """Get weather data for a specific location and time"""
        try:
            # Convert timestamp to Unix timestamp
            unix_timestamp = int(timestamp.timestamp())
            
            # Make request to OpenWeather API
            url = f"{self.base_url}/onecall/timemachine"
            params = {
                'lat': lat,
                'lon': lon,
                'dt': unix_timestamp,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant weather data
            weather_data = {
                'temperature': data['current']['temp'],
                'humidity': data['current']['humidity'],
                'weather_condition': data['current']['weather'][0]['main'],
                'clouds': data['current']['clouds'],
                'wind_speed': data['current']['wind_speed']
            }
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return None

class MoodAnalyzer:
    def __init__(self, lat: float, lon: float):
        self.weather_fetcher = WeatherDataFetcher()
        self.lat = lat
        self.lon = lon
        
    def _calculate_mood_score(self, bpm: float, weather_data: Dict) -> float:
        """Calculate mood score based on BPM and weather data"""
        # Normalize BPM to 0-1 scale (assuming typical BPM range is 60-180)
        normalized_bpm = (bpm - 60) / 120
        
        # Weather impact factors (these weights can be adjusted)
        weather_weights = {
            'temperature': 0.3,
            'humidity': 0.2,
            'clouds': 0.2,
            'wind_speed': 0.1
        }
        
        # Calculate weather score
        weather_score = (
            (weather_data['temperature'] / 40) * weather_weights['temperature'] +
            (weather_data['humidity'] / 100) * weather_weights['humidity'] +
            (weather_data['clouds'] / 100) * weather_weights['clouds'] +
            (min(weather_data['wind_speed'], 30) / 30) * weather_weights['wind_speed']
        )
        
        # Combine BPM and weather scores (adjust weights as needed)
        mood_score = (normalized_bpm * 0.6) + (weather_score * 0.4)
        
        return min(max(mood_score, 0), 1)  # Ensure score is between 0 and 1
    
    def analyze_mood_history(self, music_data: pd.DataFrame) -> pd.DataFrame:
        """Analyze mood history based on music and weather data"""
        mood_data = []
        
        for _, row in music_data.iterrows():
            timestamp = pd.to_datetime(row['timestamp'])
            
            # Get weather data for the timestamp
            weather_data = self.weather_fetcher.get_weather_data(
                self.lat, self.lon, timestamp
            )
            
            if weather_data and 'bpm' in row:
                mood_score = self._calculate_mood_score(row['bpm'], weather_data)
                
                mood_entry = {
                    'timestamp': timestamp,
                    'track_name': row['track_name'],
                    'artist_name': row['artist_name'],
                    'bpm': row['bpm'],
                    'mood_score': mood_score,
                    **weather_data
                }
                mood_data.append(mood_entry)
        
        return pd.DataFrame(mood_data)
    
    def get_mood_trends(self, mood_data: pd.DataFrame) -> Dict:
        """Analyze mood trends over different time periods"""
        # Ensure timestamp is datetime
        mood_data['timestamp'] = pd.to_datetime(mood_data['timestamp'])
        
        # Add time-based columns
        mood_data['hour'] = mood_data['timestamp'].dt.hour
        mood_data['day_of_week'] = mood_data['timestamp'].dt.day_name()
        
        # Calculate average mood by hour
        hourly_mood = mood_data.groupby('hour')['mood_score'].mean()
        
        # Calculate average mood by day of week
        daily_mood = mood_data.groupby('day_of_week')['mood_score'].mean()
        
        # Calculate correlation between BPM and mood
        bpm_correlation = mood_data['bpm'].corr(mood_data['mood_score'])
        
        # Calculate correlation between weather factors and mood
        weather_correlations = {
            'temperature': mood_data['temperature'].corr(mood_data['mood_score']),
            'humidity': mood_data['humidity'].corr(mood_data['mood_score']),
            'clouds': mood_data['clouds'].corr(mood_data['mood_score']),
            'wind_speed': mood_data['wind_speed'].corr(mood_data['mood_score'])
        }
        
        return {
            'hourly_mood': hourly_mood.to_dict(),
            'daily_mood': daily_mood.to_dict(),
            'bpm_correlation': bpm_correlation,
            'weather_correlations': weather_correlations
        }

def main():
    # Example usage
    # Load your music data
    music_data = pd.read_csv('../data/deezer_raw.csv')
    
    # Initialize analyzer with your location (example coordinates for New York City)
    analyzer = MoodAnalyzer(lat=40.7128, lon=-74.0060)
    
    # Analyze mood history
    mood_data = analyzer.analyze_mood_history(music_data)
    
    # Get mood trends
    trends = analyzer.get_mood_trends(mood_data)
    
    # Save results
    mood_data.to_csv('../data/mood_analysis.csv', index=False)
    
    # Print some insights
    print("\nMood Analysis Results:")
    print(f"BPM Correlation with Mood: {trends['bpm_correlation']:.2f}")
    print("\nWeather Correlations:")
    for factor, correlation in trends['weather_correlations'].items():
        print(f"{factor}: {correlation:.2f}")
    
    print("\nAverage Mood by Hour:")
    for hour, score in trends['hourly_mood'].items():
        print(f"{hour:02d}:00 - {score:.2f}")

if __name__ == "__main__":
    main() 