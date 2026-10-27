"""Week 2 of 52: "220 companies said no. So I'm building my own job." The edit, on the Week 1 engine (v12 standard).

    python edit/week2.py iso             clean his takes once with the ElevenLabs Voice Isolator (echo and room noise out)
    python edit/week2.py prep            cut + grade frames, matte and track Vish, write work/timeline.json
    python edit/week2.py stills 0.5,12   single frames to work/stills/ (layout checks)
    python edit/week2.py render [--jobs=3]   picture (Playwright -> ffmpeg), sound mix, mux out/week2-9x16.mp4
    python edit/week2.py mix             sound only, then mux

The script is content/shoot-sheets/2026-10-week-2-edit.json (key WEEK2), cut from what he really said on 25 and 26 Oct
(video-projects/week-02-talks/raw, linked as raw/intro). Lines he didn't film are spoken by his ElevenLabs clone
(week-02-talks/vo, made by vo_lines.py); the "Next week" card is George, as in Week 1. B-roll for the places he names is
real archive film (public domain, movingimagearchive.com -> the Internet Archive source, credits in week-02-talks/broll).
The picture, grade, cut-out, captions and sound engine are Week 1's (week-01-intro/edit/week1.py), reused, not copied.
"""
from __future__ import annotations

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
BROLL = TALKS / "broll"
ISO = P / "work" / "iso"  # cleaned takes, shared by every edit in this project
TALK_CLIPS = {"IMG_1619", "IMG_1620", "IMG_1621", "IMG_8731", "IMG_8742", "IMG_8744"}
OUTNAME = "week2-9x16.mp4"


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
MONT = 2.6  # the haircut, four quick cuts
# id, clip (None: a line in his cloned voice), runs of (from, to) word-start times kept, caption fixes, layout, look, flags
LINES = [
    ("h1", "IMG_1619", [(0.9, 3.3)], {}, "full", "night", {"gap": 1.1, "mute": 1}),  # "220 companies have said no." + the freeze
    ("h1b", "IMG_1619", [(3.3, 4.8)], {"so": "So"}, "full", "night", {"gap": 0.15}),
    ("r1", "IMG_1619", [(5.4, 5.95)], {}, "45", "night", {"gap": 1.05, "mute": 1}),  # "Let's rewind." + Week 1 runs backwards
    ("g1", "IMG_1620", [(0.0, 4.7)], {"3000": "3,000"}, "split", "night", {}),
    ("g2", "IMG_1621", [(2.7, 6.5)], {}, "split", "night", {"gap": 0.25}),
    ("c1", "IMG_8731", [(2.7, 7.6)], {"before": "Before"}, "full", "day", {"gap": MONT, "mute": 1}),  # + the haircut
    ("f1", "IMG_8742", [(21.4, 27.6)], {"before": "Before"}, "split", "day", {}),
    ("f2", "IMG_8742", [(28.5, 40.5)], {}, "split", "day", {"join": 1, "gap": 0.3}),
]
CLONES = [("k1", "WEEK2_9")]  # "So this week: profiles, portfolio, plan. Comment FRICTION and I'll send you my checklist."
NARRATOR = "WEEK2_10"      # "Next week, on Build with Vish: did reducing friction work?"
LAND = {"h1b": .2, "g2": .25, "f2": .3}
NEXT_LEAD, NEXT_TAIL = 0.35, 0.9
ARCHIVE = {  # name: (label under the print, frame offset into the clip)
    "bali": ("1937 · archive film", 0), "anywhere": ("1940 · archive film", 0), "studio": ("1946 · archive film", 0),
    "dive": ("1937 · archive film", 180)}  # the dive: he leaves the tower 1 s into the card


def vo_words(name: str) -> tuple[float, list]:
    j = json.loads((VOD / f"{name}.json").read_text())
    n = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(VOD / f"{name}.mp3")],
                             capture_output=True, text=True).stdout)
    return n, j["words"]


