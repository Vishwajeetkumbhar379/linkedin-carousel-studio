"""Reel cover (thumbnail) from the real footage: punch style (hook + key word box + face + two tiles + badge) or minimal.

    python scripts/reel_edit/cover.py video-projects/<slug> --hook="I didn't edit [this] video" --badge="FREE TOOLS · 1 COMMAND" \
        [--frame=27] [--tiles=film:EDITOR:dead,logo:claude:CLAUDE:live] [--style=minimal --big="..." --sub="..."]
Tiles: an icon name (film, spark, doc, chat) or logo:<simple-icons slug> for the real brand mark (allowed by Vish, 15 Oct).

Writes out/cover-9x16.png (1080x1920, key content inside the centre 1080x1440 grid crop) and out/cover-4x5.png (own layout).
Words in [brackets] get the colour box. The face is Vish's own cut-out frame, never generated.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from render3d import serve  # noqa: E402


SI = "https://cdn.jsdelivr.net/npm/simple-icons@13.21.0"
MANUAL = {  # brands Simple Icons doesn't carry: their plain marks, drawn from the official colours
    "linkedin": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect width="24" height="24" rx="4" fill="#0A66C2"/><text x="12" y="17.6" text-anchor="middle" font-family="Arial,Helvetica" font-weight="700" font-size="14" fill="#fff">in</text></svg>',
    "microsoft": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#F25022" d="M1 1h10.5v10.5H1z"/><path fill="#7FBA00" d="M12.5 1H23v10.5H12.5z"/><path fill="#00A4EF" d="M1 12.5h10.5V23H1z"/><path fill="#FFB900" d="M12.5 12.5H23V23H12.5z"/></svg>',
}


def logo(slug: str, out: Path) -> str:
    """Real brand mark as an SVG file: Simple Icons (CC0) in the brand colour, else a known plain mark. Vish allowed logos on 15 Oct."""
    import re
    import requests
    out.mkdir(parents=True, exist_ok=True)
    f = out / f"{slug}.svg"
    if f.exists():
        return f.name
    if slug in MANUAL:
        f.write_text(MANUAL[slug])
        return f.name
    r = requests.get(f"{SI}/icons/{slug}.svg", timeout=30)
    r.raise_for_status()
    data = requests.get(f"{SI}/_data/simple-icons.json", timeout=30).json()
    items = data if isinstance(data, list) else data.get("icons", [])
    hexc = next((i.get("hex") for i in items if re.sub(r"[^a-z0-9]", "", i.get("title", "").lower()) == slug or i.get("slug") == slug), "F4F5F7")
    f.write_text(r.text.replace("<path ", f'<path fill="#{hexc}" ', 1))
    return f.name


def best_frame(proj: Path, sp: dict) -> int:
    """The sharpest face in the take (no motion blur, hands out of the face), sampled every 5 frames."""
    import cv2
    import numpy as np
    P = sp["person"]
    best, bk = -1.0, 0
    for k in range(0, sp["frames"], 5):
        im = cv2.imread(str(proj / "work" / "frames" / f"f_{k:05d}.jpg"), cv2.IMREAD_GRAYSCALE)
        if im is None:
            continue
        face = im[P["top"]:P["top"] + 380, P["cx"] - 200:P["cx"] + 200]
        sharp = cv2.Laplacian(face, cv2.CV_64F).var()
        if sharp > best:
            best, bk = sharp, k
    return bk


def main(proj: Path, a: dict) -> None:
    from playwright.sync_api import sync_playwright

    spec = {"style": a.get("style", "punch"), "hook": a.get("hook", ""), "badge": a.get("badge", ""), "big": a.get("big", ""),
            "sub": a.get("sub", ""), "keyColor": a.get("key", "neon")}
    if spec["style"] == "punch":
        sp = json.loads((proj / "out" / "spec-work.json").read_text())
        k = int(a["frame"]) if "frame" in a else best_frame(proj, sp)
        spec.update(face=f"/video-projects/{proj.name}/work/cut/c_{k:05d}.webp", cx=sp["person"]["cx"], top=sp["person"]["top"])
        tiles = []
        for t in [t for t in a.get("tiles", "").split(",") if t]:
            p = t.split(":")
            if p[0] == "logo":  # logo:<slug>:LABEL:state
                tiles.append({"img": f"/video-projects/{proj.name}/out/logos/" + logo(p[1], proj / "out" / "logos"), "label": p[2], "state": p[3] if len(p) > 3 else ""})
            else:
                tiles.append(dict(zip(("icon", "label", "state"), p)))
        spec["tiles"] = tiles
    out = proj / "out"
    with serve(ROOT) as base, sync_playwright() as p:
        b = p.chromium.launch()
        for lay, h in (("9x16", 1920), ("4x5", 1350)):  # each layout laid out from the layers, never cropped
            pg = b.new_page(viewport={"width": 1080, "height": h})
            pg.goto(f"{base}/templates/video/talking/cover.html")
            pg.wait_for_function("window.READY === true")
            pg.evaluate("s => window.render(s)", dict(spec, layout=lay))
            pg.wait_for_function("window.DONE === true")
            pg.screenshot(path=str(out / f"cover-{lay}.png"))
            pg.close()
        b.close()
    print("wrote", out / "cover-9x16.png", out / "cover-4x5.png")


if __name__ == "__main__":
    args = dict(x[2:].split("=", 1) for x in sys.argv[2:] if x.startswith("--") and "=" in x)
    main(Path(sys.argv[1]), args)
