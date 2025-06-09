import pandas as pd
from spotify_data_fetcher import fetch_recently_played
from mood_analyzer import MoodAnalyzer
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Starting Spotify x Deezer data collection...")
        music_info = fetch_recently_played()
        
        logger.info("Starting mood analysis w/Weather & LLM")
        mood_analyzer = MoodAnalyzer()
        analyzed_tracks = mood_analyzer.analyze_mood_history(music_info)
        print(analyzed_tracks) #this is the final data
            
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        raise

if __name__ == "__main__":
    main() 