def build() -> dict:
    """Week 1's build (his takes, snapped to word boundaries, one steady speed), then the clone line and the card."""
    base.LINES, base.LAND = LINES, LAND
    runs, srcw, order, last = [], [], [], None
    for li, (lid, clip, rr, fix, lay, look, fl) in enumerate(LINES):
        prev_b = -1.0
        for k, (A, B) in enumerate(rr):
            a, b, sel = base.snap(clip, A, B)
            if k == 0 and fl.get("join") and last and last[0] == clip:
                a = last[1]
                b = a + max(1, round((b - a) * FPS)) / FPS
            if a < prev_b:
                a = prev_b
                b = a + max(1, round((b - a) * FPS)) / FPS
            prev_b = b
            runs.append({"line": lid, "clip": clip, "a": a, "b": b, "lay": lay, "look": look, "k": k, "hold": 0.0})
            for w in sel:
                x = fix.get(w["x"], w["x"])
                if x:
                    srcw.append({"line": lid, "x": x, "s0": max(a, w["t"]), "s1": min(b, w["e"]), "clip": clip})
        order.append(lid)
        gap = fl.get("gap", 0.0)
        nxt = LINES[li + 1] if li + 1 < len(LINES) else None
        if lid in LAND and not (nxt and nxt[6].get("join") and nxt[1] == clip):
            later = [w["t"] for w in base.WORDS[clip] if w["t"] > runs[-1]["b"]]
            room = (later[0] - runs[-1]["b"] - 0.05) if later else 9.0
            gap = max(gap, round(max(0.0, min(LAND[lid], room, base.DUR.get(clip, 99) - runs[-1]["b"] - 0.05)) * FPS) / FPS)
        runs[-1]["hold"] = round(gap * FPS) / FPS
        runs[-1]["mute"] = bool(fl.get("mute"))
        last = (clip, runs[-1]["b"]) if gap == 0 else None
    shots = []
    for r in runs:
        sh = shots[-1] if shots else None
        if sh and sh["clip"] == r["clip"] and sh["open"] and abs(sh["b"] - r["a"]) < 1e-3:
            sh["runs"].append(r)
        else:
            sh = {"clip": r["clip"], "a": r["a"], "runs": [r]}
            shots.append(sh)
        sh["b"], sh["hold"], sh["open"] = r["b"], r["hold"], r["hold"] == 0
    t = 0.0
    for sh in shots:  # his own pauses stay (Vish, 22 Oct): one steady speed, no cuts inside a take
        cuts, rates = [(sh["a"], sh["b"])], [base.SPEED]
        if sh["hold"] > 0:
            cuts.append((sh["b"], sh["b"] + sh["hold"]))
            rates.append(1.0)
        segs, o = [], 0.0
        for (c0, c1), r in zip(cuts, rates):
            segs.append([round(c0 - sh["a"], 4), round(c1 - sh["a"], 4), round(o, 4), round(r, 4)])
            o += (c1 - c0) / r
        dur = round(o * FPS) / FPS
        sh.update(t0=t, dur=dur, segs=segs)
        t += dur

    def omap(sh, s):
        x = s - sh["a"]
        for s0, s1, o0, r in sh["segs"]:
            if x <= s1 + 1e-6:
                return sh["t0"] + o0 + max(0.0, x - s0) / r
        s0, s1, o0, r = sh["segs"][-1]
        return sh["t0"] + o0 + (x - s0) / r

    words, lines = [], {}
    for sh in shots:
        for r in sh["runs"]:
            r["t0"], r["t1"] = omap(sh, r["a"]), omap(sh, r["b"])
            if r["hold"]:
                r["hold"] = sh["t0"] + sh["dur"] - r["t1"]
            L = lines.setdefault(r["line"], {"t0": r["t0"], "runs": []})
            L["runs"].append((r["t0"], r["t1"]))
            L["t1"] = r["t1"]
        for w in srcw:
            if w["clip"] == sh["clip"] and sh["a"] - 1e-3 <= w["s0"] < sh["b"] + 1e-3:
                words.append({"line": w["line"], "x": w["x"], "t0": omap(sh, w["s0"]), "t1": omap(sh, w["s1"])})
    # lines in his cloned voice, over cards (no picture of him: a cloned voice never plays over his face)
    k0 = t + 0.45  # the first card slides up first
    for lid, vo in CLONES:
        n, vw = vo_words(vo)
        lines[lid] = {"t0": k0, "t1": k0 + n, "runs": [(k0, k0 + n)], "vo": vo}
        order.append(lid)
        for w in vw:
            words.append({"line": lid, "x": w["w"], "t0": k0 + w["s"], "t1": k0 + w["e"]})
        t = k0 + n + 0.35
        k0 = t
    nx0, nw = t, []
    if NARRATOR:
        nn, nw = vo_words(NARRATOR)
        t = nx0 + NEXT_LEAD + nn + NEXT_TAIL
    else:
        t += 0.6
    words.sort(key=lambda w: w["t0"])
    shots_out = [{"clip": sh["clip"], "a": sh["a"], "b": sh["b"] + sh["hold"], "t0": sh["t0"], "dur": sh["dur"], "segs": sh["segs"],
                  "look": sh["runs"][0]["look"], "cut": any(r["lay"] == "cut" for r in sh["runs"]), "mute": sh["runs"][-1].get("mute", False),
                  "runs": [runs.index(r) for r in sh["runs"]]} for sh in shots]
    return {"runs": runs, "shots": shots_out, "words": words, "lines": {k: lines[k] for k in order}, "next": (nx0, nx0 + NEXT_LEAD) if NARRATOR else None,
            "vo": [[vo, lines[lid]["t0"]] for lid, vo in CLONES] + ([[NARRATOR, nx0 + NEXT_LEAD]] if NARRATOR else []),
            "next_words": nw, "dur": round(t * FPS) / FPS}


