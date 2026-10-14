"""Check a rendered talking reel: every word whole, loudness, length, layouts present.

    python scripts/reel_edit/qa.py video-projects/<slug>

Re-transcribes the delivered 9:16 file and compares it with the kept words (EDITING-PLAYBOOK: "every word whole").
"""
from __future__ import annotations

import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

if __name__ == "__main__":
    from faster_whisper import WhisperModel

    proj = Path(sys.argv[1])
    out = proj / "out"
    files = {l: out / f"{proj.name}-{l}.mp4" for l in ("9x16", "4x5", "16x9")}
    ok = True
    for l, f in files.items():
        if not f.exists():
            print("MISSING", f); ok = False; continue
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height:format=duration", "-of", "json", str(f)], capture_output=True, text=True)
        d = json.loads(r.stdout)
        print(f"{l}: {d['streams'][0]['width']}x{d['streams'][0]['height']} {float(d['format']['duration']):.2f}s")
    f = files["9x16"]
    wav = out / "qa16k.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-ac", "1", "-ar", "16000", str(wav)], check=True)
    lo = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(f), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = re.findall(r"I:\s+(-?[\d.]+) LUFS", lo)[-1]
    P = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", lo)[-1]
    print(f"loudness {I} LUFS, true peak {P} dBFS", "OK" if abs(float(I) + 14) <= 1 and float(P) <= -1.0 else "CHECK")
    a, _ = sf.read(wav, dtype="float32")
    m = WhisperModel("small.en", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(a, word_timestamps=True, beam_size=5)
    heard = [re.sub(r"[^a-z0-9']", "", w.word.lower()) for s in segs for w in s.words]
    edl = json.loads((proj / "work" / "edl.json").read_text())
    want = [re.sub(r"[^a-z0-9']", "", x["text"].lower()) for k in edl["keeps"] for x in k["w"]]
    sm = difflib.SequenceMatcher(None, want, heard)
    miss = [(op, want[i1:i2], heard[j1:j2]) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"]
    print(f"words: {len(want)} kept, {len(heard)} heard, match {sm.ratio():.0%}")
    for x in miss:
        print("  diff:", x)
    wav.unlink()
