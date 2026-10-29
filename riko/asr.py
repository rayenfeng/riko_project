"""Her ears: record your voice (push-to-talk) and turn it into text.

asr: local -> Faster-Whisper on your PC
asr: groq  -> Groq's online Whisper
"""
import io
import os

import numpy as np
import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel
from openai import OpenAI

from riko.config import need_key

SAMPLE_RATE = 16000                # what Whisper expects
WHISPER_MODEL = "base.en"          # bigger = more accurate, slower: small.en, medium.en
WHISPER_DEVICE = "cpu"             # "cuda" for an NVIDIA GPU (needs CUDA + cuDNN)
GROQ_MODEL = "whisper-large-v3-turbo"

_whisper = None  # Faster-Whisper model, loaded once by check()


def check(cfg):
    global _whisper
    if cfg["asr"] == "groq":
        need_key("GROQ_API_KEY", "asr: groq")
    else:
        print(f"[asr] loading Faster-Whisper {WHISPER_MODEL} on {WHISPER_DEVICE} (first run downloads it)...")
        _whisper = WhisperModel(WHISPER_MODEL, device=WHISPER_DEVICE, compute_type="int8")


def record():
    """Push-to-talk: Enter to start, Enter to stop. Returns WAV bytes, or None if nothing was recorded."""
    input("\nPress ENTER to talk...")
    chunks = []
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32",
                        callback=lambda data, *_: chunks.append(data.copy())):
        input("Recording... press ENTER to stop")
    if not chunks:
        return None
    audio = np.concatenate(chunks)
    print(f"[asr] recorded {len(audio) / SAMPLE_RATE:.1f}s")
    wav = io.BytesIO()
    sf.write(wav, audio, SAMPLE_RATE, format="WAV")
    return wav.getvalue()


def transcribe(wav_bytes, cfg):
    if cfg["asr"] == "groq":
        groq = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
        text = groq.audio.transcriptions.create(model=GROQ_MODEL, file=("you.wav", wav_bytes)).text
    else:
        segments, _ = _whisper.transcribe(io.BytesIO(wav_bytes), vad_filter=True)
        text = "".join(s.text for s in segments)  # each segment already starts with a space
    return text.strip()


if __name__ == "__main__":
    # Talk into your mic and see what she hears: uv run python -m riko.asr
    from riko.config import load_config
    cfg = load_config()
    check(cfg)
    print("You said:", transcribe(record(), cfg))
