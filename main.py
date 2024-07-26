import requests 
import os
from functools import wraps
from flask import Flask, render_template, url_for, request, redirect, jsonify, session

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Spotify API credentials
#CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
CLIENT_ID = '2b5e3823db8e4c2dbc07fe7486bf167c'
#CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
CLIENT_SECRET = '5c1ecda79f3947728c13ba97b1e3e629'
REDIRECT_URI = 'https://rubysong-idiomscroll-5000.codio.io/callback'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
SCOPE = 'user-read-playback-state user-modify-playback-state user-read-private user-read-email user-library-read user-library-modify'

rows = ["Guess 1", "Guess 2", "Guess 3", "Guess 4", "Guess 5", "Guess 6"]
current_row_index = 0

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
    response_data = response.json()
    session['token'] = response_data['access_token']
    # print(f"Token set: {session['token']}")
    return redirect(state or url_for('game'))

# Redirects to Spotify Authorization Page
@app.route('/login')
def login():
    next_url = request.args.get('next') or url_for('home')
    auth_url = f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&scope={SCOPE}&redirect_uri={REDIRECT_URI}&state={next_url}"
    # print(f"Authorization URL: {auth_url}")
    return redirect(auth_url)

# Login Required to Play Game
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            login_url = url_for('login', next=request.url)
            # print(f"Redirecting to login. No token found. URL: {login_url}")
            return redirect(login_url)
        return f(*args, **kwargs)
    return decorated_function

# Homepage
@app.route("/")
def home():
    return render_template('home.html')

# Gamepage
@app.route("/game")
@login_required
def game():
    return render_template('game.html', rows=rows)

# Updates Table with Guess
@app.route('/update_table', methods=['POST'])
def update_table():
    global rows, current_row_index
    if request.method == 'POST':
        new_value = request.form['guess']

        # add guess checking here

        # if guess is incorrect, add it to the table
        if current_row_index < len(rows):
            rows[current_row_index] = new_value
            row_index = current_row_index
            current_row_index = (current_row_index + 1) % len(rows)
            return jsonify(success=True, row_index=row_index, new_value=new_value)
        return jsonify(success=False)
    return render_template('game.html', rows=rows)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")