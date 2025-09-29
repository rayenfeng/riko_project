# OpenAI tool calling with history and ollama added... OpenAI has been commented out in this version
### Uses a sample function
import yaml
import gradio as gr
import json
import os
# from openai import OpenAI  
import requests # pulls network request?

#below this point is where I configured it to work for ollama, i have no idea how it works. it just works. Vibe coding my beloved.


with open('character_config.yaml', 'r') as f:
    char_config = yaml.safe_load(f)

# client = OpenAI(api_key=char_config['OPENAI_API_KEY'])

# Constants
HISTORY_FILE = char_config['history_file']
MODEL = char_config['model']
SYSTEM_PROMPT = [
    {
        "role": "system",
        "content": char_config['presets']['default']['system_prompt']
    }
]

    # SUPER IMPORTANT: If altering preexisting riko app, to include the local Ollama, you may need to reformat
    #                  you chat history or delete it all together because OpenAI and Ollama have different formatting.

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

    # Call Ollama with system prompt+history from locally hosted web app
    url = "http://localhost:11434/api/chat"
    data = {
        "model": MODEL,
        "messages": messages,
        "stream": False
    }

    response = requests.post(url, json=data)
    

    # print("Raw Ollama Response:", response.text[:300]) //also used for troubleshooting
    response.raise_for_status()  #used for troubleshooting

    result = response.json()
    return result['message']['content'] # this should return a string

    # Call OpenAI with system prompt + history
    # response = client.responses.create(
        # model=MODEL,
        # input= messages,
        # temperature=1,
        # top_p=1,
        # max_output_tokens=2048,
        # stream=False,
        # text={
            # "format": {
            # "type": "text"
            # }
        # },
    # )

    # return response


def llm_response(user_input):

    messages = load_history()

    # Append user message to memory
    messages.append({
    "role": "user",
    "content": user_input
    })



    riko_test_response = get_riko_response_no_tool(messages)


    # just append assistant message to regular response. 
    messages.append({
    "role": "assistant",
    "content": riko_test_response
    })


    save_history(messages)
    return riko_test_response


if __name__ == "__main__":
    print('running main')