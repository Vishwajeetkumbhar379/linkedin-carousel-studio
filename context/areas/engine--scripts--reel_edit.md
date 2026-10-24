# engine/scripts/reel_edit

Create, edit, and render talking‑head reels from raw footage, applying cuts, grading, and quality checks.

- `scripts/reel_edit/aroll.py`: Creates A-roll MP4 from frames and voice using ffmpeg, optional time slice, outputs file path.
- `scripts/reel_edit/broll_prep.py`: Extracts B-roll clips per broll.json into frame sequences via ffmpeg, writes index.json with frame count and dimensions. (uses broll.json)
- `scripts/reel_edit/coach.py`: Generates delivery report from edl.json and optional shoot sheet, computes pace, gaps, retakes, writes out/delivery.md. (uses cutplan.py)
- `scripts/reel_edit/cover.py`: Creates reel cover images with punch or minimal style, adding hook, badge, tiles, and face cut‑out. (uses render3d.py, cover.html)
- `scripts/reel_edit/cutplan.py`: Plans cuts for talking‑head clips, removes dead air and fillers, outputs edl.json with keep segments and reasons. (uses transcribe.py, EDITING-PLAYBOOK.md)
- `scripts/reel_edit/film.py`: Applies a film‑grade LUT to phone footage, adjusting tone, color, light, optics, and adding grain.
- `scripts/reel_edit/grade.py`: Runs quick ffmpeg‑based color looks on iPhone clips, tone‑maps HDR to SDR and writes preview strips.
- `scripts/reel_edit/make.py`: Orchestrates the full reel pipeline: transcribe, cutplan, coach, prep, render, producing 9:16 and 4:5 layouts. (uses transcribe.py, coach.py, cutplan.py, transcript.json)
- `scripts/reel_edit/prep.py`: Cuts footage per edl, generates speaker cut‑out, voice audio, and per‑frame images for rendering. (uses cutplan.py)
- `scripts/reel_edit/qa.py`: Quality‑checks rendered reels: re‑transcribes, compares words, verifies loudness, and reports mismatches.
- `scripts/reel_edit/render.py`: Renders talking‑head reels in 9:16 and 4:5 layouts from layers, outputs video, mix audio, stills, and spec. (uses render3d.py, sfx.py, prep.py, make.py, broll_prep.py, transcript.json)
- `scripts/reel_edit/transcribe.py`: Transcribes video to 16kHz WAV and JSON transcript using faster-whisper; outputs work/audio16k.wav and work/transcript.json. (uses cutplan.py, transcript.json)
