"""Week 2 of 52: "220 companies said no. So I'm building my own job." The edit, on the Week 1 engine (v12 standard).

    python edit/week2.py iso             clean his takes once with the ElevenLabs Voice Isolator (echo and room noise out)
    python edit/week2.py prep            cut + grade frames, matte and track Vish, write work/timeline.json
    python edit/week2.py stills 0.5,12   single frames to work/stills/ (layout checks)
    python edit/week2.py render [--jobs=2]   picture (Playwright -> ffmpeg), both sound mixes, both files
    python edit/week2.py mix             sound only, then both files

Vish's brief (voice note + answers, 27 Oct; content/shoot-sheets/2026-10-week-2-edit.json, key WEEK2):
- The hook has no face: huge words on his real voice, "220 companies said no. So I'm building my own job."
- He walks in at the barber, "Hi!", then the haircut fast with music; the music drops dead when he sits down.
- Two lines he didn't film are his ElevenLabs clone, always over a graphic, never over his face.
- About 40 s. Two files: out/week2-instagram-9x16.mp4 (no music: he adds "What You Waiting For?" in the app, so the reel
  joins the trending song's page) and out/week2-9x16.mp4 (our own bed, for LinkedIn and YouTube).
The picture, grade, cut-out, captions and sound engine are Week 1's (week-01-intro/edit/week1.py), reused, not copied.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

import numpy as np

P = Path(__file__).resolve().parents[1]
REPO = P.parents[1]
TALKS = P.parent / "week-02-talks"
sys.path.insert(0, str(P.parent / "week-01-intro" / "edit"))
import week1 as base  # noqa: E402

W = P / "work"
FPS, SR = base.FPS, base.SR
VOD = TALKS / "vo"
ISO = P / "work" / "iso"  # cleaned takes, shared by every edit in this project
TALK_CLIPS = {"IMG_1619", "IMG_1620", "IMG_1621", "IMG_8731", "IMG_8742", "IMG_8744"}
OUTNAME = "week2"


def _words() -> dict:
    t = json.loads((TALKS / "work" / "transcripts.json").read_text())
    return {k: [{"x": w["w"], "t": w["s"], "e": w["e"]} for w in v.get("words", [])] for k, v in t.items()}


# point the Week 1 engine at this project
base.P, base.RAW, base.W, base.OUT = P, P / "raw", W, P / "out"
base.FR, base.LUTS, base.KENNEY = W / "fr", W / "luts", P / "assets" / "kenney"
base.WORDS = _words()
base.DUR = {p.stem: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                         capture_output=True, text=True).stdout or 0) for p in (P / "raw" / "intro").glob("IMG_*.MOV")}
_audio = base.audio


def audio(src: Path) -> np.ndarray:
    """His takes come from the isolated (cleaned) audio; everything else as recorded."""
    src = Path(src)
    if src.stem in TALK_CLIPS and (ISO / f"{src.stem}.wav").exists():
        cache = W / "aud" / f"{src.stem}_iso.npy"
        if not cache.exists():
            cache.parent.mkdir(parents=True, exist_ok=True)
            raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ISO / f"{src.stem}.wav"), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                 capture_output=True, check=True).stdout
            np.save(cache, np.frombuffer(raw, np.float32))
        return np.load(cache)
    return _audio(src)


base.audio = audio

# ---------------------------------------------------------------- the cut
BEAT = 60 / 112  # the bed's tempo; the haircut cuts land on it
SHOP = [("intro/IMG_8694.MOV", 0.6), ("intro/IMG_8696.MOV", 2.0), ("intro/IMG_8696.MOV", 5.5), ("intro/IMG_8697.MOV", 0.3), ("intro/IMG_8697.MOV", 7.0)]
MONT = round(len(SHOP) * BEAT * FPS) / FPS
# In order. A take: (id, clip, runs of (from, to) word-start times kept, caption fixes, layout, look, flags).
# A clone line: (id, None, vo file in week-02-talks/vo). Layout "hide" = no picture of him (a full-screen graphic).
SEQ = [
    ("h1", "IMG_1619", [(0.9, 3.3)], {"no": "no."}, "hide", "night", {"gap": 0.45, "mute": 1}),  # the faceless hook; a beat on "no."
    ("h1b", "IMG_1619", [(3.3, 4.8)], {"so": "So"}, "hide", "night", {"gap": 0.3}),
    ("c0", "IMG_8731", [(2.1, 2.6)], {"Hi": "Hi!"}, "full", "day", {"gap": 0.75, "mute": 1, "pre": 0.45}),  # walks in + the freeze
    ("c1", "IMG_8731", [(2.7, 7.6)], {"before": "Before", "haircut": "haircut."}, "full", "day", {"gap": MONT, "mute": 1}),
    ("r1", "IMG_1619", [(5.4, 9.6)], {}, "split", "night", {"gap": 0.1}),
    ("k0", None, "WEEK2_5"),
    ("g1", "IMG_1620", [(0.0, 4.7)], {"3000": "3,000"}, "split", "night", {}),
    ("g2", "IMG_1621", [(2.7, 6.5)], {"anywhere": "anywhere."}, "split", "night", {"gap": 0.25}),
    ("f1", "IMG_8742", [(21.4, 27.6)], {"before": "Before"}, "split", "day", {"gap": 0.25}),
    ("k1", None, "WEEK2_9"),
]
NARRATOR = "WEEK2_10"  # "Next week, on Build with Vish: did reducing friction work?"
CLONE_LEAD, CLONE_TAIL = 0.35, 0.25
NEXT_LEAD, NEXT_TAIL = 0.35, 0.75


def vo_words(name: str) -> tuple[float, list]:
    j = json.loads((VOD / f"{name}.json").read_text())
    n = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(VOD / f"{name}.mp3")],
                             capture_output=True, text=True).stdout)
    return n, j["words"]


def build() -> dict:
    """His takes snapped to word boundaries at one steady speed (Week 1's rules), his clone lines in between, the card last."""
    runs, srcw, order = [], [], []
    for e in SEQ:
        if e[1] is None:
            lid, _, vo = e
            n, vw = vo_words(vo)
            runs.append({"line": lid, "clip": None, "vo": vo, "n": n, "vw": vw, "hold": 0.0})
            order.append(lid)
            continue
        lid, clip, rr, fix, lay, look, fl = e
        for k, (A, B) in enumerate(rr):
            a, b, sel = base.snap(clip, A, B)
            pre = fl.get("pre", 0.0) if k == 0 else 0.0  # picture before his first word (he walks in)
            if pre:
                a = round(max(0.0, a - pre) * FPS) / FPS
            runs.append({"line": lid, "clip": clip, "a": a, "b": b, "lay": lay, "look": look, "k": k, "hold": 0.0})
            for w in sel:
                x = fix.get(w["x"], w["x"])
                if x:
                    srcw.append({"line": lid, "x": x, "s0": max(a, w["t"]), "s1": min(b, w["e"]), "clip": clip})
        order.append(lid)
        runs[-1]["hold"] = round(fl.get("gap", 0.0) * FPS) / FPS
        runs[-1]["mute"] = bool(fl.get("mute"))
    # shots: one per take run (no joins in this edit), each mapped onto the output timeline
    t, shots, lines, words, vo = 0.0, [], {}, [], []
    for r in runs:
        if r["clip"] is None:
            t0 = t + CLONE_LEAD
            lines[r["line"]] = {"t0": t0, "t1": t0 + r["n"], "runs": [(t0, t0 + r["n"])], "clone": True}
            words += [{"line": r["line"], "x": w["w"], "t0": t0 + w["s"], "t1": t0 + w["e"]} for w in r["vw"]]
            vo.append([r["vo"], round(t0, 4)])
            t = round((t0 + r["n"] + CLONE_TAIL) * FPS) / FPS
            continue
        segs = [[0.0, round(r["b"] - r["a"], 4), 0.0, base.SPEED]]
        o = (r["b"] - r["a"]) / base.SPEED
        if r["hold"] > 0:
            segs.append([round(r["b"] - r["a"], 4), round(r["b"] - r["a"] + r["hold"], 4), round(o, 4), 1.0])
            o += r["hold"]
        dur = round(o * FPS) / FPS
        sh = {"clip": r["clip"], "a": r["a"], "b": r["b"] + r["hold"], "t0": t, "dur": dur, "segs": segs, "look": r["look"], "cut": False,
              "mute": r.get("mute", False), "lay": r["lay"], "line": r["line"], "runs": [len(shots)]}
        r["t0"], r["t1"] = t, t + (r["b"] - r["a"]) / base.SPEED
        r["hold"] = dur - (r["t1"] - t)
        L = lines.setdefault(r["line"], {"t0": r["t0"], "runs": []})
        L["runs"].append((r["t0"], r["t1"]))
        L["t1"] = r["t1"]
        for w in srcw:
            if w["clip"] == r["clip"] and w["line"] == r["line"]:
                words.append({"line": w["line"], "x": w["x"], "t0": t + (w["s0"] - r["a"]) / base.SPEED, "t1": t + (w["s1"] - r["a"]) / base.SPEED})
        shots.append(sh)
        t += dur
    nx0, nw = t, []
    if NARRATOR:  # the "Next week" card
        nn, nw = vo_words(NARRATOR)
        vo.append([NARRATOR, round(nx0 + NEXT_LEAD, 4)])
        t = nx0 + NEXT_LEAD + nn + NEXT_TAIL
    else:
        t += 0.6
    words.sort(key=lambda w: w["t0"])
    return {"runs": [r for r in runs if r["clip"]], "shots": shots, "words": words, "lines": {k: lines[k] for k in order},
            "next": (nx0, nx0 + NEXT_LEAD) if NARRATOR else None, "next_words": nw, "vo": vo, "dur": round(t * FPS) / FPS}


BROLL = TALKS / "broll"


def archive_frames(name: str, n: int) -> Path:
    """Frames of an archive B-roll clip (week-02-talks/broll/<name>_hd.mp4, public domain), cleaned up for a framed card."""
    d = W / "fr" / f"arch_{name}"
    if len(list(d.glob("*.jpg"))) < n:
        d.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(BROLL / f"{name}_hd.mp4"), "-vf",
                        f"fps={FPS},scale=960:-2:flags=lanczos,hqdn3d=2:2:3:3,unsharp=5:5:0.4:5:5:0", "-q:v", "3", str(d / "%05d.jpg")], check=True)
    return d


