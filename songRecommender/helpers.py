import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Use environment variables for credentials (set these on Railway)
# Ensure that SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, and SPOTIFY_REDIRECT_URI are set in your Railway project
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.environ.get("SPOTIFY_CLIENT_ID", "your_default_client_id"),
    client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET", "your_default_client_secret"),
    redirect_uri=os.environ.get("SPOTIFY_REDIRECT_URI", "http://localhost:8000"),  # Update in production
    scope="user-read-playback-state streaming ugc-image-upload playlist-modify-public"
), requests_timeout=10, retries=10)


def get_albums_id(ids):
    album_ids = []
    results = sp.artist_albums(ids)
    for album in results['items']:
        album_ids.append(album['id'])
    return album_ids


def get_album_songs_id(ids):
    song_ids = []
    results = sp.album_tracks(ids, offset=0)
    for songs in results['items']:
        song_ids.append(songs['id'])
    print(ids, song_ids)
    return song_ids


def get_songs_features(ids):
    meta = sp.track(ids)
    features = sp.audio_features(ids)

    # meta information
    name = meta['name']
    album = meta['album']['name']
    artist = meta['album']['artists'][0]['name']
    release_date = meta['album']['release_date']
    length = meta['duration_ms']
    popularity = meta['popularity']
    ids = meta['id']

    # audio features
    acousticness = features[0]['acousticness']
    danceability = features[0]['danceability']
    energy = features[0]['energy']
    instrumentalness = features[0]['instrumentalness']
    liveness = features[0]['liveness']
    valence = features[0]['valence']
    loudness = features[0]['loudness']
    speechiness = features[0]['speechiness']
    tempo = features[0]['tempo']
    key = features[0]['key']
    time_signature = features[0]['time_signature']

    track = [name, album, artist, ids, release_date, popularity, length, danceability, acousticness,
             energy, instrumentalness, liveness, valence, loudness, speechiness, tempo, key, time_signature]
    columns = ['name', 'album', 'artist', 'id', 'release_date', 'popularity', 'length', 'danceability',
               'acousticness', 'energy', 'instrumentalness', 'liveness', 'valence', 'loudness',
               'speechiness', 'tempo', 'key', 'time_signature']
    return track, columns


def get_songs_artist_ids_playlist(ids):
    playlist = sp.playlist_tracks(ids)
    songs_id = []
    artists_id = []
    for result in playlist['items']:
        songs_id.append(result['track']['id'])
        for artist in result['track']['artists']:
            artists_id.append(artist['id'])
    return songs_id, artists_id


def download_albums(music_id, artist=False):
    tracks = []
    columns = []
    try:
        if artist:
            ids_album = get_albums_id(music_id)
        else:
            if isinstance(music_id, list):
                ids_album = music_id
            elif isinstance(music_id, str):
                ids_album = [music_id]

        for ids in ids_album:
            song_ids = get_album_songs_id(ids=ids)
            print(f"Album Length: {len(song_ids)}")
            for song in song_ids:
                track, columns = get_songs_features(song)
                tracks.append(track)
                print(f"Song Added: {track[0]} By {track[2]} from the album {track[1]}")
        print("Music Downloaded!")
        return tracks, columns
    except Exception as e:
        print("Error in download_albums:", e)
        return tracks, columns


def download_playlist(id_playlist, n_songs):
    tracks = []
    columns = []
    try:
        songs_id = []
        for i in range(0, n_songs, 100):
            playlist = sp.playlist_tracks(id_playlist, limit=100, offset=i)
            for songs in playlist['items']:
                songs_id.append(songs['track']['id'])
        counter = 1
        for ids in songs_id:
            track, columns = get_songs_features(ids)
            tracks.append(track)
            print(f"Song {counter} Added:")
            print(f"{track[0]} By {track[2]} from the album {track[1]}")
            counter += 1
        print("Music Downloaded!")
        return tracks, columns
    except Exception as e:
        print("Error in download_playlist:", e)
        return tracks, columns
