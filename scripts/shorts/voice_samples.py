"""Audition voices for the Shorts narrator: the same hook read by several ElevenLabs voices, so Vish can pick by ear.

    python scripts/shorts/voice_samples.py [out_dir]    # default /mnt/project-files/shorts/voice-samples/

Candidates: George with natural settings (no re-spacing), George on eleven_v3 (most expressive model), and the most-used
young, conversational male narrators from the ElevenLabs voice library (social media / storytelling use cases). Library
voices are added to the account's My Voices so the API can use them. Each sample is about 150 characters.
Never prints keys. Never clones a real person's voice: only stock or library voices made for this use.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from voice import keys  # noqa: E402

TEXT = ("G. P. T. You'd think all three letters are OpenAI's. One isn't. "
        "G, generative. P, pre-trained. But T? T was invented at Google.")
NATURAL = {"stability": 0.32, "similarity_boost": 0.8, "style": 0.38, "use_speaker_boost": True, "speed": 1.06}


def key() -> str:
    ks = keys()
    if not ks:
        sys.exit("No ElevenLabs key in this environment.")
    return ks[0][1]


def library(k: str, n: int = 4) -> list[dict]:
    seen, picks = set(), []
    for use in ("social_media", "narrative_story", "informative_educational"):
        r = requests.get("https://api.elevenlabs.io/v1/shared-voices", headers={"xi-api-key": k}, timeout=60,
                         params={"page_size": 30, "gender": "male", "language": "en", "use_cases": use,
                                 "sort": "usage_character_count_1y"})
        if not r.ok:
            print(f"library search {use}: HTTP {r.status_code}", file=sys.stderr)
            continue
        for vo in r.json().get("voices", []):
            desc = " ".join(str(vo.get(x, "")) for x in ("descriptive", "description", "age", "accent")).lower()
            if vo["voice_id"] in seen or "old" in desc or "middle" in vo.get("age", ""):
                continue
            if not any(w in desc for w in ("conversational", "casual", "engaging", "energetic", "social", "natural", "youtube")):
                continue
            seen.add(vo["voice_id"])
            picks.append(vo)
            if len(picks) >= n:
                return picks
    return picks


def add(k: str, vo: dict) -> str:
    r = requests.post(f"https://api.elevenlabs.io/v1/voices/add/{vo['public_owner_id']}/{vo['voice_id']}",
                      headers={"xi-api-key": k}, json={"new_name": vo["name"][:40]}, timeout=60)
    return r.json().get("voice_id", vo["voice_id"]) if r.ok else vo["voice_id"]


def say(k: str, voice_id: str, model: str, path: Path) -> bool:
    body = {"text": TEXT, "model_id": model, "voice_settings": NATURAL if model != "eleven_v3" else {"stability": 0.5}}
    r = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}", params={"output_format": "mp3_44100_128"},
                      headers={"xi-api-key": k}, json=body, timeout=120)
    if not r.ok:
        print(f"{path.name}: HTTP {r.status_code} {r.text[:160]}", file=sys.stderr)
        return False
    path.write_bytes(r.content)
    return True


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/shorts/voice-samples/")
    out.mkdir(parents=True, exist_ok=True)
    k = key()
    cands = [("George-natural", "JBFqnCBsd6RMkjVDRZzb", "eleven_multilingual_v2", "current voice, looser and warmer settings"),
             ("George-v3", "JBFqnCBsd6RMkjVDRZzb", "eleven_v3", "current voice on the most expressive model")]
    for vo in library(k):
        cands.append((vo["name"].split()[0], add(k, vo), "eleven_multilingual_v2",
                      f"{vo.get('accent', '')} {vo.get('age', '')}, {vo.get('descriptive', '')}, library voice"))
    rows, chars = [], 0
    for i, (name, vid, model, note) in enumerate(cands, 1):
        f = out / f"{i}-{name}.mp3"
        if say(k, vid, model, f):
            chars += len(TEXT)
            rows.append({"n": i, "name": name, "voice_id": vid, "model": model, "note": note, "file": str(f)})
    (out / "samples.json").write_text(json.dumps(rows, indent=1))
    print(f"{len(rows)} samples, {chars} characters billed, in {out}")
    for r in rows:
        print(f"{r['n']}. {r['name']} ({r['model']}): {r['note']}")


if __name__ == "__main__":
    main()
