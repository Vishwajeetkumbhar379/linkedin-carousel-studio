"""A shared library of studio-quality sound effects (ElevenLabs Sound Effects), made once and reused by every edit.

    python3 video-projects/sfx-library/make_sfx.py      -> video-projects/sfx-library/<name>.mp3 (skips existing)
Key: CLAUDEELEVENLABS_API. Synthesised clicks and buzzes sounded cheap (Vish, 27 Oct); these replace them.
"""
import json
import os
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SFX = {
    "whoosh": ("fast clean cinematic whoosh transition, air swipe, no reverb tail", 0.8),
    "whoosh_soft": ("soft gentle airy swish transition, subtle", 0.6),
    "impact": ("deep cinematic boom impact hit with sub bass, short", 1.5),
    "hit_soft": ("soft punchy kick-like thud hit, modern editing sound", 0.6),
    "pop": ("short bubbly UI pop sound, clean and satisfying", 0.3),
    "click": ("crisp computer mouse click, close up", 0.3),
    "tick": ("single soft clock tick, dry", 0.3),
    "shutter": ("vintage film camera shutter click with mechanical wind", 0.8),
    "paper": ("sheet of paper sliding onto a wooden desk", 0.7),
    "type": ("three fast mechanical keyboard key presses", 0.6),
    "clippers": ("electric barber hair clippers buzzing close up, cutting hair", 2.0),
    "scissors": ("barber scissors snipping hair twice, close up", 0.8),
    "rewind": ("cassette tape rewinding fast with pitched squeal, VHS rewind", 1.2),
    "riser": ("short tension riser building up, cinematic, ends abruptly", 2.0),
    "splash": ("person jumping into the sea, big water splash", 1.5),
    "ding": ("bright notification ding, clean, positive", 0.6),
    "cash": ("cash register cha-ching, short", 1.0),
    "lock_open": ("metal padlock clicking open", 0.6),
    "stamp": ("rubber stamp hitting paper hard", 0.5),
    "keys": ("heavy mechanical keyboard typing a short word, four keys", 1.0),
    "swoosh_up": ("upward swoosh reveal, bright, short", 0.7),
    "glitch": ("short digital glitch stutter sound", 0.5),
}

if __name__ == "__main__":
    key = os.environ["CLAUDEELEVENLABS_API"]
    for name, (text, dur) in SFX.items():
        out = HERE / f"{name}.mp3"
        if out.exists():
            continue
        body = json.dumps({"text": text, "duration_seconds": max(0.5, dur), "prompt_influence": 0.6}).encode()
        req = urllib.request.Request("https://api.elevenlabs.io/v1/sound-generation", data=body, method="POST",
                                     headers={"xi-api-key": key, "Content-Type": "application/json"})
        out.write_bytes(urllib.request.urlopen(req, timeout=300).read())
        print(name, out.stat().st_size)
