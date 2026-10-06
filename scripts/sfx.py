"""Sound design for motion videos: a transition sound on every beat plus a light music bed under the voice.

    python scripts/sfx.py out/<post>/video.json      # writes out/<post>/mix.wav from voice.wav

Everything is synthesised here (no sample packs, no licences to track):
  whip / rise  -> filtered noise sweep (whoosh)
  zoom         -> whoosh plus a low thump
  click        -> short UI click
  pop          -> soft bubble pop
  bed          -> 96 bpm kick + hat + warm chord stabs, ducked under the voice
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

SR = 48000


def _env(n, a=0.01, r=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-np.maximum(0, t - a) / r)


def _bandnoise(n, lo, hi, seed):
    x = np.random.default_rng(seed).standard_normal(n)
    f = np.fft.rfft(x)
    fr = np.fft.rfftfreq(n, 1 / SR)
    f[(fr < lo) | (fr > hi)] = 0
    return np.fft.irfft(f, n)


def whoosh(dur=0.42, seed=1):
    n = int(SR * dur)
    x = _bandnoise(n, 300, 9000, seed)
    t = np.linspace(0, 1, n)
    # moving resonance: sweep a band from low to high, louder in the middle
    out = np.zeros(n)
    for k, c in enumerate(np.linspace(500, 5000, 12)):
        seg = slice(int(k * n / 12), int((k + 1) * n / 12))
        out[seg] = _bandnoise(n, c * 0.6, c * 1.6, seed + k)[seg]
    env = np.sin(np.pi * t) ** 1.5
    y = (0.5 * x + out) * env
    return y / (np.abs(y).max() + 1e-9)


def thump(dur=0.3):
    t = np.arange(int(SR * dur)) / SR
    return np.sin(2 * np.pi * (55 + 90 * np.exp(-t * 30)) * t) * np.exp(-t * 12)


def click(seed=3):
    n = int(SR * 0.05)
    x = _bandnoise(n, 1500, 9000, seed) * _env(n, 0.0005, 0.008)
    t = np.arange(n) / SR
    x += 0.6 * np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 160)
    return x / (np.abs(x).max() + 1e-9)


def pop():
    t = np.arange(int(SR * 0.16)) / SR
    y = np.sin(2 * np.pi * (380 + 900 * np.exp(-t * 40)) * t) * np.exp(-t * 28)
    return y / (np.abs(y).max() + 1e-9)


def bed(seconds, bpm=96):
    n = int(SR * seconds)
    y = np.zeros(n)
    beat = 60 / bpm
    k = thump(0.35) * 0.9
    h = _bandnoise(int(SR * 0.05), 6000, 14000, 9) * _env(int(SR * 0.05), 0.001, 0.015)
    h /= np.abs(h).max()
    t_ = 0.0
    i = 0
    while t_ < seconds:
        s = int(t_ * SR)
        if i % 4 in (0, 2):
            y[s:s + len(k)] += k[: max(0, min(len(k), n - s))]
        hs = int((t_ + beat / 2) * SR)
        if hs < n:
            y[hs:hs + len(h)] += 0.35 * h[: max(0, min(len(h), n - hs))]
        t_ += beat
        i += 1
    # warm chord stabs every bar: Fmaj7 / Am7 / Dm9 / Bbmaj7
    chords = [[174.6, 220.0, 261.6, 329.6], [220.0, 261.6, 329.6, 392.0], [146.8, 220.0, 261.6, 349.2], [233.1, 293.7, 349.2, 440.0]]
    bar = beat * 4
    tt = np.arange(int(SR * bar)) / SR
    for b in range(int(seconds / bar) + 1):
        c = chords[b % 4]
        pad = sum(np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt) for f in c) / len(c)
        pad *= np.minimum(1, tt / 0.04) * np.exp(-tt / 1.4)
        s = int(b * bar * SR)
        m = max(0, min(len(pad), n - s))
        y[s:s + m] += 0.5 * pad[:m]
    fade = np.minimum(1, np.minimum(np.arange(n) / (SR * 1.0), (n - np.arange(n)) / (SR * 1.5)))
    return y * fade


def mix(spec_path: Path) -> Path:
    spec = json.loads(spec_path.read_text())
    post = spec_path.parent
    voice, sr = sf.read(post / "voice.wav", dtype="float32")
    if voice.ndim > 1:
        voice = voice.mean(axis=1)
    assert sr == SR, sr
    n = max(len(voice), int(SR * spec["duration"]))
    fx = np.zeros(n)
    for i, b in enumerate(spec.get("beats", [])):
        tr = "pop" if i == 0 else b.get("trans", "whip")
        start = b["at"] - 0.42  # transitions land as the line starts
        if tr in ("whip", "rise"):
            s = whoosh(0.42, i) * 0.55
        elif tr == "zoom":
            s = whoosh(0.36, i) * 0.4
            th = np.zeros(len(s) + int(SR * 0.3)); th[int(SR * 0.3):int(SR * 0.3) + len(thump())] += thump()[: len(th) - int(SR * 0.3)] * 0.7
            s = np.pad(s, (0, len(th) - len(s))) + th
        elif tr == "click":
            s = np.pad(click(i), (int(SR * 0.32), 0)) * 0.6
        else:
            s = np.pad(pop(), (int(SR * 0.3), 0)) * 0.5
        a = max(0, int(start * SR))
        m = min(len(s), n - a)
        fx[a:a + m] += s[:m]
        # cursor clicks: CTA button, and the tap on the sponsored post in the feed
        if b.get("look") in ("cta", "feed"):
            c0 = int((b["at"] + (1.1 if b.get("look") == "cta" else b.get("scrollAt", 0.15) + 1.5)) * SR)
            if c0 < n:
                c = click(99) * 0.6
                fx[c0:c0 + len(c)] += c[: n - c0]
    v = np.zeros(n); v[: len(voice)] = voice
    music = bed(n / SR)
    # duck the bed under speech (envelope follower)
    env = np.convolve(np.abs(v), np.ones(int(SR * 0.25)) / (SR * 0.25), mode="same")
    duck = 1 - 0.6 * np.clip(env / (env.max() * 0.35 + 1e-9), 0, 1)
    out = v + 0.16 * fx + 0.10 * music * duck
    raw = post / "mix.raw.wav"
    sf.write(raw, out.astype(np.float32), SR)
    dst = post / "mix.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", "alimiter=limit=0.9,loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "48000", str(dst)], check=True)
    raw.unlink()
    return dst


if __name__ == "__main__":
    print(mix(Path(sys.argv[1])))
