# OpenAI tool calling with history 
### Uses a sample function
import yaml
import json
import os
from openai import OpenAI
from google import genai
from google.genai import types

with open('character_config.yaml', 'r') as f:
    char_config = yaml.safe_load(f)

PROVIDER = char_config.get('provider', 'openai')

if PROVIDER == 'gemini':
    client = genai.Client(
        api_key=os.getenv('GEMINI_API_KEY', char_config.get('GEMINI_API_KEY')),
    )
else:
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY', char_config['OPENAI_API_KEY']))

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
    """Return a reply from the configured language model."""

    if PROVIDER == 'gemini':
        contents = [
            types.Content(
                role=m["role"],
                parts=[types.Part.from_text(text="".join(item["text"] for item in m["content"]))],
            )
            for m in messages
        ]
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="text/plain",
        )
        result = ""
        for chunk in client.models.generate_content_stream(
            model=MODEL,
            contents=contents,
            config=generate_content_config,
        ):
            result += chunk.text
        return result

    # default to OpenAI
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": m["role"], "content": "".join(item["text"] for item in m["content"])} for m in messages],
        temperature=1,
        top_p=1,
        max_tokens=2048,
    )

    return response.choices[0].message.content


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
            {"type": "output_text", "text": riko_test_response}
        ]
    })

    save_history(messages)
    return riko_test_response


if __name__ == "__main__":
    print('running main')
