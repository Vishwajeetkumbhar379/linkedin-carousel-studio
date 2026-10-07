"""Render a bespoke HTML carousel (templates/carousel/<name>.html, one .slide per page) to PNG slides + PDF.

    python scripts/render_slides.py skills7 out/flagship/claude-skills
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render3d import serve  # noqa: E402


def render(name: str, out: Path) -> list[Path]:
    from playwright.sync_api import sync_playwright

    (out / "slides").mkdir(parents=True, exist_ok=True)
    paths = []
    with serve() as base, sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        pg.goto(f"{base}/carousel/{name}.html")
        pg.wait_for_function("window.READY === true")
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(800)
        for i, el in enumerate(pg.query_selector_all(".slide")):
            f = out / "slides" / f"slide-{i + 1:02d}.png"
            el.screenshot(path=str(f))
            paths.append(f)
        b.close()
    ims = [Image.open(f).convert("RGB") for f in paths]
    ims[0].save(out / "carousel.pdf", save_all=True, append_images=ims[1:], resolution=150)
    return paths


if __name__ == "__main__":
    print(len(render(sys.argv[1], Path(sys.argv[2]))), "slides")
