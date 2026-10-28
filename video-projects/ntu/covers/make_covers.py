"""Covers for Nobody Tells You EP 1 to 7: badge, a short hook, the mascot's face. Text sits inside the 4:5 grid crop (y 285 to 1635)."""
from pathlib import Path
from playwright.sync_api import sync_playwright
H = Path(__file__).resolve().parent; ROOT = H.parents[2]; FN = (ROOT / "templates/fonts-extra").as_uri(); PK = (ROOT / "brand/avatar/pack/02_expressions").as_uri()
EPS = [(1, "Nobody edited<br><i>this reel.</i>", "09_winking", "#F1ECE3"), (2, "One meeting.<br><i>Six months.</i>", "07_concerned", "#F1ECE3"),
       (3, "Bali has a<br><i>coach problem.</i>", "05_skeptical", "#E7A15A"), (4, "Confidence<br>is <i>played.</i>", "01_confident_smile", "#F1ECE3"),
       (5, "Redo it.<br><i>22 times.</i>", "04_surprised", "#F1ECE3"), (6, "Germany<br>or <i>India?</i>", "03_thoughtful", "#E7A15A"),
       (7, "Stop<br><i>hustling.</i>", "02_laughing", "#14161B")]
PAGE = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:IT;font-weight:700;src:url(FN/inter-tight-latin-700-normal.woff2)}
@font-face{font-family:IS;src:url(FN/instrument-serif-latin-400-normal.woff2)}
@font-face{font-family:IS;font-style:italic;src:url(FN/instrument-serif-latin-400-italic.woff2)}
html,body{margin:0;width:1080px;height:1920px;overflow:hidden;background:BG}
.g{position:absolute;inset:0;background-image:linear-gradient(GRID 1px,transparent 1px),linear-gradient(90deg,GRID 1px,transparent 1px);background-size:60px 60px}
.b{position:absolute;left:60px;top:320px;font:700 34px IT;letter-spacing:.12em;background:#15130F;color:#F1ECE3;padding:16px 30px;border-radius:999px}
.b b{color:#E7A15A}
.h{position:absolute;left:60px;right:40px;top:430px;font:400 178px/0.92 IS;color:FG;letter-spacing:-.01em}
.h i{color:ACC}
.m{position:absolute;left:50%;bottom:-40px;width:1000px;transform:translateX(-50%);filter:drop-shadow(0 40px 50px rgba(0,0,0,.25))}
</style></head><body><div class="g"></div><div class="b">NOBODY TELLS YOU · <b>EP N</b></div><div class="h">HOOK</div><img class="m" src="PK/FACE.png"></body></html>"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
    for n, hook, face, bg in EPS:
        dark = bg == "#14161B"
        html = PAGE
        for k, v in {"FN": FN, "PK": PK, "BG": bg, "GRID": "rgba(245,243,238,.07)" if dark else "rgba(21,19,15,.07)", "FG": "#F5F3EE" if dark else "#15130F",
                     "ACC": "#E7A15A" if dark else ("#15130F" if bg == "#E7A15A" else "#D9473A"), "EP N": f"EP {n}", "HOOK": hook, "FACE": face}.items():
            html = html.replace(k, v)
        f = H / "_c.html"; f.write_text(html); pg.goto(f.as_uri()); pg.wait_for_timeout(500)
        pg.screenshot(path=str(H / f"ntu-e{n}-cover.jpg"), type="jpeg", quality=92); print(n)
    b.close(); (H / "_c.html").unlink()
