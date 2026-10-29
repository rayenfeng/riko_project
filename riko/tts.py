"""Her voice: turn her reply into a WAV file.

tts: sovits -> GPT-SoVITS API running on your PC
tts: fish   -> Fish Audio online
"""
import io
import os
import sys

import requests
import soundfile as sf

from riko.config import ROOT, need_key

VOICE_FILE = ROOT / "client" / "audio" / "riko.wav"  # inside client/ so the avatar page can load it


def check(cfg):
    if cfg["tts"] == "fish":
        need_key("FISH_API_KEY", "tts: fish")
        return
    ref_audio = ROOT / cfg["sovits"]["ref_audio_path"]
    if not ref_audio.exists():
        sys.exit(f"[setup] Voice sample not found: {ref_audio}")
    try:
        requests.head(cfg["sovits"]["url"], timeout=3)  # any answer means it is running
    except requests.ConnectionError:
        sys.exit(f"[setup] GPT-SoVITS is not running at {cfg['sovits']['url']}. "
                 "Start its API first (python api_v2.py in your GPT-SoVITS folder), or use --tts fish.")
    print(f"[setup] GPT-SoVITS is running at {cfg['sovits']['url']}")


def speak(text, cfg):
    """Make her say `text`. Returns the path of the WAV file."""
    audio = _fish(text, cfg["fish"]) if cfg["tts"] == "fish" else _sovits(text, cfg["sovits"])
    # Re-save through soundfile: Fish's WAV header claims the clip is hours
    # long, and browsers believe it and never fire "ended". This fixes it.
    data, sample_rate = sf.read(io.BytesIO(audio))
    VOICE_FILE.parent.mkdir(parents=True, exist_ok=True)
    sf.write(VOICE_FILE, data, sample_rate)
    print(f"[tts] {cfg['tts']}: {len(data) / sample_rate:.1f}s of audio")
    return VOICE_FILE


def _sovits(text, s):
    response = requests.post(s["url"], json={
        "text": text,
        "text_lang": s["text_lang"],
        "ref_audio_path": str(ROOT / s["ref_audio_path"]),  # GPT-SoVITS needs the full path
        "prompt_text": s["prompt_text"],
        "prompt_lang": s["prompt_lang"],
    }, timeout=120)
    response.raise_for_status()
    return response.content


def _fish(text, f):
    body = {"text": text, "format": "wav"}
    if f["voice_id"]:
        body["reference_id"] = f["voice_id"]
    response = requests.post(
        "https://api.fish.audio/v1/tts",
        headers={"Authorization": f"Bearer {os.getenv('FISH_API_KEY')}", "model": f["model"]},
        json=body,
        timeout=120,
    )
    response.raise_for_status()
    return response.content


if __name__ == "__main__":
    # Test her voice on its own: uv run python -m riko.tts   (add --fish for Fish Audio)
    from riko.config import load_config
    cfg = load_config()
    if "--fish" in sys.argv:
        cfg["tts"] = "fish"
    check(cfg)
    print("Wrote", speak("If you can hear this, my voice is set up correctly.", cfg))
