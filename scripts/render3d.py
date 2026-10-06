"""Render 3D stills from JSON scene specs with Three.js in headless Chromium.

    python scripts/render3d.py spec.json out.png
    python scripts/render3d.py --batch specs_dir/ out_dir/

Specs describe items from templates/three/kit.js (objects + the mascot). Output is a PNG with
alpha, rendered at 2x then downsampled for clean edges.
"""
from __future__ import annotations

import contextlib
import functools
import http.server
import json
import socketserver
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
GL_ARGS = ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]


@contextlib.contextmanager
def serve(directory: Path = TEMPLATES):
    handler = functools.partial(_Quiet, directory=str(directory))
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as httpd:
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        try:
            yield f"http://127.0.0.1:{httpd.server_address[1]}"
        finally:
            httpd.shutdown()


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def render_specs(jobs: list[tuple[dict, Path]], supersample: int = 2) -> None:
    from playwright.sync_api import sync_playwright
    from PIL import Image

    with serve() as base, sync_playwright() as p:
        browser = p.chromium.launch(args=GL_ARGS)
        for spec, out in jobs:
            w, h = spec["width"], spec["height"]
            big = dict(spec, width=w * supersample, height=h * supersample)
            page = browser.new_page(viewport={"width": big["width"], "height": big["height"]})
            errors: list[str] = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(f"{base}/three/stage.html")
            page.wait_for_function("window.STAGE_LOADED === true", timeout=60000)
            page.evaluate("s => window.setup(s)", big)
            page.wait_for_function("window.READY === true", timeout=120000)
            if errors:
                raise RuntimeError(f"{out.name}: {errors}")
            out.parent.mkdir(parents=True, exist_ok=True)
            tmp = out.with_suffix(".big.png")
            page.locator("#c").screenshot(path=str(tmp), omit_background=True)
            im = Image.open(tmp).resize((w, h), Image.LANCZOS)
            if spec.get("trim"):
                l, t_, r, b = im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
                pad = spec.get("trim_pad", 12)
                im = im.crop((max(l - pad, 0), max(t_ - pad, 0), min(r + pad, w), min(b + pad, h)))
            im.save(out)
            tmp.unlink()
            page.close()
        browser.close()


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--batch":
        src, dst = Path(argv[1]), Path(argv[2])
        jobs = [(json.loads(f.read_text()), dst / (f.stem + ".png")) for f in sorted(src.glob("*.json"))]
    else:
        jobs = [(json.loads(Path(argv[0]).read_text()), Path(argv[1]))]
    render_specs(jobs)
    for _, out in jobs:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
