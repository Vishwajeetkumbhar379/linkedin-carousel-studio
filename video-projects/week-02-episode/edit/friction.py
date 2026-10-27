"""Reel (M1): "Before jumping into the ocean, reduce friction." His walk-and-talk, his clone in between, the locks card.

    python edit/friction.py prep | stills 0.5,8 | render [--jobs=2] | mix     -> out/friction-instagram-9x16.mp4, out/friction-9x16.mp4

Script: content/shoot-sheets/2026-10-week-2-edit.json (key FRICTION). IMG_8742 (cleaned by the Voice Isolator:
`python edit/week2.py iso`), his own sea clip for "jumping into the ocean", two clone lines over cards, no "Next week" card.
Same engine and two audio versions as week2.py.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import week2 as E  # noqa: E402

base = E.base
W = E.P / "work_friction"
E.W = base.W = W
base.FR, base.LUTS = W / "fr", W / "luts"
E.OUTNAME = "friction"
E.SEQ = [
    ("a1", "IMG_8742", [(21.4, 27.6)], {"before": "Before", "directly.": "directly."}, "full", "day", {"gap": 0.8, "mute": 1}),  # + the freeze
    ("k1", None, "FRICTION_1"),  # "Friction is anything that stands between you and a yes."
    ("a2", "IMG_8742", [(28.5, 44.0)], {"look": "looks"}, "split", "day", {"gap": 0.25}),  # profiles, portfolio, plan
    ("k2", None, "FRICTION_4"),  # "Comment FRICTION and I'll send you the checklist, with three Claude prompts."
]
E.NARRATOR = None


def plan(tl: dict) -> dict:
    L = tl["lines"]
    items, cues, geoms, bgs, nocap, fx = [], [], [], [], [], []
    T = lambda lid, s, end=False, nth=0: [w for w in tl["words"] if w["line"] == lid and s.lower() in w["x"].lower()][nth]["t1" if end else "t0"]  # noqa: E731

    def S(name, t, g, **o):
        fx.append([name, round(t, 3), g, o])

    for sh in tl["shots"]:
        n = round(sh["dur"] * E.FPS) + base.TAIL
        key = hashlib.md5(json.dumps(sh["segs"]).encode()).hexdigest()[:6]
        d = base.extract(E.P / "raw" / "intro" / f"{sh['clip']}.MOV", sh["a"], n, sh["look"], "1080:1920", f"s_{sh['clip']}_{sh['a']:.3f}_{n}_{key}",
                         matte=True, cut=False, segs=sh["segs"])
        items.append({"zc": [], "t0": round(sh["t0"], 4), "t1": round(sh["t0"] + sh["dur"], 4), "dir": str(d), "n": n, "off": 0, "kind": "talk",
                      "geom": {"full": "full", "split": "split"}[sh["lay"]], "track": None, "z": 1.0, "shot": d.name})
    k1, k2 = L["k1"]["t0"], L["k2"]["t0"]
    bgs += [[0, k1 - E.CLONE_LEAD, "ink"], [k1 - E.CLONE_LEAD, L["a2"]["t0"], "paper"], [L["a2"]["t0"], k2 - E.CLONE_LEAD, "ink"],
            [k2 - E.CLONE_LEAD, 999, "paper"]]

    # ---- hook: "Before jumping into the ocean directly": his own run into the sea, full screen, the line huge on top
    geoms.append([0, "full", 0.0])
    jump_end = T("a1", "directly", end=True) + 0.1
    src = E.P / "raw" / "travel" / "ocean" / "IMG_5708.MOV"
    n = round(jump_end * E.FPS) + base.TAIL
    d = base.extract(src, 3.9, n, "day", "1080:-2", f"b_IMG_5708_3.90_{n}_1.0", 1.0)
    items.append({"t0": 0.0, "t1": round(jump_end, 4), "dir": str(d), "n": n, "kind": "broll", "geom": "full", "kb": (1.0, 1.06), "fy": 0.5,
                  "src": str(src), "src_in": 3.9, "speed": 1.0})
    cues.append({"type": "title", "t0": 0.0, "t1": round(jump_end, 3), "words": None, "html": "Don't jump in <i class=am>yet.</i>",
                 "font": "serif", "size": 150, "y": 330, "band": False, "z": 40})
    S("whoosh", 0.0, 0.1)
    S("water-jump", 0.9, 0.16)
    # "the first thing I should do is reduce friction." then the frame freezes: he becomes a sticker
    S("whoosh", jump_end, 0.08)
    it = next(i for i in items if i["kind"] == "talk" and abs(i["t0"] - L["a1"]["t0"]) < 1e-3)
    tf0, uf = T("a1", "friction", end=True) + 0.04, L["a1"]["t1"] + 0.8
    it["freeze"] = [round(tf0, 4), round(uf, 4), int((tf0 - it["t0"]) * E.FPS)]
    tags = [[None, "Before you chase clients", tf0 + 0.04, 70, 340, -3, 46], [None, "Week 2 of 52", tf0 + 0.24, 640, 1080, 3, 38]]
    cues.append({"type": "tags", "t0": tf0, "t1": uf + 0.04, "items": [[a, b, round(c, 3), x, y, r, z_] for a, b, c, x, y, r, z_ in tags], "z": 44})
    S("shutter-old", tf0, 0.12, cut=0.5)
    S("boom", tf0, 0.12)
    for k, tg in enumerate(tags):
        S("pop", tg[2], 0.12, f=1.0 + 0.1 * k)
    nocap.append([tf0, uf])

    # ---- his clone: "Friction is anything that stands between you and a yes." The locks card, all locked
    geoms.append([k1 - E.CLONE_LEAD, "none", 0.3])
    line = [[w["x"], round(w["t0"], 3)] for w in tl["words"] if w["line"] == "k1"]
    o = [T("a2", "profiles"), T("a2", "portfolio"), T("a2", "plan")]
    cues.append({"type": "locks", "t0": k1 - E.CLONE_LEAD, "t1": k2 - E.CLONE_LEAD + 0.05, "y": 300, "line": line, "line_y": 760,
                 "line_until": L["a2"]["t0"], "open": o,
                 "rows": [["Profiles", "on the freelance platforms"], ["Portfolio", "your work, one page"], ["Plan", "what you sell, and when"]], "z": 45})
    S("paper-slide", k1 - E.CLONE_LEAD + 0.05, 0.08)
    for k in range(3):
        S("k:interface-sounds/Audio/switch_002", k1 + 0.1 + 0.12 * k, 0.06)
    nocap.append([k1 - E.CLONE_LEAD, L["a2"]["t0"]])

    # ---- profiles, portfolio, plan: him below, each lock opens as he says it
    geoms.append([L["a2"]["t0"] - 0.05, "split", 0.45])
    S("whoosh", L["a2"]["t0"], 0.07)
    for k, t_ in enumerate(o):
        S("k:interface-sounds/Audio/confirmation_001", t_, 0.1)
        S("pop", t_ + 0.05, 0.08, f=1.0 + 0.1 * k)

    # ---- the close: his clone, the keyword
    geoms.append([k2 - E.CLONE_LEAD, "none", 0.3])
    kr = [["Profiles", k2 + 0.3], ["Portfolio", k2 + 0.55], ["Plan", k2 + 0.8]]
    cues.append({"type": "kw", "t0": k2 - E.CLONE_LEAD, "t1": tl["dur"] + 1, "rows": kr, "key": "FRICTION", "key_t": T("k2", "friction"),
                 "box_t": T("k2", "comment") - 0.15, "send_t": T("k2", "checklist") - 0.1, "send": "the checklist + 3 Claude prompts",
                 "head": "The setup", "z": 47})
    S("whoosh", k2 - E.CLONE_LEAD + 0.05, 0.1, d=0.5)
    for k, (_, tk) in enumerate(kr):
        S("click", tk, 0.09, f=1.0 + 0.08 * k)
    for k in range(len("FRICTION")):
        S("click", T("k2", "friction") + 0.09 * k, 0.07, f=0.9 + 0.03 * k)
    S("pop", T("k2", "checklist"), 0.08)
    nocap.append([k2 - E.CLONE_LEAD, tl["dur"] + 1])
    cues.append({"type": "week", "t0": jump_end, "t1": k2 - E.CLONE_LEAD, "z": 46, "hide": [[k1 - E.CLONE_LEAD, L["a2"]["t0"]], [tf0, uf]]})
    music = {"start": 0.0, "boost": [0, 0], "drop": [tl["dur"], tl["dur"]], "back": tl["dur"]}  # a steady low bed (LinkedIn/YouTube file)
    return {"items": items, "cues": cues, "geoms": geoms, "bgs": bgs, "nocap": nocap, "sfx": fx, "music": music, "capy": []}


E.plan = plan

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "prep"
    opt = dict(a[2:].split("=", 1) for a in sys.argv[2:] if a.startswith("--"))
    if cmd == "prep":
        E.prep()
    elif cmd == "stills":
        base.stills([float(x) for x in sys.argv[2].split(",")])
    elif cmd == "render":
        E.finish(base.render(int(opt.get("jobs", 2))))
    elif cmd == "mix":
        E.finish(W / "picture.mp4")
