"""One command from raw phone clip to two edited layouts: 9:16 (Reels, Shorts) and 4:5 (LinkedIn).

    python scripts/reel_edit/make.py video-projects/<slug> [--page=edit-reel] [--stills-only]

Steps: transcribe (local Whisper) -> cutplan (retakes, fillers, dead air) -> prep (cut + cut-out matte)
-> coach (out/delivery.md) -> render (9:16, 4:5 from the same layers, voice + SFX + ducked bed at -14 LUFS).
Put caption spelling fixes in work/overrides.json {"fix": {"heard": "meant"}} and rerun from render.
The graphics page is per post (templates/video/talking/<page>.html), cued by the words in the shoot sheet.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent

if __name__ == "__main__":
    proj = sys.argv[1]
    extra = [a for a in sys.argv[2:] if a.startswith("--page=")]
    py = [sys.executable]
    if not (Path(proj) / "work" / "transcript.json").exists():
        subprocess.run(py + [str(HERE / "transcribe.py"), proj], check=True)
    subprocess.run(py + [str(HERE / "cutplan.py"), proj], check=True)
    subprocess.run(py + [str(HERE / "coach.py"), proj], check=True)
    subprocess.run(py + [str(HERE / "prep.py"), proj, "--scale=0.75"], check=True)
    if "--stills-only" in sys.argv:
        subprocess.run(py + [str(HERE / "render.py"), proj, "--stills=1,5,10,15,20,25,30,35"] + extra, check=True)
    else:
        subprocess.run(py + [str(HERE / "render.py"), proj, "mix-only"] + extra, check=True)
        procs = [subprocess.Popen(py + [str(HERE / "render.py"), proj, f"--layouts={lay}"] + extra) for lay in ("9x16", "4x5")]
        sys.exit(max(p.wait() for p in procs))
