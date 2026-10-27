"""Speak the lines Vish didn't film: his ElevenLabs clone for script lines, George for the "Next week" card.

    python3 video-projects/week-02-talks/vo_lines.py

Reads content/shoot-sheets/2026-10-week-2-edit.json; writes vo/<key>_<n>.mp3 + .json (word timings from
/with-timestamps). Skips lines already made, so a rerun costs nothing. Key: CLAUDEELEVENLABS_API.
"""
import base64
import json
import os
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHEET = HERE.parents[1] / "content" / "shoot-sheets" / "2026-10-week-2-edit.json"
VOICES = {"clone": "rRDZHYKovM5FXW92Zoxe", "narrator": "JBFqnCBsd6RMkjVDRZzb"}  # Young indian male (his clone), George
SETTINGS = {"clone": {"stability": 0.45, "similarity_boost": 0.9, "style": 0.15, "use_speaker_boost": True},  # as HOW-AI-EDIT
            "narrator": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.0, "use_speaker_boost": True}}


def words(al: dict) -> list:
    """Characters with times -> words with start and end."""
    out, cur, s = [], "", None
    for ch, a, b in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if ch.isspace():
            if cur:
                out.append({"w": cur, "s": round(s, 3), "e": round(e, 3)})
            cur, s = "", None
            continue
        if s is None:
            s = a
        cur, e = cur + ch, b
    if cur:
        out.append({"w": cur, "s": round(s, 3), "e": round(e, 3)})
    return out


if __name__ == "__main__":
    key = os.environ["CLAUDEELEVENLABS_API"]
    out = HERE / "vo"
    out.mkdir(exist_ok=True)
    for e in json.loads(SHEET.read_text())["edits"]:
        for n, b in enumerate(e["beats"]):
            if b["who"] not in VOICES:
                continue
            f = out / f"{e['key']}_{n}.mp3"
            if f.exists():
                continue
            body = json.dumps({"text": b["say"], "model_id": "eleven_multilingual_v2", "voice_settings": SETTINGS[b["who"]]}).encode()
            req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICES[b['who']]}/with-timestamps?output_format=mp3_44100_192",
                                         data=body, method="POST", headers={"xi-api-key": key, "Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=300))
            f.write_bytes(base64.b64decode(r["audio_base64"]))
            f.with_suffix(".json").write_text(json.dumps({"text": b["say"], "voice": b["who"], "words": words(r["alignment"])}, indent=1))
            print(f.name, b["who"], b["say"])
