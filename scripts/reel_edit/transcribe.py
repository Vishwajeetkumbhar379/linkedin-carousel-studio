"""Local transcription (faster-whisper small.en, free, CPU) of video-projects/<slug>/raw/*.

    python scripts/reel_edit/transcribe.py video-projects/<slug>

Writes work/audio16k.wav and work/transcript.json ({segments, words}). cutplan.py re-transcribes each speech island
on its own for exact word times, so this pass is only the overview.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import soundfile as sf

if __name__ == "__main__":
    from faster_whisper import WhisperModel

    proj = Path(sys.argv[1])
    w = proj / "work"
    w.mkdir(exist_ok=True)
    raw = next(p for p in (proj / "raw").iterdir() if p.suffix.lower() in (".mov", ".mp4", ".m4v"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-ac", "1", "-ar", "16000", str(w / "audio16k.wav")], check=True)
    a, _ = sf.read(w / "audio16k.wav", dtype="float32")
    m = WhisperModel("small.en", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(a, word_timestamps=True, beam_size=5, condition_on_previous_text=False)
    lines, words = [], []
    for s in segs:
        lines.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()})
        words += [{"text": x.word.strip(), "start": round(x.start, 3), "end": round(x.end, 3), "p": round(x.probability, 3)} for x in s.words]
    (w / "transcript.json").write_text(json.dumps({"segments": lines, "words": words}, indent=1))
    print("\n".join(f'{l["start"]:6.2f} {l["text"]}' for l in lines))
