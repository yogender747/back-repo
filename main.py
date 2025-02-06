import os
import psutil  # For logging memory usage (optional)
import cv2
import numpy as np
import pandas as pd
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import img_to_array  # Updated import for Keras
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# --------------------------------------------------
# Resource & Memory Optimizations
# --------------------------------------------------

# Force TensorFlow to run on CPU (prevents GPU-related issues)
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# Disable oneDNN optimizations to reduce memory usage
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# --------------------------------------------------
# Optional: Log current memory usage at startup
process = psutil.Process(os.getpid())
print("Startup Memory Usage: {:.2f} MB".format(process.memory_info().rss / 1024 / 1024))

# --------------------------------------------------
# Create Flask app and set template folder
# Assumes that the 'emotionDetection' folder is a sibling of your backend folder.
app = Flask(__name__, template_folder="../emotionDetection/templates")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersecretkey")  # Use environment variable in production

# --------------------------------------------------
# Load Face Detector & Model
# Build absolute paths based on current file's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cascade_path = os.path.join(BASE_DIR, '..', 'emotionDetection', 'haarcascade_frontalface_default.xml')
model_path = os.path.join(BASE_DIR, '..', 'emotionDetection', 'model.h5')

# Check if required files exist; if not, raise an error
if not os.path.exists(cascade_path):
    raise FileNotFoundError(f"Missing file: {cascade_path}")
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Missing file: {model_path}")

face_cascade = cv2.CascadeClassifier(cascade_path)
classifier = load_model(model_path)

# --------------------------------------------------
# Define Emotion Labels
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

# --------------------------------------------------
# Load Music Dataset
data_moods_path = os.path.join(BASE_DIR, 'songRecommender', 'data', 'data_moods.csv')
df1 = pd.read_csv(data_moods_path)

# --------------------------------------------------
# Initialize Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.environ.get("SPOTIFY_CLIENT_ID"),
    client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET"),
    redirect_uri="https://web-production-dac50.up.railway.app/callback",  # Ensure this URL is added to your Spotify Developer Dashboard
    scope="user-read-playback-state user-library-read playlist-read-private playlist-read-collaborative playlist-modify-public"
))

# --------------------------------------------------
# Additional OpenCV Settings (reduce memory usage)
cv2.setUseOptimized(False)
cv2.ocl.setUseOpenCL(False)

# --------------------------------------------------
# Routes
@app.route('/')
def index():
    return render_template('camera.html')

@app.route('/playlist.html')
def playlist():
    return render_template('playlist.html')

@app.route('/recommended-albums')
def recommended_albums():
    try:
        print("🔎 Fetching recommended albums...")
        mood = request.args.get('mood', 'happy')
        limit = 50
        offset = random.randint(0, 950)
        results = sp.search(q=mood, type='album', limit=limit, offset=offset)
        albums = results.get('albums', {}).get('items', [])
        if not albums:
            return jsonify({"error": "No recommended albums found"}), 500
        random.shuffle(albums)
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

@app.route('/emotion-history')
def emotion_history():
    return jsonify({"history": session.get('emotion_history', [])})

@app.route('/detect', methods=['POST'])
def detect():
    # Optional: Log memory usage before processing
    print("Memory before processing: {:.2f} MB".format(process.memory_info().rss / 1024 / 1024))
    
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

    # Update emotion history in session (limit to last 20 records)
    emotion_data = session.get('emotion_history', [])
    emotion_data.append({
        "emotion": detected_emotion, 
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    session['emotion_history'] = emotion_data[-20:]

    mood_mapping = {
        "Angry": "Energetic",
        "Surprise": "Energetic",
        "Fear": "Calm",
        "Neutral": "Calm",
        "Happy": "Happy",
        "Sad": "Sad"
    }
    mood = mood_mapping.get(detected_emotion, "Calm")

    df2 = df1[df1['mood'] == mood]
    if df2.empty:
        return jsonify({"error": "No songs found for this mood"}), 400

    df2 = df2.astype({'id': 'string'})
    list_of_songs = ["spotify:track:" + str(row[1]['id']) for row in df2.iterrows()]
    list_of_songs = random.sample(list_of_songs, min(len(list_of_songs), 15))

    playlist_name = f"{mood} Songs"
    user_id = sp.me()['id']
    new_playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True, description=f"Playlist for {mood} mood")
    playlist_id = new_playlist['id']
    sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist_id, tracks=list_of_songs)

    print(f"✅ Created Playlist: {playlist_name} - {playlist_id}")
    return jsonify({"emotion": detected_emotion, "redirect": f"/playlist.html?playlist={playlist_id}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=(os.environ.get("FLASK_ENV") != "production"))
