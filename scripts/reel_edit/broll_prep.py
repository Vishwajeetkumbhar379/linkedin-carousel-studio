"""Extract the B-roll clips named in video-projects/<slug>/broll.json into frame sequences the reel page can step through.

    python scripts/reel_edit/broll_prep.py video-projects/<slug>

Each clip -> work/broll/<name>/b_00000.jpg ... at 30 fps (width w). src "raw" cuts from Vish's own take (src seconds).
Writes work/broll/index.json {name: {n, w, h}} for render.py.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    proj = Path(sys.argv[1])
    cfg = json.loads((proj / "broll.json").read_text())
    out = proj / "work" / "broll"
    out.mkdir(parents=True, exist_ok=True)
    idx = {}
    raw = next(p for p in (proj / "raw").iterdir() if p.suffix.lower() in (".mov", ".mp4", ".m4v"))
    for c in cfg["clips"]:
        src = raw if c["src"] == "raw" else proj / c["src"]
        d = out / c["name"]
        d.mkdir(exist_ok=True)
        for f in d.glob("b_*.jpg"):
            f.unlink()
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(c["in"]), "-i", str(src), "-t", str(c["dur"]),
                        "-vf", f"fps=30,scale={c.get('w', 1280)}:-2", "-q:v", "3", "-start_number", "0", str(d / "b_%05d.jpg")], check=True)
        frames = sorted(d.glob("b_*.jpg"))
        from PIL import Image
        w, h = Image.open(frames[0]).size
        idx[c["name"]] = {"n": len(frames), "w": w, "h": h}
        print(c["name"], idx[c["name"]])
    (out / "index.json").write_text(json.dumps(idx))
