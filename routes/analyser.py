from flask import Flask, Blueprint, request, jsonify
import json
from dotenv import load_dotenv
from pymongo import MongoClient
from utils.weekly_summary import WeeklyAnalyser
load_dotenv()
db_url = os.environ.get("MONGO_URI")

analyser_bp = Blueprint("analyser", __name__)
client = MongoClient(db_url)
db = client["AIPR"]
collection = db["twitter_analysis"]

def fetching_avg_pipeline(topic):
    return [
    {"$match":{"name":topic}},
    {"$sort":{ created_at : -1}},
    {"$limit":7},
    {"$group":{
            "_id":"$name",
            "avg_sentiment_score":{"$avg":"$sentiment_score"},

        }}
]

def fetching_summaries(topic):
    return [
        {"$match":topic},
        {"$sort":{created_at:-1}},
        {"$limit":5},
        {"$project":{
            "_id":0,
            "name":"$name",
            "analysis_summary":1,
            "analysis_sentiment":1,
            "reason_for_respective_sentiment":1,
            "intruders":1,
            "reputation_risk":1,
            "trend_direction":1

        }}
    ]

@analyser_bp.route("/retrieve-twitter-avgs", methods = ["POST"])
def retrieve_twitter_analysis():
    data = request.json
    topic = data["topic"]
    avg_pipeline = fetching_avg_pipeline(topic)
    avgs = list(collection.aggregate(avg_pipeline))
    return jsonify(
       { "avgs":avgs}
    )
    
    
@analyser_bp.route("/weekly-report", methods = ["POST"])
def weekly_report():
    data = request.json
    topic = data["topic"]
    summary_pipeline = fetching_summaries(topic)
    weekly_scraps = list(collection.aggregate(summary_pipeline))
    weekly_summary = WeeklyAnalyser(details=weekly_scraps)
    return jsonify({weekly_summary})
    
    