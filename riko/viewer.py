"""Serves the avatar page, audio clips, and browser microphone API."""
import json
import logging
import queue
import re
import sys
import threading
import time
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

from riko import asr, llm, tts
from riko.config import ROOT

HOST, PORT = "127.0.0.1", 8080
MAX_AUDIO_BYTES = 4 * 1024 * 1024
WAKE_WORD_RE = re.compile(r"\b(?:riko|rico|reeko|rieko)\b", re.IGNORECASE)
PUNCTUATION = " ,.!?;:-"
GREETINGS = {"hey", "hi", "hello", "ok", "okay", "yo", "hey there", "hi there", "oh", "so"}

_clips = queue.Queue()
_finished = threading.Event()
_page_last_seen = float("-inf")
_avatar = None
_cfg = None
_chat_lock = threading.Lock()
_transcription_lock = threading.Lock()


class _Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        global _page_last_seen
        path = unquote(urlsplit(self.path).path)
        if path == "/avatar.vrm":
            return self._send(_avatar.read_bytes(), "application/octet-stream")
        if path == "/mode":
            return self._send(json.dumps({"web_listening": _cfg.get("web_listening", True)}).encode(), "application/json", cache="no-store")
        if path == "/next":
            _page_last_seen = time.monotonic()
            try:
                clip = _clips.get_nowait()
            except queue.Empty:
                clip = None
            return self._send(json.dumps({"audio": clip}).encode(), "application/json", cache="no-store")
        if path in ("/audio/riko.wav", "/riko.wav"):
            return self._send_audio(ROOT / "client" / "audio" / "riko.wav")
        if path == "/manifest.webmanifest":
            return self._send_file(ROOT / "client" / "manifest.webmanifest", "application/manifest+json")
        if path in ("/icon.png", "/apple-touch-icon.png"):
            return self._send_file(ROOT / "client" / "icon.png", "image/png")
        return super().do_GET()

    def do_POST(self):
        path = urlsplit(self.path).path
        if path == "/done":
            _finished.set()
            return self._send(b"{}", "application/json", cache="no-store")
        if path == "/listen":
            return self._handle_listen()
        self.send_error(HTTPStatus.NOT_FOUND)

    def _handle_listen(self):
        if not _cfg.get("web_listening", True):
            return self._json(HTTPStatus.CONFLICT, {"error": "Browser listening is disabled in terminal mode"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return self._json(HTTPStatus.BAD_REQUEST, {"error": "Invalid Content-Length"})
        if length <= 0 or length > MAX_AUDIO_BYTES:
            return self._json(HTTPStatus.BAD_REQUEST, {"error": "Audio is empty or too large"})
        audio = self.rfile.read(length)
        if len(audio) != length:
            return self._json(HTTPStatus.BAD_REQUEST, {"error": "Incomplete audio upload"})

        already_awake = parse_qs(urlsplit(self.path).query).get("wake") == ["1"]
        try:
            with _transcription_lock:
                transcript = asr.transcribe(audio, _cfg)
        except Exception:
            logging.exception("Speech transcription failed")
            return self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Could not transcribe audio"})
        logging.info("Heard: %r", transcript)

        if already_awake:
            request = transcript
        else:
            match = WAKE_WORD_RE.search(transcript)
            if not match:
                return self._json(HTTPStatus.OK, {"status": "ignored"})
            after = transcript[match.end():].strip(PUNCTUATION)
            before = transcript[:match.start()].strip(PUNCTUATION)
            request = after or ("" if before.lower() in GREETINGS else before)

        if not request.strip(PUNCTUATION):
            return self._json(HTTPStatus.OK, {"status": "awake"})

        try:
            with _chat_lock:
                answer = llm.reply(request, _cfg)
                voice_path = tts.speak(answer, _cfg)
                _clips.put(f"audio/{voice_path.name}?v={time.time_ns()}")
        except Exception:
            logging.exception("Failed to generate a reply")
            return self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Failed to generate a reply"})
        return self._json(HTTPStatus.OK, {"status": "reply", "heard": request, "reply": answer})

    def _json(self, status, value):
        return self._send(json.dumps(value).encode(), "application/json", status, cache="no-store")

    def _send_file(self, path, content_type):
        try:
            data = path.read_bytes()
        except FileNotFoundError:
            return self.send_error(HTTPStatus.NOT_FOUND)
        return self._send(data, content_type)

    def _send_audio(self, path):
        try:
            data = path.read_bytes()
        except FileNotFoundError:
            return self.send_error(HTTPStatus.NOT_FOUND)
        total = len(data)
        match = re.fullmatch(r"bytes=(\d*)-(\d*)", self.headers.get("Range", "").strip())
        status = HTTPStatus.OK
        content_range = None
        if match and (match.group(1) or match.group(2)):
            if match.group(1):
                start = int(match.group(1))
                end = int(match.group(2)) if match.group(2) else total - 1
            else:
                start = max(total - int(match.group(2)), 0)
                end = total - 1
            end = min(end, total - 1)
            if start >= total or start > end:
                self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
                self.send_header("Content-Range", f"bytes */{total}")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            data = data[start:end + 1]
            status = HTTPStatus.PARTIAL_CONTENT
            content_range = f"bytes {start}-{end}/{total}"
        return self._send(data, "audio/wav", status, content_range=content_range, ranges=True)

    def _send(self, body, content_type, status=HTTPStatus.OK, *, cache="no-cache", content_range=None, ranges=False):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", cache)
        if ranges:
            self.send_header("Accept-Ranges", "bytes")
        if content_range:
            self.send_header("Content-Range", content_range)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string, *args):
        logging.info("%s - %s", self.address_string(), format_string % args)


def start(cfg):
    global _avatar, _cfg
    _cfg = cfg
    _avatar = ROOT / cfg["vrm_model"]
    if not _avatar.exists():
        sys.exit(f"[setup] Avatar not found: {_avatar}. Check vrm_model in character_config.yaml.")
    try:
        server = ThreadingHTTPServer((HOST, PORT), partial(_Handler, directory=str(ROOT / "client")))
    except OSError:
        sys.exit(f"[setup] Port {PORT} is busy (is Riko already running?).")
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"[viewer] avatar and microphone: http://{HOST}:{PORT}  (open it, then tap once)")


def play(wav_path):
    """Play a terminal-mode voice clip in the avatar page, or through speakers."""
    import sounddevice as sd
    import soundfile as sf

    duration = sf.info(wav_path).duration
    if time.monotonic() - _page_last_seen < 2:
        _finished.clear()
        _clips.put(f"audio/{wav_path.name}?v={time.time_ns()}")
        if not _finished.wait(timeout=duration + 10):
            print("[viewer] the page never said the clip ended; carrying on")
    else:
        print("[viewer] no avatar page open, playing on speakers")
        data, sample_rate = sf.read(wav_path)
        sd.play(data, sample_rate)
        sd.wait()
