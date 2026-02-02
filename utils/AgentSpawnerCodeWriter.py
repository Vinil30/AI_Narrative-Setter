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
    def __init__(self,post_url,negativity_reason, agent_name, api_key = api_key,base_url = base_url ):
        self.api_key = api_key
        self.base_url = base_url
        self.post_url = post_url
        self.negativity_reason = negativity_reason
        self.agent_name = agent_name
        


    def template_extractor(self):
        with open("code_writer_template.py", "r") as f:
            code = f.read()
        return code  
    
    def user_prompt(self):
        prompt = f"""
    You must generate code using the template below.

    POST URL:
    {self.post_url}

    NEGATIVITY REASON:
    {self.negativity_reason}

    AGENT NAME:
    {self.agent_name}

    Here is the exact template you must follow:
    """
        prompt += self.template_extractor()
        return prompt

    def extract_json(self, text):
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON found in LLM output")
        
        return match.group()

        
    def return_agent(self):
        prompt = """
You are a Code Writing Agent.

Your only task is to generate Python code for a Twitter retweet agent.

Input you will receive:
- post_url: URL of a negative Twitter post
- negativity_reason: reason or topic of negativity
- agent_name: unique name for the agent

Your output must be valid Python code that:
1. Defines an autonomous agent named exactly as agent_name.
2. Retweets the given post_url.
3. Writes a respectful, positive counter-message.
4. Highlights positive qualities related to the negativity_reason.
5. Avoids insults, sarcasm, or personal attacks.
6. Maintains professionalism and factual tone.

Constraints:
- Generate ONLY code.
- No explanations.
- No markdown.
- No comments outside the code.
- Do NOT import unnecessary libraries.
- Assume Twitter API credentials are available via environment variables.

Output format (strict JSON):
{
  "filename": "<agent_name>.py",
  "code": "<full python code>"
}


"""
        groq_client = AsyncOpenAI(base_url = self.base_url, api_key=self.api_key)
        groq_model = OpenAIChatCompletionModel(model="llama-3.3-70b-versatile", openai_client = groq_client)
        agent = Agent(name="manager_agent", instructions = prompt, model = groq_model)
        return agent
    
    
    async def final_agent(self):
        user_prompt = self.user_prompt()
        agent = self.return_agent()
        response = await Runner.run(
            agent = agent,
            input = user_prompt
        )
        json_output = response.final_output
        output = self.extract_json(json_output)
        return output