def archive_frames(name: str, n: int) -> Path:
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
    T = lambda lid, s, **k: base.wt(tl, lid, s, **k)  # noqa: E731

    def S(name, t, g, **o):
        fx.append([name, round(t, 3), g, o])

    def B(t0, t1, rel, src_in, look="day", kb=(1.0, 1.06), speed=1.0, fy=0.5, tx=None):
        src = P / "raw" / rel
        n = max(1, round((t1 - t0) * FPS)) + base.TAIL
        d = base.extract(src, src_in, n, look, "1080:-2", f"b_{Path(rel).stem}_{src_in:.2f}_{n}_{speed}", speed)
        items.append({"t0": round(t0, 4), "t1": round(t1, 4), "dir": str(d), "n": n, "kind": "broll", "geom": "full", "kb": kb, "fy": fy,
                      "src": str(src), "src_in": src_in, "speed": speed})
        if tx:
            items[-1].update(tx=tx, txd=0.22, dx=0.0)

    def card(name, t0, t1, x=140, y=170, w=760, rot=-2.0):
        n = round((t1 - t0) * FPS) + 12 + ARCHIVE[name][1]
        d = archive_frames(name, n)
        cues.append({"type": "archive", "t0": round(t0, 3), "t1": round(t1, 3), "dir": str(d), "n": len(list(d.glob("*.jpg"))),
                     "off": ARCHIVE[name][1], "label": ARCHIVE[name][0], "x": x, "y": y, "w": w, "rot": rot, "z": 41})
        S("whoosh", t0 + 0.05, 0.08)
        S("paper-slide", t0 + 0.1, 0.06)

    def title(t0, t1, words=None, html=None, font="serif", size=96, y=None, band=False, z=45, **k):
        cues.append({"type": "title", "t0": round(t0, 3), "t1": round(t1, 3), "words": words, "html": html, "font": font, "size": size,
                     "y": y, "band": band, "z": z, **k})

    # his takes: one graded, matted shot per continuous stretch (portrait phone clips stay portrait)
    for sh in tl["shots"]:
        n = round(sh["dur"] * FPS) + base.TAIL
        portrait = sh["clip"].startswith("IMG_87")
        key = __import__("hashlib").md5(json.dumps(sh["segs"]).encode()).hexdigest()[:6]
        d = base.extract(P / "raw" / "intro" / f"{sh['clip']}.MOV", sh["a"], n, sh["look"], "1080:1920" if portrait else "1920:1080",
                         f"s_{sh['clip']}_{sh['a']:.3f}_{n}_{key}", matte=True, cut=False, segs=sh["segs"])
        for ri in sh["runs"]:
            r = tl["runs"][ri]
            items.append({"zc": [], "t0": round(r["t0"], 4), "t1": round(r["t1"] + r["hold"], 4), "dir": str(d), "n": n,
                          "off": round((r["t0"] - sh["t0"]) * FPS), "kind": "talk", "geom": {"full": "full", "45": "f45", "split": "split"}[r["lay"]],
                          "track": None, "z": 1.0, "shot": d.name})

    def zoom(lid, z0, z1, t0=None, t1=None):
        for i in items:
            if i["kind"] == "talk" and L[lid]["t0"] - 1e-3 <= i["t0"] < L[lid]["t1"] - 1e-3:
                i["zk"] = [[t0 if t0 is not None else L[lid]["t0"], z0], [t1 if t1 is not None else L[lid]["t1"], z1]]

    END = L["f2"]["t1"]
    k1 = L["k1"]["t0"]
    cues.append({"type": "week", "t0": L["h1"]["t0"] + 0.4, "t1": k1 - 0.4, "z": 46, "hide": []})
    bgs.append([0, k1 - 0.45, "ink"])
    bgs.append([k1 - 0.45, tl["dur"] + 1, "paper"])

    # ---- HOOK: "220 companies have said no." The frame freezes on "no" and he becomes a sticker; the labels pop on
    geoms.append([0, "full", 0.0])
    zoom("h1", 1.0, 1.05)
    tf0, uf = T("h1", "no", end=True) + 0.02, L["h1b"]["t0"]
    it = next(i for i in items if i["kind"] == "talk" and abs(i["t0"] - L["h1"]["t0"]) < 1e-3)
    it["freeze"] = [round(tf0, 4), round(uf, 4), it["off"] + int((tf0 - it["t0"]) * FPS)]
    tags = [[None, "220 rejections", tf0 + 0.04, 70, 340, -4, 56], ["money_with_wings", "€0 remote income", tf0 + 0.24, 90, 455, -2, 40],
            [None, "Week 2 of 52", tf0 + 0.44, 660, 350, 3, 40]]  # all above his head in the frozen frame, never on his face
    cues.append({"type": "tags", "t0": tf0, "t1": uf + 0.04, "items": [[a, b, round(c, 3), x, y, r, z_] for a, b, c, x, y, r, z_ in tags], "z": 44})
    S("shutter-old", tf0, 0.12, cut=0.5)
    S("boom", tf0, 0.14)
    for k, tg in enumerate(tags):
        S("pop", tg[2], 0.12, f=1.0 + 0.08 * k)
    nocap.append([tf0, uf])
    S("whoosh", uf, 0.07)

    # ---- "Let's rewind.": last week's reel runs backwards
    geoms.append([L["r1"]["t0"] - 0.05, "f45", 0.4])
    r0, r1 = L["r1"]["t1"] + 0.05, L["g1"]["t0"] - 0.02
    files = [str(W / "w1" / f"r{k}.jpg") for k in range(5)]
    cues.append({"type": "rewind", "t0": round(r0, 3), "t1": round(r1, 3), "files": files, "step": (r1 - r0) / len(files), "from": 111,
                 "speed": 111 / (r1 - r0), "z": 47})
    S("glitch-text", r0, 0.08, cut=r1 - r0)
    S("rwhoosh", r0 + 0.05, 0.08, d=r1 - r0)
    for k in range(len(files)):
        S("click", r0 + k * (r1 - r0) / len(files), 0.07, f=1.2 - 0.06 * k)
    nocap.append([r0, r1])

    # ---- the goal: 3,000 a month, from anywhere (archive film for the places he names)
    geoms.append([L["g1"]["t0"] - 0.1, "split", 0.5])
    S("whoosh", L["g1"]["t0"], 0.08)
    bali, anyw = T("g2", "bali"), T("g2", "anywhere")
    num = T("g1", "3,000")
    cues.append({"type": "goal", "t0": L["g1"]["t0"] + 0.1, "t1": bali - 0.02, "num_t": num, "month_t": T("g1", "month"),
                 "from_t": T("g2", "here"), "z": 40})
    base_ticks = 18
    for k in range(1, base_ticks + 1):
        S("tick", num + 0.7 * (1 - (1 - k / base_ticks) ** (1 / 3)), 0.045, f=1.0 + 0.25 * (k % 2))
    S("thump", num + 0.72, 0.2)
    card("bali", bali - 0.05, anyw - 0.02, rot=-2.5)
    card("anywhere", anyw - 0.05, L["c1"]["t0"] - 0.05, x=150, rot=2.0)

    # ---- the haircut: "Before we start the week 2 video, come with me. Let's get a haircut."
    geoms.append([L["c1"]["t0"] - 0.1, "full", 0.5])
    S("whoosh", L["c1"]["t0"], 0.08)
    m0 = L["c1"]["t1"] + 0.05
    shop = [("intro/IMG_8694.MOV", 1.6), ("intro/IMG_8695.MOV", 1.8), ("intro/IMG_8696.MOV", 2.6), ("intro/IMG_8697.MOV", 3.4)]
    step = (MONT - 0.05) / len(shop)
    for k, (rel, s) in enumerate(shop):
        B(m0 + k * step, m0 + (k + 1) * step if k < len(shop) - 1 else L["f1"]["t0"], rel, s, tx="punch" if k else "zoom")
        S("whoosh", m0 + k * step, 0.07)
        S("clipper", m0 + k * step + 0.05, 0.05, d=step * 0.8)
        S("snip", m0 + k * step + step * 0.5, 0.08)
    cues.append({"type": "label", "t0": m0 + 3 * step, "t1": L["f1"]["t0"], "text": "Fresh start.", "z": 44})
    S("pop", m0 + 3 * step, 0.1)
    nocap.append([L["c1"]["t1"], L["f1"]["t0"]])

    # ---- reduce friction: "before jumping into the ocean directly", then the three things
    geoms.append([L["f1"]["t0"] - 0.1, "split", 0.5])
    jump, first, red = T("f1", "jumping"), T("f1", "first"), T("f1", "reduce")
    card("dive", jump - 0.08, first - 0.08, rot=-2.0)
    S("water-jump", jump - 0.08 + 1.55, 0.12)  # he hits the water 1.6 s into the card (frame offset 180)
    title(first - 0.05, red - 0.05, seq(tl, "f1", "The first thing:", L), size=110, y=380, z=40)
    rows = [["Profiles", "on the freelancing platforms", T("f2", "profiles")], ["Portfolio", "my work, in one place", T("f2", "portfolio")],
            ["Plan", "content and income", T("f2", "plan")]]
    cues.append({"type": "check", "t0": red - 0.05, "t1": L["k1"]["t0"] - 0.45, "head": "Reduce friction", "rows": rows, "z": 40})
    S("thump", red, 0.16)
    S("type-hit", red + 0.1, 0.05)
    for k, r in enumerate(rows):
        S("click", r[2], 0.09, f=1.0 + 0.08 * k)
        S("pop", r[2] + 0.05, 0.07, f=0.9 + 0.08 * k)

    # ---- the close: his clone over the card, the keyword, then "Next week"
    geoms.append([k1 - 0.45, "none", 0.4])
    vw = [w for w in tl["words"] if w["line"] == "k1"]
    wv = lambda s, nth=0: [w for w in vw if s.lower() in w["x"].lower()][nth]["t0"]  # noqa: E731
    kr = [["Profiles", wv("profiles")], ["Portfolio", wv("portfolio")], ["Plan", wv("plan")]]
    cues.append({"type": "kw", "t0": k1 - 0.45, "t1": tl["next"][0] + 0.6, "rows": kr, "key": "FRICTION", "key_t": wv("friction"),
                 "box_t": wv("comment") - 0.15, "send_t": wv("send"), "z": 47})
    S("whoosh", k1 - 0.35, 0.1, d=0.5)
    for k, (_, tk) in enumerate(kr):
        S("click", tk, 0.09, f=1.0 + 0.08 * k)
    for k in range(len("FRICTION")):
        S("click", wv("friction") + 0.09 * k, 0.07, f=0.9 + 0.03 * k)
    S("pop", wv("send"), 0.08)
    nocap.append([k1 - 0.45, tl["dur"] + 1])
    n0, v0 = tl["next"]
    cues.append({"type": "next", "t0": n0, "t1": tl["dur"] + 1, "z": 48,
                 "words": [[w["w"], round(v0 + w["s"], 3), round(v0 + w["e"], 3)] for w in tl["next_words"]]})
    S("whoosh", n0 + 0.15, 0.1, d=0.5)
    S("tick", v0 + tl["next_words"][-1]["e"] - 0.1, 0.07)
    hush = [[tf0 - 0.01, uf - 0.02], [r0, r1]]
    # the landscape takes fill the frame with his face: their captions go up onto his hair, under the week label
    capy = [[L["h1"]["t0"], L["h1b"]["t1"] + 0.4, 350], [L["r1"]["t0"], L["r1"]["t1"] + 0.3, 350]]
    return {"items": items, "cues": cues, "geoms": geoms, "bgs": bgs, "nocap": nocap, "sfx": fx, "hush": hush, "end": END, "boost": [[m0, L["f1"]["t0"]]],
            "capy": capy}


