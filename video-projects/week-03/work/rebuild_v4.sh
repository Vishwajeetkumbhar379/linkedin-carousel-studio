#!/bin/bash
# Voice: Eleven v4 with his clone (Vish, 28 Oct: "sounds so good, sounds like me") for all 7, polished with breaths, re-timed, rendered with music inside. Two streams.
cd "$(dirname "$0")/.."
one() { k=$1
  [ -s ${k}_raw4.mp3 ] || python3 - "$k" <<'PY'
import json, os, re, sys, requests
k = sys.argv[1]; t = json.load(open("scripts.json"))[k]
r = requests.post("https://api.elevenlabs.io/v1/text-to-speech/rRDZHYKovM5FXW92Zoxe?output_format=mp3_44100_128", headers={"xi-api-key": os.environ["CLAUDEELEVENLABS_API"]},
                  json={"text": t, "model_id": "eleven_v4"}, timeout=300)
r.raise_for_status(); open(f"{k}_raw4.mp3", "wb").write(r.content)
PY
  python3 ../../scripts/voice_polish.py ${k}_raw4.mp3 ${k}.mp3 --speed 1.15 >/dev/null
  python3 - "$k" <<'PY'
import json, subprocess, sys, numpy as np
from faster_whisper import WhisperModel
k = sys.argv[1]; m = WhisperModel("small", device="cpu", compute_type="int8")
a = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",f"{k}.mp3","-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout, np.float32)
segs, _ = m.transcribe(a, language="en", word_timestamps=True, initial_prompt="Claude, ElevenLabs, Gemini, ChatGPT, Sri Lanka, Bali")
json.dump([{"w": x.word.strip(), "s": round(x.start, 2), "e": round(x.end, 2)} for s in segs for x in s.words], open(f"{k}_words.json", "w"))
PY
  python3 ../../scripts/canvas_reel.py . $k 2>&1 | tail -1; }
( for k in r1 r3 r5 r7; do one $k; done ) &
( for k in r2 r4 r6; do one $k; done ) &
wait; echo ALL DONE
