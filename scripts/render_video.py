"""Render a deterministic HTML/Three.js video template to MP4 (H.264, yuv420p) with ffmpeg.

    python scripts/render_video.py out/<post>/video.json            # full render
    python scripts/render_video.py out/<post>/video.json --stills   # poster frames only

The page exposes window.setup(spec) and window.frame(t); every frame is a pure function of t,
so renders are reproducible and can be split across machines.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render3d import GL_ARGS, serve  # noqa: E402


def render(spec_path: Path, stills_only: bool = False) -> Path:
    from playwright.sync_api import sync_playwright

    spec = json.loads(spec_path.read_text())
    post = spec_path.parent
    fps, dur = spec.get("fps", 30), spec["duration"]
    w, h = spec.get("width", 1080), spec.get("height", 1350)
    out = post / "video.mp4"
    with serve() as base, sync_playwright() as p:
        b = p.chromium.launch(args=GL_ARGS)
        page = b.new_page(viewport={"width": w, "height": h})
        errs: list[str] = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto(f"{base}/{spec['template']}")
        page.wait_for_function("window.STAGE_LOADED === true", timeout=60000)
        page.evaluate("s => window.setup(s)", spec)
        page.wait_for_function("window.READY === true", timeout=60000)
        if errs:
            raise RuntimeError(errs)
        (post / "frames").mkdir(exist_ok=True)
        for name, t in spec.get("posters", {}).items():
            page.evaluate("t => window.frame(t)", t)
            page.screenshot(path=str(post / "frames" / f"{name}.png"))
        if not stills_only:
            ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
                                   "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)],
                                  stdin=subprocess.PIPE)
            for k in range(int(dur * fps)):
                page.evaluate("t => window.frame(t)", k / fps)
                ff.stdin.write(page.screenshot(type="jpeg", quality=95))
                if k % (fps * 5) == 0:
                    print(f"  {k / fps:.0f}s / {dur}s", flush=True)
            ff.stdin.close()
            ff.wait()
            if (post / "voice.wav").exists():  # mux the voiceover (AAC 192k), keep video stream as is
                silent = out.with_suffix(".silent.mp4")
                out.rename(silent)
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(post / "voice.wav"), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                                "-shortest", "-movflags", "+faststart", str(out)], check=True)
                silent.unlink()
        b.close()
    return out


if __name__ == "__main__":
    print(render(Path(sys.argv[1]), "--stills" in sys.argv))
