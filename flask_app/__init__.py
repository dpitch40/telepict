from flask import Flask, render_template

from config import Config


app = Flask('Telepict')
app.config.from_object(Config)

@app.route('/')
def index():
    return render_template('index.html')