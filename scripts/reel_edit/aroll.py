"""Write the cut A-roll (real footage, cut to the plan, with the cut voice) as one MP4, optionally a time slice.

    python scripts/reel_edit/aroll.py video-projects/<slug> [--from=0 --to=6.6 --out=work/aroll-hook.mp4]

Used as the driving video for the mascot version (character swap keeps every gesture and lip movement).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    proj = Path(sys.argv[1])
    a = dict(x[2:].split("=", 1) for x in sys.argv[2:] if x.startswith("--"))
    w = proj / "work"
    meta = json.loads((w / "prep.json").read_text())
    t0, t1 = float(a.get("from", 0)), float(a.get("to", meta["duration"]))
    f0, f1 = int(round(t0 * 30)), int(round(t1 * 30))
    out = proj / a.get("out", "work/aroll.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-start_number", str(f0), "-i", str(w / "frames" / "f_%05d.jpg"),
                    "-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}", "-i", str(w / "voice.wav"), "-frames:v", str(f1 - f0),
                    "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    print(out)
