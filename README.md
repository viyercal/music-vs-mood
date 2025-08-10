# music-vs-mood
A repository containing code that predicts a user's mood from their Spotify listening history combined with environmental factors.

As an overview of the underlying code: a user's recently played set of songs from Spotify is pulled via Spotify's web API. The timestamp corresponding to when the music was played is used with location data to pull weather information, and this is combined into one payload to send to a lightweight LLM (i.e. Gemini 2.5 Flash Lite) which predicts the user's mood given this information. 

Sample output for past 5 played tracks (note slight weather differences are attributable to weather fluctuations over time as well as OpenWeatherAPI weather instability):

<img width="811" height="631" alt="image" src="https://github.com/user-attachments/assets/f97fa23a-da95-4f76-8c97-caf0d8fc4345" />

In order to run this code: 

1. Install requirements in requirements.txt 

2. Copy the .env/example file and configure to match your own API Keys, timezone, and longitude/latitude. 

3. Run main.py
