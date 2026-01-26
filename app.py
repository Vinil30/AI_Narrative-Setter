from flask import Flask, request, render_template, jsonify
import os
import json
from dotenv import load_dotenv
from utils.twitter_scrapping import TwitterScrapping

load_dotenv()

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/twitter_analysis", methods = ["POST"])
def scrap_twitter():
    data = request.json
    topic = data["topic"]
    scrapper = TwitterScrapping(topic=topic)
    result = scrapper.summarizer()
    return jsonify({
        "analysis":result
    })

if __name__ == "__main__":
    app.run(debug=True)
