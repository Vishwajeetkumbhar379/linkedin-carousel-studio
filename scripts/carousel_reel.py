"""Turn a week-series carousel (templates/carousel/<name>.html) into a 9:16 motion reel with composed music and sound design.

    python scripts/carousel_reel.py brandside-contract out/week03/carousel-contract/reel-9x16.mp4 --mood="tense, serious"

The look comes from the carousel itself (same paper, type and amber as every post), so the reels and the carousels read
as one brand. Motion: scripts/carousel_reel.js. Music: ElevenLabs Music in the brand sound (cached per reel and length),
slide changes snapped to its beat. Effects: video-projects/sfx-library. Loudness -14 LUFS.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render3d import serve  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SFX = ROOT / "video-projects" / "sfx-library"
MUSIC = ROOT / "video-projects" / "assets-music"
FPS, SR, SW = 30, 44100, 0.42
BRAND = (["modern upbeat indie electronic", "warm analog synth plucks", "punchy tight drums", "deep warm bass", "110 bpm", "confident and hopeful"],
         ["vocals", "lyrics", "singing", "sad", "corporate stock music", "tape hiss"])


def durations(meta: list[dict]) -> list[float]:
    out = []
    for i, m in enumerate(meta):
        items = m["parts"].count("item")
        code = sum(min(2.2, .35 + c / 260) * .6 for c in m["code"])
        enter = .12 * len(m["parts"]) + .26 * items + code
        read = max(0, m["words"] - 10) / 5.5  # fast enough that people pause or rewatch, which counts as watch time
        d = max(enter + 1.0, read, 2.2)
        if i == 0:
            d = 2.6  # the hook: one breath, then swipe
        elif i == len(meta) - 1:
            d = max(d, 4.0)
        out.append(min(d, 4.2))
    return out


def compose(name: str, dur: float, mood: str) -> Path:
    out = MUSIC / f"{name}_{int(dur * 10)}.mp3"
    if out.exists():
        return out
    cuts = [(0.0, "intro", ["instant energy", "filtered drums opening up", mood]), (3.0, "main", ["steady driving groove", "catchy pluck motif", mood]),
            (dur - 4.5, "lift", ["short build", "snare roll"]), (dur - 3.0, "end", ["final hit", "clean ending"])]
    secs = []
    for i, (t0, nm, styles) in enumerate(cuts):
        t1 = cuts[i + 1][0] if i + 1 < len(cuts) else dur + 0.5
        secs.append({"section_name": nm, "positive_local_styles": styles, "negative_local_styles": [],
                     "duration_ms": max(3000, int(round((t1 - t0) * 1000))), "lines": []})
    key = os.environ["CLAUDEELEVENLABS_API"]
    url = "https://api.elevenlabs.io/v1/music?output_format=mp3_44100_192"
    hdr = {"xi-api-key": key, "Content-Type": "application/json"}
    body = {"composition_plan": {"positive_global_styles": BRAND[0], "negative_global_styles": BRAND[1], "sections": secs}, "model_id": "music_v1"}
    try:
        data = urllib.request.urlopen(urllib.request.Request(url, json.dumps(body).encode(), hdr, method="POST"), timeout=600).read()
    except urllib.error.HTTPError as e:
        print("composition plan refused:", e.code, e.read()[:200])
        body = {"prompt": ", ".join(BRAND[0]) + f", {mood}. Instant start, steady driving groove, clean ending. No vocals.",
                "music_length_ms": int((dur + 0.5) * 1000), "model_id": "music_v1"}
        data = urllib.request.urlopen(urllib.request.Request(url, json.dumps(body).encode(), hdr, method="POST"), timeout=600).read()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    return out


def load(path: Path) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def beats(x: np.ndarray) -> np.ndarray:
    """Beat times of the composed track: spectral-flux onsets, tempo by autocorrelation (90 to 135 bpm), then the phase."""
    m = x.mean(1)
    hop, n = 512, 2048
    fr = np.lib.stride_tricks.sliding_window_view(m, n)[::hop] * np.hanning(n)
    mag = np.log1p(np.abs(np.fft.rfft(fr, axis=1)))
    flux = np.maximum(0, np.diff(mag, axis=0)).sum(1)
    flux = (flux - flux.mean()) / (flux.std() + 1e-9)
    fps = SR / hop
    lags = np.arange(int(fps * 60 / 135), int(fps * 60 / 90) + 1)
    ac = [np.dot(flux[:-l], flux[l:]) for l in lags]
    per = lags[int(np.argmax(ac))] / fps
    ph = np.linspace(0, per, 40, endpoint=False)
    score = [sum(np.interp(np.arange(p, len(flux) / fps, per) * fps, np.arange(len(flux)), flux)) for p in ph]
    p0 = ph[int(np.argmax(score))]
    print(f"music: {60 / per:.1f} bpm")
    return np.arange(p0, len(m) / SR, per)


def main(name: str, out: Path, mood: str) -> None:
    from playwright.sync_api import sync_playwright

    js = (Path(__file__).parent / "carousel_reel.js").read_text()
    out.parent.mkdir(parents=True, exist_ok=True)
    with serve() as base, sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        pg.goto(f"{base}/carousel/{name}.html")
        pg.wait_for_function("window.READY === true")
        pg.add_script_tag(content=js)
        meta = pg.evaluate("R.measure()")
        d = durations(meta)
        total = sum(d) + .6
        music = load(compose(name, total + 1.0, mood))
        bt = beats(music)
        # slide i+1 lands on a beat: the middle of the swipe sits on the beat nearest its planned time
        a, t = [0.0], 0.0
        for k in d[:-1]:
            t += k
            mid = bt[np.argmin(np.abs(bt - (t - SW / 2)))]
            t = max(a[-1] + 2.0, mid + SW / 2)
            a.append(round(t, 3))
        end = a[-1] + d[-1]
        bounds = [[a[i], (a[i + 1] - SW) if i + 1 < len(a) else end + 9] for i in range(len(a))]
        ev = pg.evaluate(f"R.init({json.dumps(bounds)})")
        n = int(round(end * FPS))
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                                "-crf", "17", "-pix_fmt", "yuv420p", str(out.with_suffix(".video.mp4"))], stdin=subprocess.PIPE)
        for f in range(n):
            pg.evaluate(f"R.seek({f / FPS})")
            enc.stdin.write(pg.screenshot(type="jpeg", quality=93))
        enc.stdin.close()
        enc.wait()
        b.close()

    # audio: the music bed, the effects on their events, an ending fade, -14 LUFS
    L = int((end + .1) * SR)
    mix = np.zeros((L, 2), np.float32)
    mus = music[:L]
    mus = mus / (np.sqrt((mus ** 2).mean()) + 1e-9) * .16
    fade = np.ones(len(mus), np.float32)
    k = int(1.2 * SR)
    fade[-k:] = np.linspace(1, 0, k)
    mix[:len(mus)] += mus * fade[:, None]
    cache = {}
    for t, s, g in ev:
        if s not in cache:
            cache[s] = load(SFX / f"{s}.mp3")
        x = cache[s]
        if s == "whoosh":  # peak on the slide change
            t -= np.argmax(np.abs(x).mean(1)) / SR - .2
        if s == "type":
            x = x[:int(g * SR)]
            g = .55
        i0 = int(max(0, t) * SR)
        seg = x[:max(0, L - i0)] / (np.abs(x).max() + 1e-9) * {"whoosh": .32, "whoosh_soft": .2, "pop": .22, "click": .18, "type": .2,
                                                                 "tick": .16, "ding": .22}.get(s, .2) * g
        mix[i0:i0 + len(seg)] += seg
    wav = out.with_suffix(".wav")
    import soundfile as sf
    sf.write(str(wav), np.clip(mix, -1, 1), SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out.with_suffix(".video.mp4")), "-i", str(wav), "-af", "loudnorm=I=-14:TP=-1.5:LRA=9",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    out.with_suffix(".video.mp4").unlink()
    wav.unlink()
    print(f"-> {out} ({end:.1f} s, {len(d)} slides)")


if __name__ == "__main__":
    opt = dict(a[2:].split("=", 1) for a in sys.argv[3:] if a.startswith("--"))
    main(sys.argv[1], Path(sys.argv[2]), opt.get("mood", "confident"))
