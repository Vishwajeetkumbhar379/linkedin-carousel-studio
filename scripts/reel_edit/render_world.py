"""Render a 3D world page (templates/video/world/<name>.html: init(opt) once, render(t) per frame) to an MP4.

    python scripts/reel_edit/render_world.py templates/video/world/portal-test.html out.mp4 --dur=12 --opt='{"frames": "...", "n": 135}'

WebGL runs on SwiftShader in headless Chromium (about 0.5 s a frame at 1080x1920). Audio is muxed separately.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def render(page: Path, out: Path, dur: float, opt: dict, fps: int = 30) -> Path:
    from playwright.sync_api import sync_playwright
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(fps), "-i", "-", "-c:v", "libx264",
                           "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=["--allow-file-access-from-files", "--use-gl=angle", "--use-angle=swiftshader",
                                     "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto(f"file://{page.resolve()}")
        pg.wait_for_timeout(400)
        pg.evaluate("o => init(o)", opt)
        pg.evaluate("document.fonts.ready.then(() => true)")
        for k in range(int(dur * fps)):
            pg.evaluate("t => render(t)", k / fps)
            ff.stdin.write(pg.screenshot(type="jpeg", quality=92))
        b.close()
    ff.stdin.close()
    ff.wait()
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    o = {k.lstrip("-"): v for k, _, v in (x.partition("=") for x in a if x.startswith("--"))}
    pos = [x for x in a if not x.startswith("--")]
    print(render(Path(pos[0]), Path(pos[1]), float(o.get("dur", 10)), json.loads(o.get("opt", "{}"))))
