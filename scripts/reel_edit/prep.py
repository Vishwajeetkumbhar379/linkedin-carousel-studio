"""Cut the footage to the plan and matte the speaker, in one pass over the raw file.

    python scripts/reel_edit/prep.py video-projects/<slug> [--ratio=0.25] [--scale=0.5]

Reads raw/*.mov|mp4 and work/edl.json (cutplan.py). Writes, per output frame at 30 fps:
  work/frames/f_00000.jpg   the real shot (full frame, for room shots and punch-ins)
  work/cut/c_00000.webp     the speaker cut out (RGBA, Robust Video Matting, MIT, runs on CPU via onnxruntime)
  work/voice.wav            the voice cut on the same times (48 kHz), 8 ms fades at every join
Lip sync: every output frame maps to the nearest raw frame of the same source time, audio is cut sample-exact.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import soundfile as sf

FPS = 30
MODEL = Path("/home/user/models/rvm_mobilenetv3_fp32.onnx")


def src_times(edl: dict) -> list[float]:
    n = int(round(edl["duration"] * FPS))
    out = []
    for k in range(n):
        t = k / FPS
        seg = max((s for s in edl["keeps"] if s["out_start"] <= t + 1e-6), key=lambda s: s["out_start"])
        st = seg["src_start"] + (t - seg["out_start"])
        out.append(min(st, seg["src_end"] - 1 / FPS))
    return out


def voice(raw: Path, edl: dict, w: Path) -> None:
    wav = w / "voice48k.wav"
    if not wav.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-ac", "1", "-ar", "48000", str(wav)], check=True)
    a, sr = sf.read(wav, dtype="float32")
    parts, fade = [], int(0.008 * sr)
    total = int(round(edl["duration"] * FPS)) * sr // FPS
    for i, s in enumerate(edl["keeps"]):
        if i:  # silence between islands (gap added by the plan)
            prev = edl["keeps"][i - 1]
            gap = s["out_start"] - (prev["out_start"] + prev["src_end"] - prev["src_start"])
            if gap > 0.001:
                parts.append(np.zeros(int(round(gap * sr)), np.float32))
        seg = a[int(round(s["src_start"] * sr)):int(round(s["src_end"] * sr))].copy()
        seg[:fade] *= np.linspace(0, 1, fade)
        seg[-fade:] *= np.linspace(1, 0, fade)
        parts.append(seg)
    v = np.concatenate(parts)
    v = np.pad(v, (0, max(0, total - len(v))))[:total]
    sf.write(w / "voice.wav", v, sr)


def main(proj: Path, ratio: float = 0.25, scale: float = 0.5, work: str = "work", src: str | None = None) -> None:
    import onnxruntime as ort

    w = proj / work
    w.mkdir(exist_ok=True)
    edl = json.loads((proj / "work" / "edl.json").read_text())
    if src:  # an already-cut A-roll (the mascot swap): frame k is output frame k, the voice is the cut voice
        raw = proj / src
        times = [k / FPS for k in range(int(round(edl["duration"] * FPS)))]
        if w != proj / "work":
            import shutil
            shutil.copy(proj / "work" / "voice.wav", w / "voice.wav")
    else:
        raw = next(p for p in (proj / "raw").iterdir() if p.suffix.lower() in (".mov", ".mp4", ".m4v"))
        voice(raw, edl, w)
        times = src_times(edl)
    (w / "frames").mkdir(exist_ok=True)
    (w / "cut").mkdir(exist_ok=True)
    cap = cv2.VideoCapture(str(raw))
    fps = cap.get(cv2.CAP_PROP_FPS)
    want: dict[int, list[int]] = {}
    for k, t in enumerate(times):
        want.setdefault(int(round(t * fps)), []).append(k)
    sess = ort.InferenceSession(str(MODEL), providers=["CPUExecutionProvider"])
    rec = [np.zeros([1, 1, 1, 1], np.float32)] * 4
    dr = np.array([ratio], np.float32)
    last = max(want)
    i, prev_idx, done = 0, None, 0
    while i <= last:
        ok, bgr = cap.read()
        if not ok:
            break
        if i in want:
            if src and bgr.shape[:2] != (1920, 1080):
                bgr = cv2.resize(bgr, (1080, 1920), interpolation=cv2.INTER_LANCZOS4)
            h, wd = bgr.shape[:2]
            small = cv2.resize(bgr, (int(wd * scale) // 2 * 2, int(h * scale) // 2 * 2), interpolation=cv2.INTER_AREA)
            if prev_idx is not None and i - prev_idx > 3:  # jumped over a cut: let the state settle on this frame
                for _ in range(2):
                    _, _, *rec = sess.run(None, {"src": (small[:, :, ::-1].transpose(2, 0, 1)[None] / 255).astype(np.float32),
                                                 "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3], "downsample_ratio": dr})
            fgr, pha, *rec = sess.run(None, {"src": (small[:, :, ::-1].transpose(2, 0, 1)[None] / 255).astype(np.float32),
                                             "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3], "downsample_ratio": dr})
            alpha = cv2.resize(pha[0, 0], (wd, h), interpolation=cv2.INTER_CUBIC)
            alpha = np.clip(alpha, 0, 1)
            rgba = np.dstack([bgr, (alpha * 255).astype(np.uint8)])
            for k in want[i]:
                cv2.imwrite(str(w / "frames" / f"f_{k:05d}.jpg"), bgr, [cv2.IMWRITE_JPEG_QUALITY, 90])
                cv2.imwrite(str(w / "cut" / f"c_{k:05d}.webp"), rgba, [cv2.IMWRITE_WEBP_QUALITY, 88])
            done += 1
            prev_idx = i
            if done % 100 == 0:
                print(f"{done}/{len(want)} frames", flush=True)
        i += 1
    meta = {"frames": len(times), "fps": FPS, "duration": len(times) / FPS, "src_fps": fps}
    (w / "prep.json").write_text(json.dumps(meta))
    print("prep done", meta)


if __name__ == "__main__":
    args = dict(a[2:].split("=") for a in sys.argv[2:] if a.startswith("--"))
    main(Path(sys.argv[1]), float(args.get("ratio", 0.25)), float(args.get("scale", 0.5)), args.get("work", "work"), args.get("src"))
