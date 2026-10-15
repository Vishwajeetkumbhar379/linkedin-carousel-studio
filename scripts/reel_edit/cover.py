"""Reel cover (thumbnail) from the real footage: punch style (hook + key word box + face + two tiles + badge) or minimal.

    python scripts/reel_edit/cover.py video-projects/<slug> --hook="I didn't edit [this] video" --badge="FREE TOOLS · 1 COMMAND" \
        [--frame=27] [--tiles=film:EDITOR:dead,spark:CLAUDE:live] [--style=minimal --big="..." --sub="..."]

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
        spec["tiles"] = [dict(zip(("icon", "label", "state"), t.split(":"))) for t in a.get("tiles", "").split(",") if t]
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
