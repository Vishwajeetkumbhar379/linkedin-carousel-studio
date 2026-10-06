"""Voiceover for videos: natural pacing, soft breaths, timings that drive scenes and subtitles.

    python scripts/voiceover.py out/<post>/video.json [--voice af_heart] [--no-breaths] [--no-bed]

Reads `narration` from video.json: a list of scenes, each a list of phrases. Writes
  out/<post>/voice.wav      final mix (voice + optional soft ambient bed), loudness-normalised
  out/<post>/voice.json     phrase and scene timings (seconds), used by the video renderer
and rewrites each scene's `at`/`until` in video.json to match the audio, so pictures follow the voice.

Engines (pick with --engine, default: gemini when GEMINI_API_KEY is set, else kokoro):
  gemini  Gemini 3.8 Flash TTS (natural prosody, real breaths, style prompts). Needs GEMINI_API_KEY
          as an environment variable (set it in the cloud environment settings, never in the repo).
          One request per scene so intonation flows across a whole thought.
  kokoro  Kokoro-82M via kokoro-onnx (model Apache-2.0, code MIT), runs on CPU.
Model files live in $KOKORO_DIR (default /home/user/models/kokoro), downloaded from
github.com/thewh1teagle/kokoro-onnx releases. For Vish's own voice, see docs/voice.md.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

SR = 24000
KOKORO_DIR = Path(os.environ.get("KOKORO_DIR", "/home/user/models/kokoro"))
PAUSE = {",": 0.14, ";": 0.2, ":": 0.2, ".": 0.3, "?": 0.34, "!": 0.3}
SCENE_GAP = 0.35


def breath(seed: int, dur: float = 0.34, level_db: float = -34.0) -> np.ndarray:
    """A soft inhale: band-limited noise with a rise-and-fall envelope. Quiet on purpose."""
    rng = np.random.default_rng(seed)
    n = int(SR * dur)
    noise = rng.standard_normal(n)
    # crude band-pass 400 Hz to 3.5 kHz via FFT mask
    f = np.fft.rfft(noise)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    f[(freqs < 400) | (freqs > 3500)] = 0
    f *= np.exp(-((freqs - 1400) / 1300) ** 2)
    x = np.fft.irfft(f, n)
    env = np.sin(np.linspace(0, np.pi, n)) ** 1.6
    x = x * env
    x /= np.max(np.abs(x)) + 1e-9
    return x * (10 ** (level_db / 20))


def ambient_bed(seconds: float, level_db: float = -31.0) -> np.ndarray:
    """Warm, slow pad (Dmaj9 voicing) so the voice doesn't sit on dead silence."""
    t = np.arange(int(SR * seconds)) / SR
    notes = [146.83, 220.0, 277.18, 329.63, 440.0]
    x = sum(np.sin(2 * np.pi * f * t + i) * (0.6 + 0.4 * np.sin(2 * np.pi * (0.05 + i * 0.013) * t)) for i, f in enumerate(notes))
    x = x / len(notes)
    fade = np.minimum(1, np.minimum(t / 2.0, (seconds - t) / 2.5))
    return x * fade * (10 ** (level_db / 20))


def voice_style(k, voice: str):
    """'am_puck' or a blend like 'am_puck:0.6,am_fenrir:0.4' (weighted average of style vectors)."""
    if ":" not in voice:
        return voice
    parts = [(n, float(w)) for n, w in (x.split(":") for x in voice.split(","))]
    total = sum(w for _, w in parts)
    return sum(k.get_voice_style(n) * (w / total) for n, w in parts)