# ---------------------------------------------------------------- the picture + graphics
def plan(tl: dict) -> dict:
    L = tl["lines"]
    items, cues, geoms, bgs, nocap, fx = [], [], [], [], [], []
    T = lambda lid, s, end=False, nth=0: [w for w in tl["words"] if w["line"] == lid and s.lower() in w["x"].lower()][nth]["t1" if end else "t0"]  # noqa: E731

    def S(name, t, g, **o):
        fx.append([name, round(t, 3), g, o])

    def B(t0, t1, rel, src_in, look="day", kb=(1.0, 1.06), speed=1.0, fy=0.5, tx="punch"):
        src = P / "raw" / rel
        n = max(1, round((t1 - t0) * FPS)) + base.TAIL
        d = base.extract(src, src_in, n, look, "1080:-2", f"b_{Path(rel).stem}_{src_in:.2f}_{n}_{speed}", speed)
        items.append({"t0": round(t0, 4), "t1": round(t1, 4), "dir": str(d), "n": n, "kind": "broll", "geom": "full", "kb": kb, "fy": fy,
                      "src": str(src), "src_in": src_in, "speed": speed, "tx": tx, "txd": 0.22, "dx": 0.0})

    def title(t0, t1, words=None, html=None, font="serif", size=96, y=None, z=45, **k):
        cues.append({"type": "title", "t0": round(t0, 3), "t1": round(t1, 3), "words": words, "html": html, "font": font, "size": size,
                     "y": y, "band": False, "z": z, **k})

    # his takes (the hook's take is sound only: no picture is graded for it)
    for sh in tl["shots"]:
        if sh["lay"] == "hide":
            continue
        n = round(sh["dur"] * FPS) + base.TAIL
        portrait = sh["clip"].startswith("IMG_87")
        key = hashlib.md5(json.dumps(sh["segs"]).encode()).hexdigest()[:6]
        d = base.extract(P / "raw" / "intro" / f"{sh['clip']}.MOV", sh["a"], n, sh["look"], "1080:1920" if portrait else "1920:1080",
                         f"s_{sh['clip']}_{sh['a']:.3f}_{n}_{key}", matte=True, cut=False, segs=sh["segs"])
        items.append({"zc": [], "t0": round(sh["t0"], 4), "t1": round(sh["t0"] + sh["dur"], 4), "dir": str(d), "n": n, "off": 0, "kind": "talk",
                      "geom": {"full": "full", "45": "f45", "split": "split"}[sh["lay"]], "track": None, "z": 1.0, "shot": d.name})

    # ---- HOOK, no face: the words land on his voice; his real rejection emails flash behind
    geoms.append([0, "none", 0.0])
    bgs.append([0, L["c0"]["t0"], "black"])
    ws = [w for w in tl["words"] if w["line"] in ("h1", "h1b")]
    wt = lambda s: next(w for w in ws if w["x"].lower().startswith(s.lower()))  # noqa: E731
    cues.append({"type": "hook", "t0": 0.0, "t1": L["c0"]["t0"] + 0.02, "z": 45,
                 "n220": [wt("220")["t0"], wt("220")["t1"]], "companies": wt("companies")["t0"], "said": wt("said")["t0"], "no": wt("no")["t0"],
                 "so": wt("so")["t0"], "building": wt("building")["t0"], "own": wt("own")["t0"], "job": wt("job")["t0"],
                 "shots": [f"../assets/rejections/img_864{4 + k}.jpg" for k in range(4)]})
    S("thump", wt("220")["t0"], 0.28)
    for k in range(14):
        S("tick", wt("220")["t0"] + (wt("220")["t1"] - wt("220")["t0"]) * (1 - (1 - (k + 1) / 14) ** 2), 0.04, f=1.0 + 0.2 * (k % 2))
    S("thump", wt("companies")["t0"], 0.14)
    S("boom", wt("no")["t0"], 0.3)
    S("k:impact-sounds/Audio/impactMetal_heavy_002", wt("no")["t0"], 0.12)
    S("whoosh", wt("so")["t0"], 0.1)
    for k, s in enumerate(("building", "own", "job")):
        S("pop", wt(s)["t0"], 0.12, f=1.0 + 0.12 * k)
    S("boom", wt("job")["t0"] + 0.1, 0.18)
    nocap.append([0, L["c0"]["t0"]])

    # ---- "Hi!": he walks into the room and waves; the frame freezes, he becomes a sticker, the labels pop on
    geoms.append([L["c0"]["t0"], "full", 0.0])
    bgs.append([L["c0"]["t0"], 999, "ink"])
    S("whoosh", L["c0"]["t0"], 0.08)
    it = next(i for i in items if i["kind"] == "talk" and abs(i["t0"] - L["c0"]["t0"]) < 1e-3)
    tf0 = T("c0", "hi", end=True) + 0.05
    uf = L["c1"]["t0"]
    it["freeze"] = [round(tf0, 4), round(uf, 4), int((tf0 - it["t0"]) * FPS)]
    tags = [[None, "This is Vish", tf0 + 0.04, 80, 330, -4, 58], [None, "Week 2 of 52", tf0 + 0.26, 610, 1060, 3, 40]]
    cues.append({"type": "tags", "t0": tf0, "t1": uf + 0.04, "items": [[a, b, round(c, 3), x, y, r, z_] for a, b, c, x, y, r, z_ in tags], "z": 44})
    S("shutter-old", tf0, 0.12, cut=0.5)
    S("boom", tf0, 0.1)
    for k, tg in enumerate(tags):
        S("pop", tg[2], 0.12, f=1.0 + 0.1 * k)
    nocap.append([tf0, uf])

    # ---- the haircut: five cuts on the beat, music up
    m0 = L["c1"]["t1"] + 0.05
    for k, (rel, s) in enumerate(SHOP):
        a, b = m0 + k * BEAT, (m0 + (k + 1) * BEAT) if k < len(SHOP) - 1 else L["r1"]["t0"]
        B(a, b, rel, s, tx="zoom" if k == 0 else "punch")
        S("whoosh", a, 0.06)
        S("clipper", a + 0.04, 0.05, d=BEAT * 0.8)
        S("snip", a + BEAT * 0.55, 0.07)
    cues.append({"type": "label", "t0": m0 + 3 * BEAT, "t1": L["r1"]["t0"], "text": "Fresh start.", "z": 44})
    S("pop", m0 + 3 * BEAT, 0.1)
    nocap.append([L["c1"]["t1"], L["r1"]["t0"]])

    # ---- the music drops dead: "Let's rewind." Week 1 flashes backwards, then "the debt, the no job"
    geoms.append([L["r1"]["t0"], "split", 0.0])
    r0 = T("r1", "rewind", end=True) + 0.02
    r1 = T("r1", "so") - 0.03
    files = [str(W / "w1" / f"r{k}.jpg") for k in range(5)]
    cues.append({"type": "rewind", "t0": round(r0, 3), "t1": round(r1, 3), "files": files, "step": (r1 - r0) / len(files), "from": 111,
                 "speed": 111 / max(0.1, r1 - r0), "z": 47})
    S("rwhoosh", r0, 0.08, d=max(0.3, r1 - r0))
    S("glitch-text", r0, 0.06, cut=max(0.2, r1 - r0))
    nocap.append([r0, r1])
    tags = [[None, "40K debt", T("r1", "debt"), 130, 430, -4, 64], [None, "No job", T("r1", "job"), 560, 600, 4, 64]]  # above his box
    cues.append({"type": "tags", "t0": T("r1", "debt") - 0.02, "t1": L["r1"]["t1"] + 0.15, "items": [[a, b, round(c, 3), x, y, r, z_] for a, b, c, x, y, r, z_ in tags], "z": 44})
    for k, tg in enumerate(tags):
        S("pop", tg[2], 0.12, f=1.0 + 0.12 * k)

    # ---- his clone over the page: 220 rejections, done waiting
    k0 = L["k0"]["t0"]
    geoms.append([k0 - CLONE_LEAD, "none", 0.3])
    bgs.append([k0 - CLONE_LEAD, L["g1"]["t0"], "paper"])
    line = [[w["x"], round(w["t0"], 3)] for w in tl["words"] if w["line"] == "k0"][2:]  # after "220 rejections."
    cues.append({"type": "wall2", "t0": k0 - CLONE_LEAD, "t1": L["g1"]["t0"] + 0.02, "count_t": T("k0", "220"), "count_d": 0.8,
                 "done_t": line[0][1] - 0.1, "yes_t": T("k0", "yes"), "line": line, "z": 46})
    S("paper-slide", k0 - CLONE_LEAD + 0.05, 0.08)
    for k in range(4):
        S("click", k0 - 0.2 + 0.14 * k, 0.07, f=0.9 + 0.05 * k)
    S("thump", T("k0", "rejections"), 0.18)
    S("whoosh", T("k0", "done"), 0.12, d=0.5)
    S("thump", T("k0", "yes"), 0.16)
    nocap.append([k0 - CLONE_LEAD, L["g1"]["t0"]])

    # ---- the goal: 3,000 a month, from here, Bali, anywhere (his own footage)
    geoms.append([L["g1"]["t0"] - 0.05, "split", 0.45])
    S("whoosh", L["g1"]["t0"], 0.08)
    num = T("g1", "3,000")
    here, bali, anyw = T("g2", "here"), T("g2", "bali"), T("g2", "anywhere")
    cues.append({"type": "goal", "t0": L["g1"]["t0"] + 0.1, "t1": here - 0.1, "num_t": num, "month_t": T("g1", "month"),
                 "from_t": T("g2", "from"), "z": 40})
    for k in range(1, 19):
        S("tick", num + 0.7 * (1 - (1 - k / 18) ** (1 / 3)), 0.045, f=1.0 + 0.25 * (k % 2))
    S("thump", num + 0.72, 0.2)
    geoms.append([here - 0.08, "full", 0.25])
    B(here - 0.08, bali - 0.06, "travel/cities/IMG_8516.MOV", 1.0, tx="zoom")
    B(bali - 0.06, anyw - 0.06, "travel/ocean/IMG_4594.MOV", 2.0)
    B(anyw - 0.06, L["f1"]["t0"], "travel/ocean/IMG_3547.mov", 3.0)
    for s in (here, bali, anyw):
        S("whoosh", s - 0.08, 0.08)

    # ---- reduce friction: "before jumping into the ocean" (his own dive), then the title above him
    geoms.append([L["f1"]["t0"] - 0.05, "split", 0.4])
    jump, d_end = T("f1", "jumping"), T("f1", "directly", end=True) + 0.1
    geoms.append([jump - 0.08, "full", 0.2])
    B(jump - 0.08, d_end, "travel/ocean/IMG_5708.MOV", 3.9, tx="zoom")
    S("water-jump", jump - 0.08 + 0.9, 0.14)  # he hits the water about 0.9 s into the clip
    geoms.append([d_end, "split", 0.35])
    title(T("f1", "first"), T("f1", "reduce") - 0.02, html="The first thing:", size=96, y=400, z=40)
    title(T("f1", "reduce"), L["k1"]["t0"] - CLONE_LEAD, html="Reduce <i class=am>friction.</i>", size=150, y=380, z=40)
    S("type-hit", T("f1", "reduce"), 0.07)
    S("thump", T("f1", "friction"), 0.14)

    # ---- the close (his clone) and "Next week"
    k1 = L["k1"]["t0"]
    geoms.append([k1 - CLONE_LEAD, "none", 0.3])
    bgs.append([k1 - CLONE_LEAD, 999, "paper"])
    kr = [["Profiles", T("k1", "profiles")], ["Portfolio", T("k1", "portfolio")], ["Plan", T("k1", "plan")]]
    cues.append({"type": "kw", "t0": k1 - CLONE_LEAD, "t1": tl["next"][0] + 0.6, "rows": kr, "key": "FRICTION", "key_t": T("k1", "friction"),
                 "box_t": T("k1", "comment") - 0.15, "send_t": T("k1", "checklist") - 0.25, "send": "for my checklist", "z": 47})
    S("whoosh", k1 - CLONE_LEAD + 0.05, 0.1, d=0.5)
    for k, (_, tk) in enumerate(kr):
        S("click", tk, 0.09, f=1.0 + 0.08 * k)
    for k in range(len("FRICTION")):
        S("click", T("k1", "friction") + 0.09 * k, 0.07, f=0.9 + 0.03 * k)
    S("pop", T("k1", "checklist"), 0.08)
    nocap.append([k1 - CLONE_LEAD, tl["dur"] + 1])
    n0, v0 = tl["next"]
    cues.append({"type": "next", "t0": n0, "t1": tl["dur"] + 1, "z": 48,
                 "words": [[w["w"], round(v0 + w["s"], 3), round(v0 + w["e"], 3)] for w in tl["next_words"]]})
    S("whoosh", n0 + 0.15, 0.1, d=0.5)
    S("tick", v0 + tl["next_words"][-1]["e"] - 0.1, 0.07)
    cues.append({"type": "week", "t0": L["c0"]["t0"], "t1": k1 - CLONE_LEAD, "z": 46,
                 "hide": [[k0 - CLONE_LEAD, L["g1"]["t0"]], [tf0, uf]]})

    # the music (LinkedIn/YouTube file): starts on "Hi!", up for the haircut, dead from "rewind" to the goal, back under the rest
    music = {"start": L["c0"]["t0"], "boost": [m0, L["r1"]["t0"]], "drop": [L["r1"]["t0"], L["g1"]["t0"]], "back": L["g1"]["t0"]}
    capy = []
    return {"items": items, "cues": cues, "geoms": geoms, "bgs": bgs, "nocap": nocap, "sfx": fx, "music": music, "capy": capy}


