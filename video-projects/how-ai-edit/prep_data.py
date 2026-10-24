"""Real data the film shows, taken from the Week 1 project (the clip where Whisper heard "Rish").

    python3 video-projects/how-ai-edit/prep_data.py

- src/data/rish.json: the clip's real word times (faster-whisper) and its loudness envelope (200 per second)
- public/rish/fNN.jpg + mNN.png + oNN.png: 24 frames of the clip (0.0 to 2.4 s), their RVM mattes (the cut-out)
  and the matte's outline as a soft glowing line
- src/data/music.json: the first 6 s of the posted Week 1 reel's mix, with its real true silence (2.57 to 2.87 s)
Frames are his face, so public/rish/ stays out of git.
"""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "reel_edit"))
from film import Matte  # noqa: E402

W1 = ROOT / "video-projects" / "week-01-intro"
HERE = Path(__file__).resolve().parent
CLIP = "IMG_1597"


def envelope(wav: Path, rate: int = 200, until: float = 4.8) -> list[float]:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(wav), "-vn", "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    hop = 16000 // rate
    n = min(len(x) // hop, int(until * rate))
    rms = np.sqrt(np.array([np.mean(x[i * hop:(i + 1) * hop] ** 2) for i in range(n)]) + 1e-9)
    db = 20 * np.log10(rms)
    v = np.clip((db + 60) / 50, 0, 1)  # -60 dB .. -10 dB -> 0..1
    return [round(float(a), 3) for a in v]


def frames():
    out = HERE / "public" / "rish"
    out.mkdir(parents=True, exist_ok=True)
    src = W1 / "raw" / "intro" / f"{CLIP}.MOV"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "0", "-t", "2.4", "-i", str(src), "-vf", "scale=540:960,fps=30",
                          "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 960, 540, 3)
    mt = Matte()
    for _ in range(4):  # let the recurrent state settle on the first frame
        mt(fr[0])
    k = 0
    for i, f in enumerate(fr):
        a = mt(f)
        if i % 3:
            continue
        k += 1
        cv2.imwrite(str(out / f"f{k:02d}.jpg"), f, [cv2.IMWRITE_JPEG_QUALITY, 90])
        m = cv2.resize((np.clip(a, 0, 1) * 255).astype(np.uint8), (540, 960), interpolation=cv2.INTER_LINEAR)
        cv2.imwrite(str(out / f"m{k:02d}.png"), m)
        hard = (m > 127).astype(np.uint8) * 255
        edge = cv2.morphologyEx(hard, cv2.MORPH_GRADIENT, np.ones((5, 5), np.uint8))
        glow = cv2.max(edge, cv2.GaussianBlur(edge, (0, 0), 6) * 2)
        cv2.imwrite(str(out / f"o{k:02d}.png"), glow)
    print("frames:", k)


if __name__ == "__main__":
    words = json.loads((W1 / "work" / "intro_words.json").read_text())[CLIP]
    data = {"clip": CLIP, "words": [{"w": w["x"], "s": w["t"], "e": w["e"]} for w in words],
            "env": envelope(W1 / "work" / f"{CLIP}.wav"), "rate": 200,
            "fix": {"Rish,": "Vish,"}, "kept": [[0.0, 1.3], [1.35, 2.4]]}  # edit/week1.py, beats n1 and n1a
    (HERE / "src" / "data").mkdir(exist_ok=True)
    (HERE / "src" / "data" / "rish.json").write_text(json.dumps(data))
    print("words:", len(data["words"]), "env:", len(data["env"]))
    reel = W1 / "out" / "week1-intro-9x16.mp4"
    music = {"env": envelope(reel, 100, 6.0), "rate": 100, "silence": [2.57, 2.87]}
    (HERE / "src" / "data" / "music.json").write_text(json.dumps(music))
    frames()
