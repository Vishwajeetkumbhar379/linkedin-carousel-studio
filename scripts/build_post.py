"""Render a post folder (deck.json) to slides/*.png and carousel.pdf with the studio templates.

    python scripts/build_post.py out/2026-10-06-eu-ai-text-watermark
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from carousel.render import _merge  # noqa: E402
from carousel import aurora  # noqa: E402
from carousel.studio import H, W, render_html_page, render_slide  # noqa: E402

SEARCH = [ROOT / "templates" / "video" / "sprites" / "vish", ROOT / "out" / "_samples" / "3d", ROOT / "brand" / "mascot" / "poses-v4", ROOT / "brand" / "mascot" / "poses-v3", ROOT / "brand" / "mascot" / "poses-v2", ROOT / "brand" / "mascot" / "poses", ROOT / "brand" / "avatar"]


def find_assets(deck: dict, post: Path) -> dict:
    keys = {s.get(k) for s in deck["slides"] for k in ("hero", "mascot", "dof_hero")} - {None}
    keys |= {L["asset"] for s in deck["slides"] for L in s.get("layers", []) if L.get("asset")}
    keys |= {deck.get("cover_hero")} - {None}
    found = {}
    for k in keys:
        for d in [post / "assets", *SEARCH]:
            hits = sorted(d.glob(f"{k}*.png")) if d.exists() else []
            if hits:
                found[k] = hits[0]
                break
        else:
            raise FileNotFoundError(f"asset '{k}' not found in {[str(x) for x in SEARCH]}")
    return found


def build(post: Path) -> Path:
    from playwright.sync_api import sync_playwright

    deck = json.loads((post / "deck.json").read_text())
    assets = find_assets(deck, post)
    slides = deck["slides"]
    (post / "slides").mkdir(exist_ok=True)
    parts: list[bytes] = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": W, "height": H})
        for i, s in enumerate(slides, 1):
            html = (aurora.render_slide if deck.get("system") == "aurora" else render_slide)(s, i, len(slides), deck, assets)
            (post / "slides" / f"slide-{i:02d}.html").write_text(html) if "--keep-html" in sys.argv else None
            render_html_page(html, post / "slides" / f"slide-{i:02d}.png", parts, page)
        b.close()
    pdf = post / "carousel.pdf"
    _merge(parts, pdf)
    return pdf


if __name__ == "__main__":
    for a in [x for x in sys.argv[1:] if not x.startswith("--")]:
        print(build(Path(a)))
