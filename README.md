# music-vs-mood
A repository containing code that predicts a user's mood from their Spotify listening history combined with environmental factors.

As an overview of the underlying code: a user's recently played set of songs from Spotify is pulled via Spotify's web API, and bpm info is taken from Deezer's API by matching song titles & artists. The timestamp corresponding to when the music was played is used with location data to pull weather information, and this is combined into one payload to send to a lightweight LLM (i.e. Gemini 2.5 Flash) which predicts the user's mood given this information. 


Sample Output for past 5 played tracks:

![image](https://github.com/user-attachments/assets/b65eab97-70f3-487f-a9ac-43b131787401)