def synth(narration: list[list[str]], voice: str, breaths: bool, base_speed: float = 1.0) -> tuple[np.ndarray, list[dict]]:
    from kokoro_onnx import Kokoro

    k = Kokoro(str(KOKORO_DIR / "kokoro-v1.0.onnx"), str(KOKORO_DIR / "voices-v1.0.bin"))
    style = voice_style(k, voice)
    out, timings, t = [], [], 0.0
    lead = np.zeros(int(SR * 0.25))
    out.append(lead)
    t += len(lead) / SR
    for si, scene in enumerate(narration):
        if si and breaths:
            b = breath(si)
            out.append(b)
            t += len(b) / SR
        s_start = t
        # Whole scene in one pass: intonation carries across phrases instead of resetting at each one,
        # which is most of what made the old phrase-by-phrase read sound robotic.
        audio, sr = k.create(" ".join(scene), voice=style, speed=base_speed, lang="en-us")
        assert sr == SR
        audio = _trim(audio.astype(np.float32))
        phrases = [{"text": p, "start": round(t + a, 3), "end": round(t + b, 3)} for p, (a, b) in zip(scene, _phrase_bounds(audio, scene))]
        out.append(audio)
        t += len(audio) / SR
        timings.append({"start": round(s_start, 3), "end": round(t, 3), "phrases": phrases})
        out.append(np.zeros(int(SR * SCENE_GAP)))
        t += SCENE_GAP
    return np.concatenate(out), timings


GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
GEMINI_MODEL = os.environ.get("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")
GEMINI_STYLE = ("young male creator talking to a friend, warm and energetic, a little amused, "
                "conversational not announcer, natural breaths, vary the pace, lean into the key word")


def _find_audio(obj):
    """Return the first base64 audio payload anywhere in an Interactions API response."""
    if isinstance(obj, dict):
        if obj.get("type") == "audio" and isinstance(obj.get("data"), str):
            return obj["data"]
        if "output_audio" in obj and isinstance(obj["output_audio"], dict) and obj["output_audio"].get("data"):
            return obj["output_audio"]["data"]
        for v in obj.values():
            r = _find_audio(v)
            if r:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = _find_audio(v)
            if r:
                return r
    return None


def gemini_tts(text: str, voice: str, style: str) -> np.ndarray:
    import base64
    import io
    import urllib.request

    # Either GEMINI_API_KEY is in the environment, or the key is an environment "API credential" that the
    # network proxy adds as the x-goog-api-key header on requests to generativelanguage.googleapis.com.
    key = os.environ.get("GEMINI_API_KEY")
    body = {"model": GEMINI_MODEL,
            "input": [{"type": "user_input", "content": [{"type": "text", "text": text,
                       "annotations": [{"type": "speech_metadata", "style": style}]}]}],
            "response_format": {"type": "audio"},
            "generation_config": {"speech_config": [{"voice": voice}]}}
    req = urllib.request.Request(GEMINI_URL, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **({"x-goog-api-key": key} if key else {})})
    import time
    import urllib.error

    for attempt in range(6):  # free tier allows 3 requests a minute: wait and retry on 429
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                resp = json.loads(r.read())
            break
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 5:
                raise
            m = re.search(r"retry in (\d+)", e.read().decode())
            time.sleep(int(m.group(1)) + 2 if m else 25)
    b64 = _find_audio(resp)
    if not b64:
        raise RuntimeError(f"no audio in response: {str(resp)[:300]}")
    raw = base64.b64decode(b64)
    if raw[:4] == b"RIFF":
        audio, sr = sf.read(io.BytesIO(raw), dtype="float32")
    else:  # bare 16-bit PCM at 24 kHz
        audio, sr = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768, SR
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    if sr != SR:
        audio = np.interp(np.linspace(0, len(audio), int(len(audio) * SR / sr), endpoint=False), np.arange(len(audio)), audio).astype(np.float32)
    return audio


def _trim(audio: np.ndarray, thr: float = 0.004) -> np.ndarray:
    idx = np.where(np.abs(audio) > thr)[0]
    return audio[max(idx[0] - 240, 0): idx[-1] + 480] if len(idx) else audio