def face_track(d: Path) -> list:
    """Where his face is, frame by frame (YuNet, scripts/reel_edit/safe_zones.py), for selfie clips: the body matte's head
    estimate drifts when a bright window sits above him. Cached in track_face.json."""
    out = d / "track_face.json"
    if out.exists():
        return json.loads(out.read_text())
    import cv2
    from scipy.ndimage import gaussian_filter1d
    sys.path.insert(0, str(REPO / "scripts" / "reel_edit"))
    from safe_zones import faces
    files = sorted(d.glob("*.jpg"))
    xs, ys = np.full(len(files), np.nan), np.full(len(files), np.nan)
    for i in range(0, len(files), 3):
        fs = faces(cv2.imread(str(files[i])))
        if fs:
            x0, y0, x1, y1 = max(fs, key=lambda f: (f[2] - f[0]) * (f[3] - f[1]))
            xs[i], ys[i] = (x0 + x1) / 2, (y0 + y1) / 2
    for arr, dflt in ((xs, 540.0), (ys, 760.0)):
        ok = ~np.isnan(arr)
        arr[~ok] = np.interp(np.nonzero(~ok)[0], np.nonzero(ok)[0], arr[ok]) if ok.any() else dflt
    tr = [[round(float(a), 1), round(float(b), 1)] for a, b in zip(gaussian_filter1d(xs, 8, mode="nearest"), gaussian_filter1d(ys, 8, mode="nearest"))]
    out.write_text(json.dumps(tr))
    return tr


