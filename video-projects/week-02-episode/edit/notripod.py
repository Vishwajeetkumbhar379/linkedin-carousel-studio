"""Short (T5, Mon 3 Nov): "I don't have a tripod. I don't have a mic." Same engine as week2.py, its own cut and cards.

    python edit/notripod.py prep | stills 0.5,8 | render [--jobs=3] | mix     -> out/notripod-9x16.mp4

Script: content/shoot-sheets/2026-10-week-2-edit.json (key NOTRIPOD). His walk-and-talk IMG_8744 (cleaned by the Voice
Isolator: `python edit/week2.py iso`), then two lines in his clone over cards, no "Next week" card.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import week2 as E  # noqa: E402

base = E.base
W = E.P / "work_notripod"
E.W = base.W = W
base.FR, base.LUTS = W / "fr", W / "luts"
E.OUTNAME = "notripod"
E.SEQ = [
    ("n1", "IMG_8744", [(6.0, 8.1)], {"tripod": "tripod."}, "full", "day", {"gap": 0.9, "mute": 1}),  # "I don't have a tripod. I don't have a mic." + the freeze
    ("n2", "IMG_8744", [(16.6, 22.4)], {}, "split", "day", {}),
    ("n3", "IMG_8744", [(22.7, 28.8)], {}, "full", "day", {"gap": 0.2}),
    ("c1", None, "NOTRIPOD_3"),  # "Every video on this account so far was shot on my phone."
    ("c2", None, "NOTRIPOD_4"),  # "So what would you buy first? A tripod, or a mic?"
]
E.NARRATOR = None



def plan(tl: dict) -> dict:
    L = tl["lines"]
    items, cues, geoms, bgs, nocap, fx = [], [], [], [], [], []
    T = lambda lid, s, **k: base.wt(tl, lid, s, **k)  # noqa: E731

    def S(name, t, g, **o):
        fx.append([name, round(t, 3), g, o])

    for sh in tl["shots"]:
        n = round(sh["dur"] * E.FPS) + base.TAIL
        key = __import__("hashlib").md5(__import__("json").dumps(sh["segs"]).encode()).hexdigest()[:6]
        d = base.extract(E.P / "raw" / "intro" / f"{sh['clip']}.MOV", sh["a"], n, sh["look"], "1080:1920", f"s_{sh['clip']}_{sh['a']:.3f}_{n}_{key}",
                         matte=True, cut=False, segs=sh["segs"])
        for ri in sh["runs"]:
            r = tl["runs"][ri]
            items.append({"zc": [], "t0": round(r["t0"], 4), "t1": round(r["t1"] + r["hold"], 4), "dir": str(d), "n": n,
                          "off": round((r["t0"] - sh["t0"]) * E.FPS), "kind": "talk", "geom": {"full": "full", "split": "split"}[r["lay"]],
                          "track": None, "z": 1.0, "shot": d.name})
    c1, c2 = L["c1"]["t0"], L["c2"]["t0"]
    cues.append({"type": "week", "t0": 0.3, "t1": c1 - 0.4, "z": 46, "hide": []})
    bgs += [[0, c1 - 0.45, "ink"], [c1 - 0.45, tl["dur"] + 1, "paper"]]
    # hook: the frame freezes on "mic", he becomes a sticker, two labels pop on
    geoms.append([0, "full", 0.0])
    tf0, uf = T("n1", "mic", end=True) + 0.02, L["n2"]["t0"]
    it = next(i for i in items if abs(i["t0"] - L["n1"]["t0"]) < 1e-3)
    it["freeze"] = [round(tf0, 4), round(uf, 4), it["off"] + int((tf0 - it["t0"]) * E.FPS)]
    tags = [[None, "No tripod.", tf0 + 0.04, 80, 340, -4, 56], [None, "No mic.", tf0 + 0.24, 560, 1130, 4, 56]]
    cues.append({"type": "tags", "t0": tf0, "t1": uf + 0.04, "items": [[a, b, round(c, 3), x, y, r, z_] for a, b, c, x, y, r, z_ in tags], "z": 44})
    S("shutter-old", tf0, 0.12, cut=0.5)
    S("boom", tf0, 0.14)
    for k, tg in enumerate(tags):
        S("pop", tg[2], 0.12, f=1.0 + 0.1 * k)
    nocap.append([tf0, uf])
    # "not going super fancy": a 1946 film studio; "thousands of euros before earning them": 0 before 1
    geoms.append([L["n2"]["t0"] - 0.1, "split", 0.5])
    S("whoosh", L["n2"]["t0"], 0.08)
    fancy = T("n2", "fancy")
    n = round((T("n2", "investing") - fancy + 0.2) * E.FPS) + 12
    d = E.archive_frames("studio", n)
    cues.append({"type": "archive", "t0": round(fancy - 0.3, 3), "t1": round(T("n2", "investing") - 0.05, 3), "dir": str(d),
                 "n": len(list(d.glob("*.jpg"))), "off": 0, "label": "1946 · archive film", "x": 140, "y": 170, "w": 760, "rot": -2.0, "z": 41})
    S("paper-slide", fancy - 0.2, 0.07)
    cues.append({"type": "title", "t0": round(T("n2", "investing") - 0.05, 3), "t1": round(L["n2"]["t1"] + 0.3, 3),
                 "words": None, "html": "€0 <i>before</i> <span class=am>€1</span>", "font": "serif", "size": 190, "y": 330, "band": False, "z": 40})
    S("thump", T("n2", "thousands"), 0.18)
    geoms.append([L["n3"]["t0"] - 0.1, "full", 0.5])
    S("whoosh", L["n3"]["t0"], 0.07)
    # clone lines over cards: his real reels, then the question
    geoms.append([c1 - 0.45, "none", 0.4])
    vw = lambda lid, s: [w for w in tl["words"] if w["line"] == lid and s.lower() in w["x"].lower()][0]["t0"]  # noqa: E731
    files = [str(E.W.parent / "work" / "w1" / f"r{k}.jpg") for k in (0, 3, 1)] + [str(W / "hae.jpg"), str(W / "w2.jpg"), str(E.W.parent / "work" / "w1" / "r4.jpg")]
    times = [c1 - 0.1 + 0.22 * k for k in range(len(files))]
    cues.append({"type": "grid", "t0": c1 - 0.45, "t1": c2 - 0.1, "files": files, "times": times, "label_t": vw("c1", "phone") - 0.1, "z": 47})
    S("whoosh", c1 - 0.35, 0.1, d=0.5)
    for k, tt in enumerate(times):
        S("shutter-old", tt, 0.06, cut=0.25)
    cues.append({"type": "choice", "t0": c2 - 0.4, "t1": tl["dur"] + 1, "a_t": vw("c2", "tripod"), "b_t": vw("c2", "mic"), "z": 48})
    S("whoosh", c2 - 0.3, 0.1, d=0.5)
    S("click", vw("c2", "tripod"), 0.1)
    S("click", vw("c2", "mic"), 0.1, f=1.15)
    S("pop", vw("c2", "mic") + 0.4, 0.08)
    nocap.append([c1 - 0.45, tl["dur"] + 1])
    hush = [[tf0 - 0.01, uf - 0.02]]
    music = {"start": 0.0, "boost": [0, 0], "drop": [tl["dur"], tl["dur"]], "back": tl["dur"]}  # a steady low bed (LinkedIn/YouTube file)
    return {"items": items, "cues": cues, "geoms": geoms, "bgs": bgs, "nocap": nocap, "sfx": fx, "hush": hush, "music": music,
            "capy": [[L["n1"]["t0"], L["n2"]["t0"], 400], [L["n3"]["t0"], L["c1"]["t0"], 400]]}  # selfie close-ups: captions above his head


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
