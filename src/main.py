import pandas as pd
from spotify_data_fetcher import fetch_recently_played
from mood_analyzer import MoodAnalyzer, WeatherDataFetcher
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ensure_data_directory():
    """Ensure the data directory exists"""
    data_dir = Path('../data')
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def main():
    try:
        # Initialize data directory
        data_dir = ensure_data_directory()
        
        # Step 1: Collect Spotify data
        logger.info("Starting Spotify data collection...")
        music_info = fetch_recently_played()
        #print(music_info)
        
        # Step 2: Analyze mood based on music and weather
        logger.info("Starting mood analysis...")
        weather_fetcher = WeatherDataFetcher()
        weather_data = weather_fetcher.get_weather_data(music_info['played_at'])
        #print(weather_data)
        mood_analyzer = MoodAnalyzer()
        final_data = mood_analyzer.predict_mood_with_llm(music_info, weather_data, music_info['played_at'])
        all_data = music_info | weather_data
        prediction = final_data
        all_data['predicted_mood'] = prediction
        print(all_data)
        '''
        # Print sample of results
        print("\nSample of Results:")
        print(f"Total entries analyzed: {len(final_data)}")
        print("\nFirst 3 entries:")
        for _, row in final_data.head(3).iterrows():
            print(f"\nTime: {row['timestamp']}")
            print(f"Track: {row['track_name']} by {row['artist_name']}")
            print(f"Temperature: {row['temperature']}°C")
            print(f"Predicted Mood: {row['predicted_mood']}")'''
            
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        raise

if __name__ == "__main__":
    main() 