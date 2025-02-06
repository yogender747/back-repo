from flask import Flask, render_template, request, jsonify, session
import cv2
import numpy as np
from keras.models import load_model
from keras.preprocessing.image import img_to_array
import pandas as pd
import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for session management

# ✅ Load Face Detector & Model
face_cascade = cv2.CascadeClassifier(r'D:\AI\FR\emotionDetection\haarcascade_frontalface_default.xml')
classifier = load_model(r'D:\AI\FR\emotionDetection\model.h5')

# ✅ Emotion Labels
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

# ✅ Load Music Dataset
data_moods_path = r'D:\AI\FR\songRecommender\data\data_moods.csv'
df1 = pd.read_csv(data_moods_path)

# ✅ Initialize Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="af82b6b373624e18be88dd94e0a97065",
    client_secret="33827c4e4ffd40b7b1f8e3492a2345ad",
    redirect_uri="http://localhost:8000",
    scope="user-read-playback-state user-library-read playlist-read-private playlist-read-collaborative playlist-modify-public"
))

@app.route('/')
def index():
    return render_template('camera.html')

@app.route('/playlist.html')
def playlist():
    return render_template('playlist.html')

# ✅ Updated: Fetch Recommended Albums (Now Using a broader search with randomized offset)
@app.route('/recommended-albums')
def recommended_albums():
    try:
        print("🔎 Fetching recommended albums...")

        # Get the mood parameter from the request query string; default to 'happy'
        mood = request.args.get('mood', 'happy')
        
        # Define the maximum number of albums to fetch (Spotify allows up to 50 per request for search)
        limit = 50
        
        # To get a variety of albums, choose a random offset (Spotify’s search API supports an offset up to 1000)
        offset = random.randint(0, 950)
        
        # Use the search endpoint to look for albums matching the mood keyword.
        results = sp.search(q=mood, type='album', limit=limit, offset=offset)
        albums = results.get('albums', {}).get('items', [])
        
        if not albums:
            return jsonify({"error": "No recommended albums found"}), 500
        
        # Shuffle the albums to get different results each time.
        random.shuffle(albums)
        
        # Build album data from all fetched albums.
        album_data = [
            {
                "name": album['name'],
                "artist": album['artists'][0]['name'],
                "url": album['external_urls']['spotify'],
                "image": album['images'][0]['url'] if album.get('images') and len(album['images']) > 0 else "https://via.placeholder.com/100"
            }
            for album in albums
        ]
        
        return jsonify({"albums": album_data})
    
    except Exception as e:
        print("🚨 Error fetching recommended albums:", str(e))
        return jsonify({"error": str(e)}), 500

# ✅ Store & Retrieve Emotion History
@app.route('/emotion-history')
def emotion_history():
    """
    API to retrieve detected emotion history.
    """
    emotion_data = session.get('emotion_history', [])
    return jsonify({"history": emotion_data})

@app.route('/detect', methods=['POST'])
def detect():
    file = request.files.get('image')
    if file is None:
        return jsonify({"error": "No image received"}), 400

    npimg = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({"error": "Error decoding image"}), 400

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        return jsonify({"error": "No face detected"}), 400

    # ✅ Detect Emotion
    emotions_detected = []
    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        roi_gray = cv2.resize(roi_gray, (48, 48))

        roi = roi_gray.astype("float") / 255.0
        roi = img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)

        prediction = classifier.predict(roi)[0]
        label = emotion_labels[np.argmax(prediction)]
        emotions_detected.append(label)

    detected_emotion = max(set(emotions_detected), key=emotions_detected.count)

    # ✅ Store Emotion History (keep only the last 20 records in session)
    emotion_data = session.get('emotion_history', [])
    emotion_data.append({"emotion": detected_emotion, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    session['emotion_history'] = emotion_data[-20:]

    # ✅ Map Emotions to Playlists
    mood_mapping = {
        "Angry": "Energetic",
        "Surprise": "Energetic",
        "Fear": "Calm",
        "Neutral": "Calm",
        "Happy": "Happy",
        "Sad": "Sad"
    }
    mood = mood_mapping.get(detected_emotion, "Calm")

    # ✅ Fetch Songs Based on Mood
    df2 = df1[df1['mood'] == mood]
    if df2.empty:
        return jsonify({"error": "No songs found for this mood"}), 400

    df2 = df2.astype({'id': 'string'})
    list_of_songs = ["spotify:track:" + str(row[1]['id']) for row in df2.iterrows()]
    list_of_songs = random.sample(list_of_songs, min(len(list_of_songs), 15))

    # ✅ Create Playlist on Spotify
    playlist_name = f"{mood} Songs"
    user_id = sp.me()['id']
    new_playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True, description=f"Playlist for {mood} mood")
    playlist_id = new_playlist['id']
    sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist_id, tracks=list_of_songs)

    print(f"✅ Created Playlist: {playlist_name} - {playlist_id}")

    # ✅ Return JSON Response with Redirect URL to playlist.html
    return jsonify({"emotion": detected_emotion, "redirect": f"/playlist.html?playlist={playlist_id}"})

if __name__ == '__main__':
    app.run(debug=True)