def _phrase_bounds(audio: np.ndarray, phrases: list[str]) -> list[tuple[float, float]]:
    """Split one take into phrases: walk forward, and for each phrase cut at the longest pause inside a
    window around where its share of the characters says it should end. Never earlier than 55% of that."""
    n = len(audio) / SR
    if len(phrases) == 1:
        return [(0.0, n)]
    hop = int(SR * 0.01)
    env = np.array([np.sqrt(np.mean(audio[i:i + hop] ** 2)) for i in range(0, len(audio) - hop, hop)])
    quiet = env < max(env.max() * 0.04, 1e-4)
    weight = [len(p) + 6 for p in phrases]  # +6: every phrase carries some fixed onset/offset time
    cuts, prev = [], 0
    for k in range(len(phrases) - 1):
        remaining = len(env) - prev
        exp = remaining * weight[k] / sum(weight[k:])
        lo, hi = prev + int(exp * 0.55), min(prev + int(exp * 1.6), len(env) - 1)
        best, best_len, i = prev + int(exp), -1e9, lo
        while i < hi:
            if quiet[i]:
                j = i
                while j < len(quiet) and quiet[j]:
                    j += 1
                score = (j - i) - 0.12 * abs((i + j) // 2 - (prev + exp))
                if score > best_len:
                    best, best_len = (i + j) // 2, score
                i = j
            else:
                i += 1
        cuts.append(best)
        prev = best
    edges = [0.0, *[c * hop / SR for c in cuts], n]
    return [(edges[i], edges[i + 1]) for i in range(len(phrases))]

def synth_gemini(narration: list[list[str]], voice: str, style: str) -> tuple[np.ndarray, list[dict]]:
    """Whole script in ONE request: the model paces the story itself (and the free tier allows only
    3 requests a minute). Lines are then placed at the natural pauses."""
    audio = _trim(gemini_tts("\n\n".join(" ".join(sc) for sc in narration), voice, style))
    flat = [p for sc in narration for p in sc]
    bounds = _phrase_bounds(audio, flat)
    lead = 0.2
    timings, k = [], 0
    for sc in narration:
        ph = [{"text": p, "start": round(lead + bounds[k + i][0], 3), "end": round(lead + bounds[k + i][1], 3)} for i, p in enumerate(sc)]
        k += len(sc)
        timings.append({"start": ph[0]["start"], "end": ph[-1]["end"], "phrases": ph})
    return np.concatenate([np.zeros(int(SR * lead), dtype=np.float32), audio]), timings


def synth_from_take(narration: list[list[str]], path: str) -> tuple[np.ndarray, list[dict]]:
    """Re-use a saved full-script take (e.g. voice-candidates/gemini-puck.wav) without calling the API."""
    audio, sr = sf.read(path, dtype="float32")
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    assert sr == SR, sr
    audio = _trim(audio)
    flat = [p for sc in narration for p in sc]
    bounds = _phrase_bounds(audio, flat)
    lead, timings, k = 0.2, [], 0
    for sc in narration:
        ph = [{"text": p, "start": round(lead + bounds[k + i][0], 3), "end": round(lead + bounds[k + i][1], 3)} for i, p in enumerate(sc)]
        k += len(sc)
        timings.append({"start": ph[0]["start"], "end": ph[-1]["end"], "phrases": ph})
    return np.concatenate([np.zeros(int(SR * lead), dtype=np.float32), audio]), timings


def synth_gemini_per_scene(narration: list[list[str]], voice: str, style: str) -> tuple[np.ndarray, list[dict]]:
    out, timings, t = [np.zeros(int(SR * 0.2))], [], 0.2
    for scene in narration:
        audio = _trim(gemini_tts(" ".join(scene), voice, style))
        s_start = t
        phrases = [{"text": p, "start": round(t + a, 3), "end": round(t + b, 3)} for p, (a, b) in zip(scene, _phrase_bounds(audio, scene))]
        out.append(audio)
        t += len(audio) / SR
        timings.append({"start": round(s_start, 3), "end": round(t, 3), "phrases": phrases})
        gap = 0.28
        out.append(np.zeros(int(SR * gap)))
        t += gap
    return np.concatenate(out), timings


def chunk_caption(p: dict, max_words: int = 7) -> list[dict]:
    """Split a phrase into short subtitle chunks, timed by character share (good enough at speech pace)."""
    words = p["text"].split()
    n = max(1, -(-len(words) // max_words))
    size = -(-len(words) // n)
    parts = [" ".join(words[i:i + size]) for i in range(0, len(words), size)]
    total = sum(len(x) for x in parts)
    t, out = p["start"], []
    for x in parts:
        d = (p["end"] - p["start"]) * len(x) / total
        out.append({"at": round(t, 3), "until": round(t + d + 0.08, 3), "text": x})
        t += d
    return out


def main(spec_path: Path, voice: str, breaths: bool, bed: bool, speed: float = 1.0, engine: str = "kokoro", style: str = GEMINI_STYLE) -> None:
    spec = json.loads(spec_path.read_text())
    narration = spec["narration"]
    if engine == "auto":
        try:
            audio, timings = synth_gemini_per_scene(narration, "Puck" if ":" in voice or "_" in voice else voice, style)
            engine = "gemini"
        except Exception as e:  # noqa: BLE001  (no credential or no network: fall back to the offline voice)
            print(f"Gemini TTS unavailable ({e}); using Kokoro")
            engine = "kokoro"
            audio, timings = synth(narration, voice if "_" in voice else "am_puck:0.6,am_fenrir:0.4", breaths, speed)
    elif engine == "gemini":  # one request per scene: exact scene timing, natural flow within each thought
        audio, timings = synth_gemini_per_scene(narration, voice, style)
    elif engine.startswith("take:"):
        audio, timings = synth_from_take(narration, engine[5:])
        engine = "gemini"
    elif engine == "gemini-oneshot":
        audio, timings = synth_gemini(narration, voice, style)
    else:
        audio, timings = synth(narration, voice, breaths, speed)
    dur = len(audio) / SR + 0.8
    mix = np.zeros(int(SR * dur), dtype=np.float32)
    mix[: len(audio)] += audio
    if bed:
        mix += ambient_bed(dur).astype(np.float32)
    post = spec_path.parent
    raw = post / "voice.raw.wav"
    sf.write(raw, mix, SR)
    # broadcast-style loudness for social video, with a gentle de-esser-ish high shelf cut
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af",
                    "highshelf=f=7000:g=-2,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,loudnorm=I=-15:TP=-1.5:LRA=9",
                    "-ar", "48000", str(post / "voice.wav")], check=True)
    raw.unlink()
    # pictures follow the voice: one beat per spoken phrase (motion template), or one scene per scene
    if "beats" in spec:
        flat = [p for tm in timings for p in tm["phrases"]]
        assert len(flat) == len(spec["beats"]), f"{len(flat)} phrases but {len(spec['beats'])} beats"
        for b, p in zip(spec["beats"], flat):
            b["at"], b["until"], b["say"] = round(p["start"], 2), round(p["end"], 2), p["text"]
    for scene, tm in zip(spec.get("scenes", []), timings):
        scene["at"], scene["until"] = round(tm["start"] - 0.15, 2), round(tm["end"] + 0.1, 2)
    spec["duration"] = round(dur + 0.6, 2)
    spec["captions"] = [c for tm in timings for p in tm["phrases"] for c in chunk_caption(p)]
    spec["voice"] = {"engine": GEMINI_MODEL if engine.startswith("gemini") else "kokoro-82m", "voice": voice, "breaths": breaths, "bed": bed}
    spec_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False))
    (post / "voice.json").write_text(json.dumps({"voice": voice, "duration": dur, "scenes": timings}, indent=1))
    print(f"voice.wav {dur:.1f}s, {sum(len(s) for s in narration)} phrases, voice {voice}")


if __name__ == "__main__":
    a = sys.argv[1:]
    eng = a[a.index("--engine") + 1] if "--engine" in a else "auto"
    v = a[a.index("--voice") + 1] if "--voice" in a else ("am_puck:0.6,am_fenrir:0.4" if eng == "kokoro" else "Puck")
    sp = float(a[a.index("--speed") + 1]) if "--speed" in a else 1.0
    st = a[a.index("--style") + 1] if "--style" in a else GEMINI_STYLE
    main(Path(a[0]), v, "--no-breaths" not in a, "--no-bed" not in a, sp, eng, st)
