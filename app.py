from flask import Flask, request, render_template, jsonify
import os
import json
from dotenv import load_dotenv
from routes.twitter import twitter_bp
load_dotenv()

app = Flask(__name__)
app.register_blueprint(twitter_bp)


@app.route("/")
def home():
    return render_template("admin_page.html")

if __name__ == "__main__":
    app.run(debug=True)
