from dotenv import load_dotenv
import os
import json
import requests
from openai import OpenAI
twitter_api_key = os.environ.get("twitter_rapid_api_key")
gemini_api_key = os.environ.get("gemini_api_key")
url = "https://twitter241.p.rapidapi.com/search"
base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
class TwitterScrapping:
    def __init__(self,topic,url = url,gemini_api_key = gemini_api_key, twitter_api_key = twitter_api_key, base_url = base_url):
        self.gemini_api_key = gemini_api_key
        self.twitter_api_key = twitter_api_key
        self.topic = topic
        self.url = url
        self.base_url = base_url

    def twitter_scrapper(self):
        params = {
            "type": "Top",
            "count": 2,
            "query": f"{self.topic}",
            "lang":"en"
        }

        headers = {
            "x-rapidapi-host": "twitter241.p.rapidapi.com",
            "x-rapidapi-key": self.twitter_api_key
        }

        response = requests.get(self.url, headers=headers, params=params)
        data = response.json()

        tweets = []

        instructions = (
            data.get("result", {})
                .get("timeline", {})
                .get("instructions", [])
        )

        for instruction in instructions:
            for entry in instruction.get("entries", []):
                content = entry.get("content", {})
                item = content.get("itemContent", {})
                tweet_result = item.get("tweet_results", {}).get("result")

                if tweet_result and "legacy" in tweet_result:
                    tweets.append(tweet_result["legacy"])
        
        return tweets
    def summarizer(self):
        context = self.twitter_scrapper()

        prompt = f"""You are expert twitter analyst and here are the top 2 on the topic:{self.topic} and the tweets are {context},
        analyse the comments and provide suggestions to the person to improve his positive image in society and maintain dignity in social media.
        """
        messages = [{"role":"user", "content":"You are an expert analyser"},
                    {"role":"system", "content":prompt}]
        client = OpenAI(api_key=self.gemini_api_key, base_url=self.base_url)
        response = client.chat.completions.create(
            messages= messages,
            model="gemini-2.5-flash"

        )
        return response.choices[0].message