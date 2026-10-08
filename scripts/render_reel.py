"""Render a bespoke motion reel (templates/video/reels/<name>.html) to a finished MP4 with voice, SFX and a ducked bed.

    python scripts/render_reel.py out/flagship/claude-instagram claude-instagram [--stills]

Reads <dir>/voice.json (line timings from scripts/voice_clone.py) and <dir>/voice.wav.
The page exposes setup(spec) / frame(t) and publishes window.SFX = [{t, s}] for the sound design.
Writes <dir>/frames/*.png (QA stills), <dir>/video.mp4.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render3d import GL_ARGS, serve  # noqa: E402
import sfx  # noqa: E402

FPS = 30


def word_time(line: dict, word: str) -> float | None:
    words = line["text"].split()
    tot = sum(len(w) + 1 for w in words)
    acc = 0
    for w in words:
        if re.sub(r"\W", "", w).lower().startswith(word):
            return line["start"] + (line["end"] - line["start"]) * acc / tot
        acc += len(w) + 1
    return None


def spec_for(d: Path) -> dict:
    v = json.loads((d / "voice.json").read_text())
    L = v["lines"]
    words = {}
    for key in ("publish", "comments", "scraping", "overnight"):
        for ln in L:
            t = word_time(ln, key)
            if t is not None:
                words[key] = round(t, 3)
                break
    return {"lines": L, "duration": round(L[-1]["end"] + 2.4, 2), "words": words}


def render(d: Path, name: str, stills_only: bool = False) -> Path:
    from playwright.sync_api import sync_playwright

    spec = spec_for(d)
    D = spec["duration"]
    (d / "frames").mkdir(exist_ok=True)
    silent = d / "video-silent.mp4"
    with serve() as base, sync_playwright() as p:
        b = p.chromium.launch(args=GL_ARGS)
        page = b.new_page(viewport={"width": 1080, "height": 1350})
        errs: list[str] = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto(f"{base}/video/reels/{name}.html")
        page.wait_for_function("window.STAGE_LOADED === true && window.gsap", timeout=60000)
        page.evaluate("s => window.setup(s)", spec)
        page.wait_for_function("window.READY === true", timeout=60000)
        if errs:
            raise RuntimeError(errs)
        events = page.evaluate("window.SFX")
        # one QA still in the middle of every line
        for i, ln in enumerate(spec["lines"]):
            for tag, t in (("a", ln["start"] + 0.35), ("b", (ln["start"] + ln["end"]) / 2 + 0.4)):
                page.evaluate("t => window.frame(t)", t)
                page.screenshot(path=str(d / "frames" / f"l{i + 1}{tag}.png"))
        page.evaluate("t => window.frame(t)", D - 0.5)
        page.screenshot(path=str(d / "frames" / "end.png"))
        if stills_only:
            b.close()
            return d / "frames"
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                               "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(silent)],
                              stdin=subprocess.PIPE)
        for k in range(int(D * FPS)):
            page.evaluate("t => window.frame(t)", k / FPS)
            ff.stdin.write(page.screenshot(type="jpeg", quality=94))
            if k % (FPS * 5) == 0:
                print(f"  {k / FPS:.0f}s / {D}s", flush=True)
        ff.stdin.close()
        ff.wait()
        b.close()
        if errs:
            raise RuntimeError(errs)
    # ---- sound: voice + synthesised SFX + ducked bed ----
    voice, sr = sf.read(str(d / "voice.wav"), dtype="float32")
    if voice.ndim > 1:
        voice = voice.mean(axis=1)
    assert sr == sfx.SR, sr
    n = int(D * sr)
    out = np.zeros(n, dtype=np.float32)
    out[:min(n, len(voice))] += voice[:n]
    fx = np.zeros(n, dtype=np.float32)
    gen = {"whip": lambda k: sfx.whoosh(0.42, seed=k) * 0.55, "zoom": lambda k: np.concatenate([sfx.whoosh(0.4, seed=k)]) * 0.5,
           "thump": lambda k: sfx.thump() * 0.7, "click": lambda k: sfx.click(seed=k) * 0.6, "pop": lambda k: sfx.pop() * 0.45,
           "key": lambda k: sfx.click(seed=100 + k) * 0.16}
    for k, e in enumerate(events):
        s = gen.get(e["s"], gen["pop"])(k).astype(np.float32)
        i = int(e["t"] * sr)
        if i < n:
            fx[i:i + len(s)] += s[:n - i]
    bed = sfx.bed(D).astype(np.float32)[:n]
    env = np.convolve(np.abs(out), np.ones(int(0.25 * sr)) / int(0.25 * sr), mode="same")
    duck = 1.0 - 0.72 * np.clip(env / (env.max() * 0.35 + 1e-9), 0, 1)
    mix = out + fx + np.pad(bed, (0, n - len(bed))) * 0.32 * duck
    mix /= max(1.0, np.abs(mix).max() / 0.95)
    sf.write(str(d / "mix.wav"), mix, sr)
    final = d / "video.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(d / "mix.wav"), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-af", "loudnorm=I=-14:TP=-1.0:LRA=11", "-shortest", "-movflags", "+faststart", str(final)], check=True)
    silent.unlink(missing_ok=True)
    print(final)
    return final


if __name__ == "__main__":
    render(Path(sys.argv[1]), sys.argv[2], "--stills" in sys.argv)
