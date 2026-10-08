"""Render a comment-gated mini guide (out/guides/<slug>/post.json) in the "Comment X to get the guide" format.

    python scripts/render_guide.py out/guides/<slug> [...]

Writes into the post folder:
  preview.png     the LinkedIn / Instagram image: the guide open in a document viewer with a comment banner
  slides/*.png    the mini-guide pages (1080x1350), slides.zip for an Instagram carousel
  guide.pdf       the same pages as a PDF (LinkedIn document post, or the file to send to commenters)
  caption.md, first-comment.md   post text and sources, plus the full-guide link on buildwithvish
Template: templates/carousel/guide-doc.html (one art direction per comment keyword, brand fonts and violet lead).
"""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render3d import serve  # noqa: E402

SITE = "https://buildwithvish.netlify.app/#read-"


def render(d: Path) -> Path:
    from playwright.sync_api import sync_playwright

    post = json.loads((d / "post.json").read_text())
    (d / "slides").mkdir(exist_ok=True)
    for old in (d / "slides").glob("slide-*.png"):
        old.unlink()
    with serve() as base, sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        errs: list[str] = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(f"{base}/carousel/guide-doc.html")
        pg.wait_for_function("window.STAGE_LOADED === true")
        pg.evaluate("document.fonts.ready")
        pg.evaluate("p => window.setup(p)", post)
        pg.wait_for_function("window.READY === true")
        pg.wait_for_timeout(900)
        if errs:
            raise RuntimeError(errs)
        shots = []
        for i, el in enumerate(pg.query_selector_all("#deck > .slide")):
            f = d / "slides" / f"slide-{i + 1:02d}.png"
            el.screenshot(path=str(f))
            shots.append(f)
        pg.query_selector("#deck > .preview").screenshot(path=str(d / "preview.png"))
        b.close()
    ims = [Image.open(f).convert("RGB") for f in shots]
    ims[0].save(d / "guide.pdf", save_all=True, append_images=ims[1:], resolution=150)
    with zipfile.ZipFile(d / "slides.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.write(d / "preview.png", "slide-00-cover.png")
        for f in shots:
            z.write(f, f.name)
    link = SITE + post["slug"]
    (d / "caption.md").write_text(post["caption"].strip() + "\n")
    srcs = "\n".join(f"- {s.get('what', '')}: {s['url']} (checked {s.get('checked', '')})" for s in post.get("sources", []))
    fc = post.get("first_comment", "")
    fc = fc if isinstance(fc, str) else "\n".join(fc if isinstance(fc, list) else [str(fc)])
    (d / "first-comment.md").write_text(f"Full guide (free): {link}\n\n{fc}\n\nSources:\n{srcs}\n")
    (d / "guide.md").write_text(f"# {post['title']}\n\nSend this to everyone who comments {post['keyword']}:\n\n{link}\n\nPDF version: guide.pdf in this folder.\n")
    print(f"{d.name}: {len(shots)} pages, preview.png, guide.pdf, slides.zip -> {link}")
    return d / "preview.png"


if __name__ == "__main__":
    for a in sys.argv[1:]:
        render(Path(a))
