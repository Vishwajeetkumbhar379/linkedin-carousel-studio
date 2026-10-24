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
            "voice_settings": {"stability": v.get("stability", 0.5), "similarity_boost": v.get("similarity", 0.75), "style": v.get("style", 0.0),
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


def tts_v3(text: str, v: dict) -> tuple[bytes, str]:
    """eleven_v3 (breaths, audio tags like [excited]): plain endpoint, timings come from Whisper instead."""
    body = {"text": text, "model_id": "eleven_v3", "voice_settings": {"stability": v.get("stability", 0.0)}}
    last = ""
    for name, key in keys():
        r = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{v['voice_id']}", params={"output_format": "mp3_44100_128"},
                          headers={"xi-api-key": key, "content-type": "application/json"}, json=body, timeout=240)
        if r.ok:
            return r.content, name
        last = f"{name}: HTTP {r.status_code} {r.text[:200]}"
    sys.exit(f"ElevenLabs v3 failed on every key. Last: {last}")


def whisper_words(wav: Path, script_words: list[str]) -> list[tuple[float, float]]:
    """Word times for the script's own words: Whisper word timestamps matched in order, gaps interpolated."""
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    # decode with ffmpeg ourselves: faster-whisper's own decoder breaks on newer PyAV (metadata_errors kwarg)
    pcm = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(wav), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         check=True, capture_output=True).stdout
    segs, _ = m.transcribe(np.frombuffer(pcm, np.float32), language="en", word_timestamps=True, initial_prompt=" ".join(script_words))
    hw = [(w.word, w.start, w.end) for sg in segs for w in sg.words]
    n = lambda x: re.sub(r"[^a-z0-9]", "", x.lower())
    out, j = [None] * len(script_words), 0
    for i, w in enumerate(script_words):
        for k in range(j, min(j + 6, len(hw))):
            a, b = n(w), n(hw[k][0])
            if a and b and (a == b or a.startswith(b) or b.startswith(a)):
                out[i], j = (hw[k][1], hw[k][2]), k + 1
                break
    for i in range(len(out)):  # fill misses between neighbours
        if out[i] is None:
            p = next((out[q][1] for q in range(i - 1, -1, -1) if out[q]), 0.0)
            nx = next((out[q][0] for q in range(i + 1, len(out)) if out[q]), p + 0.4)
            out[i] = (p, max(p + 0.05, min(nx, p + 0.35)))
    return out


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
        t, res = v.get("lead", 0.15), []
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

    if v.get("model") == "eleven_v3":
        return voice_v3(spec, out, lines, v)
    audio, al, keyname = tts(full, v)
    with tempfile.TemporaryDirectory() as td:
        mp3 = Path(td) / "v.mp3"
        mp3.write_bytes(audio)
        (out / "voice-raw.mp3").write_bytes(audio)
        wav = Path(td) / "v.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3), "-ac", "1", "-ar", str(SR), str(wav)], check=True)
        raw, _ = sf.read(str(wav), dtype="float32")
    cs, ce = al["character_start_times_seconds"], al["character_end_times_seconds"]

    if v.get("natural"):  # keep the read exactly as spoken (its own breaths and pauses): only trim the lead-in
        lead = v.get("lead", 0.02)
        a_first = cs[spans(lines[0]["text"], offs[0])[0][1]]
        a0 = max(0.0, a_first - 0.03)
        shift = lead - a0
        mix = np.concatenate([np.zeros(int(lead * SR), np.float32), raw[int(a0 * SR):].astype(np.float32), np.zeros(int(0.5 * SR), np.float32)])
        res = []
        for i, ln in enumerate(lines):
            ws = spans(ln["text"], offs[i])
            res.append({"text": ln["text"], "start": round(cs[ws[0][1]] + shift, 3), "end": round(ce[ws[-1][2] - 1] + shift, 3),
                        "words": [{"w": w, "start": round(cs[a] + shift, 3), "end": round(ce[b - 1] + shift, 3)} for w, a, b in ws]})
        return finish(spec, out, full, keyname, mix, res)

    # cut each line out on its own and re-space them with clean gaps
    lead = v.get("lead", 0.15)
    pieces, res, t = [np.zeros(int(lead * SR), np.float32)], [], lead
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
    return finish(spec, out, full, keyname, mix, res)


def voice_v3(spec, out, lines, v):
    tagged = "\n".join((ln.get("tag", v.get("tag", "")) + " " + ln["text"]).strip() for ln in lines)
    if "--reuse" in sys.argv and (out / "voice-raw.mp3").exists():  # re-align a take already paid for
        keyname = "reused take"
    else:
        audio, keyname = tts_v3(tagged, v)
        (out / "voice-raw.mp3").write_bytes(audio)
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "v.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(out / "voice-raw.mp3"), "-ac", "1", "-ar", str(SR), str(wav)], check=True)
        raw, _ = sf.read(str(wav), dtype="float32")
        words = [w for ln in lines for w in ln["text"].split()]
        times = whisper_words(wav, words)
    lead = v.get("lead", 0.02)
    a0 = max(0.0, times[0][0] - 0.05)
    shift = lead - a0
    mix = np.concatenate([np.zeros(int(lead * SR), np.float32), raw[int(a0 * SR):].astype(np.float32), np.zeros(int(0.5 * SR), np.float32)])
    res, k = [], 0
    for ln in lines:
        ws = ln["text"].split()
        tt = times[k:k + len(ws)]
        k += len(ws)
        res.append({"text": ln["text"], "start": round(tt[0][0] + shift, 3), "end": round(tt[-1][1] + shift, 3),
                    "words": [{"w": w, "start": round(a + shift, 3), "end": round(b + shift, 3)} for w, (a, b) in zip(ws, tt)]})
    return finish(spec, out, tagged, keyname, mix, res)


def finish(spec, out, full, keyname, mix, res):
    v = spec["voice"]
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
