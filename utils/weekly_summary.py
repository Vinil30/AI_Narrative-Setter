from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()
groq_api_key = os.environ.get("groq_api_key")

class WeeklyAnalyser:
    def __init__(self,details,url,client,groq_api_key = groq_api_key):
        self.details = details
        self.groq_api_key = groq_api_key
        self.url = "https://api.groq.com/openai/v1"
        self.client = OpenAI(api_key=groq_api_key, base_url=self.url)

    def extract_json(self, text):
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON found in LLM output")
        return json.loads(match.group())
    def analyser(self):
        prompt = f"""You are an expert twitter reputation analyst and the following are the last 5 tweets extract results {self.details},
        your job is analyse the threats to reputation, provide conclusion and suggestions and overcome the negativity at the root level,
        also tell if some sort of long term negative narrative has been in process on the respective person or company.
        Respond in strict JSON
        {{
        weekly_analysis:"....something 400-500 words"
        }}"""

        messages = [{"role":"system","content":"You are an expert analyser and personal reputation handling agent."},
                    {"role":"user","content":prompt}]
        response = self.client.chat.completions.create(
            messages= messages,
            model="llama-3.3-70b-versatile"

        )
        output = response.choices[0].message.content
        final_output = self.extract_json(output)
        return final_output
    