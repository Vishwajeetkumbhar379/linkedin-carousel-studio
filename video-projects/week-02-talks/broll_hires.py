"""Re-cut each archive B-roll pick from its Internet Archive source film at 640x480 (the archive site serves 320x240).

    python3 video-projects/week-02-talks/broll_hires.py

broll/credits.json names each pick's film and its in and out points; IA_IDS maps the film to its Prelinger item
(public domain). The films are fetched with curl (ffmpeg can't use the proxy) and deleted after. The cut is checked against the site's own clip (first-frame correlation) so the timing matches.
Writes broll/<name>_hd.mp4 and adds the Internet Archive item to the credit.
"""
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
B = HERE / "broll"
SRC = B / "_src"
IA_IDS = {"Flying the Lindbergh Trail (Part I)": "Flyingth1937", "Flying the Lindbergh Trail (Part II)": "Flyingth1937_2",
          "Journalism": "Journali1940", "RCA Presentation: Television, An": "RCAPrese1939",
          "Sound And The Story": "SoundAndTheS", "California Picture Book": "Californ1946"}


def frame(src: str, t: float, size=(160, 120)) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", src, "-frames:v", "1", "-vf", f"scale={size[0]}:{size[1]},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(size[1], size[0]).astype(np.float32) if len(raw) == size[0] * size[1] else None


def corr(a, b) -> float:
    a, b = a - a.mean(), b - b.mean()
    return float((a * b).sum() / (np.sqrt((a * a).sum() * (b * b).sum()) + 1e-6))


if __name__ == "__main__":
    cred = json.loads((B / "credits.json").read_text())
    SRC.mkdir(exist_ok=True)
    for name, c in cred.items():
        if (B / f"{name}_hd.mp4").exists() and "hd" in c:
            continue
        ident = IA_IDS[c["film"]]
        url = str(SRC / f"{ident}.mp4")
        if not Path(url).exists():  # ffmpeg can't use the session proxy, so curl fetches the film first (deleted after)
            subprocess.run(["curl", "-sS", "-L", "-m", "900", "-o", url, f"https://archive.org/download/{ident}/{ident}.mp4"], check=True)
        a, b = c["at"]
        ref = frame(str(B / f"{name}.mp4"), 0.5)
        # find the offset between the two transfers: try the site's time, then nudge by up to 1.5 s
        best = max(((corr(ref, f), d) for d in np.arange(-1.5, 1.51, 0.1) if (f := frame(url, a + 0.5 + d)) is not None), default=(0, 0))
        off = best[1] if best[0] > 0.6 else 0.0
        out = B / f"{name}_hd.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a + off:.3f}", "-i", url, "-t", f"{b - a:.3f}", "-an", "-c:v", "libx264", "-crf", "12", "-preset", "slow", str(out)], check=True)
        c["hd"] = {"internet_archive": f"https://archive.org/details/{ident}", "file": f"{ident}.mp4", "offset_s": round(float(off), 2), "match": round(best[0], 3)}
        Path(url).unlink()  # one film on disk at a time
        print(name, ident, "match", round(best[0], 3), "offset", round(float(off), 2))
    (B / "credits.json").write_text(json.dumps(cred, indent=1))
    for f in SRC.iterdir():
        f.unlink()
    SRC.rmdir()
