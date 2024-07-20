import requests 
import os
from flask import Flask, render_template, url_for

AUTH_URL = 'https://accounts.spotify.com/api/token'
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': os.environ.get('SPOTIFY_CLIENT_ID'),
    'client_secret': os.environ.get('SPOTIFY_CLIENT_SECRET'),
})
auth_response_data = auth_response.json()
access_token = auth_response_data['access_token']
headers = {'Authorization': 'Bearer {token}'.format(token=access_token)}

BASE_URL = 'https://api.spotify.com/v1/'

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/game")
def game():
    return render_template('game.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")