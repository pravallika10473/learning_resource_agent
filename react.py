import os
from dotenv import load_dotenv
from openai import OpenAI
import re
import httpx
import json
from function import search_youtube_videos, transcript_analyzer
from messages import system_message1, system_message2
import argparse

# Load environment variables from .env file
load_dotenv()

# Access the API key from environment variables
api_key = os.getenv('OPENAI_API_KEY')

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)

class Agent:
    def __init__(self, system=""):
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        completion = client.chat.completions.create(
                        model="gpt-4o", 
                        temperature=0,
                        messages=self.messages)
        return completion.choices[0].message.content
    
known_actions = {
    "search_youtube": search_youtube_videos,
    "transcript_analyzer": transcript_analyzer
}

action_re = re.compile('^Action: (\w+): (.*)$')   # python regular expression to selection action
system_message = system_message1.strip()

def query(question, max_turns=10):
    i = 0
    bot = Agent(system_message)
    next_prompt = question
    while i < max_turns:
        i += 1
        result = bot(next_prompt)
        print(result)
        actions = [
            action_re.match(a) 
            for a in result.split('\n') 
            if action_re.match(a)
        ]
        if actions:
            # There is an action to run
            action, action_input = actions[0].groups()
            if action not in known_actions:
                raise Exception("Unknown action: {}: {}".format(action, action_input))
            print(" -- running {} {}".format(action, action_input))
            observation = known_actions[action](action_input)
            # print("Observation:", observation)
            next_prompt = "Observation: {}".format(observation)
        else:
            return

if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("question", type=str, help="The question to query.")
    # args = parser.parse_args()
    parser= argparse.ArgumentParser()

    parser.add_argument("--query", type=str, help="Query to gpt")
    args=parser.parse_args()
    question=args.query
    query(question=question)
