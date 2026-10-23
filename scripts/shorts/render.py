"""Render a Short: templates/video/shorts/<template>.html + out/shorts/<slug>/voice.{wav,json} -> video.mp4 (1080x1920, 30 fps).

    python scripts/shorts/render.py content/shorts/<slug> [--stills] [--jobs=4] [--mix-only]

--mix-only reuses video-silent.mp4 and only redoes the sound (after a new voice or SFX change).

The page exposes setup(spec) / frame(t) and publishes window.SFX = [{t, s}]. Frames are captured in parallel
browser workers (each renders a contiguous chunk), joined, then mixed with the voice, SFX and the bed.
Writes out/shorts/<slug>/{stills/*.png, video.mp4, cover.png}.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import soundfile as sf

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from render3d import GL_ARGS, serve  # noqa: E402
import sound  # noqa: E402

FPS = 30
W, H = 1080, 1920


def _page(p, base: str, template: str, spec: dict):
    exe = os.environ.get("CHROMIUM_PATH") or next((c for c in ("/opt/pw-browsers/chromium",) if Path(c).exists()), None)
    b = p.chromium.launch(args=GL_ARGS, executable_path=exe)
    page = b.new_page(viewport={"width": W, "height": H})
    errs: list[str] = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.goto(f"{base}/video/shorts/{template}.html")
    page.wait_for_function("window.STAGE_LOADED === true && window.gsap", timeout=60000)
    page.evaluate("s => window.setup(s)", spec)
    page.wait_for_function("window.READY === true", timeout=60000)
    if errs:
        raise RuntimeError(errs)
    return b, page, errs


def _chunk(args) -> str:
    from playwright.sync_api import sync_playwright
    template, spec, k0, k1, outp = args
    with serve() as base, sync_playwright() as p:
        b, page, errs = _page(p, base, template, spec)
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                               "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", outp], stdin=subprocess.PIPE)
        for k in range(k0, k1):
            page.evaluate("t => window.frame(t)", k / FPS)
            ff.stdin.write(page.screenshot(type="jpeg", quality=93))
        ff.stdin.close()
        ff.wait()
        b.close()
        if errs:
            raise RuntimeError(errs)
    return outp


def render(src: Path, stills_only: bool = False, jobs: int = 4, mix_only: bool = False) -> Path:
    from playwright.sync_api import sync_playwright
    script = json.loads((src / "script.json").read_text())
    out = ROOT / "out" / "shorts" / script["slug"]
    v = json.loads((out / "voice.json").read_text())
    D = round(v["duration"] + 0.35, 2)
    spec = {"lines": v["lines"], "duration": D}
    (out / "stills").mkdir(parents=True, exist_ok=True)
    with serve() as base, sync_playwright() as p:
        b, page, _ = _page(p, base, script["template"], spec)
        events = page.evaluate("window.SFX")
        for i, ln in enumerate(spec["lines"]):
            for tag, t in (("a", ln["start"] + 0.3), ("b", (ln["start"] + ln["end"]) / 2), ("c", ln["end"] - 0.1)):
                page.evaluate("t => window.frame(t)", t)
                page.screenshot(path=str(out / "stills" / f"l{i + 1}{tag}.png"))
        page.evaluate("t => window.frame(t)", 0.0)
        page.screenshot(path=str(out / "stills" / "frame0.png"))
        page.evaluate("t => window.frame(t)", D - 1 / FPS)
        page.screenshot(path=str(out / "stills" / "last.png"))
        b.close()
    if stills_only:
        return out / "stills"
    silent = out / "video-silent.mp4"
    if not (mix_only and silent.exists()):
        _frames(script, spec, out, D, jobs)
    return _audio(out, events, D)


def _frames(script: dict, spec: dict, out: Path, D: float, jobs: int) -> None:
    n = int(D * FPS)
    cuts = [round(n * i / jobs) for i in range(jobs + 1)]
    tmp = out / ".parts"
    tmp.mkdir(exist_ok=True)
    parts = [str(tmp / f"p{i}.mp4") for i in range(jobs)]
    with ProcessPoolExecutor(jobs) as ex:
        list(ex.map(_chunk, [(script["template"], spec, cuts[i], cuts[i + 1], parts[i]) for i in range(jobs)]))
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    silent = out / "video-silent.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out / "video-silent.mp4")], check=True)
    for p in parts:
        Path(p).unlink(missing_ok=True)


def _audio(out: Path, events: list, D: float) -> Path:
    silent = out / "video-silent.mp4"

    voice, sr = sf.read(str(out / "voice.wav"), dtype="float32")
    if voice.ndim > 1:
        voice = voice.mean(axis=1)
    assert sr == sound.SR, sr
    mixed = sound.mix(voice, events, D)
    sf.write(str(out / "mix.wav"), mixed, sound.SR)
    final = out / "video.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(out / "mix.wav"), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-af", "loudnorm=I=-14:TP=-1.0:LRA=11", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(final)], check=True)
    print(final)
    return final


if __name__ == "__main__":
    jobs = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--jobs=")), 4)
    render(Path(sys.argv[1]), "--stills" in sys.argv, jobs, "--mix-only" in sys.argv)
