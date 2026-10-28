"""Week 2's friction section shown, not just said: render edit/friction_insert.html over 41.0 to 64.2 s and lay it on the cut.
    python edit/friction_insert.py          -> out/week2-9x16.mp4 (the base cut is kept as work/week2-base.mp4)
Beats land on the words of the k1 line in work/timeline.json, so a new voice re-times it. Picture only; the mix stays.
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright

E = Path(__file__).resolve().parent
P = E.parent
ROOT = P.parents[1]
FPS = 30
WEAK = {"a", "the", "to", "my", "and", "of", "with", "on", "from", "for", "is", "that", "would", "they", "this", "what"}

tl = json.loads((P / "work" / "timeline.json").read_text())
W = [{"w": w["x"], "s": w["t0"], "e": w["t1"]} for w in tl["words"] if w["line"] == "k1"]
T0, T1 = round((W[0]["s"] - 0.45) * FPS) / FPS, round(tl["next"][0] * FPS) / FPS
chunks, cur = [], []
for i, w in enumerate(W):
    cur.append(w)
    end = re.search(r"[.,?!:]$", w["w"]) or i == len(W) - 1
    if end or (len(cur) >= 2 and w["w"].lower().strip(".,?!") not in WEAK) or len(cur) == 3:
        chunks.append({"s": cur[0]["s"], "e": cur[-1]["e"] + 0.15, "t": " ".join(x["w"] for x in cur).rstrip(".,")}); cur = []
for c, d in zip(chunks, chunks[1:]):
    c["e"] = min(c["e"], d["s"])

page = (E / "friction_insert.html").read_text().replace("__FONTS__", (ROOT / "templates/fonts-extra").as_uri())
page = page.replace("__DATA__", json.dumps({"words": W, "t0": T0, "t1": T1, "chunks": chunks}))
filled = E / "_friction_insert_filled.html"
filled.write_text(page)
ins = P / "work" / "friction_insert.mp4"
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "17",
                        "-pix_fmt", "yuv420p", str(ins)], stdin=subprocess.PIPE)
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1920})
    pg.goto(filled.as_uri()); pg.wait_for_timeout(700)
    for f in range(int(round((T1 - T0) * FPS))):
        pg.evaluate(f"seek({T0 + f / FPS})")
        enc.stdin.write(pg.screenshot(type="jpeg", quality=94))
    b.close()
enc.stdin.close(); enc.wait()

out = P / "out" / "week2-9x16.mp4"
base = P / "work" / "week2-base.mp4"
if not base.exists() or base.stat().st_mtime < out.stat().st_mtime - 5:
    shutil.copy2(out, base)  # the cut the engine made; the insert always goes on a clean copy
d = T1 - T0
fc = (f"[1:v]format=yuva420p,fade=t=in:st=0:d=0.25:alpha=1,fade=t=out:st={d - 0.25:.3f}:d=0.25:alpha=1,setpts=PTS+{T0}/TB[i];"
      f"[0:v][i]overlay=0:0:enable='between(t,{T0},{T1})'[v]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(base), "-i", str(ins), "-filter_complex", fc, "-map", "[v]", "-map", "0:a",
                "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-c:a", "copy", "-movflags", "+faststart", str(out)], check=True)
print("->", out, f"insert {T0:.2f} to {T1:.2f} s")
