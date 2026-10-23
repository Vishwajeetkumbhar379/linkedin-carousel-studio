"""Sound design for Shorts: synthesised SFX (no samples, no licences) and a dark, pulsing bed that sits under the voice.

Every visual event in the template publishes {t, s}; `mix()` places one sound per event, ducks the bed under the voice,
and normalises to -14 LUFS later in ffmpeg.
"""
from __future__ import annotations

import numpy as np

SR = 48000


def _t(d):
    return np.arange(int(SR * d)) / SR


def _noise(n, seed):
    return np.random.default_rng(seed).standard_normal(n)


def _lp(x, a):  # one-pole low-pass, a in (0, 1) (scalar or per-sample): smaller = darker
    a = np.broadcast_to(np.asarray(a, dtype=float), x.shape)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += a[i] * (v - acc)
        y[i] = acc
    return y


def _norm(x, peak=1.0):
    return x / (np.abs(x).max() + 1e-9) * peak


def whoosh(seed=1, d=0.5):
    t = _t(d)
    n = _noise(len(t), seed)
    sweep = np.linspace(0.02, 0.35, len(t)) ** 1.5
    y = np.empty_like(n)
    acc = 0.0
    for i, v in enumerate(n):
        acc += sweep[i] * (v - acc)
        y[i] = acc
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    return _norm(y * env, 0.5)


def thump():
    t = _t(0.45)
    f = 48 + 90 * np.exp(-t * 18)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    return _norm(y + 0.15 * _noise(len(t), 3) * np.exp(-t * 60), 0.9)


def tick(seed=0):
    t = _t(0.06)
    y = np.sin(2 * np.pi * (1800 + 120 * (seed % 5)) * t) * np.exp(-t * 90) + 0.4 * _noise(len(t), seed) * np.exp(-t * 220)
    return _norm(y, 0.32)


def pop():
    t = _t(0.18)
    y = np.sin(2 * np.pi * (300 + 1100 * np.exp(-t * 35)) * t) * np.exp(-t * 26)
    return _norm(y, 0.5)


def ding():
    t = _t(1.2)
    y = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, a, k in ((1318.5, 1, 3.2), (2637, 0.35, 5), (3951, 0.15, 7)))
    return _norm(y, 0.35)


def click():
    t = _t(0.05)
    return _norm(_noise(len(t), 7) * np.exp(-t * 300) + np.sin(2 * np.pi * 900 * t) * np.exp(-t * 120), 0.45)


def zip_(seed=4):
    t = _t(1.3)
    f = 300 + 2600 * (t / t[-1]) ** 2
    y = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.25 + _lp(_noise(len(t), seed), 0.3)
    return _norm(y * (t / t[-1]) ** 1.2 * np.exp(-np.maximum(0, t - 1.15) * 30), 0.32)


def rise():
    t = _t(2.4)
    f = 110 * 2 ** (3 * t / t[-1])
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.5 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR)
    y += 0.6 * _lp(_noise(len(t), 8), 0.05 + 0.3 * t / t[-1])
    return _norm(y * (t / t[-1]) ** 2, 0.4)


def scratch():
    t = _t(0.3)
    return _norm(_lp(_noise(len(t), 11), 0.25) * np.sin(np.pi * t / 0.3) * (1 + np.sin(2 * np.pi * 28 * t)), 0.35)


def coin():
    t = _t(0.7)
    y = (np.sin(2 * np.pi * 1975 * t) * (t < 0.08) + np.sin(2 * np.pi * 2637 * t) * (t >= 0.08)) * np.exp(-t * 6)
    return _norm(y, 0.3)


def send():
    w = whoosh(5, 0.35)
    p = pop()
    y = np.zeros(max(len(w), len(p)))
    y[:len(p)] += p
    y[:len(w)] += 0.7 * w
    return _norm(y, 0.55)


def tap():
    return click() * 0.8


GEN = {"whoosh": whoosh, "thump": thump, "tick": tick, "pop": pop, "ding": ding, "click": click, "zip": zip_,
       "rise": rise, "scratch": scratch, "coin": coin, "send": send, "tap": tap}


def bed(seconds: float, bpm: float = 84) -> np.ndarray:
    """Dark, curious bed: a low drone, a soft pulse on every beat, a ticking hat, a slow arp. A minor."""
    n = int(SR * seconds)
    t = np.arange(n) / SR
    drone = sum(a * np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 0.07 * t)) for f, a in ((55, 1), (82.4, 0.5), (110, 0.35)))
    drone *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t) ** 2
    y = 0.35 * drone
    beat = 60 / bpm
    kick = thump() * 0.5
    hat = _norm(_noise(int(SR * 0.03), 2) * np.exp(-np.arange(int(SR * 0.03)) / SR * 140), 0.12)
    arp = [220, 261.6, 329.6, 392, 329.6, 261.6, 196, 246.9]
    at = _t(beat / 2)
    k = 0
    tt = 0.0
    while tt < seconds:
        s = int(tt * SR)
        if k % 2 == 0:
            m = min(len(kick), n - s)
            y[s:s + m] += kick[:m]
        h = int((tt + beat / 2) * SR)
        if h < n:
            m = min(len(hat), n - h)
            y[h:h + m] += hat[:m]
        for j in range(2):
            a0 = int((tt + j * beat / 2) * SR)
            if a0 < n:
                f = arp[(2 * k + j) % len(arp)]
                note = (np.sin(2 * np.pi * f * at) + 0.3 * np.sin(4 * np.pi * f * at)) * np.exp(-at * 7) * 0.16
                m = min(len(note), n - a0)
                y[a0:a0 + m] += note[:m]
        tt += beat
        k += 1
    fade = np.minimum(1, np.minimum(t / 0.3, (seconds - t) / 0.4))
    return _norm(y * np.clip(fade, 0, 1), 0.8)


def mix(voice: np.ndarray, events: list[dict], seconds: float) -> np.ndarray:
    n = int(seconds * SR)
    v = np.zeros(n, np.float32)
    v[:min(n, len(voice))] = voice[:n]
    fx = np.zeros(n, np.float32)
    for k, e in enumerate(events):
        g = GEN.get(e["s"], pop)
        try:
            s = g(k) if g in (whoosh, tick, zip_) else g()
        except TypeError:
            s = g()
        i = int(e["t"] * SR)
        if i < n:
            m = min(len(s), n - i)
            fx[i:i + m] += s[:m].astype(np.float32)
    b = bed(seconds).astype(np.float32)[:n]
    env = np.convolve(np.abs(v), np.ones(int(0.2 * SR)) / int(0.2 * SR), mode="same")
    duck = 1.0 - 0.6 * np.clip(env / (env.max() * 0.3 + 1e-9), 0, 1)
    out = v + 0.55 * fx + 0.22 * b * duck
    return out / max(1.0, np.abs(out).max() / 0.95)
