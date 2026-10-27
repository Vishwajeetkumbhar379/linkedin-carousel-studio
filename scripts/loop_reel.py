"""Short loop reel (6 to 12 s): one real clip of Vish, one line of text in the brand type, no music baked in
(Vish adds the trending song in the app). Reach tests from footage we already have (CONTENT-OS, short loops).

    python scripts/loop_reel.py <clip> <start> <dur> <look> <out.mp4> --text="220 rejections later. <i>Still showing up.</i>" [--y=330]
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "reel_edit"))
from film import chain  # noqa: E402

TPL = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:IS;src:url(file://%(f)s/instrument-serif-latin-400-normal.woff2)}
@font-face{font-family:IS;font-style:italic;src:url(file://%(f)s/instrument-serif-latin-400-italic.woff2)}
html,body{margin:0;width:1080px;height:1920px;background:transparent}
div{position:absolute;left:70px;right:70px;top:%(y)spx;text-align:center;font:400 96px/1.04 IS;color:#fff;
text-shadow:0 4px 30px rgba(0,0,0,.55),0 2px 6px rgba(0,0,0,.5)}
i{color:#E7A15A}</style></head><body><div>%(t)s</div></body></html>"""


def main(src, start, dur, look, out, text, y="330"):
    from playwright.sync_api import sync_playwright
    out = Path(out).resolve()
    work = out.with_suffix("")
    work.mkdir(parents=True, exist_ok=True)
    (work / "t.html").write_text(TPL % {"f": ROOT / "templates/fonts-extra", "y": y, "t": text})
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto((work / "t.html").as_uri())
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(300)
        pg.screenshot(path=str(work / "t.png"), omit_background=True)
        b.close()
    vf = chain(Path(src), look, work)
    vf = (vf + "," if vf else "") + "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(dur), "-i", str(src), "-loop", "1", "-i", str(work / "t.png"),
                    "-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=48000:cl=stereo",
                    "-filter_complex", f"[0:v]{vf}[v];[v][1:v]overlay=0:0:shortest=1[o]", "-map", "[o]", "-map", "2:a",
                    "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-c:a", "aac", "-t", str(dur), "-movflags", "+faststart", str(out)], check=True)
    print("->", out)


if __name__ == "__main__":
    a = sys.argv[1:6]
    opt = dict(x[2:].split("=", 1) for x in sys.argv[6:] if x.startswith("--"))
    main(*a, text=opt["text"], y=opt.get("y", "330"))
