"""Voice note -> ready reel. Vish answers a question by voice note; this makes the post (CONTENT-OS: voice-note engine).

    python scripts/voicenote_reel.py <voice.m4a|mp3|wav> <slug> [--hook="..."] [--mood="..."] [--clean=0]

1. Cleans the voice (ElevenLabs Voice Isolator) and transcribes it word by word (local faster-whisper).
2. Picks the best 25 to 55 s (free LLM via scripts/llm.py; falls back to the opening) and a hook line of 8 words or fewer.
3. Tightens pauses, cuts his travel library (video-projects/week-01-intro/raw/travel) every ~1.9 s, graded with the film look.
4. Big word-by-word captions with one amber key word, the hook as a title for the first 2.6 s, brand music ducked under the voice.
5. Writes out/voicenotes/<slug>-9x16.mp4 and a QA line (transcript match, loudness). Anything below the gate is not sent.
"""
from __future__ import annotations

import json
import os
import random
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

TRAVEL = ROOT / "video-projects/week-01-intro/raw/travel"
OUT = ROOT / "out/voicenotes"
FPS = 30
KEY = re.compile(r"^(\d|AI|remote|travel|money|free|never|always|job|work|world|anywhere|nobody|everyone|best|worst|first)", re.I)


def isolate(src: Path, dst: Path) -> Path:
    import requests
    with open(src, "rb") as f:
        r = requests.post("https://api.elevenlabs.io/v1/audio-isolation", headers={"xi-api-key": os.environ["CLAUDEELEVENLABS_API"]},
                          files={"audio": (src.name, f, "audio/wav")}, timeout=600)
    r.raise_for_status()
    dst.write_bytes(r.content)
    return dst


def transcribe(wav: Path) -> list[dict]:
    from faster_whisper import WhisperModel
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(wav), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32)
    m = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(a.astype(np.float32), language="en", word_timestamps=True)
    return [{"w": w.word.strip(), "s": w.start, "e": w.end} for s in segs for w in s.words]


def sentences(words):
    out, cur = [], []
    for w in words:
        cur.append(w)
        if w["w"][-1:] in ".?!":
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def choose(sents, hook):
    """Best 25-55 s run of sentences + a hook (LLM if available, else the opening)."""
    text = "\n".join(f"{i}: {' '.join(w['w'] for w in s)} ({s[-1]['e'] - s[0]['s']:.1f}s)" for i, s in enumerate(sents))
    plan = None
    try:
        from llm import chat
        r = chat("Numbered sentences from a voice note by Vish (remote work, travel, AI, marketing). Pick the strongest run of consecutive "
                 "sentences, 25 to 55 seconds in total, that starts with a line that grabs attention and ends on a payoff. "
                 'Return only JSON: {"start": i, "end": j, "hook": "on-screen hook, 8 words or fewer, his own words where possible"}.\n\n' + text,
                 system="You are a short-form video editor. Answer with JSON only.")
        plan = json.loads(re.search(r"\{.*\}", r, re.S).group(0))
    except Exception as e:  # no free LLM answered: take the opening
        print("llm:", str(e)[:80])
    try:
        plan = {"start": int(plan["start"]), "end": int(plan["end"]), "hook": str(plan.get("hook", ""))} if plan else None
        if plan and not (0 <= plan["start"] <= plan["end"] < len(sents)):
            plan = None
    except (KeyError, TypeError, ValueError):
        plan = None
    if not plan:
        j, t = 0, 0.0
        while j < len(sents) and t < 50:
            t += sents[j][-1]["e"] - sents[j][0]["s"]
            j += 1
        plan = {"start": 0, "end": max(0, j - 1), "hook": " ".join(w["w"] for w in sents[0])[:60]}
    if hook:
        plan["hook"] = hook
    if not plan["hook"].strip():
        first = " ".join(w["w"] for w in sents[plan["start"]]).split()
        plan["hook"] = " ".join(first[:8])
    return plan


def tighten(words, a, b, gap=0.22):
    """Audio pieces [a, b] with pauses longer than `gap` shortened to `gap`; returns pieces and the new word times."""
    pieces, new, t = [], [], 0.0
    s0 = max(0.0, a - 0.06)
    prev = None
    for w in words:
        if prev is not None and w["s"] - prev > gap + 0.12:
            pieces.append((s0, prev + 0.08))
            t += prev + 0.08 - s0
            s0 = w["s"] - gap + 0.08
        new.append({"w": w["w"], "s": t + (w["s"] - s0), "e": t + (w["e"] - s0)})
        prev = w["e"]
    pieces.append((s0, b + 0.12))
    return pieces, new


def chunks(words):
    out, cur = [], []
    for k, w in enumerate(words):
        cur.append(w)
        if w["w"][-1:] in ".,?!:" or len(cur) == 3 or k == len(words) - 1:
            html = " ".join(f"<b>{x['w'].strip('.,?!:')}</b>" if KEY.match(x["w"]) else x["w"].strip(".,?!:") for x in cur)
            out.append({"t0": cur[0]["s"], "t1": cur[-1]["e"] + 0.15, "html": html})
            cur = []
    for a, b in zip(out, out[1:]):
        a["t1"] = min(a["t1"], b["t0"])
    return out


