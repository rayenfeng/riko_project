# OpenAI tool calling with history 
### Uses a sample function
import yaml
import gradio as gr
import json
import os
from openai import OpenAI

with open('character_config.yaml', 'r') as f:
    char_config = yaml.safe_load(f)

# Initialize OpenAI client with custom endpoint support
client_kwargs = {'api_key': char_config['OPENAI_API_KEY']}
if char_config.get('OPENAI_API_BASE') and char_config['OPENAI_API_BASE'].strip():
    client_kwargs['base_url'] = char_config['OPENAI_API_BASE'].strip()

client = OpenAI(**client_kwargs)

# Constants
HISTORY_FILE = char_config['history_file']
MODEL = char_config['model']
SYSTEM_PROMPT =  [
        {
            "role": "system",
            "content": [
                {
                    "type": "input_text",
                    "text": char_config['presets']['default']['system_prompt']  
                }
            ]
        }
    ]

# Load/save chat history
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return SYSTEM_PROMPT

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)



def get_riko_response_no_tool(messages):

    # Call OpenAI with system prompt + history
    response = client.responses.create(
        model=MODEL,
        input= messages,
        temperature=1,
        top_p=1,
        max_output_tokens=2048,
        stream=False,
        text={
            "format": {
            "type": "text"
            }
        },
    )

    return response


def llm_response(user_input):

    messages = load_history()

    # Append user message to memory
    messages.append({
        "role": "user",
        "content": [
            {"type": "input_text", "text": user_input}
        ]
    })


    riko_test_response = get_riko_response_no_tool(messages)


    # just append assistant message to regular response. 
    messages.append({
    "role": "assistant",
    "content": [
        {"type": "output_text", "text": riko_test_response.output_text}
    ]
    })

    save_history(messages)
    return riko_test_response.output_text


if __name__ == "__main__":
    print('running main')