def seq(tl, lid, text, L):
    """Week 1's seq(): a title's words timed to when he says them."""
    import re
    spoken = [w for w in tl["words"] if w["line"] == lid]
    out, j = [], 0
    norm = lambda x: re.sub(r"[^a-z0-9%]", "", x.lower())  # noqa: E731
    for tok in text.split():
        html, plain = tok, tok.strip("*^")
        if tok.startswith("*"):
            html = f"<i>{plain}</i>"
        k = next((m for m in range(j, len(spoken)) if norm(spoken[m]["x"]) == norm(plain)), None)
        tt = spoken[k]["t0"] if k is not None else (out[-1][1] if out else L[lid]["t0"])
        j = k + 1 if k is not None else j
        out.append([html, round(tt, 3)])
    return out


def prep() -> dict:
    tl = build()
    pl = plan(tl)
    base.run_jobs()
    for it in pl["items"]:
        it["n"] = base.count(Path(it["dir"]))
        if it["kind"] == "talk":
            it["track"] = json.loads((Path(it["dir"]) / "track.json").read_text())
    for it in pl["items"]:
        if it.get("freeze"):
            it["fz"] = base.freeze_cut(Path(it["dir"]), it["freeze"][2])
    pl["caps"] = base.captions(tl, pl["nocap"])
    pl["sfx"].sort(key=lambda x: x[1])
    pl.update(dur=tl["dur"], fps=FPS, words=tl["words"], runs=tl["runs"], shots=tl["shots"], next=tl["next"], vo=tl["vo"],
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
    if name == "clipper":  # a buzzing trimmer: a 120 Hz rasp with a fast flutter
        d = o.get("d", 0.5)
        t = np.arange(int(d * SR)) / SR
        saw = 2 * ((t * 118) % 1) - 1
        y = (saw * (0.75 + 0.25 * np.sin(2 * np.pi * 31 * t)) + 0.3 * rng.standard_normal(len(t))) * np.minimum(1, t / 0.03) * np.minimum(1, (d - t) / 0.05)
        from scipy.signal import butter, sosfilt
        y = sosfilt(butter(2, [300, 4000], "band", fs=SR, output="sos"), y)
        return (y / (np.abs(y).max() + 1e-9)).astype(np.float32), 0
    if name == "snip":  # two blades closing: two bright clicks 40 ms apart
        t = np.arange(int(0.09 * SR)) / SR
        c = lambda t0: np.where(t >= t0, np.sin(2 * np.pi * 5200 * (t - t0)) * np.exp(-(t - t0) / 0.004) + 0.5 * rng.standard_normal(len(t)) * np.exp(-np.maximum(0, t - t0) / 0.0015) * (t >= t0), 0)  # noqa: E731
        y = c(0.0) + 0.8 * c(0.04)
        return (y / (np.abs(y).max() + 1e-9)).astype(np.float32), 0
    return _sound(name, o)


_sound = base.sound
base.sound = sound


def mix() -> Path:
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
        k = 1.19 if name == NARRATOR else 1.0
        v = _audio(VOD / f"{name}.mp3").copy()
        v *= k * his / (np.sqrt(np.mean(v[np.abs(v) > 0.02] ** 2)) + 1e-6)
        i = at(t0)
        voice[i:i + len(v)] += v[: max(0, n - i)]

    def ramp(points):
        xs, ys = zip(*points)
        return np.interp(np.arange(n) / SR, xs, ys).astype(np.float32)

    # music: one steady bed under him (no pumping), up for the haircut, under the narrator, hard silence on the freeze
    bed = _audio(P / "assets" / "music" / "bed.mp3")
    song = np.zeros(n, np.float32)
    song[: min(n, len(bed))] = bed[:n]
    env = np.sqrt(uniform_filter1d(song ** 2, int(2.0 * SR))) + 1e-4
    pts = [(0, 0.022)]
    for m0, m1 in tl.get("boost", []):  # up for a montage
        pts += [(m0 - 0.2, 0.022), (m0 + 0.1, 0.085), (m1 - 0.2, 0.085), (m1 + 0.2, 0.022)]
    target = ramp(pts + [(999, 0.022)])
    song *= uniform_filter1d(np.clip(target / env, 0, 6), int(0.5 * SR))
    hush = np.ones(n, np.float32)
    for h0, h1 in tl.get("hush", []):
        i0, i1 = at(h0), at(h1)
        hush[i0:i1] = 0.0
        hush[max(0, i0 - q):i0] = np.linspace(1, 0, i0 - max(0, i0 - q))
        hush[i1:i1 + q] = np.linspace(0, 1, len(hush[i1:i1 + q]))
    v0 = tl["next"][1] if tl.get("next") else tl["dur"] - 1.0
    music = song * hush * ramp([(0, 1), (v0 - 0.25, 1), (v0 + 0.05, 0.45 if tl.get("next") else 1.0), (tl["dur"] - 1.2, 0.45 if tl.get("next") else 0.8),
                                (tl["dur"], 0.0), (999, 0.0)])
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
    out = (voice + fx + music + amb)[:end]
    wav = W / "mix.wav"
    sf.write(wav, np.stack([out, out], 1), SR, subtype="FLOAT")
    return wav


def mux(picture: Path, wav: Path) -> Path:
    (P / "out").mkdir(exist_ok=True)
    out = P / "out" / OUTNAME
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(picture), "-i", str(wav), "-filter_complex",
                    "[1:a]alimiter=limit=0.8:attack=4:release=60:level=disabled,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000,"
                    "alimiter=limit=0.84:attack=2:release=50:level=disabled[a]", "-map", "0:v", "-map", "[a]", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    return out


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
        pic = base.render(int(opt.get("jobs", 3)))
        print("->", mux(pic, mix()))
    elif cmd == "mix":
        print("->", mux(W / "picture.mp4", mix()))
