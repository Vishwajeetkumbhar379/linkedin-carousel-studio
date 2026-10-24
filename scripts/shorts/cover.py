"""Clickbait cover for a Short: a clean frame of the episode + a provocative headline (templates/video/shorts/cover.html).

    python scripts/shorts/cover.py content/shorts/<slug> [--bg-only]

Reads script.json "cover": {"line": i, "at": 0..1 (or "t": seconds), "lines": ["CHATGPT CAN'T", "[READ]", "YOUR MESSAGE"], "kicker": "...",
"circle": {"x","y","rx","ry"}, "arrow": [x1, y1, x2, y2], "bend": px, "cam": {"p","l","f"} to override the camera on 3D pages}. [word] = the amber pill.
Needs out/shorts/<slug>/voice.json (timings). Writes out/shorts/<slug>/{cover-bg.png, cover.png}.
Rule (Vish, 24 Oct 2026): extremely provocative and attention-grabbing; nobody clicks without it. Claims must match the video.
"""
from __future__ import annotations

import base64
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from render3d import GL_ARGS, serve  # noqa: E402

HIDE = "#cap,#tag,#handle,#hud,.hl,.ov,.side,.cbub,#vig,#grain{display:none!important}"


def main(src: Path, bg_only: bool = False) -> Path:
    from playwright.sync_api import sync_playwright
    script = json.loads((src / "script.json").read_text())
    c = script["cover"]
    out = ROOT / "out" / "shorts" / script["slug"]
    v = json.loads((out / "voice.json").read_text())
    spec = {"lines": v["lines"], "duration": round(v["duration"] + 0.35, 2)}
    exe = os.environ.get("CHROMIUM_PATH") or next((p for p in ("/opt/pw-browsers/chromium",) if Path(p).exists()), None)
    with serve() as base, sync_playwright() as p:
        b = p.chromium.launch(args=GL_ARGS, executable_path=exe)
        page = b.new_page(viewport={"width": 1080, "height": 1920})
        page.goto(f"{base}/video/shorts/{script['template']}.html")
        page.wait_for_function("window.STAGE_LOADED === true", timeout=60000)
        page.evaluate("s => window.setup(s)", spec)
        page.wait_for_function("window.READY === true", timeout=60000)
        page.add_style_tag(content=HIDE)
        if c.get("cam"):
            page.evaluate("c => { window.COVER_CAM = c; }", c["cam"])
        t = c["t"] if "t" in c else (lambda ln: ln["start"] + c.get("at", 0.5) * (ln["end"] - ln["start"]))(v["lines"][c["line"]])
        page.evaluate("t => window.frame(t)", t)
        page.screenshot(path=str(out / "cover-bg.png"))
        if not bg_only:
            page.goto(f"{base}/video/shorts/cover.html")
            page.wait_for_function("window.STAGE_LOADED === true", timeout=60000)
            bg = "data:image/png;base64," + base64.b64encode((out / "cover-bg.png").read_bytes()).decode()
            ep = f"{script.get('series', 'Inside AI').upper()} · EP {script.get('episode', '')}"
            page.evaluate("c => window.setup(c)", dict(c, bg=bg, ep=ep))
            page.wait_for_function("window.READY === true", timeout=60000)
            page.screenshot(path=str(out / "cover.png"))
        b.close()
    res = out / ("cover-bg.png" if bg_only else "cover.png")
    print(res)
    return res


if __name__ == "__main__":
    main(Path(sys.argv[1]), "--bg-only" in sys.argv)
