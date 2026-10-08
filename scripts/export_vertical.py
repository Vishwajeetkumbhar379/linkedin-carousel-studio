"""9:16 versions for Instagram Reels and YouTube Shorts, plus slide ZIPs for Instagram carousels.

    python scripts/export_vertical.py out/batch-01/<post> [...]     # any post folders; videos and carousels both work

Video: the 4:5 master (1080x1350) sits in a 1080x1920 frame over a blurred, darkened copy of itself. It is placed high
(scaled to 90%, centred, top at 190 px) so the burned-in captions land above the area Instagram and YouTube cover with buttons and the caption.
Writes <post>/video-9x16.mp4. Carousel: writes <post>/slides.zip (PNG slides in order; Instagram takes up to 20).
"""
from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

TOP = 190  # 4:5 master scaled to 90% (972x1215), centred: captions stay clear of the right-hand buttons and the bottom caption area


def vertical(post: Path) -> Path | None:
    src = post / "video.mp4"
    if not src.exists():
        return None
    dst = post / "video-9x16.mp4"
    if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
        return dst
    vf = (f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=28:2,eq=brightness=-0.22:saturation=0.8[bg];"
          f"[0:v]scale=972:1215[fg];[bg][fg]overlay=54:{TOP},format=yuv420p")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-filter_complex", vf, "-c:v", "libx264", "-preset", "medium",
                    "-crf", "19", "-c:a", "copy", "-movflags", "+faststart", str(dst)], check=True)
    return dst


def slides_zip(post: Path) -> Path | None:
    slides = sorted((post / "slides").glob("slide-*.png"))
    if not slides:
        return None
    dst = post / "slides.zip"
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_STORED) as z:
        for s in slides[:20]:
            z.write(s, s.name)
    return dst


if __name__ == "__main__":
    for a in sys.argv[1:]:
        p = Path(a)
        print(p.name, vertical(p) or slides_zip(p))
