"""Reel cover in the framed-print style (Week 2 cover, v12 standard): a line on top, Vish's sharpest real frame as a print
in a sleeve, three stickers, a serif line with one amber italic phrase. Navy for every talking reel, so the grid reads as one.

    python scripts/print_cover.py --frames="video-projects/week-02-episode/work_friction/fr/s_IMG_8742_*" --top="Before you jump in" \
        --bottom="reduce <i>friction.</i>" --tags="Profiles|Portfolio|Plan" --out=video-projects/week-02-episode/out/friction-cover.jpg

The photo is the sharpest face among the graded frames (no captions on them), cropped around the face. Never generated.
"""
from __future__ import annotations

import glob
import sys
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "reel_edit"))
from safe_zones import faces  # noqa: E402

POS = [("left:86px;top:500px;transform:rotate(-7deg);padding:14px 26px", ""), ("left:600px;top:1150px;transform:rotate(6deg);padding:14px 26px", " ac"),
       ("left:118px;top:1372px;transform:rotate(-3deg);padding:14px 26px", "")]


def photo(pattern: str, out: Path) -> None:
    files = sorted(f for d in glob.glob(pattern) for f in sorted(glob.glob(d + "/*.jpg"))[::3])
    best, pick = -1.0, None
    for f in files:
        img = cv2.imread(f)
        fs = faces(img)
        if not fs:
            continue
        x0, y0, x1, y1 = max(fs, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))
        sharp = cv2.Laplacian(cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
        score = sharp * min(1.0, (x1 - x0) / 300)  # sharp, and big enough to read in the grid
        if score > best:
            best, pick = score, (img, (x0, y0, x1, y1))
    img, (x0, y0, x1, y1) = pick
    h, w = img.shape[:2]
    cw = min(w, int((x1 - x0) * 2.6))
    ch = min(h, int(cw * 1000 / 780))
    cw = int(ch * 780 / 1000)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    left = max(0, min(w - cw, cx - cw // 2))
    top = max(0, min(h - ch, cy - int(ch * .36)))
    cv2.imwrite(str(out), img[top:top + ch, left:left + cw], [cv2.IMWRITE_JPEG_QUALITY, 95])


def main(a: dict) -> None:
    from playwright.sync_api import sync_playwright

    out = Path(a["out"])
    tmp = out.with_suffix(".photo.jpg")
    photo(a["frames"], tmp)
    tags = "\n".join(f'<div class="a tag{c}" style="{p}">{t}</div>' for t, (p, c) in zip(a.get("tags", "").split("|"), POS) if t)
    html = (ROOT / "templates/cover/print-cover.html").read_text()
    for k, v in {"TOP": a["top"], "BOTTOM": a["bottom"], "PHOTO": tmp.resolve().as_uri(), "TAGS": tags,
                 "TOPSIZE": a.get("topsize", "104"), "BOTSIZE": a.get("botsize", "96")}.items():
        html = html.replace("{{" + k + "}}", v)
    page = out.with_suffix(".html")
    page.write_text(html)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto(page.resolve().as_uri())
        pg.wait_for_function("window.READY === true")
        pg.evaluate("document.fonts.ready")
        pg.screenshot(path=str(out), type="jpeg", quality=94)
        b.close()
    page.unlink()
    tmp.unlink()
    print("->", out)


if __name__ == "__main__":
    main(dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--")))
