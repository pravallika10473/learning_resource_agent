import os
from dotenv import load_dotenv
from openai import OpenAI
import json
from function import search_youtube_videos
import argparse

# Load environment variables from .env file
load_dotenv()

# Access the API key from environment variables
api_key = os.getenv('OPENAI_API_KEY')

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)

parser= argparse.ArgumentParser()

parser.add_argument("--query", type=str, help="Query to gpt")
args=parser.parse_args()
query=args.query

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_youtube_videos",
            "description": "Search YouTube for videos based on a keyword",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "The keyword to search for on YouTube",
                    },
                    "channel_id": {
                        "type": "string",
                        "description": "The ID of the specific YouTube channel (optional)",
                        "default": None
                    },
                    "filter_keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional filters for the search results",
                        "default": None
                    }
                },
                "required": ["keyword"],
            },
        }
    }
]

# Initial message to start the process
messages = [
    {"role": "system", "content": "You are a smart research assistant. Use the tools to look up information. \
You are allowed to make multiple calls (either together or in sequence). \
Only look up information when you are sure of what you want. \
If you need to look up some information before asking a follow up question, you are allowed to do that!"},
    {"role": "user", "content": query}
]

# Function to process the chat completion and handle tool calls
def process_completion(client, messages, tools):
    call_count = 0  # Initialize call counter

    while True:
        call_count += 1  # Increment call counter

        # Create a chat completion
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        # Get the first message choice
        choice = completion.choices[0]

        # Check for tool calls in the message
        if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
            tool_call = choice.message.tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "search_youtube_videos":
                # Call the function with the arguments
                result = search_youtube_videos(**function_args)

                # Convert result to JSON string
                result_json_str = json.dumps(result)

                # Add the function result to the messages
                messages.append({"role": "function", "name": "search_youtube_videos", "content": result_json_str})

        else:
            # If no tool call, print the assistant's response and break the loop
            print(choice.message.content)
        if choice.finish_reason=="stop":
            break
            

    # Print the number of times the model was called
    print(f"Model was called {call_count} times.")

# Process the initial completion
process_completion(client, messages, tools)


