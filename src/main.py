import pandas as pd
from spotify_data_fetcher import fetch_recently_played
from mood_analyzer import MoodAnalyzer
import logging
from pathlib import Path
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def convert_to_local_time(utc_time_str: str) -> str:
    """Convert UTC timestamp to local timezone"""
    try:
        utc_time = datetime.fromisoformat(utc_time_str.replace('Z', '+00:00'))
        # Get user's timezone from env or default to system timezone
        user_timezone = os.getenv('TIMEZONE', 'America/Los_Angeles')
        local_tz = pytz.timezone(user_timezone)
        local_time = utc_time.astimezone(local_tz)
        return local_time.strftime('%I:%M %p')
    except Exception as e:
        logger.error(f"Error converting time: {e}")
        return utc_time_str  # Return orig. string if conversion fails

def main():
    try:
        logger.info("Starting Spotify x Deezer data collection...")
        music_info = fetch_recently_played()
        
        if not music_info:
            logger.error("No music data collected")
            return
            
        logger.info("Analyzing mood based on music and weather data...")
        mood_analyzer = MoodAnalyzer()
        analyzed_tracks = mood_analyzer.analyze_mood_history(music_info)

        #output: proj this into ui? future improvement
        print("\n=== Music Mood Analysis Results ===")
        print(f"Overall Predicted Mood: {analyzed_tracks[1]['predicted_mood']}")
        print("\nTrack Details:")
        print("-" * 80)
        
        for track_num, track_data in analyzed_tracks.items():
            # Convert UTC timestamp to local time
            local_time = convert_to_local_time(track_data['played_at'])
            
            print(f"\nTrack {track_num}:")
            print(f"Time: {local_time}")
            print(f"Track: {track_data['track_name']} by {track_data['artist_name']}")
            print(f"BPM: {track_data['bpm']}")
            print(f"Temperature: {track_data['temperature']}°C")
            print(f"Weather: {track_data['type_of_weather']}")
            print("-" * 40)
            
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    main() 