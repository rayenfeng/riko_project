# litellm tool calling with history
import yaml
import json
import os
from litellm import completion

with open('character_config.yaml', 'r') as f:
    char_config = yaml.safe_load(f)

# Set the API key for Groq
os.environ["GROQ_API_KEY"] = char_config.get('GROQ_API_KEY', 'YOUR_GROQ_API_KEY')

# Constants
HISTORY_FILE = char_config['history_file']
# We will use a Groq model. The user can change this in the config.
MODEL = char_config.get('model', 'groq/llama3-8b-8192')
SYSTEM_PROMPT =  [
        {
            "role": "system",
            "content": char_config['presets']['default']['system_prompt']
        }
    ]

# Load/save chat history
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    # Make sure the system prompt is always the first message
    return [SYSTEM_PROMPT[0]]

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def get_riko_response_no_tool(messages):
    # Call litellm with system prompt + history
    response = completion(
        model=MODEL,
        messages=messages,
        temperature=1,
        top_p=1,
        max_tokens=2048,
        stream=False,
    )
    return response

def llm_response(user_input):
    messages = load_history()

    # Append user message to memory
    messages.append({
        "role": "user",
        "content": user_input
    })

    riko_test_response = get_riko_response_no_tool(messages)

    # Get the response text from the litellm response
    response_text = riko_test_response.choices[0].message.content

    # Append assistant message to regular response.
    messages.append({
        "role": "assistant",
        "content": response_text
    })

    save_history(messages)
    return response_text

if __name__ == "__main__":
    print('running main')
