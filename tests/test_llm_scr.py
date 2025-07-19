import os
import sys
import json
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import server.process.llm_funcs.llm_scr as llm

def test_llm_response(monkeypatch, tmp_path):
    # use temporary history file
    hist = tmp_path / "history.json"
    monkeypatch.setattr(llm, "HISTORY_FILE", str(hist))

    def fake_get(messages):
        return "ok"

    monkeypatch.setattr(llm, "get_riko_response_no_tool", fake_get)

    result = llm.llm_response("hi")
    assert result == "ok"

    with open(hist) as f:
        data = json.load(f)
    assert data[-1]["role"] == "assistant"


def test_gemini_provider(monkeypatch):
    monkeypatch.setattr(llm, "PROVIDER", "gemini")

    class DummyChunk:
        def __init__(self, text):
            self.text = text

    class DummyModels:
        def generate_content_stream(self, model, contents, config):
            yield DummyChunk("ok")

    monkeypatch.setattr(llm, "client", type("client", (), {"models": DummyModels()})())

    msg = [{"role": "user", "content": [{"text": "hi"}]}]
    assert llm.get_riko_response_no_tool(msg) == "ok"

