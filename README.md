# Project Riko

Project Riko is a anime focused LLM project by Just Rayen. She listens, and remembers your conversations. It combines supports multiple LLM Backends, including OpenAI, Ollama and OpenRouter.

Riko is a conversational chatbot that uses your chosen AI model, including OpenAI, Ollama, and OpenRouter. It uses GPT-SoVITS, and Faster-Whisper ASR into a fully configurable conversational pipeline. 

**tested with python 3.10 Windows >10 and Linux Ubuntu**
## ✨ Features

- 💬 **LLM-based dialogue** using OpenAI, Ollama, or OpenRouter
- 🧠 **Conversation memory** to keep context during interactions
- 🔊 **Voice generation** via GPT-SoVITS API
- 🎧 **Speech recognition** using Faster-Whisper
- 📁 Clean YAML-based config for personality configuration


## ⚙️ Configuration

All prompts and parameters are stored in `character_config.yaml`.

```yaml
history_file: chat_history.json

# LLM Provider settings
# Set active_provider to 'openai', 'openrouter', or 'ollama'
active_provider: openrouter

llm_providers:
  openai:
    api_key: "YOUR_OPENAI_API_KEY"  # Replace with your actual OpenAI key
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini" # Replace with your desired model
  openrouter:
  api_key: "YOUR_OPENROUTER_API_KEY" # Replace with your actual OpenRouter key
    base_url: "https://openrouter.ai/api/v1"
    model: "deepseek/deepseek-r1-0528:free" # Replace with your desired model
  ollama:
    base_url: "http://localhost:11434/v1"
    model: "YOUR_MODEL" # You can choose any model you have pulled with Ollama

presets:
  default:
    system_prompt: |
      You are a helpful assistant named Riko.
      You speak like a snarky anime girl.
      Always refer to the user as "senpai".

sovits_ping_config:
  text_lang: en
  prompt_lang : en
  ref_audio_path : YOUR_AUDIO_PATH # Replace with your actual audio path
  prompt_text : This is a sample voice for you to just get started with because it sounds kind of cute but just make sure this doesn't have long silences.
  
````

You can define personalities by modiying the config file.

## Automated Setup

### Run the setup script:
Windows:

    setup.bat

Linux:

  For Linux please follow the Manual Setup instructions below.


## 🛠️ Manual Setup

### Install Dependencies

```bash
pip install uv 
uv pip install -r extra-req.txt
uv pip install -r requirements.txt
```

**If you want to use GPU support for Faster whisper** Make sure you also have:

* CUDA & cuDNN installed correctly (for Faster-Whisper GPU support)
* `ffmpeg` installed (for audio processing)


## 🧪 Usage

### 1. Run the start script:
#### Windows:
```bash
start_riko.bat
````
#### Linux:
```bash
chmod +x start_riko.sh
./start_riko.sh
```

The flow:

1. Riko listens to your voice via microphone (push to talk)
2. Transcribes it with Faster-Whisper
3. Passes it to GPT (with history)
4. Generates a response
5. Synthesizes Riko's voice using GPT-SoVITS
6. Plays the output back to you


## 📌 TODO / Future Improvements

* [ ] GUI or web interface
* [ ] Live microphone input support
* [ ] Emotion or tone control in speech synthesis
* [ ] VRM model frontend


## 🧑‍🎤 Credits

* Voice synthesis powered by [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)
* ASR via [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper)
* Language model via [OpenAI GPT](https://platform.openai.com)
* Windows and Linux scripts: [byKoma](https://github.com/byKoma)


## 📜 License

MIT — feel free to clone, modify, and build your own waifu voice companion.


