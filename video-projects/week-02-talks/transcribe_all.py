"""Transcribe every clip in raw/ (faster-whisper small, local) and save thumbnails, for the content plan.

    python3 video-projects/week-02-talks/transcribe_all.py

work/transcripts.json: {clip: {dur, text, words: [{w, s, e}]}}; work/thumbs/<clip>_<k>.jpg at 15/50/85%.
"""
import json
import subprocess
from pathlib import Path

from faster_whisper import WhisperModel
import soundfile as sf

HERE = Path(__file__).resolve().parent
RAW, WORK = HERE / "raw", HERE / "work"
(WORK / "thumbs").mkdir(parents=True, exist_ok=True)
m = WhisperModel("small", device="cpu", compute_type="int8")
out = {}
for f in sorted(RAW.glob("*.MOV")):
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)], capture_output=True, text=True).stdout)
    for k, p in enumerate((0.15, 0.5, 0.85)):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{dur * p:.2f}", "-i", str(f), "-frames:v", "1", "-vf", "scale=-2:480", str(WORK / "thumbs" / f"{f.stem}_{k}.jpg")], check=True)
    wav = WORK / f"{f.stem}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-ac", "1", "-ar", "16000", str(wav)], check=True)
    a, _ = sf.read(wav, dtype="float32")
    segs, info = m.transcribe(a, word_timestamps=True, beam_size=5, condition_on_previous_text=False, vad_filter=True)
    words, text = [], []
    for s in segs:
        text.append(s.text.strip())
        words += [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for w in (s.words or [])]
    out[f.stem] = {"dur": round(dur, 2), "lang": info.language, "text": " ".join(text), "words": words}
    print(f.stem, round(dur, 1), info.language, "|", " ".join(text)[:200], flush=True)
(WORK / "transcripts.json").write_text(json.dumps(out, indent=1))
