"""Scripted reel: narration (Vish or his clone) + a shot plan per line (archive film and his travel footage), big
captions, source cards, brand music ducked under the voice. -14 LUFS.

    python scripts/script_reel.py video-projects/<proj>      (needs vo.mp3, vo_words.json, vo_lines_t.json, plan.json)

plan.json: {"hook": "...", "mood": "...", "key": "regex of caption words to mark amber" (optional),
            "shots": [[t0, "file", in_s, "arch"|"film"], ...] (cut on the word: t0 from vo_words.json), or
            "lines": [[["file", in_s, kind], ...], ...] (one list per spoken line, split evenly),
            "sources": [[t0, t1, "Story: ..."]]}. Archive shots are framed 4:3 in black and white with grain over a blurred fill.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "reel_edit"))
from carousel_reel import SFX, SR, compose, load  # noqa: E402
from film import chain  # noqa: E402
from voicenote_reel import CAP, chunks  # noqa: E402


def shot(src: Path, ss: float, d: float, kind: str, out: Path, work: Path):
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)],
                               capture_output=True, text=True).stdout)
    ss = max(0.0, min(ss, dur - d - 0.05))
    if kind == "arch":
        fc = (f"[0:v]split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:2,eq=brightness=-0.18[bg];"
              f"[b]scale=1080:810:force_original_aspect_ratio=increase,crop=1080:810,hue=s=0,eq=contrast=1.12,noise=alls=14:allf=t[fg];[bg]hue=s=0[bg2];[bg2][fg]overlay=0:420,fps=30,format=yuv420p")
    else:
        fc = f"[0:v]{chain(src, 'day', work)},scale=1188:2112:force_original_aspect_ratio=increase,crop=1080:1920:x='(in_w-1080)/2+t*12':y='(in_h-1920)/2',fps=30,format=yuv420p"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.2f}", "-t", f"{d:.3f}", "-i", str(src), "-filter_complex", fc, "-an",
                    "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", str(out)], check=True)


def main(proj: Path):
    import soundfile as sf
    from voicenote_reel import pngs
    plan = json.loads((proj / "plan.json").read_text())
    words = json.loads((proj / "vo_words.json").read_text())
    lines = json.loads((proj / "vo_lines_t.json").read_text())
    vo = load(proj / "vo.mp3").mean(1)
    end = len(vo) / SR + 1.2
    work = proj / "work"
    work.mkdir(exist_ok=True)
    starts = [max(0.0, ln["t0"] - 0.12) for ln in lines] + [end]
    parts, cuts = [], []
    if "shots" in plan:
        seq = plan["shots"]
    else:
        seq = [[starts[i] + (starts[i + 1] - starts[i]) * k / len(sh), *s] for i, sh in enumerate(plan["lines"]) for k, s in enumerate(sh)]
    seq[0][0] = 0.0
    bounds = [s[0] for s in seq] + [end]
    for k, (t0, f, ss, kind) in enumerate(seq):
        # frame-exact lengths, so the concat never drifts from the voice
        d = round(bounds[k + 1] * 30) / 30 - round(t0 * 30) / 30
        out = work / f"s_{hashlib.md5(repr((f, ss, round(d, 4), kind)).encode()).hexdigest()[:10]}.mp4"
        if not out.exists():  # shots are cached, so a plan tweak re-cuts only what changed
            shot(ROOT / f, ss, d, kind, out, work)
        parts.append(out)
        cuts.append(t0)
    (work / "list.txt").write_text("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(work / "list.txt"), "-c", "copy", str(work / "pic.mp4")], check=True)
    # audio: voice, ducked music, a soft whoosh on every cut
    L = int(end * SR)
    v = np.zeros(L, np.float32)
    vv = vo / (np.sqrt((vo ** 2).mean()) + 1e-9) * 0.1
    v[:len(vv)] = vv[:L]
    music = load(compose("sr-" + proj.name, end + 1, plan.get("mood", "cinematic, reflective, hopeful"))).mean(1)[:L]
    music = np.pad(music, (0, max(0, L - len(music))))
    env = np.convolve(np.abs(v), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
    duck = 1.0 - 0.7 * np.clip(env / (env.max() * 0.25 + 1e-9), 0, 1)
    mix = v + music / (np.sqrt((music ** 2).mean()) + 1e-9) * 0.065 * duck
    w = load(SFX / "whoosh_soft.mp3").mean(1)
    w = w / (np.abs(w).max() + 1e-9)
    for t in cuts[1:]:
        i0 = int(max(0, t - np.argmax(np.abs(w)) / SR) * SR)
        seg = w[:max(0, L - i0)] * 0.05
        mix[i0:i0 + len(seg)] += seg
    sf.write(str(work / "mix.wav"), np.clip(np.stack([mix, mix], 1), -1, 1), SR)
    # overlays: hook title, captions, source cards
    ch = chunks(words, re.compile(plan["key"], re.I)) if "key" in plan else chunks(words)
    items = [f'<div class="h">{plan["hook"]}</div>'] + [f'<div class="c">{c["html"]}</div>' for c in ch]
    items += [f'<div style="position:absolute;left:60px;right:60px;top:1250px;text-align:center;font:500 30px/1.3 monospace;letter-spacing:.06em;color:#E8E1D4;opacity:.85">{s[2]}</div>'
              for s in plan.get("sources", [])]
    caps = pngs(items, work)
    times = [(0, 2.8)] + [(c["t0"], c["t1"]) for c in ch] + [(s[0], s[1]) for s in plan.get("sources", [])]
    inputs = ["-i", str(work / "pic.mp4")] + sum([["-i", str(p)] for p in caps], [])
    f, last = [], "[0:v]"
    for k, (a, b) in enumerate(times):
        f.append(f"{last}[{k + 1}:v]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[v{k}]")
        last = f"[v{k}]"
    out = proj / f"{proj.name}-9x16.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-i", str(work / "mix.wav"), "-filter_complex", ";".join(f), "-map", last,
                    "-map", f"{len(caps) + 1}:a", "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-c:v", "libx264", "-crf", "21", "-maxrate", "25M", "-bufsize", "50M", "-preset", "medium",
                    "-c:a", "aac", "-b:a", "256k", "-t", f"{end:.2f}", "-movflags", "+faststart", str(out)], check=True)
    print("->", out, f"{end:.1f} s, {len(parts)} shots")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
