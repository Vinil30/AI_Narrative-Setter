from flask import Flask, request, render_template, jsonify, Blueprint
import os
import json
from dotenv import load_dotenv
from twitter_scrapping import TwitterScrapping
from datetime import datetime

load_dotenv()
db_url = os.environ.get("MONGO_URI")
twitter_bp = Blueprint("twitter", __name__)

client = MongoClient(db_url)
db = client["AIPR"]
collection = db["twitter_analysis"]
def structure_analysis(result):
    return {
            "name": result["name"],
            "analysis_summary": result["analysis_summary"],
            "analysis_sentiment": result["analysis_sentiment"],
            "sentiment_score": result["sentiment_score"],
            "reason_for_respective_sentiment": result["reason_for_respective_sentiment"],

            "key_themes": result.get("key_themes", []),
            "negativity_severity": result["negativity_severity"],

            "intruders": result.get("intruders", []),

            "dos": result.get("dos", []),
            "donts": result.get("donts", []),

            "tone_analysis": result["tone_analysis"],
            "tone_suggestions": result["tone_suggestions"],

            "reputation_risk": result["reputation_risk"],
            "risk_reason": result["risk_reason"],
            "trend_direction": result["trend_direction"]
        }

@twitter_bp.route("/twitter_analysis", methods = ["POST"])
def scrap_twitter():
    data = request.json
    topic = data["topic"]
    scrapper = TwitterScrapping(topic=topic)
    result = scrapper.summarizer()
    structured_result = structure_analysis(result)
    structured_result["created_at"] = datetime.utcnow()
    collection.insert_one(structured_result)
    return jsonify({
        "analysis":result
    })