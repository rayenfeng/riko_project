from pathlib import Path
import uuid

from server.process.llm_funcs.llm_scr import llm_response
from server.process.tts_func.sovits_ping import sovits_gen, play_audio

print("\n ==== Riko Text Chat ====")
print("Type 'exit' to quit.\n")

while True:
    user_text = input("You: ")
    if user_text.lower() in {"exit", "quit"}:
        break

    reply = llm_response(user_text)
    print(f"Riko: {reply}")

    uid = uuid.uuid4().hex
    out_path = Path("audio") / f"output_{uid}.wav"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    audio_file = sovits_gen(reply, out_path)
    if audio_file:
        play_audio(audio_file)

    for fp in out_path.parent.glob("*.wav"):
        fp.unlink()

