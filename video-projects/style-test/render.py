"""Render scene.html (window.seek(t)) frame by frame over vo.mp3, with SFX on the beats. python3 render.py"""
import json, subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
H = Path(__file__).resolve().parent; SFX = H.parent / "sfx-library"; FPS = 30
W = json.loads((H / "words.json").read_text())
at = lambda w, n=0: [x["s"] for x in W if x["w"].lower().strip(".,").startswith(w)][n]
dur = W[-1]["e"] + 1.1
(H / "work").mkdir(exist_ok=True)
page = (H / "scene.html").read_text().replace("__WORDS__", json.dumps(W)).replace("📍 ", "")
(H / "work/s.html").write_text(page.replace("../../templates", "../../../templates"))
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(H / "work/pic.mp4")], stdin=subprocess.PIPE)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
    pg.goto((H / "work/s.html").as_uri()); pg.wait_for_timeout(400)
    for f in range(int(dur * FPS)):
        pg.evaluate(f"seek({f / FPS})"); enc.stdin.write(pg.screenshot(type="jpeg", quality=93))
    b.close()
enc.stdin.close(); enc.wait()
cues = [("whoosh_soft", 0.0, .5), ("pop", at("india"), .5), ("whoosh_soft", at("then") - .1, .6), ("stamp", at("cancelled"), .9), ("stamp", at("cancelled") + .18, .7),
        ("whoosh_soft", at("stuck"), .6), ("tick", at("six"), .5), ("whoosh", at("for", 2), .6), ("hit_soft", at("hell") - .05, .9)]
ins = ["-i", str(H / "vo.mp3")] + sum([["-i", str(SFX / f"{c}.mp3")] for c, _, _ in cues], [])
fl = [f"[{i + 2}:a]adelay={int(t * 1000)}|{int(t * 1000)},volume={v * 0.35}[s{i}]" for i, (_, t, v) in enumerate(cues)]
mix = "[1:a]" + "".join(f"[s{i}]" for i in range(len(cues))) + f"amix=inputs={len(cues) + 1}:normalize=0,loudnorm=I=-14:TP=-1.5[a]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(H / "work/pic.mp4"), *ins, "-filter_complex", ";".join(fl + [mix]), "-map", "0:v", "-map", "[a]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{dur:.2f}", "-movflags", "+faststart", str(H / "style-test-9x16.mp4")], check=True)
print("->", H / "style-test-9x16.mp4", f"{dur:.1f}s")
