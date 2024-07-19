from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', subtitle='Guess the song name!', text='Click on the play button to replay')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")