import requests 
import random
import time
import os
from functools import wraps
from flask import Flask, render_template, url_for, request, redirect, jsonify, session

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Spotify API Variables
#CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
CLIENT_ID = '2b5e3823db8e4c2dbc07fe7486bf167c'
#CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
CLIENT_SECRET = '5c1ecda79f3947728c13ba97b1e3e629'
REDIRECT_URI = 'https://rubysong-idiomscroll-5000.codio.io/callback'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
SCOPE = 'streaming app-remote-control user-read-email user-read-playback-state user-modify-playback-state user-read-private user-library-read'
# playlist-read-private

# Guesses-Table Variables
rows = ["Guess 1", "Guess 2", "Guess 3", "Guess 4", "Guess 5", "Guess 6"]

# Creates Access Token for Session
@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    response = requests.post(TOKEN_URL, data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })
    token_info = response.json()
    session['token'] = token_info['access_token']
    session['refresh_token'] = token_info['refresh_token']
    session['token_expires_at'] = time.time() + token_info['expires_in']
    return redirect(state or url_for('game'))

# Redirects to Spotify Authorization Page
@app.route('/login')
def login():
    next_url = request.args.get('next') or url_for('home')
    auth_url = f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&scope={SCOPE}&redirect_uri={REDIRECT_URI}&state={next_url}"
    # print(f"Authorization URL: {auth_url}")
    return redirect(auth_url)

# Check if Token has Expired
def is_token_expired():
    return time.time() > session.get('token_expires_at', 0)

# Refresh Expired Token
def refresh_token():
    refresh_token = session.get('refresh_token')
    response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })
    token_info = response.json()
    session['token'] = token_info['access_token']
    session['token_expires_at'] = time.time() + token_info['expires_in']
    if 'refresh_token' in token_info:
        session['refresh_token'] = token_info['refresh_token']

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Homepage
@app.route("/")
def home():
    return render_template('home.html')

# Gamepage
@app.route("/game")
def game():
    token = session.get('token')
    if not token:
        return redirect(url_for('login', next=request.url))
    return render_template('game.html', rows=rows)

# Chooses a Random Song from a Random Playlist
@app.route('/random_song')
def random_song():
    token = session.get('token')
    if not token:
        return jsonify({'error': 'Unauthorized'}), 401

    # Get User Playlists
    playlists_response = requests.get(
        'https://api.spotify.com/v1/me/playlists',
        headers={'Authorization': f'Bearer {token}'}
    ).json()

    playlists = playlists_response.get('items', [])
    if not playlists:
        return jsonify({'error': 'No playlists found'}), 404

    # Choose a Random Playlist
    playlist = random.choice(playlists)
    playlist_id = playlist['id']

    # Get Tracks from the Playlist
    tracks_response = requests.get(
        f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks',
        headers={'Authorization': f'Bearer {token}'}
    ).json()

    tracks = tracks_response.get('items', [])
    if not tracks:
        return jsonify({'error': 'No tracks found in the playlist'}), 404

    # Choose a Random Track
    track = random.choice(tracks)
    track_uri = track['track']['uri']
    track_title = track['track']['name']
    track_artist = ', '.join([artist['name'] for artist in track['track']['artists']])
    track_image = track['track']['album']['images'][0]['url']

    return jsonify({'track_uri': track_uri, 'track_title': track_title, 'track_artist': track_artist, 'track_image': track_image})

# Play a New Song in Player
@app.route('/play_track', methods=['POST'])
def play_track():
    token = session.get('token')
    if not token:
        return jsonify({'error': 'Unauthorized'}), 401

    track_uri = request.json.get('track_uri')
    device_id = request.json.get('device_id')
    if not track_uri or not device_id:
        return jsonify({'error': 'No track URI or device ID provided'}), 400

    response = requests.put(
        'https://api.spotify.com/v1/me/player/play',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        json={
            'device_id': device_id,
            'uris': [track_uri]
        }
    )

    if response.status_code == 204:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'error': 'Failed to start playback'}), response.status_code

# Updates Table with Guess
@app.route('/update_table', methods=['POST'])
def update_table():
    global rows, current_row_index
    if request.method == 'POST':
        new_value = request.form['guess']
        return jsonify(success=True, new_value=new_value)
    return render_template('game.html', rows=rows)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")