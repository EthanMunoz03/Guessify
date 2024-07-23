import requests 
import os
from flask import Flask, render_template, url_for, request, redirect, jsonify

# Spotify API Authorization
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

rows = ["Guess 1", "Guess 2", "Guess 3", "Guess 4", "Guess 5", "Guess 6"]
current_row_index = 0

# Homepage
@app.route("/")
def home():
    return render_template('home.html')

# Game page
@app.route("/game", methods=['GET', 'POST'])
def game():
    
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