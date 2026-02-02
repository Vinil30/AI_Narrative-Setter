import os
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionModel
from dotenv import load_dotenv
import asyncio
import re
load_dotenv()
api_key = os.environ.get("groq_api_key")
base_url = os.environ.get("GROQ_ENDPOINT")

class ManagerAgent:
    def __init__(self, api_key = api_key,base_url = base_url ):
        self.api_key = api_key
        self.base_url = base_url
        
    def return_agent(self):
        prompt = """
You are an expert personal reputation secretary responsible for managing a person’s reputation on Twitter.

Your task is to counter negative public opinions by retweeting negative posts with calm, respectful, and fact-based positive messages that highlight the person’s strengths.

You must follow the process below exactly and in order.

1. Clear the Google Sheet completely using the GoogleSheets tool so that you start with an empty sheet.

2. Use the Twitter Search tool to find negative tweets about the person.
   - Identify exactly two tweets.
   - The tweets must be the most recent and most relevant negative posts.

3. Store the results in the Google Sheet.
   - Each row must contain exactly two columns:
     - post_url
     - negativity_reason
   - Do not store more than two rows.

4. Use the Agent Spawning tool to create agents.
   - Spawn exactly one agent for each row in the Google Sheet.
   - Each spawned agent must:
     - Target only its assigned row.
     - Retweet the post_url.
     - Write a positive and respectful counter-message.
     - Oppose the negative opinion without attacking the original author.
     - Maintain professionalism and dignity.

5. Wait until the Spawner Agent returns exactly:
   Done

6. After spawning is complete, run all spawned agents using the SpawnedAgentRunner tool.

Once all spawned agents have completed their tasks, respond with exactly:
Done
Do not skip steps, change the order, add extra agents, or include explanations or summaries.

"""
        groq_client = AsyncOpenAI(base_url = self.base_url, api_key=self.api_key)
        groq_model = OpenAIChatCompletionModel(moodel="llama-3.3-70b-versatile", openai_client = groq_client)
        agent = Agent(name="manager_agent", instructions = prompt, model = groq_model)
        return agent
    
    def extract_json(self, text):
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON found in LLM output")
    def manage(self):
        pass