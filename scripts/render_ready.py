"""Render every voiced, not-yet-rendered video in a folder (SFX mix + MP4), N at a time.

    python scripts/render_ready.py out/batch-01 [--jobs=3]
"""
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_batch as m  # noqa: E402

folder = Path(sys.argv[1])
extra = [Path(a) for a in sys.argv[2:] if not a.startswith("--")]
jobs = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--jobs=")), 3))
ready = sorted(p / "video.json" for p in [*folder.iterdir(), *extra] if (p / "voice.wav").exists() and not (p / "video.mp4").exists())
for s in ready:
    m.finish(s)
print("rendering", [s.parent.name for s in ready], flush=True)
with ThreadPoolExecutor(max_workers=jobs) as ex:
    for line in ex.map(m.render, ready):
        print(line, flush=True)