def prep() -> dict:
    tl = build()
    pl = plan(tl)
    base.run_jobs()
    for it in pl["items"]:
        it["n"] = base.count(Path(it["dir"]))
        if it["kind"] == "talk":
            selfie = Path(it["dir"]).name.startswith("s_IMG_87") and it["geom"] == "split"
            it["track"] = face_track(Path(it["dir"])) if selfie else json.loads((Path(it["dir"]) / "track.json").read_text())
    for it in pl["items"]:
        if it.get("freeze"):
            it["fz"] = base.freeze_cut(Path(it["dir"]), it["freeze"][2])
    pl["caps"] = base.captions(tl, pl["nocap"])
    pl["sfx"].sort(key=lambda x: x[1])
    pl.update(dur=tl["dur"], fps=FPS, words=tl["words"], shots=tl["shots"], next=tl["next"], vo=tl["vo"],
              lines={k: [round(v["t0"], 3), round(v["t1"], 3)] for k, v in tl["lines"].items()})
    (W / "timeline.json").write_text(json.dumps(pl))
    print(f"timeline: {tl['dur']:.2f} s, {len(pl['items'])} picture items, {len(pl['cues'])} graphics, {len(pl['caps'])} captions")
    return pl


# ---------------------------------------------------------------- sound
def isolate() -> None:
    """ElevenLabs Voice Isolator on each take he speaks in (once, cached in work/iso). Key: CLAUDEELEVENLABS_API."""
    import soundfile as sf
    key = os.environ["CLAUDEELEVENLABS_API"]
    ISO.mkdir(parents=True, exist_ok=True)
    for c in sorted(TALK_CLIPS):
        out = ISO / f"{c}.wav"
        if out.exists():
            continue
        x = _audio(P / "raw" / "intro" / f"{c}.MOV")
        buf = io.BytesIO()
        sf.write(buf, x, SR, format="WAV", subtype="PCM_16")
        b = "----vishbound"
        body = (f"--{b}\r\nContent-Disposition: form-data; name=\"audio\"; filename=\"{c}.wav\"\r\nContent-Type: audio/wav\r\n\r\n").encode() \
            + buf.getvalue() + f"\r\n--{b}--\r\n".encode()
        req = urllib.request.Request("https://api.elevenlabs.io/v1/audio-isolation", data=body, method="POST",
                                     headers={"xi-api-key": key, "Content-Type": f"multipart/form-data; boundary={b}"})
        mp3 = urllib.request.urlopen(req, timeout=600).read()
        y = subprocess.run(["ffmpeg", "-v", "error", "-i", "pipe:0", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], input=mp3,
                           capture_output=True, check=True).stdout
        y = np.frombuffer(y, np.float32).copy()
        y = np.pad(y, (0, max(0, len(x) - len(y))))[: len(x)]  # same timing as the take
        sf.write(out, y, SR, subtype="PCM_24")
        print("isolated", c, round(len(x) / SR, 1), "s")


