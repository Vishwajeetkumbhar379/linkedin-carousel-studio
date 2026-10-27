"""Make a voice sound close, clean and quick: the one voice chain for every reel (real recordings and the clone).
    python scripts/voice_polish.py <in> <out.wav> [--speed 1.15] [--no-isolate]
1. ElevenLabs Voice Isolator takes out the room (the echo also lives in the clone, which learned it from room recordings).
2. Pauses are shortened, never cut to dead air: each one shrinks to at most MAX_PAUSE with soft equal-power joins,
   so a sentence ends on its natural decay instead of a switch.
3. Faster delivery, same pitch (ffmpeg atempo, gentle ratios only).
4. Close-mic tone: rumble out, proximity warmth, less boxiness, presence and air, de-essed, compressed, levelled.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import numpy as np

SR = 48000
MAX_PAUSE, XF = 0.2, 0.035  # longest pause kept, crossfade (s)
TONE = ("highpass=f=75,lowshelf=f=140:g=3,equalizer=f=350:t=q:w=1.2:g=-2.5,equalizer=f=4200:t=q:w=1:g=2.5,"
        "highshelf=f=10000:g=1.5,deesser=i=0.4,acompressor=threshold=-21dB:ratio=3:attack=5:release=90:makeup=3,"
        "alimiter=limit=0.9,loudnorm=I=-16:TP=-1.5:LRA=7")


def decode(path: Path) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def isolate(path: Path, work: Path) -> Path:
    import requests
    mp3 = work / (path.stem + "_iso_in.mp3")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-ac", "1", "-b:a", "192k", str(mp3)], check=True)
    with open(mp3, "rb") as f:
        r = requests.post("https://api.elevenlabs.io/v1/audio-isolation", headers={"xi-api-key": os.environ["CLAUDEELEVENLABS_API"]},
                          files={"audio": (mp3.name, f, "audio/mpeg")}, timeout=600)
    r.raise_for_status()
    out = work / (path.stem + "_iso.mp3"); out.write_bytes(r.content)
    return out


def tighten(x: np.ndarray) -> np.ndarray:
    """Shrink every pause longer than MAX_PAUSE, keeping KEEP_EDGE of decay each side, joined with an equal-power crossfade."""
    hop = int(0.01 * SR)
    env = np.sqrt(np.convolve(x ** 2, np.ones(hop) / hop, mode="same"))
    quiet = env < max(1e-4, np.percentile(env, 95) * 0.012)  # about -38 dB under the loud parts: soft words stay
    out, i, n = [], 0, len(x)
    while i < n:
        if not quiet[i]:
            j = i
            while j < n and not quiet[j]: j += 1
            out.append(x[i:j]); i = j; continue
        j = i
        while j < n and quiet[j]: j += 1
        if (j - i) / SR > MAX_PAUSE and i > 0 and j < n:
            # keep the decay after the word and the breath before the next, meeting in an equal-power crossfade
            xf = int(XF * SR); half = int(MAX_PAUSE * SR / 2) + xf // 2
            a, b = x[i:i + half], x[j - half:j]
            t = np.linspace(0, np.pi / 2, xf)
            out.append(np.concatenate([a[:-xf], a[-xf:] * np.cos(t) + b[:xf] * np.sin(t), b[xf:]]))
        else:
            out.append(x[i:j])
        i = j
    return np.concatenate(out)


def main(src: Path, dst: Path, speed: float = 1.15, iso: bool = True):
    work = dst.parent / "work"; work.mkdir(parents=True, exist_ok=True)
    clean = isolate(src, work) if iso and os.environ.get("CLAUDEELEVENLABS_API") else src
    x = tighten(decode(clean))
    tmp = work / (dst.stem + "_tight.wav")
    import soundfile as sf
    sf.write(tmp, x, SR, subtype="FLOAT")
    af = (f"atempo={speed}," if abs(speed - 1) > 0.01 else "") + TONE
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-af", af, "-ar", str(SR), "-ac", "1", str(dst)], check=True)
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(dst)], capture_output=True, text=True).stdout)
    print(f"{src.name} -> {dst.name}: {len(decode(src)) / SR:.1f}s -> {d:.1f}s")


if __name__ == "__main__":
    a = sys.argv[1:]
    sp = float(a[a.index("--speed") + 1]) if "--speed" in a else 1.15
    main(Path(a[0]).resolve(), Path(a[1]).resolve(), sp, "--no-isolate" not in a)
