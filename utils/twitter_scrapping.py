from dotenv import load_dotenv
import os
import json
import requests
from openai import OpenAI
load_dotenv(override=True)
twitter_api_key = os.environ.get("twitter_rapid_api_key")
groq_api_key = os.environ.get("groq_api_key")
url = "https://twitter241.p.rapidapi.com/search"
base_url="https://api.groq.com/openai/v1"
import re
class TwitterScrapping:
    def __init__(self,topic,url = url,groq_api_key = groq_api_key, twitter_api_key = twitter_api_key, base_url = base_url):
        self.groq_api_key = groq_api_key
        self.twitter_api_key = twitter_api_key
        self.topic = topic
        self.url = url
        self.base_url = base_url

    def extract_json(self, text):
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON found in LLM output")

        return json.loads(match.group())
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

        prompt = f"""
            You are an expert Twitter reputation analyst.

            Below are the top 10 tweets and their comments related to the person: {self.topic}
            Tweets data:
            {context}

            Tasks:
            1. Analyze public sentiment and themes.
            2. Identify unnecessary negativity and its severity.
            3. Provide actionable, reputation-safe recommendations.

            Respond ONLY in strict JSON format.

            Expected JSON:
            {{
            "name":"{self.topic}",
            "analysis_summary":"~100 words factual summary",
            "analysis_sentiment":"positive/negative/neutral",
            "sentiment_score":"float between -1 and 1",
            "reason_for_respective_sentiment":"clear explanation",
            "key_themes":[
                {{"theme":"...","impact":"positive/negative"}}
            ],
            "negativity_severity":"low/medium/high",
            "intruders":[
                {{"tweet":"...","reason":"why it spreads negativity"}}
            ],
            "dos":[ "...", "..." ],
            "donts":[ "...", "..." ],
            "tone_analysis":"...",
            "tone_suggestions":"...",
            "reputation_risk":"low/medium/high",
            "risk_reason":"...",
            "trend_direction":"improving/declining/stable"
            }}

            Rules:
            - Do NOT hallucinate tweets
            - If data is insufficient, mention it explicitly
            - No emojis, no markdown, no extra text
            """

        messages = [{"role":"user", "content":"You are an expert analyser"},
                    {"role":"system", "content":prompt}]
        client = OpenAI(api_key=self.groq_api_key, base_url=self.base_url)
        response = client.chat.completions.create(
            messages= messages,
            model="llama-3.3-70b-versatile"

        )
        output = response.choices[0].message.content
        final_output = self.extract_json(output)
        return final_output
    