def sound(name: str, o: dict):
    """Week 1's sounds, plus the barber's clippers and scissors (synthesised)."""
    rng = np.random.default_rng(len(name))
    if name == "clipper":  # a buzzing trimmer: a 118 Hz rasp with a fast flutter
        d = o.get("d", 0.5)
        t = np.arange(int(d * SR)) / SR
        saw = 2 * ((t * 118) % 1) - 1
        y = (saw * (0.75 + 0.25 * np.sin(2 * np.pi * 31 * t)) + 0.3 * rng.standard_normal(len(t))) * np.minimum(1, t / 0.03) * np.minimum(1, (d - t) / 0.05)
        from scipy.signal import butter, sosfilt
        y = sosfilt(butter(2, [300, 4000], "band", fs=SR, output="sos"), y)
        return (y / (np.abs(y).max() + 1e-9)).astype(np.float32), 0
    if name == "snip":  # two blades closing: two bright clicks 40 ms apart
        t = np.arange(int(0.09 * SR)) / SR

        def c(t0):
            on = t >= t0
            return np.where(on, np.sin(2 * np.pi * 5200 * (t - t0)) * np.exp(-(t - t0) / 0.004), 0) \
                + 0.5 * rng.standard_normal(len(t)) * np.exp(-np.maximum(0, t - t0) / 0.0015) * on
        y = c(0.0) + 0.8 * c(0.04)
        return (y / (np.abs(y).max() + 1e-9)).astype(np.float32), 0
    return _sound(name, o)


