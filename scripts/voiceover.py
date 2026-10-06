"""Voiceover for videos: natural pacing, soft breaths, timings that drive scenes and subtitles.

    python scripts/voiceover.py out/<post>/video.json [--voice af_heart] [--no-breaths] [--no-bed]

Reads `narration` from video.json: a list of scenes, each a list of phrases. Writes
  out/<post>/voice.wav      final mix (voice + optional soft ambient bed), loudness-normalised
  out/<post>/voice.json     phrase and scene timings (seconds), used by the video renderer
and rewrites each scene's `at`/`until` in video.json to match the audio, so pictures follow the voice.

Engine: Kokoro-82M via kokoro-onnx (model Apache-2.0, code MIT), runs on CPU.
Model files live in $KOKORO_DIR (default /home/user/models/kokoro), downloaded from
github.com/thewh1teagle/kokoro-onnx releases. For Vish's own voice, see docs/voice.md.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

SR = 24000
KOKORO_DIR = Path(os.environ.get("KOKORO_DIR", "/home/user/models/kokoro"))
PAUSE = {",": 0.16, ";": 0.22, ":": 0.22, ".": 0.38, "?": 0.42, "!": 0.38}
SCENE_GAP = 0.5


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


def synth(narration: list[list[str]], voice: str, breaths: bool) -> tuple[np.ndarray, list[dict]]:
    from kokoro_onnx import Kokoro

    k = Kokoro(str(KOKORO_DIR / "kokoro-v1.0.onnx"), str(KOKORO_DIR / "voices-v1.0.bin"))
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
        phrases = []
        for pi, phrase in enumerate(scene):
            speed = 1.0 + (0.025 if pi % 3 == 1 else -0.015 if pi % 3 == 2 else 0)
            audio, sr = k.create(phrase, voice=voice, speed=speed, lang="en-us")
            assert sr == SR
            audio = np.trim_zeros(audio.astype(np.float32), "fb")
            phrases.append({"text": phrase, "start": round(t, 3), "end": round(t + len(audio) / SR, 3)})
            out.append(audio)
            t += len(audio) / SR
            gap = PAUSE.get(phrase.strip()[-1], 0.12)
            out.append(np.zeros(int(SR * gap)))
            t += gap
        timings.append({"start": round(s_start, 3), "end": round(t, 3), "phrases": phrases})
        out.append(np.zeros(int(SR * SCENE_GAP)))
        t += SCENE_GAP
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


def main(spec_path: Path, voice: str, breaths: bool, bed: bool) -> None:
    spec = json.loads(spec_path.read_text())
    narration = spec["narration"]
    audio, timings = synth(narration, voice, breaths)
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
    # pictures follow the voice
    for scene, tm in zip(spec["scenes"], timings):
        scene["at"], scene["until"] = round(tm["start"] - 0.15, 2), round(tm["end"] + 0.1, 2)
    spec["duration"] = round(dur + 0.6, 2)
    spec["captions"] = [c for tm in timings for p in tm["phrases"] for c in chunk_caption(p)]
    spec["voice"] = {"engine": "kokoro-82m", "voice": voice, "breaths": breaths, "bed": bed}
    spec_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False))
    (post / "voice.json").write_text(json.dumps({"voice": voice, "duration": dur, "scenes": timings}, indent=1))
    print(f"voice.wav {dur:.1f}s, {sum(len(s) for s in narration)} phrases, voice {voice}")


if __name__ == "__main__":
    a = sys.argv[1:]
    v = a[a.index("--voice") + 1] if "--voice" in a else "af_heart"
    main(Path(a[0]), v, "--no-breaths" not in a, "--no-bed" not in a)
