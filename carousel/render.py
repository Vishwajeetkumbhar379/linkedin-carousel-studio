"""Render a deck (JSON) to PNG slides and one LinkedIn-ready PDF."""
from __future__ import annotations

import json
from pathlib import Path

from .templates import H, W, render_slide, validate


def render(deck: dict, out: Path, png: bool = True) -> Path:
    from playwright.sync_api import sync_playwright

    problems = validate(deck)
    if problems:
        raise ValueError("Deck fails the style rules:\n- " + "\n- ".join(problems))
    out.mkdir(parents=True, exist_ok=True)
    slides = deck["slides"]
    html = [render_slide(s, i, len(slides), deck["author"]) for i, s in enumerate(slides, 1)]
    pdf_path = out / f"{deck.get('slug', 'carousel')}.pdf"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H})
        pdfs = []
        for i, h in enumerate(html, 1):
            page.set_content(h, wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            if png:
                page.screenshot(path=str(out / f"slide-{i:02d}.png"))
            pdfs.append(page.pdf(width=f"{W}px", height=f"{H}px", print_background=True, page_ranges="1"))
        browser.close()
    _merge(pdfs, pdf_path)
    return pdf_path


def _merge(parts: list[bytes], path: Path) -> None:
    from io import BytesIO

    from pypdf import PdfReader, PdfWriter

    w = PdfWriter()
    for b in parts:
        for pg in PdfReader(BytesIO(b)).pages:
            w.add_page(pg)
    w.add_metadata({"/Title": path.stem.replace("-", " ").title()})
    with open(path, "wb") as f:
        w.write(f)


def load(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