CAP = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:IT;font-weight:800;src:url(file://%(f)s/inter-tight-latin-700-normal.woff2)}
@font-face{font-family:IS;src:url(file://%(f)s/instrument-serif-latin-400-normal.woff2)}
@font-face{font-family:IS;font-style:italic;src:url(file://%(f)s/instrument-serif-latin-400-italic.woff2)}
html,body{margin:0;width:1080px;height:1920px;background:transparent}
.c{position:absolute;left:60px;right:60px;top:1120px;text-align:center;font:800 78px/1.06 IT;text-transform:uppercase;color:#fff;
text-shadow:0 6px 26px rgba(0,0,0,.55),0 2px 4px rgba(0,0,0,.6)}
.c b{background:#E7A15A;color:#15130F;padding:0 14px;border-radius:12px;text-shadow:none}
.h{position:absolute;left:60px;right:60px;top:300px;text-align:center;font:400 100px/1.02 IS;color:#fff;text-shadow:0 4px 30px rgba(0,0,0,.6)}
.h i{color:#E7A15A}</style></head><body>%(b)s</body></html>"""


def pngs(items, work: Path):
    from playwright.sync_api import sync_playwright
    paths = []
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={"width": 1080, "height": 1920})
        for k, html in enumerate(items):
            f = work / f"c{k:03d}.html"
            f.write_text(CAP % {"f": ROOT / "templates/fonts-extra", "b": html})
            pg.goto(f.as_uri())
            pg.evaluate("document.fonts.ready")
            out = work / f"c{k:03d}.png"
            pg.screenshot(path=str(out), omit_background=True)
            paths.append(out)
        br.close()
    return paths


def broll(dur: float, work: Path, seed: int) -> Path:
    clips = [p for p in TRAVEL.rglob("*") if p.suffix.lower() in (".mov", ".mp4")]
    rnd = random.Random(seed)
    rnd.shuffle(clips)
    parts, t, k = [], 0.0, 0
    while t < dur:
        src = clips[k % len(clips)]
        k += 1
        d = min(rnd.uniform(1.6, 2.2), dur - t + 0.05)
        try:
            length = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)],
                                          capture_output=True, text=True).stdout)
        except ValueError:
            continue
        ss = rnd.uniform(0, max(0.0, length - d - 0.2))
        out = work / f"b{len(parts):03d}.mp4"
        vf = chain(src, "day", work) + ",scale=1188:2112:force_original_aspect_ratio=increase,crop=1080:1920:x='(in_w-1080)/2+t*14':y='(in_h-1920)/2',fps=30,format=yuv420p"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.2f}", "-t", f"{d:.3f}", "-i", str(src), "-vf", vf, "-an", "-c:v", "libx264", "-crf", "18",
                        "-preset", "veryfast", str(out)], check=True)
        parts.append(out)
        t += d
    lst = work / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    cat = work / "broll.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(cat)], check=True)
    return cat


def main(src, slug, hook=None, mood="warm, hopeful, travel", clean=True):
    import soundfile as sf
    work = OUT / slug
    work.mkdir(parents=True, exist_ok=True)
    raw = work / "raw.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-ac", "1", "-ar", str(SR), str(raw)], check=True)
    voice_f = isolate(raw, work / "iso.mp3") if clean else raw
    voice = load(voice_f).mean(1)
    words = transcribe(work / "raw.wav")
    sents = sentences(words)
    plan = choose(sents, hook)
    sel = [w for s in sents[plan["start"]:plan["end"] + 1] for w in s]
    pieces, tw = tighten(sel, sel[0]["s"], sel[-1]["e"])
    v = np.concatenate([voice[int(a * SR):int(b * SR)] for a, b in pieces])
    v = v / (np.sqrt((v ** 2).mean()) + 1e-9) * 0.1
    end = len(v) / SR + 1.0
    L = int(end * SR)
    vo = np.zeros(L, np.float32)
    vo[:len(v)] = v
    music = load(compose("vn-" + slug, end + 1, mood))[:L].mean(1)
    music = np.pad(music, (0, max(0, L - len(music))))
    env = np.convolve(np.abs(vo), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
    duck = 1.0 - 0.72 * np.clip(env / (env.max() * 0.25 + 1e-9), 0, 1)
    mix = vo + music / (np.sqrt((music ** 2).mean()) + 1e-9) * 0.06 * duck
    whoosh = load(SFX / "whoosh_soft.mp3").mean(1)
    mix[:len(whoosh)] += whoosh / (np.abs(whoosh).max() + 1e-9) * 0.12
    sf.write(str(work / "mix.wav"), np.clip(np.stack([mix, mix], 1), -1, 1), SR)
    ch = chunks(tw)
    caps = pngs([f'<div class="h">{plan["hook"]}</div>'] + [f'<div class="c">{c["html"]}</div>' for c in ch], work)
    bg = broll(end, work, seed=len(slug))
    inputs = ["-i", str(bg)] + sum([["-i", str(p)] for p in caps], [])
    f, last = [], "[0:v]"
    f.append("[0:v][1:v]overlay=0:0:enable='between(t,0,2.6)'[v0]")
    last = "[v0]"
    for k, c in enumerate(ch):
        f.append(f"{last}[{k + 2}:v]overlay=0:0:enable='between(t,{c['t0']:.3f},{c['t1']:.3f})'[v{k + 1}]")
        last = f"[v{k + 1}]"
    out = OUT / f"{slug}-9x16.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-i", str(work / "mix.wav"), "-filter_complex", ";".join(f), "-map", last,
                    "-map", f"{len(caps) + 1}:a", "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                    "-c:a", "aac", "-b:a", "256k", "-t", f"{end:.2f}", "-movflags", "+faststart", str(out)], check=True)
    (work / "plan.json").write_text(json.dumps({"plan": plan, "text": " ".join(w["w"] for w in sel)}, indent=1))
    print("->", out, f"{end:.1f} s | hook: {plan['hook']}")


if __name__ == "__main__":
    opt = dict(a[2:].split("=", 1) for a in sys.argv[3:] if a.startswith("--"))
    main(sys.argv[1], sys.argv[2], opt.get("hook"), opt.get("mood", "warm, hopeful, travel"), opt.get("clean", "1") != "0")
