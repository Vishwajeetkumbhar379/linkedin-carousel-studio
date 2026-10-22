"""Measure a reference reel the way an editor would: every cut, the script with timings, sound hits, layout per shot.

    python scripts/research/reel_teardown.py <video.mp4> [...] --out=research/creators/teardown

Per video writes <id>/: shots.json (cut times, shot lengths), transcript.json (word times), sfx.json (onsets),
sheet_XX.jpg (one frame per shot, numbered with its start time) and strip_XX.jpg (10 fps strips of the busiest shots).
Local and free: ffmpeg scene detection, faster-whisper, numpy onsets.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont


def cuts(v: Path, thr: float = 0.22) -> list[float]:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(v), "-vf", f"select='gt(scene,{thr})',showinfo", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    import re
    return [round(float(x), 3) for x in re.findall(r"pts_time:([\d.]+)", r)]


def frame(v: Path, t: float, w: int = 240) -> Image.Image:
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(v), "-frames:v", "1", "-vf", f"scale={w}:-2", "-f", "image2pipe", "-c:v", "png", "-"],
                       capture_output=True)
    from io import BytesIO
    if not r.stdout and t > 0.2:  # past the last decodable frame: step back
        return frame(v, t - 0.2, w)
    return Image.open(BytesIO(r.stdout)).convert("RGB")


def sheet(frames: list[tuple[float, Image.Image]], cols: int, path: Path) -> None:
    w, h = frames[0][1].size
    rows = -(-len(frames) // cols)
    c = Image.new("RGB", (w * cols, (h + 22) * rows), "white")
    d = ImageDraw.Draw(c)
    for i, (t, im) in enumerate(frames):
        x, y = (i % cols) * w, (i // cols) * (h + 22)
        c.paste(im, (x, y + 22))
        d.text((x + 4, y + 4), f"{t:.2f}s", fill="black")
    c.save(path, quality=82)


def onsets(v: Path) -> list[float]:
    wav = Path("/tmp") / (v.stem + "_td.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(v), "-ac", "1", "-ar", "16000", str(wav)], check=True)
    a, sr = sf.read(wav, dtype="float32")
    hop, n = 160, 512
    frames = np.lib.stride_tricks.sliding_window_view(np.pad(a, (0, n)), n)[::hop] * np.hanning(n)
    mag = np.abs(np.fft.rfft(frames, axis=1))
    hi = mag[:, 64:].sum(1)  # >2 kHz: whooshes, clicks, pops live here more than voice
    flux = np.maximum(0, np.diff(hi, prepend=hi[0]))
    thr = np.median(flux) + 6 * np.std(flux)
    pk = [i for i in range(1, len(flux) - 1) if flux[i] > thr and flux[i] >= flux[i - 1] and flux[i] >= flux[i + 1]]
    out, last = [], -1.0
    for i in pk:
        t = i * hop / sr
        if t - last > 0.15:
            out.append(round(t, 2)); last = t
    wav.unlink()
    return out


def transcript(v: Path) -> dict:
    from faster_whisper import WhisperModel
    wav = Path("/tmp") / (v.stem + "_tr.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(v), "-ac", "1", "-ar", "16000", str(wav)], check=True)
    a, _ = sf.read(wav, dtype="float32")
    m = WhisperModel("small.en", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(a, word_timestamps=True, beam_size=5)
    words = [{"t": round(w.start, 2), "e": round(w.end, 2), "x": w.word.strip()} for s in segs for w in s.words]
    wav.unlink()
    return {"words": words, "text": " ".join(w["x"] for w in words)}


def main(v: Path, out: Path) -> None:
    d = out / v.stem
    d.mkdir(parents=True, exist_ok=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(v)], capture_output=True, text=True).stdout)
    c = [0.0] + cuts(v)
    shots = [{"t": c[i], "len": round((c[i + 1] if i + 1 < len(c) else dur) - c[i], 2)} for i in range(len(c))]
    lens = [s["len"] for s in shots]
    tr = transcript(v)
    sfx = onsets(v)
    wpm = len(tr["words"]) / max(1e-6, (tr["words"][-1]["e"] - tr["words"][0]["t"])) * 60 if tr["words"] else 0
    stats = {"duration": round(dur, 2), "shots": len(shots), "median_shot": float(np.median(lens)), "mean_shot": round(float(np.mean(lens)), 2),
             "longest_shot": max(lens), "first_cut": c[1] if len(c) > 1 else None, "wpm": round(wpm), "sfx_hits": len(sfx),
             "first_word": tr["words"][0]["t"] if tr["words"] else None}
    (d / "shots.json").write_text(json.dumps({"stats": stats, "shots": shots}, indent=1))
    (d / "transcript.json").write_text(json.dumps(tr, indent=1))
    (d / "sfx.json").write_text(json.dumps(sfx))
    # one frame per shot (a third of the way in), 8 per row, 32 per sheet
    fr = [(s["t"], frame(v, s["t"] + min(s["len"] * 0.35, 0.6))) for s in shots]
    for k in range(0, len(fr), 32):
        sheet(fr[k:k + 32], 8, d / f"sheet_{k // 32:02d}.jpg")
    # 10 fps strips of the 4 longest shots: how things move inside a shot
    for j, s in enumerate(sorted(shots, key=lambda s: -s["len"])[:4]):
        ts = np.arange(s["t"], s["t"] + min(s["len"], 2.4), 0.1)
        sheet([(t, frame(v, t, 180)) for t in ts], 12, d / f"strip_{j:02d}.jpg")
    print(v.stem, json.dumps(stats))


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    o = Path(next((x.split("=", 1)[1] for x in sys.argv[1:] if x.startswith("--out=")), "research/creators/teardown"))
    for v in a:
        main(Path(v), o)
