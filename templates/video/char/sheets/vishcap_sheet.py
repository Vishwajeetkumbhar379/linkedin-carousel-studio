"""Character sheet for the 2D cap-and-hoodie Vish (templates/video/char/vishcap.js): faces, mouths, poses, walk. Writes PNGs to argv[1]."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[4]; OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
FN = (ROOT / "templates/fonts-extra").as_uri(); JS = (ROOT / "templates/video/char/vishcap.js").read_text()
PAGE = """<!doctype html><html><head><meta charset="utf-8"><style>@font-face{font-family:IT;font-weight:700;src:url(FN/inter-tight-latin-700-normal.woff2)}
body{margin:0;background:#F1ECE3}canvas{display:block}</style></head><body><canvas id=c></canvas><script>JS</script><script>
const c=document.getElementById('c'),g=c.getContext('2d');
window.sheet=(W,H,items)=>{c.width=W;c.height=H;g.fillStyle='#F1ECE3';g.fillRect(0,0,W,H);
 g.strokeStyle='rgba(21,19,15,.06)';for(let x=0;x<W;x+=60){g.beginPath();g.moveTo(x,0);g.lineTo(x,H);g.stroke();}for(let y=0;y<H;y+=60){g.beginPath();g.moveTo(0,y);g.lineTo(W,y);g.stroke();}
 for(const it of items){g.save();g.beginPath();g.rect(it.cx,it.cy,it.cw,it.ch);g.clip();VishCap.draw(g,it);g.restore();
  g.fillStyle='#15130F';g.font='700 22px IT';g.fillText(it.label||'',it.cx+12,it.cy+30);}};
document.fonts.load('700 30px IT').then(()=>{window.READY=1});
</script></body></html>""".replace("FN", FN).replace("JS", JS)
f = OUT / "_sheet.html"; f.write_text(PAGE)
faces = ["smile", "laugh", "thought", "surprised", "skeptical", "focused", "concerned", "pleased", "wink", "neutral"]
mouths = [("rest", None), ("A", {"o": .75, "w": .6, "r": 0, "f": 0}), ("E", {"o": .35, "w": .9, "r": 0, "f": 0}), ("O", {"o": .55, "w": .2, "r": 1, "f": 0}),
          ("U", {"o": .3, "w": .1, "r": 1, "f": 0}), ("M", {"o": 0, "w": .5, "r": 0, "f": 0}), ("F", {"o": .2, "w": .6, "r": 0, "f": 1}), ("blink", None)]
poses = ["rest", "explain", "point_up", "point_left", "point_right", "present", "think", "arms", "thumbs", "wave"]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1600, "height": 1200}); pg.goto(f.as_uri()); pg.wait_for_function("window.READY")
    W, cw, ch = 5 * 320, 320, 380
    items = [dict(cx=(i % 5) * cw, cy=(i // 5) * ch, cw=cw, ch=ch, label=e, expr=e, x=(i % 5) * cw + cw / 2, y=(i // 5) * ch + 1240 * 0.62 - 380 + 470, s=0.62, t=0.0) for i, e in enumerate(faces)]
    for it in items: it["y"] = it["cy"] + 175 + 1380 * 0.62
    pg.evaluate("a=>sheet(a[0],a[1],a[2])", [W, 2 * ch, items]); pg.locator("canvas").screenshot(path=str(OUT / "faces.png"))
    items = []
    for i, (lab, tk) in enumerate(mouths):
        it = dict(cx=(i % 4) * 400, cy=(i // 4) * 420, cw=400, ch=420, label=lab, expr="neutral", talk=tk, s=0.8, t=0.0, blink=1 if lab == "blink" else 0)
        it["x"] = it["cx"] + 200; it["y"] = it["cy"] + 190 + 1380 * 0.8; items.append(it)
    pg.evaluate("a=>sheet(a[0],a[1],a[2])", [1600, 840, items]); pg.locator("canvas").screenshot(path=str(OUT / "mouths.png"))
    items = []
    for i, ps in enumerate(poses):
        it = dict(cx=(i % 5) * 320, cy=(i // 5) * 560, cw=320, ch=560, label=ps, pose=ps, expr=None, s=0.3, t=0.3)
        it["x"] = it["cx"] + 160; it["y"] = it["cy"] + 540; items.append(it)
    pg.evaluate("a=>sheet(a[0],a[1],a[2])", [1600, 1120, items]); pg.locator("canvas").screenshot(path=str(OUT / "poses.png"))
    items = []
    for i in range(6):
        it = dict(cx=i * 266, cy=0, cw=266, ch=560, label=f"walk {i}", pose="rest", walk=i * 3.1416 / 3, dir=1, s=0.3, t=i * 0.1)
        it["x"] = it["cx"] + 133; it["y"] = 540; items.append(it)
    pg.evaluate("a=>sheet(a[0],a[1],a[2])", [1600, 560, items]); pg.locator("canvas").screenshot(path=str(OUT / "walk.png"))
    b.close()
print("ok", OUT)
