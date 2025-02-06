import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import random

# Use environment variables for credentials (provide defaults for local testing)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.environ.get("SPOTIFY_CLIENT_ID", "your_default_client_id"),
    client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET", "your_default_client_secret"),
    redirect_uri=os.environ.get("SPOTIFY_REDIRECT_URI", "https://web-production-dac50.up.railway.app/callback"),
    scope="user-read-playback-state streaming ugc-image-upload playlist-modify-public"
))

# Use a relative path for the data CSV (assuming test.py is in songRecommender/)
data_path = os.path.join(os.path.dirname(__file__), "data", "data_moods.csv")
df1 = pd.read_csv(data_path)

# Use a relative path for new.txt (assuming new.txt is in project-root)
new_txt_path = os.path.join(os.path.dirname(__file__), "..", "new.txt")
with open(new_txt_path, 'r') as fp:
    mood = fp.read().strip()

df2 = df1.loc[df1['mood'] == mood]
df2 = df2.astype({'id': 'string'})
list_of_songs = []
for row in df2.iterrows():
    list_of_songs.append("spotify:track:" + str(row[1]['id']))
list_of_songs = random.sample(list_of_songs, min(15, len(list_of_songs)))
print("Number of songs selected:", len(list_of_songs))
playlist_name = mood + ' Songs'
playlist_description = mood + ' Songs'
user_id = sp.me()['id']
sp.user_playlist_create(user=user_id, name=playlist_name, public=True, description=playlist_description)
prePlaylists = sp.user_playlists(user=user_id)
playlist = prePlaylists['items'][0]['id']
print("Created Playlist ID:", playlist)
sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist, tracks=list(list_of_songs))
print("Created " + mood + " playlist")
with open(new_txt_path, 'w') as fp:
    fp.write(playlist)
# Run test2.py via a relative path
os.system('python "' + os.path.join(os.path.dirname(__file__), "test2.py") + '"')
