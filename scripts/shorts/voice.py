"""Voice a Short with ElevenLabs: the whole script in ONE request (one consistent read), word timings from the
character alignment, then the lines re-spaced with clean gaps.

    python scripts/shorts/voice.py content/shorts/<slug>            # real voice -> out/shorts/<slug>/voice.wav + voice.json
    python scripts/shorts/voice.py content/shorts/<slug> --estimate # silent timing guess for building the animation

Keys (environment secrets, never printed): ELEVENLABS_API_KEY first, CLAUDEELEVENLABS_API (second account) when the
first one fails for quota or auth. `.env.local` at the repo root is read as a fallback. Billing is 1 credit per character
on eleven_multilingual_v2; every run appends the count to out/shorts/elevenlabs-usage.json.
"""
from __future__ import annotations

import base64
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import requests
import soundfile as sf

ROOT = Path(__file__).resolve().parents[2]
SR = 48000
API = "https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps"


def keys() -> list[tuple[str, str]]:
    env = dict(os.environ)
    local = ROOT / ".env.local"
    if local.exists():
        for ln in local.read_text().splitlines():
            m = re.match(r"\s*([A-Z0-9_]+)\s*=\s*['\"]?([^'\"]+)['\"]?\s*$", ln)
            if m and m.group(1) not in env:
                env[m.group(1)] = m.group(2)
    return [(n, env[n]) for n in ("ELEVENLABS_API_KEY", "CLAUDEELEVENLABS_API") if env.get(n)]


def tts(text: str, v: dict) -> tuple[bytes, dict, str]:
    body = {"text": text, "model_id": v.get("model", "eleven_multilingual_v2"),
            "voice_settings": {"stability": v.get("stability", 0.5), "similarity_boost": 0.75, "style": v.get("style", 0.0),
                               "use_speaker_boost": True, "speed": v.get("speed", 1.0)}}
    ks = keys()
    if not ks:
        sys.exit("No ElevenLabs key in this environment (ELEVENLABS_API_KEY / CLAUDEELEVENLABS_API).")
    last = ""
    for name, key in ks:
        r = requests.post(API.format(voice=v["voice_id"]), params={"output_format": "mp3_44100_128"},
                          headers={"xi-api-key": key, "content-type": "application/json"}, json=body, timeout=180)
        if r.ok:
            j = r.json()
            return base64.b64decode(j["audio_base64"]), j["alignment"], name
        last = f"{name}: HTTP {r.status_code} {r.text[:200]}"
        print(f"ElevenLabs refused with {name} ({r.status_code}); trying the next key", file=sys.stderr)
    sys.exit(f"ElevenLabs failed on every key. Last: {last}")


def spans(text: str, start: int) -> list[tuple[str, int, int]]:
    return [(m.group(0), start + m.start(), start + m.end()) for m in re.finditer(r"\S+", text)]


def voice(src: Path, estimate: bool = False) -> Path:
    spec = json.loads((src / "script.json").read_text())
    v = spec["voice"]
    out = ROOT / "out" / "shorts" / spec["slug"]
    out.mkdir(parents=True, exist_ok=True)
    lines = spec["lines"]
    full, offs = "", []
    for ln in lines:
        offs.append(len(full))
        full += ln["text"] + "\n"

    if estimate:  # 2.6 words a second, the George pace measured on the Week 1 card
        t, res = 0.15, []
        for ln in lines:
            ws, wt = [], t
            for w in ln["text"].split():
                d = 0.16 + 0.055 * len(re.sub(r"\W", "", w))
                ws.append({"w": w, "start": round(wt, 3), "end": round(wt + d, 3)})
                wt += d + 0.03
            res.append({"text": ln["text"], "start": round(t, 3), "end": round(wt, 3), "words": ws})
            t = wt + (v["scene_gap"] if ln.get("pause_after") else v["gap"])
        dur = t + 0.6
        sf.write(str(out / "voice.wav"), np.zeros(int(dur * SR), dtype=np.float32), SR)
        (out / "voice.json").write_text(json.dumps({"estimate": True, "lines": res, "duration": round(dur, 3)}, indent=1))
        return out

    audio, al, keyname = tts(full, v)
    with tempfile.TemporaryDirectory() as td:
        mp3 = Path(td) / "v.mp3"
        mp3.write_bytes(audio)
        (out / "voice-raw.mp3").write_bytes(audio)
        wav = Path(td) / "v.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3), "-ac", "1", "-ar", str(SR), str(wav)], check=True)
        raw, _ = sf.read(str(wav), dtype="float32")
    cs, ce = al["character_start_times_seconds"], al["character_end_times_seconds"]

    # cut each line out on its own and re-space them with clean gaps
    pieces, res, t = [np.zeros(int(0.15 * SR), np.float32)], [], 0.15
    for i, ln in enumerate(lines):
        o = offs[i]
        ws = spans(ln["text"], o)
        a, b = cs[ws[0][1]], ce[ws[-1][2] - 1]
        a0, b0 = max(0.0, a - 0.04), min(len(raw) / SR, b + 0.14)
        seg = raw[int(a0 * SR):int(b0 * SR)].copy()
        fade = int(0.012 * SR)
        seg[:fade] *= np.linspace(0, 1, fade)
        seg[-fade:] *= np.linspace(1, 0, fade)
        shift = t - a0
        res.append({"text": ln["text"], "start": round(a + shift, 3), "end": round(b + shift, 3),
                    "words": [{"w": w, "start": round(cs[s] + shift, 3), "end": round(ce[e - 1] + shift, 3)} for w, s, e in ws]})
        pieces.append(seg)
        t += len(seg) / SR
        g = v["scene_gap"] if ln.get("pause_after") else v["gap"]
        pieces.append(np.zeros(int(g * SR), np.float32))
        t += g
    pieces.append(np.zeros(int(0.5 * SR), np.float32))
    mix = np.concatenate(pieces)
    sf.write(str(out / "voice.wav"), mix, SR)
    (out / "voice.json").write_text(json.dumps({"estimate": False, "voice": v["name"], "lines": res, "duration": round(len(mix) / SR, 3)}, indent=1))

    usage = ROOT / "out" / "shorts" / "elevenlabs-usage.json"
    log = json.loads(usage.read_text()) if usage.exists() else []
    log.append({"slug": spec["slug"], "chars": len(full), "key": keyname})
    usage.write_text(json.dumps(log, indent=1))
    print(f"voiced {spec['slug']}: {len(full)} characters on {keyname}, {len(mix) / SR:.1f} s")
    return out


if __name__ == "__main__":
    voice(Path(sys.argv[1]), "--estimate" in sys.argv)
