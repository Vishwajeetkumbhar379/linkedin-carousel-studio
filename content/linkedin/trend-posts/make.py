"""Trend image posts for LinkedIn (and Instagram): a still (1080 x 1350) and a 7-second animated version of the same hook.
    python make.py      -> <name>.png, <name>.mp4
Facts are checked and dated in sources.txt (all within 14 days of 28 Oct 2026). Vish's mascot is the real 3D pack.
"""
import json, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

H = Path(__file__).resolve().parent; ROOT = H.parents[2]; FN = (ROOT / "templates/fonts-extra").as_uri(); PK = (ROOT / "brand/avatar/pack").as_uri()
POSTS = [
 {"name": "opus-55-limits", "bg": "#0B0B0D", "fg": "#F5F3EE", "accent": "#E7A15A", "kicker": "NEW TODAY · 28 OCT 2026",
  "big": "−40%", "count": [0, -40, "", "%"], "line": "Claude just got cheaper.<br><i>And your limits just got reset.</i>",
  "sub": "Claude Opus 5.5 costs 40% less than Opus 5 on typical work, writes 30% faster, and paid plans get higher five-hour limits.",
  "widget": "limit", "mascot": "03_gestures/08_thumbs_up.png"},
 {"name": "agent-skills-280m", "bg": "#F1ECE3", "fg": "#15130F", "accent": "#D9473A", "kicker": "AI NEWS · 22 OCT 2026",
  "big": "280M", "count": [0, 280, "", "M"], "line": "installs of one tiny file:<br><i>SKILL.md</i>",
  "sub": "1 million skills published. Now an open standard under the Linux Foundation, used by ChatGPT, Cursor, GitHub Copilot, VS Code and 70+ more.",
  "widget": "folder", "mascot": "03_gestures/01_point_screen_left.png"},
 {"name": "instagram-90-min", "bg": "#E8231C", "fg": "#FFFDF8", "accent": "#0B0B0D", "kicker": "INSTAGRAM · 26 OCT 2026",
  "big": "90 min", "count": [0, 90, "", " min"], "line": "Instagram is testing<br><i>90-minute videos.</i>",
  "sub": "Horizontal, long-form, called Features. Select US creators for now. Here is what changes for brand deals.",
  "widget": "timeline", "mascot": "02_expressions/04_surprised.png"},
]
PAGE = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:IT;font-weight:700;src:url(FN/inter-tight-latin-700-normal.woff2)}
@font-face{font-family:IT;font-weight:500;src:url(FN/inter-tight-latin-500-normal.woff2)}
@font-face{font-family:IS;src:url(FN/instrument-serif-latin-400-normal.woff2)}
@font-face{font-family:IS;font-style:italic;src:url(FN/instrument-serif-latin-400-italic.woff2)}
@font-face{font-family:GM;src:url(FN/geist-mono-latin-500-normal.woff2)}
html,body{margin:0;width:1080px;height:1350px;overflow:hidden;background:BG;color:FG;font-family:IT}
.k{position:absolute;left:72px;top:70px;font:500 28px GM;letter-spacing:.12em;opacity:.8}
.k b{display:inline-block;width:14px;height:14px;border-radius:50%;background:AC;margin-right:14px;vertical-align:2px}
.big{position:absolute;left:66px;top:150px;font:700 196px/1 IT;letter-spacing:-.04em;color:AC;font-variant-numeric:tabular-nums;white-space:nowrap}
.line{position:absolute;left:72px;right:72px;top:390px;font:700 76px/1.06 IT;letter-spacing:-.01em}
.line i{font:400 92px/1 IS;font-style:italic;color:AC}
.sub{position:absolute;left:72px;width:600px;top:640px;font:500 34px/1.38 IT;opacity:.82}
.w{position:absolute;left:72px;top:900px;width:620px;height:300px}
.m{position:absolute;right:-40px;bottom:-30px;height:MH;filter:drop-shadow(0 30px 40px rgba(0,0,0,.25))}
.foot{position:absolute;left:72px;bottom:56px;font:700 28px IT;opacity:.9}
.bar{height:46px;border-radius:23px;background:rgba(127,127,127,.25);overflow:hidden;margin-top:22px}.bar i{display:block;height:100%;width:0;background:AC;border-radius:23px}
.bl{font:500 26px GM;letter-spacing:.08em;opacity:.8}
.file{display:inline-block;margin:12px 10px 0 0;padding:12px 16px;border-radius:14px;background:rgba(127,127,127,.14);font:500 24px GM}
.folder{width:170px;height:118px;border-radius:18px;background:AC;position:relative;margin-bottom:14px}.folder:before{content:"";position:absolute;left:0;top:-26px;width:110px;height:40px;border-radius:14px 14px 0 0;background:AC}
.tl{display:flex;gap:8px;align-items:flex-end;height:200px}.tl i{flex:1;background:AC;border-radius:8px;opacity:.85}
</style></head><body>
<div class="k"><b></b>KICK</div><div class="big" id="big">BIG</div><div class="line">LINE</div><div class="sub">SUB</div><div class="w" id="w"></div>
<img class="m" src="PK/MASCOT"><div class="foot">@buildwith.vish</div>
<script>
const P = DATA, cl = (x) => Math.max(0, Math.min(1, x)), eo = (x) => 1 - Math.pow(1 - cl(x), 4);
const W = document.getElementById("w");
if (P.widget === "limit") W.innerHTML = '<div class="bl">FIVE-HOUR LIMIT</div><div class="bar"><i id="f"></i></div><div class="bl" id="lt" style="margin-top:18px">USED</div>';
if (P.widget === "folder") W.innerHTML = '<div class="folder"></div><span class="file">SKILL.md</span><span class="file">scripts/</span><span class="file">reference/</span>';
if (P.widget === "timeline") W.innerHTML = '<div class="bl">REEL vs FEATURE</div><div class="tl">' + Array.from({length: 18}, (_, i) => `<i style="height:${i === 0 ? 8 : 100}%"></i>`).join("") + '</div>';
window.seek = (t) => {
  const [a, b, pre, suf] = P.count, v = a + (b - a) * eo((t - 0.3) / 2.2), n = Math.round(v);
  document.getElementById("big").textContent = t < 0 ? P.big : `${pre}${(n < 0 ? "−" : "") + Math.abs(n).toLocaleString("en-GB")}${suf}`;
  if (P.widget === "limit") { const used = t < 3 ? eo(t / 2.6) : 1 - eo((t - 3.2) / 1.2); document.getElementById("f").style.width = `${(t < 0 ? 0.04 : used) * 100}%`; document.getElementById("lt").textContent = t < 0 || t > 3.6 ? "RESET ✓ USE IT WHENEVER" : "USED"; }
  if (P.widget === "timeline") [...W.querySelectorAll(".tl i")].forEach((b, i) => { b.style.transform = `scaleY(${t < 0 ? 1 : eo((t - 0.5 - i * 0.08) / 0.5)})`; b.style.transformOrigin = "bottom"; });
  if (P.widget === "folder") [...W.querySelectorAll(".file")].forEach((f, i) => { const q = t < 0 ? 1 : eo((t - 1.0 - i * 0.35) / 0.5); f.style.opacity = q; f.style.transform = `translateY(${(1 - q) * 30}px)`; });
};
seek(-1);
</script></body></html>"""
with sync_playwright() as p:
    b = p.chromium.launch()
    for P in POSTS:
        html = PAGE
        for k, v in {"FN": FN, "PK": PK, "BG": P["bg"], "FG": P["fg"], "AC": P["accent"], "KICK": P["kicker"], "BIG": P["big"], "LINE": P["line"], "SUB": P["sub"],
                     "MASCOT": P["mascot"], "MH": "560px" if "expressions" in P["mascot"] else "720px", "DATA": json.dumps(P)}.items():
            html = html.replace(k, v)
        f = H / f"_{P['name']}.html"; f.write_text(html)
        pg = b.new_page(viewport={"width": 1080, "height": 1350}); pg.goto(f.as_uri()); pg.wait_for_timeout(700)
        pg.screenshot(path=str(H / f"{P['name']}.png"))
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-r", "30", "-i", "-", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(H / f"{P['name']}.mp4")], stdin=subprocess.PIPE)
        for i in range(30 * 7):
            pg.evaluate(f"seek({i / 30})"); enc.stdin.write(pg.screenshot(type="jpeg", quality=92))
        enc.stdin.close(); enc.wait(); pg.close(); f.unlink()
        print(P["name"])
    b.close()
