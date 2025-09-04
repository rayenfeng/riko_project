from faster_whisper import WhisperModel
from process.asr_func.asr_push_to_talk import record_and_transcribe
from process.llm_funcs.llm_scr import llm_response
from process.tts_func.sovits_ping import sovits_gen, play_audio
from pathlib import Path
import os
import time
### transcribe audio 
import uuid
import soundfile as sf


def get_wav_duration(path):
    with sf.SoundFile(path) as f:
        return len(f) / f.samplerate


print(' \n ========= Starting Chat... ================ \n')
whisper_model = WhisperModel("base.en", device="cpu", compute_type="float32")

while True:

    conversation_recording = output_wav_path = Path("audio") / "conversation.wav"
    conversation_recording.parent.mkdir(parents=True, exist_ok=True)

    user_spoken_text = record_and_transcribe(whisper_model, conversation_recording, input_wav_path="character_files/main_sample.wav")

    ### pass to LLM and get a LLM output.

    llm_output = llm_response(user_spoken_text)

    tts_read_text = llm_output

    ### file organization 

    # 1. Generate a unique filename
    uid = uuid.uuid4().hex
    filename = f"output_{uid}.wav"
    output_wav_path = Path("audio") / filename
    output_wav_path.parent.mkdir(parents=True, exist_ok=True)

    # generate audio and save it to client/audio 
    gen_aud_path = sovits_gen(tts_read_text,output_wav_path)

    if gen_aud_path:
        play_audio(output_wav_path)
    else:
        print("Could not generate audio, skipping playback. Please ensure the TTS server is running.")
    # clean up audio files
    [fp.unlink() for fp in Path("audio").glob("*.wav") if fp.is_file()]
    # # Example
    # duration = get_wav_duration(output_wav_path)

    # print("waiting for audio to finish...")
    # time.sleep(duration)
