import os
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionModel, function_tool
from dotenv import load_dotenv
import asyncio
import re
load_dotenv()
api_key = os.environ.get("groq_api_key")
base_url = os.environ.get("GROQ_ENDPOINT")

class SpawnerAgent:
    def __init__(self, api_key = api_key,base_url = base_url):
        self.api_key = api_key
        self.base_url = base_url
        
    def return_agent(self):
        prompt = """
You are an Orchestrator Agent.

Your responsibility is to coordinate the creation of Twitter retweet agents using tools.
You must NOT write code yourself.

Context:
- You have access to a Google Sheets tool containing rows of negative Twitter posts.
- Each row contains:
  1. post_url
  2. negativity_reason

Workflow:
1. Read all rows from the Google Sheet.
2. For each row:
   - Extract the post_url and negativity_reason.
   - Call the Code Writing Agent tool with ONLY the following information:
     - post_url
     - negativity_reason
     - a unique agent_name
3. Receive generated code from the Code Writing Agent.
4. Immediately pass the received code to the File Writing Agent tool.
5. Repeat until all rows are processed.

Rules:
- Spawn exactly one agent per row.
- Do NOT generate code yourself.
- Do NOT modify Google Sheets.
- Do NOT analyze or edit the generated code.
- Do NOT keep or reason over code content.
- Treat code as opaque data.

Completion:
- Wait until all File Writing Agent calls confirm success.
- When all tasks are completed, respond with exactly:
  Done

No explanations. No summaries. No additional text.


"""
        groq_client = AsyncOpenAI(base_url = self.base_url, api_key=self.api_key)
        groq_model = OpenAIChatCompletionModel(moodel="llama-3.3-70b-versatile", openai_client = groq_client)
        agent = Agent(name="manager_agent", instructions = prompt, model = groq_model)
        return agent
    
    def extract_json(self, text):
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON found in LLM output")
    @function_tool
    def file_writer(filename: str, code: str) -> str:
        """
        Writes generated agent code to a file under the spawned_agents directory.
        """
        base_dir = "spawned_agents"
        os.makedirs(base_dir, exist_ok=True)
        if not filename.endswith(".py"):
            filename = f"{filename}.py"
        file_path = os.path.join(base_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
        return "Written"

    