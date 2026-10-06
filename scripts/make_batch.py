"""Turn written topics (content/batch-XX/*.json, see content/batch-01/BRIEF.md) into ready post folders.

    python scripts/make_batch.py content/batch-01            # writes out/batch-01/NN-slug/
    python scripts/make_batch.py content/batch-01 --voice    # + voices all videos (3 per Gemini request)
    python scripts/make_batch.py content/batch-01 --render   # + SFX mix, carousel PDFs, video renders (parallel)

Per post: caption.md, first-comment.md, sources.md, article.md, meta.json, and either
video.json (motion template, Vish's avatar reacting per beat) or deck.json (Aurora paper carousel).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
SITE = "https://buildwithvish.netlify.app"
SHORT = {"AI tools that change marketing work": "AI x Marketing", "Creator economy x AI": "Creator economy",
         "Real workflows and prompts": "Workflows", "Career and AI Ops pivot": "AI careers", "Contrarian takes": "Hot take"}
AV_TOP = {"hook": 180, "text": 730, "stamp": 740, "chips": 780, "stat": 185, "bars": 190, "versus": 960, "chat": 960, "feed": 640, "cta": 185}


def load(batch: Path) -> list[dict]:
    topics = []
    for f in sorted(batch.glob("*.json")):
        topics += json.loads(f.read_text())
    topics.sort(key=lambda t: -float(t.get("score", 0)))
    return topics


def sources_md(t: dict) -> str:
    rows = "\n".join(f"| {f['claim']} | {f['source_name']}: {f['url']} | {f['date']} |" for f in t.get("facts", []))
    return f"# Sources: {t['title']}\n\n| Claim | Source | Date |\n|---|---|---|\n{rows}\n"


def video_spec(t: dict) -> dict:
    beats = []
    for i, b in enumerate(t["beats"]):
        b = dict(b)
        if i == 0:
            b.pop("trans", None)
            b.setdefault("avatar", t.get("cover", {}).get("avatar", "surprised"))
            if b["avatar"] == "full":
                b["avatar"] = "point"
        av = b.get("avatar")
        if av:
            b["avTop"] = AV_TOP.get(b.get("look", "text"), 600)
            b["avSide"] = "right" if b.get("look") in ("hook", "stat", "cta") else ("left" if i % 2 else "right")
            if b.get("look") == "cta":
                b["avatar"] = "laugh"
        beats.append(b)
    if beats and beats[-1].get("look") == "cta":
        beats[-1].setdefault("button", "Follow Vish")
    return {"slug": t["slug"], "direction": "Motion graphics · beat per line · Vish avatar", "format": "video",
            "template": "video/motion.html", "width": 1080, "height": 1350, "fps": 30,
            "tag": SHORT.get(t.get("pillar"), "AI x Marketing"), "narration": t["narration"], "beats": beats,
            "duration": 36, "posters": {}, "sfx": True}


def deck_spec(t: dict) -> dict:
    slides = [dict(s) for s in t["slides"]]
    cov = slides[0]
    cov.setdefault("chip", SHORT.get(t.get("pillar"), "AI x Marketing"))
    c = t.get("cover", {})
    face = {"surprised": "surprised", "smirk": "smirk", "laugh": "laugh"}.get(c.get("avatar"), None)
    cov["mid_style"] = "justify-content:flex-start;padding-top:56px"
    cov["hero"] = c.get("hero", "c-click-v6" if "click" in json.dumps(c).lower() else "a-cover-v6")
    cov["hero_style"] = "left:150px;bottom:30px;width:780px"
    layers = []
    if c.get("avatar") == "full":
        cov["hero_style"] = "left:26px;bottom:60px;width:760px"
        layers.append({"asset": "vish-3d-full-cut", "style": "right:34px;bottom:58px;height:680px"})
    elif face:
        layers.append({"asset": f"vish-badge-{face}", "style": "left:40px;top:720px;width:210px;transform:rotate(-6deg)"})
    if c.get("label"):
        layers.append({"html": c["label"], "class": "tag dark", "style": "left:50%;top:760px;transform:translateX(-50%) rotate(-2deg)"})
    cov["layers"] = layers
    if slides[-1].get("type") == "cta":
        slides[-1].update({"mascot": "vish-badge-laugh", "mascot_style": "left:50%;transform:translateX(-50%);top:118px;width:200px", "mid_style": "padding-top:200px"})
    for s in slides[1:-1]:
        if s.get("type") == "point" and not s.get("mascot") and slides.index(s) % 3 == 1:
            s["mascot"], s["mascot_style"] = "dot-pro-wink-point", "right:90px;top:250px;width:150px"
    return {"slug": t["slug"], "direction": "Aurora Glass · paper", "format": "carousel", "pillar": t.get("pillar"),
            "author": {"name": "Vish Kumbhar", "handle": "Build with Vish"}, "site_label": "buildwithvish.netlify.app",
            "page_url": f"{SITE}/#read-{t['slug']}", "slides": slides, "system": "aurora", "variant": "paper", "seed": len(t["slug"])}


def write(batch: Path) -> list[Path]:
    name = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--out=")), batch.name)
    out = ROOT / "out" / name
    posts = []
    for n, t in enumerate(load(batch), 1):
        d = out / t["slug"]
        d.mkdir(parents=True, exist_ok=True)
        cap = t["caption"].replace("—", ",").replace("–", ",")
        (d / "caption.md").write_text(cap.strip() + "\n")
        (d / "first-comment.md").write_text(t.get("first_comment", "").strip() + "\n")
        (d / "sources.md").write_text(sources_md(t))
        (d / "article.md").write_text(f"# {t['title']}\n\n{t['article'].strip()}\n")
        (d / "meta.json").write_text(json.dumps({k: t.get(k) for k in ("slug", "format", "pillar", "score", "title", "hook", "subtitle", "cover", "site_slug")}, indent=1, ensure_ascii=False))
        if t["format"] == "video":
            spec_f = d / "video.json"
            if not spec_f.exists():
                spec_f.write_text(json.dumps(video_spec(t), indent=2, ensure_ascii=False))
        else:
            (d / "deck.json").write_text(json.dumps(deck_spec(t), indent=2, ensure_ascii=False))
        posts.append(d)
    return posts


def voice_group(specs: list[Path]) -> None:
    """Voice up to 3 videos in ONE Gemini request, then split each video out at the long pauses."""
    import numpy as np
    import soundfile as sf
    import voiceover as v

    data = [json.loads(p.read_text()) for p in specs]
    text = "\n\n<long pause>\n\n".join("\n\n".join(" ".join(sc) for sc in d["narration"]) for d in data)
    audio = v._trim(v.gemini_tts(text, v.GEMINI_VOICE, v.GEMINI_STYLE))
    flat = [p for d in data for sc in d["narration"] for p in sc]
    sf.write(specs[0].parent.parent / f"group-{specs[0].parent.name}.wav", audio, v.SR)
    bounds = v.phrase_bounds(audio, flat)
    k = 0
    for p, d in zip(specs, data):
        n = sum(len(sc) for sc in d["narration"])
        a, b = bounds[k][0], bounds[k + n - 1][1]
        k += n
        take = p.parent / "voice-take.wav"
        sf.write(take, audio[int(a * v.SR): int(b * v.SR)], v.SR)
        v.main(p, v.GEMINI_VOICE, False, False, 1.0, f"take:{take}")


def finish(spec: Path) -> None:
    d = json.loads(spec.read_text())
    B = d["beats"]
    d["duration"] = round(B[-1]["until"] + 2.8, 2)
    P = {}
    for i, b in enumerate(B):
        nxt = B[i + 1]["at"] - 0.42 if i + 1 < len(B) else d["duration"]
        P[f"b{i + 1:02d}"] = round(b["at"] + 0.8 * (nxt - b["at"]), 2)
    d["posters"] = P
    spec.write_text(json.dumps(d, indent=2, ensure_ascii=False))
    subprocess.run([sys.executable, str(ROOT / "scripts" / "sfx.py"), str(spec)], check=True)


def render(spec: Path) -> str:
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "render_video.py"), str(spec)], capture_output=True, text=True)
    return f"{spec.parent.name}: {'ok' if r.returncode == 0 else r.stderr[-400:]}"


if __name__ == "__main__":
    batch = Path(sys.argv[1])
    posts = write(batch)
    print(f"{len(posts)} posts in out/{batch.name}")
    vids = [p / "video.json" for p in posts if (p / "video.json").exists()]
    if "--voice" in sys.argv:
        todo = [s for s in vids if not (s.parent / "voice.wav").exists()]
        for i in range(0, len(todo), 3):
            grp = todo[i:i + 3]
            try:
                voice_group(grp)
                print("voiced", [g.parent.name for g in grp], flush=True)
            except Exception as e:  # noqa: BLE001
                print("voice failed", [g.parent.name for g in grp], e, flush=True)
    if "--render" in sys.argv:
        for p in posts:
            if (p / "deck.json").exists():
                subprocess.run([sys.executable, str(ROOT / "scripts" / "build_post.py"), str(p)], check=True)
        ready = [s for s in vids if (s.parent / "voice.wav").exists()]
        for s in ready:
            finish(s)
        with ThreadPoolExecutor(max_workers=int(re.sub(r"\D", "", next((a for a in sys.argv if a.startswith("--jobs=")), "--jobs=3")) or 3)) as ex:
            for line in ex.map(render, [s for s in ready if not (s.parent / "video.mp4").exists()]):
                print(line, flush=True)