_sound = base.sound
base.sound = sound


def mix() -> tuple[Path, Path]:
    """Two mixes from the same stems: Instagram (voice + effects + room sound; the trending song is added in the app) and
    LinkedIn/YouTube (the same, plus our bed)."""
    import soundfile as sf
    from scipy.ndimage import uniform_filter1d
    tl = json.loads((W / "timeline.json").read_text())
    n = int(tl["dur"] * SR) + SR
    at = lambda t: int(t * SR)  # noqa: E731
    voice = np.zeros(n, np.float32)
    jobs = []
    for sh in tl["shots"]:
        a = audio(P / "raw" / "intro" / f"{sh['clip']}.MOV")
        speech = []
        for k, (s0, s1, o0, r) in enumerate(sh["segs"]):
            x = a[at(sh["a"] + s0): at(sh["a"] + s1)].copy()
            if sh.get("mute") and k == len(sh["segs"]) - 1:
                x *= 0.0
            else:
                speech.append(x)
            jobs.append([x, r, sh["t0"] + o0, (s1 - s0) / r, sh])
        sh["gain"] = min(4.0, 0.085 / (np.sqrt(np.mean(np.concatenate(speech) ** 2)) + 1e-6)) if speech else 1.0
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(4) as ex:
        outs = list(ex.map(lambda j: base.stretch(j[0], j[1], True), jobs))
    q = int(0.012 * SR)
    for (x, r, t0, dur, sh), y in zip(jobs, outs):
        m = int(round(dur * SR))
        y = np.pad(y, (0, max(0, m - len(y))))[:m] * sh["gain"]
        if len(y) > 2 * q:
            y[:q] *= np.linspace(0, 1, q)
            y[-q:] *= np.linspace(1, 0, q)
        i = at(t0)
        voice[i:i + len(y)] += y[: max(0, n - i)]
    # his voice, already isolated: only a gentle polish (Vish, 27 Oct: enhanced, never unreal)
    vin, vout = W / "voice_raw.wav", W / "voice_clean.wav"
    sf.write(vin, voice, SR, subtype="FLOAT")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(vin), "-af",
                    "highpass=f=80,equalizer=f=250:t=q:w=1.1:g=-2,equalizer=f=3500:t=q:w=1.3:g=2,highshelf=f=9000:g=1.5,deesser=i=0.35:m=0.5:f=0.5,"
                    "acompressor=threshold=0.08:ratio=2.5:attack=6:release=120:makeup=2:knee=4,alimiter=limit=0.9:level=disabled",
                    "-ar", str(SR), "-ac", "1", "-c:a", "pcm_f32le", str(vout)], check=True)
    voice, _ = sf.read(vout, dtype="float32")
    voice = np.pad(voice, (0, max(0, n - len(voice))))[:n]
    sp = voice[np.abs(voice) > 0.02]
    his = np.sqrt(np.mean(sp ** 2)) if len(sp) else 0.08
    for name, t0 in tl["vo"]:  # clone lines and the narrator, at his level (the narrator +1.5 dB, measured in Week 1)
        v = _audio(VOD / f"{name}.mp3").copy()
        v *= (1.19 if name == NARRATOR else 1.0) * his / (np.sqrt(np.mean(v[np.abs(v) > 0.02] ** 2)) + 1e-6)
        i = at(t0)
        voice[i:i + len(v)] += v[: max(0, n - i)]

    def ramp(points):
        xs, ys = zip(*points)
        return np.interp(np.arange(n) / SR, xs, ys).astype(np.float32)

    # the bed: from "Hi!", up for the haircut, dead silence when he sits down, back (from later in the track) under the goal
    mu = tl["music"]
    bed = _audio(P / "assets" / "music" / "bed.mp3")
    song = np.zeros(n, np.float32)
    s0, d0, d1 = at(mu["start"]), at(mu["drop"][0]), at(mu["back"])
    song[s0:d0] = bed[: d0 - s0]
    tail = bed[at(18.0):]
    song[d1:d1 + min(len(tail), n - d1)] = tail[: n - d1]
    env = np.sqrt(uniform_filter1d(song ** 2, int(2.0 * SR))) + 1e-4
    b0, b1 = mu["boost"]
    target = ramp([(0, 0.022), (b0 - 0.15, 0.022), (b0 + 0.05, 0.09), (b1, 0.09), (b1 + 0.01, 0.0), (mu["back"] - 0.01, 0.0),
                   (mu["back"] + 0.6, 0.022), (999, 0.022)])
    song *= np.clip(target / env, 0, 6)
    hard = np.ones(n, np.float32)  # the drop: a 12 ms edge, true silence
    hard[d0:d1] = 0.0
    hard[max(0, d0 - q):d0] = np.linspace(1, 0, d0 - max(0, d0 - q))
    v0 = tl["next"][1] if tl.get("next") else tl["dur"] - 0.6
    duck = 0.45 if tl.get("next") else 1.0  # under the narrator
    music = song * hard * ramp([(0, 1), (v0 - 0.25, 1), (v0 + 0.05, duck), (tl["dur"] - 1.2, duck), (tl["dur"], 0.0), (999, 0.0)])
    music[:s0] = 0.0
    # the barber shop's own sound, low, under the haircut
    amb = np.zeros(n, np.float32)
    for it in tl["items"]:
        if it["kind"] != "broll":
            continue
        a_ = _audio(Path(it["src"]))
        x = a_[at(it["src_in"]):at(it["src_in"] + (it["t1"] - it["t0"]))].copy()
        if len(x) < 400:
            continue
        x *= 0.05 / (np.sqrt(np.mean(x ** 2)) + 1e-6)
        f = min(len(x) // 3, int(0.08 * SR))
        x[:f] *= np.linspace(0, 1, f)
        x[-f:] *= np.linspace(1, 0, f)
        i = at(it["t0"])
        amb[i:i + len(x)] += x[: max(0, n - i)]
    fx = np.zeros(n, np.float32)
    for name, t_, g, o in tl["sfx"]:
        x, hit = base.sound(name, o)
        i = at(max(0.0, t_)) - hit
        if i < 0:
            x, i = x[-i:], 0
        e = min(n, i + len(x))
        fx[i:e] += g * x[: e - i]
    end = at(tl["dur"])
    np.savez(W / "stems.npz", voice=voice[:end], fx=fx[:end], music=music[:end], amb=amb[:end])
    outs = []
    for name, mus in (("mix_instagram.wav", 0.0), ("mix.wav", 1.0)):
        out = (voice + fx + amb + mus * music)[:end]
        wav = W / name
        sf.write(wav, np.stack([out, out], 1), SR, subtype="FLOAT")
        outs.append(wav)
    return outs[0], outs[1]


def mux(picture: Path, wav: Path, name: str) -> Path:
    (P / "out").mkdir(exist_ok=True)
    out = P / "out" / name
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(picture), "-i", str(wav), "-filter_complex",
                    "[1:a]alimiter=limit=0.8:attack=4:release=60:level=disabled,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000,"
                    "alimiter=limit=0.84:attack=2:release=50:level=disabled[a]", "-map", "0:v", "-map", "[a]", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    return out


def finish(picture: Path) -> None:
    ig, li = mix()
    print("->", mux(picture, ig, f"{OUTNAME}-instagram-9x16.mp4"), "(add the trending song in Instagram)")
    print("->", mux(picture, li, f"{OUTNAME}-9x16.mp4"), "(LinkedIn, YouTube Shorts)")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "prep"
    opt = dict(a[2:].split("=", 1) for a in sys.argv[2:] if a.startswith("--"))
    if cmd == "iso":
        isolate()
    elif cmd == "prep":
        prep()
    elif cmd == "stills":
        base.stills([float(x) for x in sys.argv[2].split(",")])
    elif cmd == "render":
        finish(base.render(int(opt.get("jobs", 2))))
    elif cmd == "mix":
        finish(W / "picture.mp4")
