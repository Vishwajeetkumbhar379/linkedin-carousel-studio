"""Week 1 intro reel: the edit decision list, frame prep, compositor render and sound mix, in one file.

    python edit/week1.py prep            cut + grade frames, matte and track Vish, key the cats, write work/timeline.json
    python edit/week1.py stills 0.5,12   render single frames to work/stills/ (layout checks)
    python edit/week1.py render [--jobs=3]   render the picture (Playwright -> ffmpeg), mix the sound, mux out/week1-intro-9x16.mp4
    python edit/week1.py mix             sound only (voice + music + SFX), then mux

Everything is driven by the transcript (work/intro_words.json): each spoken line is cut on word boundaries snapped to the
audio, B-roll and graphics are timed to the words, the montage after the drop cuts on the music's beats (129 bpm).
Raw footage, frames and renders stay in raw/ and work/ (gitignored). Comp page: edit/comp.html.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

P = Path(__file__).resolve().parents[1]
RAW, W, OUT = P / "raw", P / "work", P / "out"
FR = W / "fr"
FPS, SR = 30, 48000
REPO = P.parents[1]
sys.path.insert(0, str(REPO / "scripts" / "reel_edit"))
from grade import probe  # noqa: E402
import film  # noqa: E402

WORDS = json.loads((W / "intro_words.json").read_text())
DUR = {p.stem: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                   capture_output=True, text=True).stdout or 0) for p in (P / "raw" / "intro").glob("IMG_*.MOV")}
MUSIC = P / "assets" / "music" / "a-new-life.mp3"
LBEAT = 0.71985  # "Loser": the beat period; its chorus lands on "travel the world", so the montage cuts on this grid

# ---------------------------------------------------------------- the cut (his words, in order)
# id, clip, runs of (from, to) word-start times kept, caption fixes, layout, look, flags.
# Vish, 22 Oct: no chopping inside his takes. "join" continues the same take from where the last line ended, so every
# natural pause and aside stays ("that one hurt"); takes only change at a full sentence, under B-roll or a dissolve.
LINES = [
    ("h1", "IMG_1578", [(1.1, 2.4)], {}, "cut", "night", {}),
    ("h2", "IMG_1578", [(2.8, 4.1)], {}, "cut", "night", {"join": 1}),
    ("h3", "IMG_1578", [(4.25, 7.3)], {"to.": "too."}, "cut", "night", {"join": 1}),
    ("h4", "IMG_1578", [(7.7, 8.3)], {}, "cut", "night", {"join": 1}),
    ("h5", "IMG_1578", [(9.2, 11.3)], {}, "cut", "night", {"join": 1}),
    ("h6", "IMG_1578", [(13.4, 14.3)], {}, "full", "night", {"gap": 0.3}),
    ("n1", "IMG_1597", [(0.0, 2.4)], {"Rish,": "Vish,"}, "45", "night", {"gap": 2.4, "mute": 1}),
    ("n1b", "IMG_1597", [(2.9, 4.3)], {}, "45", "night", {}),
    ("c1", "IMG_1581", [(0.0, 7.0)], {"a": "the"}, "45", "soft", {}),
    ("g1", "IMG_1582", [(1.0, 4.0)], {}, "45", "soft", {}),
    ("g2", "IMG_1582", [(4.2, 6.2)], {}, "45", "soft", {"join": 1}),
    ("g3", "IMG_1582", [(7.3, 9.8)], {}, "45", "soft", {"join": 1}),
    ("r1", "IMG_1583", [(1.7, 7.0)], {}, "45", "soft", {}),
    ("r2", "IMG_1583", [(12.5, 14.3)], {"breaker,": "breakup,"}, "45", "night", {}),
    ("r3", "IMG_1583", [(16.3, 17.0)], {}, "45", "night", {"join": 1}),
    ("r4", "IMG_1583", [(18.4, 19.6)], {}, "45", "night", {"join": 1, "gap": 0.5}),
    ("s1", "IMG_1585", [(0.0, 1.0)], {}, "split", "night", {}),
    ("s2", "IMG_1585", [(1.7, 3.0)], {}, "split", "night", {"join": 1}),
    ("s3", "IMG_1585", [(3.4, 4.9)], {}, "split", "night", {"join": 1}),
    ("s4", "IMG_1585", [(5.8, 7.2)], {}, "split", "night", {"join": 1}),
    ("s5", "IMG_1585", [(7.6, 9.3)], {}, "split", "night", {"join": 1, "gap": 0.3}),
    ("l1", "IMG_1586", [(0.0, 2.0)], {}, "45", "night", {}),
    ("l1b", "IMG_1586", [(2.4, 9.3)], {}, "45", "night", {"join": 1}),
    ("l2", "IMG_1586", [(10.1, 11.3)], {}, "45", "night", {"join": 1}),
    ("l3", "IMG_1586", [(12.2, 15.5)], {}, "45", "night", {"join": 1, "gap": 2.8}),
    ("m1", "IMG_1588", [(0.0, 3.2)], {}, "45", "night", {}),
    ("m1b", "IMG_1588", [(6.1, 9.1)], {}, "45", "night", {"join": 1}),
    ("m2", "IMG_1588", [(9.6, 10.95)], {}, "45", "night", {"join": 1}),
    ("w1", "IMG_1593", [(0.0, 2.9)], {"the": ""}, "45", "night", {}),
    ("w2", "IMG_1593", [(3.8, 6.1)], {}, "45", "night", {"join": 1}),
    ("w3", "IMG_1593", [(7.2, 7.4)], {}, "45", "night", {"join": 1}),
    ("w4", "IMG_1593", [(8.7, 8.9)], {}, "45", "night", {"join": 1}),
    ("w5", "IMG_1593", [(10.3, 10.4)], {}, "45", "night", {"join": 1}),
    ("w6", "IMG_1593", [(11.3, 11.4)], {}, "45", "night", {"join": 1}),
    ("w7", "IMG_1593", [(12.6, 12.7)], {}, "45", "night", {"join": 1}),
    ("e1", "IMG_1594", [(0.0, 2.8)], {}, "45", "night", {}),
]
FAIL = (63.95, 1.2, 64.85)  # yoga/IMG_2362: in, speed, the moment his back hits the mat
DANCE = ("IMG_1594", 4.5, 6.5)  # his dance, arms out (he starts at 4.4 s and slows to a stop at 6.6 s)
DANCE_IN = 1.0                   # seconds of him dancing before he shrinks into the cats
CATS = (3.5, 3.6)                # cats clip in, seconds (two cats from 3.5 s); the cat song plays from DANCE start
TAIL = 18          # extra frames on every shot, for dissolves into the next one


# ---------------------------------------------------------------- audio helpers
def audio(src: Path) -> np.ndarray:
    cache = W / "aud" / (src.stem + ".npy")
    if not cache.exists():
        cache.parent.mkdir(exist_ok=True)
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                             capture_output=True, check=True).stdout
        np.save(cache, np.frombuffer(raw, np.float32))
    return np.load(cache)


def envelope(a: np.ndarray) -> np.ndarray:
    hop = SR // 100  # 10 ms
    n = len(a) // hop
    fr = a[: n * hop].reshape(n, hop)
    return 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-7)


def snap(clip: str, A: float, B: float) -> tuple[float, float, list]:
    """Source in/out for the words starting in [A, B): starts just before the first word's onset, ends just after the
    last word's sound dies (scanned from its start, never into the next word)."""
    ws = WORDS[clip]
    sel = [w for w in ws if A - 1e-6 <= w["t"] < B]
    nxt = [w for w in ws if w["t"] >= B]
    prv = [w for w in ws if w["t"] < A - 1e-6]
    env = envelope(audio(RAW / "intro" / f"{clip}.MOV"))
    thr = max(np.percentile(env, 8) + 12, np.percentile(env, 50) - 4, env.max() - 32)
    voiced = env > thr
    i0 = int(sel[0]["t"] * 100)
    lo = int(max(sel[0]["t"] - 0.2, (prv[-1]["e"] - 0.02) if prv else 0) * 100)
    on = np.nonzero(voiced[i0:i0 + 30])[0]
    k = i0 + (on[0] if len(on) else 0)
    if k == i0:  # already voiced at whisper's start: walk back to the onset
        while k > lo and voiced[k - 1]:
            k -= 1
    a = max(lo / 100, k / 100 - 0.05)
    cap = min((nxt[0]["t"] - 0.03) if nxt else 1e9, sel[-1]["e"] + 0.35)
    j0 = max(int(sel[-1]["t"] * 100), k)
    vv = np.nonzero(voiced[j0:int(cap * 100)])[0]
    end = j = j0 + (vv[0] if len(vv) else 0)
    quiet = 0
    while j < int(cap * 100) and j < len(voiced):  # last word: run until 120 ms of quiet
        if voiced[j]:
            end, quiet = j, 0
        else:
            quiet += 1
            if quiet >= 12:
                break
        j += 1
    b = max(min(cap, end / 100 + 0.08), a + 0.2)
    b = max(b, min(cap, min(sel[-1]["e"], sel[-1]["t"] + 0.5) - 0.05))  # keep soft word endings (the s in "fails")
    n = max(1, round((b - a) * FPS))
    return round(a, 3), round(a + n / FPS, 4), sel


# ---------------------------------------------------------------- timeline
# Pace (Vish, 22 Oct, after v4): one steady speed for everything (no ramps), and dead air or looking-away pauses cut
# out like a pro edit: a line gets a beat to land (LAND, seconds on screen), then the cut goes to LEAD before his next
# word. Every jump cut is either under B-roll or gets a static punch-in.
SPEED = 1.1
CUT_DEAD_AIR = False  # Vish, 22 Oct: no cuts inside his takes; one steady speed, his own pauses
PAUSE = 0.25        # the beat after an ordinary sentence
INLINE = 0.18       # the beat at a pause inside a sentence
LEAD = 0.10         # on screen before the next word after a cut
LAND = {"h4": .3, "h6": .45, "n1b": .35, "c1": .4, "g3": .55, "r2": .5, "r3": .6, "r4": .45,
        "l1b": .35, "l2": .55, "m2": .45, "w1": .7, "w7": .4, "e1": .35}


def build() -> dict:
    # pass 1: what is kept, in source time
    runs, srcw, order = [], [], []
    last = None
    for li, (lid, clip, rr, fix, lay, look, fl) in enumerate(LINES):
        prev_b = -1.0
        for k, (A, B) in enumerate(rr):
            a, b, sel = snap(clip, A, B)
            if k == 0 and fl.get("join") and last and last[0] == clip:  # same take: start exactly where it left off
                a = last[1]
                b = a + max(1, round((b - a) * FPS)) / FPS
            if a < prev_b:  # never replay audio inside a line
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
        if "until" in fl:
            gap = round(max(0.0, fl["until"] - runs[-1]["b"]) * FPS) / FPS
        nxt = LINES[li + 1] if li + 1 < len(LINES) else None
        if not gap and lid in LAND and not (nxt and nxt[6].get("join") and nxt[1] == clip):
            # the take ends on a line that should land: let it run on a beat (never into his next word)
            later = [w["t"] for w in WORDS[clip] if w["t"] > runs[-1]["b"]]
            room = (later[0] - runs[-1]["b"] - 0.05) if later else 9.0
            src_end = DUR.get(clip, 99) - runs[-1]["b"] - 0.05
            gap = round(max(0.0, min(LAND[lid], room, src_end)) * FPS) / FPS
        runs[-1]["hold"] = gap  # the picture (and the take) keeps running, at normal speed
        runs[-1]["mute"] = bool(fl.get("mute"))  # his take is silent under the hold (a graphic covers it)
        last = (clip, runs[-1]["b"]) if gap == 0 else None
    runs.append({"line": "dance", "clip": DANCE[0], "a": DANCE[1], "b": DANCE[2], "lay": "45", "look": "night", "k": 0, "hold": 0.0})
    # pass 2: shots (continuous stretches of a take) and their time maps
    shots = []
    for r in runs:
        sh = shots[-1] if shots else None
        if sh and sh["clip"] == r["clip"] and sh["open"] and abs(sh["b"] - r["a"]) < 1e-3:
            sh["runs"].append(r)
        else:
            sh = {"clip": r["clip"], "a": r["a"], "runs": [r]}
            shots.append(sh)
        sh["b"] = r["b"]
        sh["hold"] = r["hold"]
        sh["open"] = r["hold"] == 0
    t = 0.0
    for sh in shots:
        ws = [w for w in srcw if w["clip"] == sh["clip"] and sh["a"] - 1e-3 <= w["s0"] < sh["b"] + 1e-3]
        isl = []  # spoken islands (words closer than 0.22 s belong together): [start, end, first line, last line]
        for w in ws:
            if isl and w["s0"] - isl[-1][1] < 0.22:
                isl[-1][1] = max(isl[-1][1], w["s1"])
                isl[-1][3] = w["line"]
            else:
                isl.append([w["s0"], w["s1"], w["line"], w["line"]])
        keep, cur = [], sh["a"]
        for k in range(len(isl) - 1):
            end, nxt = isl[k][1] + 0.06, isl[k + 1][0]
            boundary = isl[k][3] != isl[k + 1][2]
            land = LAND.get(isl[k][3], PAUSE) if boundary else INLINE
            if CUT_DEAD_AIR and nxt - end > (land + LEAD) * SPEED + 0.12:  # dead air: land, then cut before his next word
                keep.append([cur, min(nxt, end + land * SPEED)])
                cur = max(keep[-1][1], nxt - LEAD * SPEED)
        keep.append([cur, sh["b"]])
        cuts, rates = [], []
        for k0, k1 in keep:
            cuts.append((k0, k1))
            rates.append(SPEED)
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

    def omap(sh, s):  # source time (absolute) -> output time
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
            if r["line"] == "dance":
                continue
            L = lines.setdefault(r["line"], {"t0": r["t0"], "runs": []})
            L["runs"].append((r["t0"], r["t1"]))
            L["t1"] = r["t1"]
        for w in srcw:
            if w["clip"] == sh["clip"] and sh["a"] - 1e-3 <= w["s0"] < sh["b"] + 1e-3:
                words.append({"line": w["line"], "x": w["x"], "t0": omap(sh, w["s0"]), "t1": omap(sh, w["s1"])})
    words.sort(key=lambda w: w["t0"])
    lines = {k: lines[k] for k in order}
    dr = runs[-1]
    cats_t0 = dr["t0"] + DANCE_IN
    dance = (dr["t0"], cats_t0)
    t = cats_t0 + CATS[1]
    shots_out = [{"clip": sh["clip"], "a": sh["a"], "b": sh["b"] + sh["hold"], "t0": sh["t0"], "dur": sh["dur"], "segs": sh["segs"],
                  "look": sh["runs"][0]["look"], "cut": any(r["lay"] == "cut" for r in sh["runs"]), "mute": sh["runs"][-1].get("mute", False),
                  "runs": [runs.index(r) for r in sh["runs"]]} for sh in shots]
    return {"runs": runs, "shots": shots_out, "words": words, "lines": lines, "dance": dance, "cats": (cats_t0, t),
            "dur": round(t * FPS) / FPS}


def wt(tl: dict, lid: str, sub: str, end: bool = False, nth: int = 0) -> float:
    m = [w for w in tl["words"] if w["line"] == lid and sub.lower() in w["x"].lower()]
    return m[nth]["t1" if end else "t0"]


# ---------------------------------------------------------------- frame extraction + film grade
# extract() only registers a job; run_jobs() does them in parallel: ffmpeg cut + film LUT, then per frame the matte
# (speaker shots), the head track, and film.finish() (light pool, lens defocus, halation, diffusion).
JOBS: list[dict] = []
LUTS = W / "luts"


def extract(src: Path, a: float, n: int, look: str | None, size: str, name: str, speed: float = 1.0,
            matte: bool = False, cut: bool = False, segs: list | None = None) -> Path:
    d = FR / name
    if not (d / "finished").exists() and not any(j["d"] == str(d) for j in JOBS):
        JOBS.append(dict(src=str(src), a=a, n=n, look=look, size=size, d=str(d), speed=speed, matte=matte, cut=cut, segs=segs))
    return d


def retime(segs: list) -> str:
    """select + setpts: keep only the kept stretches of the take (cuts), lay them end to end at their speed; the last
    one runs on past the end for the dissolve tail."""
    sel = "+".join(f"between(t\\,{s0 - 0.001:.4f}\\,{(s1 if i < len(segs) - 1 else s1 + 2.0):.4f})" for i, (s0, s1, o0, r) in enumerate(segs))
    e = None
    for s0, s1, o0, r in reversed(segs):
        term = f"({o0:.5f}+(T-{s0:.5f})/{r:.5f})"
        e = term if e is None else f"if(lt(T\\,{s1:.5f})\\,{term}\\,{e})"
    return f"select='{sel}',setpts='({e})/TB'"


def count(d: Path) -> int:
    return len(list(d.glob("*.jpg")))


def run_job(j: dict) -> str:
    import cv2
    from scipy.ndimage import gaussian_filter1d
    d, src, look = Path(j["d"]), Path(j["src"]), j["look"]
    d.mkdir(parents=True, exist_ok=True)
    if not (d / "done").exists():
        pts = retime(j["segs"]) + "," if j.get("segs") else (f"setpts=PTS/{j['speed']}," if j["speed"] != 1 else "")
        grade = film.chain(src, look, LUTS) + "," if look else ""
        vf = f"{pts}fps={FPS},{grade}scale={j['size']}:flags=lanczos,format=yuvj420p"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-threads", "2", "-ss", f"{j['a']:.3f}", "-i", str(src), "-vf", vf,
                        "-frames:v", str(j["n"]), "-q:v", "2", str(d / "%05d.jpg")], check=True)
        (d / "done").write_text("1")
    files = sorted(d.glob("*.jpg"))
    if look is None:
        (d / "finished").write_text("1")
        return str(d)
    alphas, centers, track = [None] * len(files), [None] * len(files), []
    if j["matte"]:
        mt = film.Matte(threads=1)
        first = cv2.imread(str(files[0]))
        mt(first), mt(first)  # settle the recurrent state on the first frame
        for i, f in enumerate(files):
            al = mt(cv2.imread(str(f)))
            alphas[i] = al.astype(np.float16)
            centers[i] = film.pool_center(cv2.resize(al, (al.shape[1] // 2, al.shape[0] // 2)))
            m = (al > 0.5).astype(np.uint8)
            cnt, lab, st, _ = cv2.connectedComponentsWithStats(m)
            if cnt > 1:
                m = lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
                top = np.nonzero(m.any(1))[0][0]
                hh = int(0.15 * m.shape[0])
                yy, xx = np.nonzero(m[top:top + hh])
                track.append([float(xx.mean() * 2), float((top + min(hh, yy.max() + 1) / 2) * 2)])
            else:
                track.append(None)
        # smooth the head track and the light pool over the shot (no breathing)
        xs = np.array([p[0] if p else np.nan for p in track])
        ys = np.array([p[1] if p else np.nan for p in track])
        for arr, dflt in ((xs, 960.0), (ys, 300.0)):
            ok = ~np.isnan(arr)
            arr[~ok] = np.interp(np.nonzero(~ok)[0], np.nonzero(ok)[0], arr[ok]) if ok.any() else dflt
        def lock(v, dz):  # a locked-off camera that only drifts when he would leave the frame
            c, out = float(np.median(v[:15])), []
            for x in v:
                c = x - dz if x > c + dz else (x + dz if x < c - dz else c)
                out.append(c)
            return gaussian_filter1d(np.array(out), 20, mode="nearest")
        xs, ys = lock(gaussian_filter1d(xs, 6, mode="nearest"), 150), lock(gaussian_filter1d(ys, 6, mode="nearest"), 100)
        (d / "track.json").write_text(json.dumps([[round(float(a), 1), round(float(b), 1)] for a, b in zip(xs, ys)]))
        cs = gaussian_filter1d(np.array(centers, np.float64), 12, axis=0, mode="nearest")
        centers = [tuple(c) for c in cs]
    if j["cut"]:
        (d / "cut").mkdir(exist_ok=True)
    for i, f in enumerate(files):
        bgr = cv2.imread(str(f))
        al = alphas[i].astype(np.float32) if alphas[i] is not None else None
        out = film.finish(bgr, look, al, centers[i])
        cv2.imwrite(str(f), out, [cv2.IMWRITE_JPEG_QUALITY, 93])
        if j["cut"]:  # the cut-out comes from the graded frame before any glow, with the wall's colour cleaned off the edge
            h, w = bgr.shape[:2]
            a = cv2.resize(np.clip(al, 0, 1), (w, h), interpolation=cv2.INTER_CUBIC)
            a = np.clip((a - 0.1) / 0.9, 0, 1)  # drop the matte's faint tail
            a = cv2.GaussianBlur(cv2.erode(a, np.ones((5, 5), np.uint8)), (5, 5), 0)
            core = (a > 0.97).astype(np.float32)
            fb = bgr.astype(np.float32)
            wsum = cv2.GaussianBlur(core, (0, 0), 10)
            fg = cv2.GaussianBlur(fb * core[..., None], (0, 0), 10) / np.maximum(wsum, 1e-4)[..., None]
            fg = np.where((core[..., None] > 0) | (wsum[..., None] < 0.02), fb, fg)
            cv2.imwrite(str(d / "cut" / (f.stem + ".webp")), np.dstack([np.clip(fg, 0, 255).astype(np.uint8), (a * 255).astype(np.uint8)]),
                        [cv2.IMWRITE_WEBP_QUALITY, 88])
    (d / "finished").write_text("1")
    return str(d)


def run_jobs(workers: int = 4) -> None:
    import shutil
    from concurrent.futures import ProcessPoolExecutor
    if not JOBS:
        return
    for j in JOBS:  # a shot interrupted mid-grade would be graded twice: start it again from the source
        d = Path(j["d"])
        if d.exists() and not (d / "finished").exists():
            shutil.rmtree(d)
    if LUTS.exists():
        shutil.rmtree(LUTS)
    for look in film.LOOKS:
        film.write_lut(look, LUTS / f"film-{look}.cube")
    jobs = sorted(JOBS, key=lambda j: -j["n"] * (3 if j["matte"] else 1))
    print(f"grading {len(jobs)} shots ({sum(j['n'] for j in jobs)} frames) on {workers} workers", flush=True)
    with ProcessPoolExecutor(workers) as ex:
        for k, d in enumerate(ex.map(run_job, jobs), 1):
            print(f"  {k}/{len(jobs)} {Path(d).name}", flush=True)
    JOBS.clear()


def key_cats(n: int) -> Path:
    d = FR / "cats"
    if (d / "cut").exists() and len(list((d / "cut").glob("*.webp"))) >= n:
        return d
    import cv2
    src = FR / "cats"
    run_job(dict(src=str(RAW / "intro" / "cats_snapgram.mp4"), a=CATS[0], n=n, look=None, size="720:1280", d=str(src), speed=1.0,
                 matte=False, cut=False))
    (d / "cut").mkdir(exist_ok=True)
    for f in sorted(src.glob("*.jpg"))[:n]:
        bgr = cv2.imread(str(f))
        b, g, r = [c.astype(np.float32) for c in cv2.split(bgr)]
        k = g - np.maximum(r, b)  # greenness
        a = np.clip(1 - (k - 40) / 60, 0, 1)
        a = cv2.GaussianBlur(a, (3, 3), 0)
        g2 = np.minimum(g, np.maximum(r, b) + 8)  # despill
        out = cv2.merge([b, g2, r, a * 255]).astype(np.uint8)
        cv2.imwrite(str(d / "cut" / (f.stem + ".webp")), out, [cv2.IMWRITE_WEBP_QUALITY, 90])
    return d


# ---------------------------------------------------------------- the picture + graphics plan
def plan(tl: dict) -> dict:
    L = tl["lines"]
    items, cues, geoms, bgs, nocap = [], [], [], [], []
    T = lambda lid, s, **k: wt(tl, lid, s, **k)  # noqa: E731

    def B(t0, t1, rel, src_in, geom, look="day", kb=(1.0, 1.08), speed=1.0, size=None, name=None, fy=0.5, tx=None):
        src = RAW / rel
        n = max(1, round((t1 - t0) * FPS)) + TAIL
        pr = probe(src)
        w, h = int(pr.get("width", 1080)), int(pr.get("height", 1920))
        rot = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream_side_data=rotation",
                              "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout.strip()
        if rot in ("90", "-90", "270", "-270"):
            w, h = h, w
        size = size or ("1080:-2" if h > w else "-2:1080")
        nm = name or f"b_{Path(rel).stem}_{src_in:.2f}_{n}_{speed}"
        d = extract(src, src_in, n, look, size, nm, speed)
        items.append({"t0": round(t0, 4), "t1": round(t1, 4), "dir": str(d), "n": n, "kind": "broll", "geom": geom, "kb": kb, "fy": fy,
                      "src": str(src), "src_in": src_in, "speed": speed})
        if tx == "zoom":  # pushes in through a blur, a whoosh peaking on the cut
            items[-1].update(tx="zoom", txd=0.3, dx=0.24)
            S("whoosh", t0, 0.11)

    # talking: one shot per continuous stretch of a take (graded, matted, framed and re-timed as one)
    for sh in tl["shots"]:
        n = round(sh["dur"] * FPS) + TAIL
        key = hashlib.md5(json.dumps(sh["segs"]).encode()).hexdigest()[:6]
        d = extract(RAW / "intro" / f"{sh['clip']}.MOV", sh["a"], n, sh["look"], "1920:1080", f"s_{sh['clip']}_{sh['a']:.3f}_{n}_{key}",
                    matte=True, cut=sh["cut"], segs=sh["segs"])
        cuts_out = [round(sh["t0"] + o0, 4) for (s0, s1, o0, rr), prev in zip(sh["segs"][1:], sh["segs"]) if abs(s0 - prev[1]) > 1e-3]
        zc = [[t, 1.08 if k % 2 == 0 else 1.0] for k, t in enumerate(cuts_out)]
        for ri in sh["runs"]:
            r = tl["runs"][ri]
            items.append({"zc": [] if sh["cut"] else zc, "t0": round(r["t0"], 4), "t1": round(r["t1"] + r["hold"], 4), "dir": str(d), "n": n,
                          "off": round((r["t0"] - sh["t0"]) * FPS), "kind": "cut" if r["lay"] == "cut" else "talk",
                          "geom": {"cut": "full", "full": "full", "45": "f45", "split": "split"}[r["lay"]], "track": None, "z": 1.0,
                          "shot": d.name})

    def run_items(lid):
        return [i for i in items if i["kind"] in ("talk", "cut") and L[lid]["t0"] - 1e-3 <= i["t0"] < L[lid]["t1"] - 1e-3]

    def zoom(lid, z0, z1, t0=None, t1=None):
        for i in run_items(lid):
            i["zk"] = [[t0 if t0 is not None else L[lid]["t0"], z0], [t1 if t1 is not None else L[lid]["t1"], z1]]

    def seq(lid, text, start=0):
        """Words for a title, timed to when he says them. text: tokens matched in order to the transcript of the line;
        *word* = italic, ^word^ = amber, / = line break."""
        spoken = [w for w in tl["words"] if w["line"] == lid]
        out, j = [], start
        norm = lambda x: re.sub(r"[^a-z0-9%]", "", x.lower())  # noqa: E731
        for tok in text.split():
            if tok == "/":
                out.append(["\n", 0])
                continue
            html, plain = tok, tok.strip("*^")
            if tok.startswith("*"):
                html = f"<i>{plain}</i>"
            if tok.startswith("^"):
                html = f"<span class=am>{plain}</span>"
            k = next((m for m in range(j, len(spoken)) if norm(spoken[m]["x"]) == norm(plain)), None)
            tt = spoken[k]["t0"] if k is not None else (out[-1][1] if out else L[lid]["t0"])
            j = k + 1 if k is not None else j
            out.append([html, round(tt, 3)])
        return out

    fx = []

    def S(name, t, g, **o):  # a sound on the picture: whooshes peak at t, everything else starts at t
        fx.append([name, round(t, 3), g, o])

    def ticks(t0, d, n, ease, g=0.05, gap=0.04):  # one tick per step of a rolling number
        last = -1.0
        for k in range(1, n + 1):
            u = next((j / 400 for j in range(401) if ease(j / 400) * n >= k), 1.0)
            if t0 + u * d - last >= gap:
                last = t0 + u * d
                S("tick", last, g, f=1.0 + 0.25 * (k % 2))

    eo = lambda u: 1 - (1 - u) ** 3  # noqa: E731
    eio = lambda u: 4 * u ** 3 if u < .5 else 1 - (-2 * u + 2) ** 3 / 2  # noqa: E731

    def title(t0, t1, words=None, html=None, font="serif", size=96, y=None, band=False, z=45, **k):
        cues.append({"type": "title", "t0": round(t0, 3), "t1": round(t1, 3), "words": words, "html": html, "font": font, "size": size,
                     "y": y, "band": band, "z": z, **k})

    END = L["e1"]["t1"]
    cues.append({"type": "week", "t0": L["n1"]["t0"] + 0.5, "t1": END, "z": 46,
                 "hide": [[L["c1"]["t0"], L["c1"]["t1"]], [L["n1"]["t1"], L["n1b"]["t0"]]]})

    # ---- HOOK: his real room, softened behind him; the words tuck behind his head as he says them
    for lid in ("h1", "h2", "h3", "h4", "h5"):  # one slow push across the whole hook take
        zoom(lid, 1.0, 1.06, L["h1"]["t0"], L["h5"]["t1"])
    title(-0.6, L["h1"]["t1"], html="I just<br><i>broke up.</i>", size=250, y=170, z=20)  # on screen from frame one
    S("boom", 0.0, 0.2)
    h2 = L["h2"]["t0"]  # 40K rolls up like an odometer behind his head, ticking, and slams
    cues.append({"type": "counter", "t0": h2, "t1": L["h2"]["t1"], "digits": "40", "suffix": "K", "size": 430, "y": 130, "z": 20,
                 "roll": 0.42, "stagger": 0.12})
    ticks(h2, 0.42, 24, eo, 0.055, 0.035)
    S("thump", h2 + 0.54, 0.3)
    title(T("h2", "in"), L["h2"]["t1"], seq("h2", "*in* *debt.*"), size=170, y=1400, z=40)
    B(T("h3", "moved") - 0.04, T("h3", "where"), "travel/cities/IMG_8516.MOV", 0.6, "full", kb=(1.0, 1.04), tx="zoom")
    title(T("h3", "moved"), T("h3", "where"), html="New country.", font="sans", size=140, y=1400, z=40)
    title(T("h3", "speak"), L["h3"]["t1"], html="<span class=am>0%</span>", font="sans", size=360, y=70, z=20)
    S("pop", T("h3", "speak"), 0.12)
    S("click", T("h3", "language"), 0.08)
    S("thump", T("h4", "no"), 0.16)
    S("thump", T("h4", "job"), 0.2)
    S("airport-ding", T("h5", "booked") - 0.05, 0.07)
    title(T("h3", "language"), L["h3"]["t1"], html="<i>German.</i>", size=170, y=1400, z=40)
    title(L["h4"]["t0"], L["h4"]["t1"], seq("h4", "No / job."), font="sans", size=300, y=160, z=20)
    title(L["h5"]["t0"], T("h5", "to") - 0.04, seq("h5", "Booked a / *flight.*"), size=230, y=170, z=20)
    B(T("h5", "to") - 0.04, L["h5"]["t1"], "travel/planes/IMG_1110.MOV", 4.0, "full", kb=(1.04, 1.0), tx="zoom")
    S("jet-whoosh", T("h5", "to") - 0.5, 0.08, cut=2.4, fin=0.3)
    S("paper-slide", T("h5", "to") + 0.05, 0.08)
    S("rwhoosh", L["h6"]["t0"], 0.1)  # into "What am I doing?": a reverse swell and a low hit, no pause
    S("boom", L["h6"]["t0"], 0.3)
    cues.append({"type": "pass", "t0": T("h5", "to"), "t1": L["h5"]["t1"] + 0.05, "z": 40})
    zoom("h6", 1.0, 1.08, L["h6"]["t0"], L["h6"]["t1"] + 0.3)
    title(L["h6"]["t0"], L["h6"]["t1"] + 0.3, seq("h6", "*What* *am* *I* / *doing?*"), size=170, y=1250, z=40)
    nocap += [[0, L["h6"]["t1"] + 0.3]]

    # ---- the 4:5 frame from "Hey, I'm Vish"
    geoms.append([L["n1"]["t0"] - 0.1, "f45", 0.6])
    bgs.append([0, L["n1b"]["t1"], "ink"])
    S("whoosh", L["n1"]["t0"] + 0.2, 0.07)
    # Vish, 22 Oct (v9, refs @sakchham_films, @ayyitsjamie): on "I'm Vish" the frame freezes, he gets a white sticker
    # outline and his labels pop on; after "27" the music stops dead and his passport photos land on a page, kid to now
    tf0, ph0 = T("n1", "vish") - 0.03, L["n1"]["t1"] + 0.02
    it_n1 = next(i for i in items if i["kind"] == "talk" and abs(i["t0"] - L["n1"]["t0"]) < 1e-3)
    it_n1["freeze"] = [round(tf0, 4), round(ph0 + 0.05, 4), it_n1["off"] + int((tf0 - it_n1["t0"]) * FPS)]
    tags = [[None, "This is Vish", tf0 + 0.03, 80, 420, -4, 58], ["mobile_phone", "Social media", tf0 + 0.2, 560, 560, 5, 40],
            ["person_in_lotus_position", "Yoga", tf0 + 0.33, 60, 930, -6, 40], ["robot", "AI", tf0 + 0.46, 790, 900, 4, 40],
            ["airplane", "Travel", tf0 + 0.59, 690, 1230, -3, 40], [None, "27", T("n1", "27"), 110, 1190, 6, 96]]
    cues.append({"type": "tags", "t0": tf0, "t1": ph0 + 0.05, "items": [[a, b, round(c, 3), x, y, r, z_] for a, b, c, x, y, r, z_ in tags], "z": 44})
    S("shutter-old", tf0, 0.12, cut=0.5)
    S("boom", tf0, 0.12)
    for k_, tg in enumerate(tags):
        S("pop", tg[2], 0.12, f=1.0 + 0.07 * k_)
    photos = sorted((W / "photos").glob("p*.jpg"))
    ptimes = [round(ph0 + 0.12 + 0.24 * k, 3) for k in range(len(photos))]
    cues.append({"type": "photos", "t0": ph0, "t1": L["n1b"]["t0"] + 0.02, "files": [str(x) for x in photos], "times": ptimes,
                 "text_t": ptimes[-1] + 0.3, "w": 560, "z": 47})
    for k_, tp in enumerate(ptimes):
        S("click", tp, 0.14, f=0.9 + 0.04 * k_)
        S("thump", tp, 0.05)
    S("thump", ptimes[-1] + 0.3, 0.14)
    nocap += [[L["n1"]["t0"], L["n1b"]["t0"]]]
    # Vish, 22 Oct (v9): say that he builds with AI and that this video was edited by Claude
    cues.append({"type": "sticker", "t0": T("n1b", "this") - 0.05, "t1": L["n1b"]["t1"] + 0.35, "emoji": "robot", "z": 44,
                 "text": "Edited 100% by AI.", "sub": "every cut, sound + graphic: Claude", "x": 175, "y": 1235, "rot": -3})
    S("pop", T("n1b", "this") - 0.05, 0.14, f=0.85)
    S("ping", T("n1b", "this") + 0.08, 0.05)

    # ---- the soft middle: paper
    bgs.append([L["c1"]["t0"], L["r2"]["t0"] + 0.5, "paper"])
    S("paper-slide", L["c1"]["t0"] - 0.05, 0.07)
    title(L["c1"]["t0"], L["c1"]["t1"], seq("c1", "I always wanted to start this. / But I never had the *confidence* / or the discipline."),
          size=70, band=True, shadow=0, lh=1.08)
    nocap += [[L["c1"]["t0"], L["c1"]["t1"]]]
    zoom("c1", 1.25, 1.25)
    title(L["g1"]["t0"], T("g1", "moved") - 0.04, seq("g1", "Quit my job."), font="sans", size=96, band=True, shadow=0)
    S("click", L["g1"]["t0"] + 0.05, 0.08)
    title(T("g1", "moved"), L["g1"]["t1"] + 0.3, seq("g1", "Germany."), font="sans", size=96, band=True, shadow=0)
    B(T("g1", "moved") - 0.03, L["g1"]["t1"] + 0.3, "travel/cities/IMG_7352.MOV", 1.0, "f45", kb=(1.0, 1.04), tx="zoom")
    title(L["g3"]["t0"], L["g3"]["t1"], seq("g3", "I doubted my / *whole* *life.*"), size=96, band=True, shadow=0)
    nocap += [[L["g3"]["t0"], L["g3"]["t1"]]]
    zoom("g3", 1.0, 1.04)
    title(L["r1"]["t0"], T("r1", "220") - 0.05, seq("r1", "No friends. / No family."), font="sans", size=88, band=True, shadow=0)
    wall_end = L["r2"]["t0"] + 0.6  # stays up across the cut into the next take, then fades
    cues.append({"type": "wall", "t0": T("r1", "220") - 0.1, "t1": wall_end, "z": 42, "count_t": T("r1", "220"),
                 "count_d": max(0.9, T("r1", "rejections") - T("r1", "220") + 0.3), "stamp_t": T("r1", "rejections") + 0.2})
    nocap += [[T("r1", "220") - 0.1, wall_end]]
    for k_ in range(4):
        S("paper-slide", T("r1", "220") + k_ * 0.22, 0.07)
    S("thump", T("r1", "rejections") + 0.2, 0.14)
    title(L["r2"]["t0"] + 0.4, L["r3"]["t0"], seq("r2", "And honestly, / the breakup,"), size=88, band=True)
    title(L["r3"]["t0"], L["r4"]["t0"], seq("r3", "*that* *one* *hurt.*"), size=96, band=True)
    title(L["r4"]["t0"], L["r4"]["t1"] + 0.5, seq("r4", "But this is a / good ^distraction.^"), size=88, band=True)
    nocap += [[L["r2"]["t0"], L["r4"]["t1"] + 0.5]]
    zoom("r2", 1.0, 1.05, L["r2"]["t0"], L["r4"]["t1"])
    for lid in ("r3", "r4"):
        zoom(lid, 1.0, 1.05, L["r2"]["t0"], L["r4"]["t1"])

    # ---- what I've got: the speaker below, his stats above
    geoms.append([L["s1"]["t0"] - 0.1, "split", 0.6])
    bgs.append([L["r2"]["t0"] + 0.5, L["l2"]["t0"], "ink"])
    s5e = L["s5"]["t1"]
    fills = [["Social media", 8, "", T("s2", "social")], ["Influencer marketing", 9, "", T("s3", "influencer")],
             ["Yoga", 7, "", T("s4", "yoga")], ["Building with AI", 8, "", T("s4", "yoga") + 0.7],
             ["Master's", 9, "thesis · Feb", T("s5", "master")],
             ["German", 1, "1 / 10", T("s5", "master") + 0.25], ["Job offers", 0, "0 of 220", T("s5", "master") + 0.4],
             ["Remote income", 0, "0", T("s5", "master") + 0.55]]
    cues.append({"type": "stats", "t0": L["s1"]["t0"] + 0.2, "t1": L["l1"]["t0"] + 0.75, "scatter": L["l1"]["t0"] + 0.05, "z": 40,
                 "fills": fills})
    S("whoosh", L["s1"]["t0"] + 0.2, 0.08)
    for k_, (_, v, _, ft) in enumerate(fills):
        S("pop", ft, 0.1 if v > 1 else 0.08, f=(1.0 + 0.08 * k_) if v > 1 else 0.72)
    B(T("s4", "taught") - 0.03, L["s4"]["t1"], "travel/yoga/IMG_2362.MOV", 22.6, "split", kb=(1.0, 1.03), tx="zoom")

    # ---- life is all over the place
    # Vish, 22 Oct (v9): animate it instead of showing friends. He stays in the speaker box below; above him the stat
    # card breaks apart, the words land all over the place, then a 3D juggler, the to-do list and the debt counter.
    nocap += [[L["l1"]["t0"], L["l1"]["t1"]]]
    l0, so = L["l1"]["t0"], [T("l1b", "so", nth=k) for k in range(3)]
    words = [["all", T("l1", "all"), 300, 330, -11, 170, 0], ["over", T("l1", "over"), 770, 300, 8, 170, 0],
             ["the", T("l1", "the"), 320, 610, 7, 120, 0], ["place.", T("l1", "place"), 720, 610, -6, 200, 1],
             ["right now.", T("l1", "right"), 540, 850, 0, 64, 0]]
    cues.append({"type": "chaos", "t0": l0 + 0.05, "t1": so[0] + 0.1, "lead_t": T("l1", "life"), "z": 41, "words": words,
                 "objs": ["laptop", "airplane", "books", "mobile_phone", "hot_beverage", "graduation_cap", "money_with_wings",
                          "backpack", "alarm_clock", "camera_with_flash"]})
    S("whoosh", l0 + 0.3, 0.13, d=0.6)
    S("swoosh-windy", l0 + 0.1, 0.05)
    for w_ in words[:4]:
        S("thump", w_[1] - 0.04, 0.15 if w_[0] != "place." else 0.2)
        S("click", w_[1] - 0.04, 0.05)
    S("tick", words[4][1], 0.05)
    balls = [["mobile_phone", so[0]], ["robot", T("l1b", "many")], ["clapper_board", T("l1b", "interests")],
             ["person_in_lotus_position", so[1]], ["airplane", T("l1b", "hobbies") - 0.1], ["snow-capped_mountain", T("l1b", "hobbies") + 0.15]]
    cues.append({"type": "juggle", "t0": so[0] - 0.15, "t1": so[2] + 0.05, "fig": "person_juggling", "z": 41, "balls": balls,
                 "heads": [["interests.", T("l1b", "interests")], ["hobbies.", T("l1b", "hobbies")]]})
    S("whoosh", so[0] - 0.05, 0.08)
    for k_, (_, tb) in enumerate(balls):
        S("pop", tb, 0.11, f=1.0 + 0.09 * k_)
    td0 = so[2] - 0.08
    rows = [["graduation_cap", "Finish my master's"], ["speaking_head", "Learn German"], ["laptop", "Build a remote income"],
            ["world_map", "Travel the world"]]
    cues.append({"type": "todo", "t0": td0, "t1": T("l1b", "the") - 0.02, "z": 41,
                 "rows": [r + [td0 + 0.25 + 0.3 * k] for k, r in enumerate(rows)]})
    S("whoosh", td0 + 0.12, 0.1)
    for k_ in range(len(rows)):
        S("click", td0 + 0.25 + 0.3 * k_, 0.09, f=1.0 + 0.06 * k_)
    dt0, land = T("l1b", "the") - 0.1, T("l1b", "debt") + 0.05
    cues.append({"type": "debt", "t0": dt0, "t1": L["l2"]["t0"] + 0.05, "value": 40000, "land": land, "z": 41})
    S("whoosh", dt0 + 0.1, 0.08)
    ticks(dt0 + 0.08, land - dt0 - 0.08, 20, eo, 0.05, 0.045)
    S("thump", land, 0.28)
    S("boom", land, 0.14)
    # the turn: music out, black, his words alone
    bgs.append([L["l2"]["t0"], L["l3"]["t0"], "black"])
    geoms.append([L["l2"]["t0"] - 0.05, "f45", 0.6])
    title(L["l2"]["t0"], L["l3"]["t0"] + 0.2, seq("l2", "But one thing / is *sure,*"), size=96, band=True)
    nocap += [[L["l2"]["t0"], L["l3"]["t1"]]]
    bgs.append([L["l3"]["t0"], L["m1"]["t0"], "ink"])
    B(T("l3", "work") - 0.03, T("l3", "travel") - 0.02, "travel/cafes/IMG_3995.MOV", 0.2, "f45", kb=(1.0, 1.04), tx="zoom")
    title(T("l3", "work"), T("l3", "travel") - 0.02, seq("l3", "Work remotely."), font="sans", size=96, band=True)
    # the drop: the frame opens to full screen, the montage cuts on the music's beat
    drop = T("l3", "travel") - 0.02
    geoms.append([drop, "full", 0.5])
    mont = [("travel/ocean/IMG_5708.MOV", 3.5), ("travel/bike/IMG_1754.MOV", 9.4), ("travel/ocean/IMG_4594.MOV", 4.0),
            ("travel/friends/IMG_5615.MOV", 7.0), ("travel/ocean/IMG_1503.MOV", 10.5)]
    end = L["m1"]["t0"]
    for i, (rel, s) in enumerate(mont):
        t0, t1 = drop + i * LBEAT, (drop + (i + 1) * LBEAT if i < len(mont) - 1 else end)
        B(t0, t1, rel, s, "full", kb=(1.0, 1.04))
        items[-1].update(dx=0.35) if i == 0 else items[-1].update(dx=0.0, tx="punch", txd=0.22)
    S("boom", drop, 0.3)
    S("whoosh", drop, 0.12)
    S("riser-drama", drop - 1.6, 0.05, tail=1.6)
    title(drop + 0.05, L["l3"]["t1"] + 1.2, seq("l3", "*travel* / *the* *world.*"), size=200, y=700, z=45)
    geoms.append([L["m1"]["t0"] - 0.1, "f45", 0.6])
    S("whoosh", L["m1"]["t0"] + 0.15, 0.07)

    # ---- max out every stat (push-ups)
    bgs.append([L["m1"]["t0"], END, "ink"])
    title(T("m1", "max"), L["m1b"]["t1"], seq("m1", "Max out / ^every^ ^skill.^"), font="sans", size=96, band=True)
    cues.append({"type": "chips", "t0": T("m1", "max") + 0.6, "t1": L["m1b"]["t0"] + 2.6, "step": 0.75, "z": 40,
                 "items": ["confidence", "discipline", "German", "courage"]})
    for k_ in range(4):
        S("pop", T("m1", "max") + 0.6 + 0.75 * k_, 0.1, f=1.0 + 0.1 * k_)
    title(L["m2"]["t0"], L["m2"]["t1"] + 0.2, seq("m2", "I have to / make this *happen.*"), size=88, band=True)
    nocap += [[L["m2"]["t0"], L["m2"]["t1"] + 0.2]]
    zoom("m2", 1.0, 1.05)
    # week one
    title(L["w1"]["t0"], T("w1", "week") - 0.05, seq("w1", "I don't know / *how* yet,"), size=88, band=True)
    cues.append({"type": "weekcard", "t0": T("w1", "week") - 0.1, "t1": L["w1"]["t1"] + 0.6, "z": 44, "strobe": 0.44})
    for k_ in range(4):
        S("click", T("w1", "week") - 0.1 + 0.11 * k_, 0.12, f=1.0 + 0.1 * (k_ % 2))
    S("boom", T("w1", "week") + 0.34, 0.24)
    S("type-bell", T("w1", "week") + 0.15, 0.05)
    nocap += [[L["w1"]["t0"], L["w1"]["t1"] + 0.6]]
    title(L["w2"]["t0"], L["w7"]["t1"], seq("w2", "Every week, / ^everything.^"), font="sans", size=96, band=True)
    nocap += [[L["w2"]["t0"], L["w7"]["t1"]]]
    # fresh footage for the promise (nothing seen earlier in the reel), Vish 22 Oct
    flashes = [("w3", "The trials.", "travel/yoga/IMG_2362.MOV", 45.0, 1.0, (1.0, 1.04), 0.5),  # kicking up into a handstand
               ("w4", "The fails.", "travel/yoga/IMG_2362.MOV", FAIL[0], FAIL[1], (1.04, 1.0), 0.5),  # and toppling onto his back
               ("w5", "The work.", "travel/cafes/IMG_7358.MOV", 3.0, 1.0, (1.03, 1.0), 0.5),
               ("w6", "The travel.", "travel/planes/IMG_6726.MOV", 2.1, 1.0, (1.03, 1.0), 0.5)]
    for lid, lab, rel, s, sp, kb, fy in flashes:
        t0, t1 = L[lid]["t0"] - 0.02, L[lid]["t1"]
        if rel:
            B(t0, t1, rel, s, "f45", kb=kb, speed=sp, fy=fy, tx="zoom")
            items[-1]["dx"] = 0.16
            if lid == "w4":
                S("k:impact-sounds/Audio/impactSoft_heavy_000", t0 + (FAIL[2] - s) / sp, 0.3)
                S("boom", t0 + (FAIL[2] - s) / sp, 0.12)
        else:
            cues.append({"type": "mail", "t0": t0, "t1": t1, "z": 38})
        cues.append({"type": "label", "t0": t0, "t1": t1, "text": lab, "z": 44})
        S("click", t0 + 0.02, 0.07)
    # come with me, the dance, the cats
    title(L["e1"]["t0"], L["e1"]["t1"] + 0.2, seq("e1", "So come with me / and join my *journey.*"), size=88, band=True)
    d0, d1 = tl["dance"]
    title(d0 + 0.05, d1 + 0.3, html="<i>me, trying to max out<br>my dance stat:</i>", size=80, band=True)
    S("pop", d0 + 0.05, 0.08, f=0.9)
    nocap += [[L["e1"]["t0"], tl["dur"]]]
    c0, c1 = tl["cats"]
    cd = key_cats(round(CATS[1] * FPS))
    # the morph: his dancing frame shrinks into the middle and dissolves as the cats come into focus there
    M = 0.7
    for it in items:
        if it["kind"] == "talk" and abs(it["t1"] - c0) < 0.05:
            it["t1"] = round(c0 + M, 4)
    cues.append({"type": "cats", "t0": c0 - 0.1, "t1": c1 + 1, "dir": str(cd / "cut"), "n": round(CATS[1] * FPS), "z": 30, "morph": M})
    bgs.append([c0 + M, c1 + 1, "paper"])
    S("whoosh", c0 + 0.1, 0.1, d=0.6)
    S("pop", c0 + 0.1, 0.1)
    S("pop", c0 + 0.25, 0.1, f=1.15)
    S("pencil-scribble", c0 + 0.3, 0.05, cut=0.6)
    S("tick", c0 + 0.6, 0.05)
    geoms.append([c0 - 0.1, "none", M])
    hush = [[L["h6"]["t0"] - 0.03, L["n1"]["t0"] - 0.02], [ph0, L["n1b"]["t0"] - 0.01],
            [L["r3"]["t0"] - 0.05, L["r4"]["t0"] - 0.05], [L["l2"]["t0"] - 0.02, L["l3"]["t0"] - 0.02]]
    return {"items": items, "cues": cues, "geoms": geoms, "bgs": bgs, "nocap": nocap, "sfx": fx, "hush": hush}


def freeze_cut(d: Path, idx: int, ring: int = 9) -> str:
    """One frame of a shot as a sticker: Vish cut out (RVM matte), a white outline around him, transparent elsewhere."""
    import cv2
    out = d / f"freeze_{idx}.webp"
    if out.exists():
        return str(out)
    files = sorted(d.glob("*.jpg"))
    mt = film.Matte(threads=2)
    for f in files[max(0, idx - 8): idx]:  # settle the recurrent matte on the frames before
        mt(cv2.imread(str(f)))
    bgr = cv2.imread(str(files[idx]))
    h, w = bgr.shape[:2]
    a = cv2.resize(np.clip(mt(bgr), 0, 1).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
    core = (a > 0.5).astype(np.uint8)
    cnt, lab, st, _ = cv2.connectedComponentsWithStats(core)
    if cnt > 1:
        core = (lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
    a = a * cv2.dilate(core, np.ones((5, 5), np.uint8))
    rim = cv2.GaussianBlur(cv2.dilate(core, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * ring + 1, 2 * ring + 1))).astype(np.float32), (0, 0), 1.2)
    rgb = bgr.astype(np.float32) * a[..., None] + 255.0 * (1 - a[..., None])
    alpha = np.maximum(a, rim)
    cv2.imwrite(str(out), np.dstack([np.clip(rgb, 0, 255).astype(np.uint8), (alpha * 255).astype(np.uint8)]), [cv2.IMWRITE_WEBP_QUALITY, 92])
    return str(out)


def captions(tl: dict, nocap: list) -> list:
    caps, cur = [], []
    def flush():
        if cur:
            caps.append({"t0": cur[0]["t0"], "t1": cur[-1]["t1"], "w": [[w["x"], round(w["t0"], 3), round(w["t1"], 3)] for w in cur]})
    for w in tl["words"]:
        if any(a - 1e-3 <= w["t0"] < b for a, b in nocap):
            flush(); cur = []
            continue
        if cur and (len(cur) >= 6 or len(" ".join(x["x"] for x in cur + [w])) > 30 or cur[-1]["x"][-1] in ".?"
                    or (cur[-1]["x"][-1] == "," and len(cur) >= 3) or w["t0"] - cur[-1]["t1"] > 0.7):
            flush(); cur = []
        cur.append(w)
    flush()
    for i, c in enumerate(caps):  # hold until the next chunk (max 0.4 s past the last word)
        nxt = caps[i + 1]["t0"] if i + 1 < len(caps) else c["t1"] + 0.4
        c["t1"] = round(min(nxt, c["t1"] + 0.4), 3)
        for a, b in nocap:  # never hang over a full-screen graphic or a label
            if c["t0"] < a < c["t1"]:
                c["t1"] = round(a, 3)
    return caps


def prep() -> dict:
    tl = build()
    pl = plan(tl)
    run_jobs()
    for it in pl["items"]:  # real frame counts and head tracks, now that the shots are graded
        it["n"] = count(Path(it["dir"]))
        if it["kind"] in ("talk", "cut"):
            it["track"] = json.loads((Path(it["dir"]) / "track.json").read_text())
    for it in pl["items"]:
        if it.get("freeze"):
            it["fz"] = freeze_cut(Path(it["dir"]), it["freeze"][2])
    pl["caps"] = captions(tl, pl["nocap"])
    pl["sfx"].sort(key=lambda x: x[1])
    pl["dur"] = tl["dur"]
    pl["fps"] = FPS
    pl["lines"] = {k: [round(v["t0"], 3), round(v["t1"], 3)] for k, v in tl["lines"].items()}
    pl["words"] = tl["words"]
    pl["runs"] = tl["runs"]
    pl["shots"] = tl["shots"]
    pl["dance"], pl["cats"] = tl["dance"], tl["cats"]
    (W / "timeline.json").write_text(json.dumps(pl))
    print(f"timeline: {tl['dur']:.2f} s, {len(pl['items'])} picture items, {len(pl['cues'])} graphics, {len(pl['caps'])} captions")
    return pl


# ---------------------------------------------------------------- render
def page(pw):
    b = pw.chromium.launch(args=["--allow-file-access-from-files", "--disable-web-security"])
    pg = b.new_page(viewport={"width": 1080, "height": 1920})
    pg.goto(f"file://{P / 'edit' / 'comp.html'}")
    pg.evaluate("tl => init(tl)", json.loads((W / "timeline.json").read_text()))
    pg.evaluate("document.fonts.ready.then(() => true)")
    return b, pg


def stills(ts: list[float]) -> None:
    from playwright.sync_api import sync_playwright
    (W / "stills").mkdir(exist_ok=True)
    with sync_playwright() as pw:
        b, pg = page(pw)
        for t in ts:
            pg.evaluate("t => render(t)", t)
            pg.screenshot(path=str(W / "stills" / f"s_{t:06.2f}.jpg"), type="jpeg", quality=85)
        b.close()
    print("stills ->", W / "stills")


def render_part(k0: int, k1: int, out: Path) -> None:
    from playwright.sync_api import sync_playwright
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-i", "-", "-c:v", "libx264",
                           "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
                           "-color_trc", "bt709", str(out)], stdin=subprocess.PIPE)
    with sync_playwright() as pw:
        b, pg = page(pw)
        for k in range(k0, k1):
            pg.evaluate("t => render(t)", k / FPS)
            ff.stdin.write(pg.screenshot(type="jpeg", quality=92))
            if (k - k0) % 150 == 0:
                print(f"  {out.name}: frame {k - k0}/{k1 - k0}", flush=True)
        b.close()
    ff.stdin.close()
    ff.wait()


def render(jobs: int = 3) -> Path:
    tl = json.loads((W / "timeline.json").read_text())
    n = round(tl["dur"] * FPS)
    cuts = [round(n * i / jobs) for i in range(jobs + 1)]
    parts = [W / f"part{i}.mp4" for i in range(jobs)]
    with ThreadPoolExecutor(jobs) as ex:
        list(ex.map(lambda i: render_part(cuts[i], cuts[i + 1], parts[i]), range(jobs)))
    lst = W / "parts.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    silent = W / "picture.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)], check=True)
    for p in parts:
        p.unlink()
    return silent


# ---------------------------------------------------------------- sound
def sfx(name: str) -> np.ndarray:
    return audio(P / "assets" / "sfx" / f"{name}.mp3")


KENNEY = P / "assets" / "kenney"


def _syn(name: str, o: dict) -> tuple[np.ndarray, int]:
    """Clean synthesised hits. Returns (samples, index of the hit point)."""
    from scipy.signal import istft, stft
    rng = np.random.default_rng(len(name) + int(o.get("d", 0) * 100))
    def tt(d):
        return np.arange(int(d * SR)) / SR
    if name == "pop":  # a round mouth pop: fast pitch drop, tiny decay
        t = tt(0.09); f = 480 + 800 * np.exp(-t / 0.010)
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 - np.exp(-t / 0.0008)) * np.exp(-t / 0.022), 0
    elif name == "tick":  # a dry tick for rolling numbers
        t = tt(0.03)
        x = np.sin(2 * np.pi * 4200 * t) * np.exp(-t / 0.0035) + 0.35 * rng.standard_normal(len(t)) * np.exp(-t / 0.001), 0
    elif name == "click":  # a UI click: a short bright transient with a little body
        t = tt(0.05)
        x = (0.6 * rng.standard_normal(len(t)) * np.exp(-t / 0.0012) + np.sin(2 * np.pi * 2200 * t) * np.exp(-t / 0.006)
             + 0.5 * np.sin(2 * np.pi * 600 * t) * np.exp(-t / 0.01)), 0
    elif name == "ping":  # a small bright sparkle
        t = tt(0.6)
        x = (np.sin(2 * np.pi * 2637 * t) * np.exp(-t / 0.12) + 0.6 * np.sin(2 * np.pi * 3951 * t) * np.exp(-t / 0.08)) * (1 - np.exp(-t / 0.002)), 0
    elif name in ("boom", "thump"):  # a sub hit with a saturated top, so phones hear it too
        d, f0, f1, dec = (1.0, 95, 42, 0.32) if name == "boom" else (0.35, 150, 62, 0.09)
        t = tt(d); f = f1 + (f0 - f1) * np.exp(-t / 0.06)
        y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / dec) * (1 - np.exp(-t / 0.002))
        y = np.tanh(1.8 * y) / np.tanh(1.8) + 0.25 * rng.standard_normal(len(t)) * np.exp(-t / 0.0015)
        x = y, 0
    elif name in ("whoosh", "rwhoosh"):  # band-passed air sweeping up to the cut, then away (rwhoosh: swells into it)
        d = o.get("d", 0.42); pk = 0.72 if name == "whoosh" else 0.97
        m = int(d * SR); z = rng.standard_normal(m + 2048)
        f, tf, Z = stft(z, SR, nperseg=1024, noverlap=768)
        u = np.clip(tf / d, 0, 1)
        c = np.where(u < pk, 260 * (5200 / 260) ** (u / pk), 5200 * (500 / 5200) ** ((u - pk) / max(1e-3, 1 - pk)))
        G = np.exp(-0.5 * (np.log2(np.maximum(f[:, None], 20) / c[None, :]) / 1.0) ** 2)
        _, y = istft(Z * G, SR, nperseg=1024, noverlap=768)
        y = y[:m]; un = np.arange(m) / m
        env = np.where(un < pk, (un / pk) ** 2.2, np.exp(-(un - pk) / max(1e-3, 1 - pk) * 4))
        x = y * env, int(pk * m)
    else:
        raise KeyError(name)
    y, hit = x
    y = np.asarray(y, np.float32)
    return y / (np.abs(y).max() + 1e-9), hit


def sound(name: str, o: dict) -> tuple[np.ndarray, int]:
    if name.startswith("k:"):
        y, hit = audio(KENNEY / (name[2:] + ".ogg")).copy(), 0
    elif (P / "assets" / "sfx" / f"{name}.mp3").exists():
        y, hit = sfx(name).copy(), 0
    else:
        y, hit = _syn(name, o)
    if o.get("tail"):  # only the last part (a riser's top)
        y = y[-int(o["tail"] * SR):]
        q = int(0.4 * SR); y[:q] *= np.linspace(0, 1, q)
    if o.get("cut"):
        y = y[: int(o["cut"] * SR)]
        q = int(0.1 * SR); y[-q:] *= np.linspace(1, 0, q)
    fi = int(o.get("fin", 0.0) * SR)
    if fi:
        y[:fi] *= np.linspace(0, 1, fi)
    if o.get("f", 1.0) != 1.0:  # pitch it (a pop that climbs with each new item)
        k = o["f"]
        y = np.interp(np.arange(0, len(y) - 1, k), np.arange(len(y)), y).astype(np.float32)
        hit = int(hit / k)
    pkv = np.abs(y).max() + 1e-9
    return y / pkv, hit


def stretch(x: np.ndarray, rate: float, speech: bool) -> np.ndarray:
    """Time-stretch a mono chunk, pitch kept: rubberband for his voice, atempo for pauses (room tone)."""
    if abs(rate - 1.0) < 1e-3 or len(x) < 256:
        return x
    import tempfile
    import soundfile as sf
    with tempfile.TemporaryDirectory() as td:
        src, dst = Path(td) / "a.wav", Path(td) / "b.wav"
        sf.write(src, x, SR, subtype="FLOAT")
        af = f"rubberband=tempo={rate:.5f}:transients=mixed:formant=preserved" if speech else f"atempo={rate:.5f}"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", af, "-ar", str(SR), "-ac", "1", "-c:a", "pcm_f32le", str(dst)],
                       check=True)
        y, _ = sf.read(dst, dtype="float32")
    return y


def mix() -> Path:
    """His voice re-timed on the same map as the picture, plus sound design. No music in the file: the trending song
    is added in Instagram (licensed there, and the reel joins the song's audio page); see out/post-kit.md."""
    from concurrent.futures import ThreadPoolExecutor
    tl = json.loads((W / "timeline.json").read_text())
    L = tl["lines"]
    n = int(tl["dur"] * SR) + SR
    voice = np.zeros(n, np.float32)
    jobs = []
    for sh in tl["shots"]:
        a = audio(RAW / "intro" / f"{sh['clip']}.MOV")
        speech_rms = []
        for k_, (s0, s1, o0, r) in enumerate(sh["segs"]):
            x = a[int((sh["a"] + s0) * SR): int((sh["a"] + s1) * SR)].copy()
            sp = True
            if sh.get("mute") and k_ == len(sh["segs"]) - 1:
                x *= 0.0
            else:
                speech_rms.append(x)
            jobs.append([x, r, sp, sh["t0"] + o0, (s1 - s0) / r, sh])
        sh["gain"] = min(4.0, 0.085 / (np.sqrt(np.mean(np.concatenate(speech_rms) ** 2)) + 1e-6)) if speech_rms else 1.0
    with ThreadPoolExecutor(4) as ex:
        outs = list(ex.map(lambda j: stretch(j[0], j[1], j[2]), jobs))
    fade = int(0.012 * SR)
    for (x, r, sp, t0, dur, sh), y in zip(jobs, outs):
        m = int(round(dur * SR))
        y = np.pad(y, (0, max(0, m - len(y))))[:m] * sh["gain"]
        if len(y) > 2 * fade:
            y[:fade] *= np.linspace(0, 1, fade)
            y[-fade:] *= np.linspace(1, 0, fade)
        i = int(round(t0 * SR))
        voice[i:i + len(y)] += y[: max(0, n - i)]
    def at(t):
        return int(t * SR)
    words = tl["words"]
    def T(lid, s, end=False):
        m = [w for w in words if w["line"] == lid and s.lower() in w["x"].lower()]
        return m[0]["t1" if end else "t0"]
    # his voice, clear and close: rumble out, light spectral denoise, less boxiness, presence and air, de-ess, even level
    import soundfile as sf
    from scipy.ndimage import uniform_filter1d
    vin, vout = W / "voice_raw.wav", W / "voice_clean.wav"
    sf.write(vin, voice, SR, subtype="FLOAT")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(vin), "-af",
                    "highpass=f=80,afftdn=nr=10:nf=-48:tn=1,equalizer=f=250:t=q:w=1.1:g=-3,equalizer=f=120:t=q:w=0.8:g=1.5,"
                    "equalizer=f=3500:t=q:w=1.3:g=3,highshelf=f=9000:g=2,deesser=i=0.4:m=0.5:f=0.5,"
                    "acompressor=threshold=0.08:ratio=3:attack=6:release=120:makeup=2:knee=4,alimiter=limit=0.9:level=disabled",
                    "-ar", str(SR), "-ac", "1", "-c:a", "pcm_f32le", str(vout)], check=True)
    voice, _ = sf.read(vout, dtype="float32")
    voice = np.pad(voice, (0, max(0, n - len(voice))))[:n]
    drop = T("l3", "travel") - 0.02
    mont1 = L["m1"][0]
    dance0, cats0 = tl["dance"]

    def ramp(points):  # piecewise-linear level curve from (time, value) points
        xs, ys = zip(*points)
        return np.interp(np.arange(n) / SR, xs, ys).astype(np.float32)

    # music: "Loser" (Vish's pick) from the first frame, its chorus on "travel the world"; low-passed under the hard part
    # and opening at "But here's what I've got"; held at ONE steady level under his voice (no pumping), up only for the
    # travel montage; then the cat song from the moment he starts dancing, into the cats
    loser, cat = audio(P / "assets" / "music" / "loser.wav"), audio(RAW / "intro" / "cats_snapgram.mp4")
    beat, b0, chorus = 0.71985, 0.222, 11.0
    bar = 4 * beat
    ch0 = b0 + round((chorus - b0) / beat) * beat
    verse, body, loop = loser[at(b0):at(b0 + 4 * bar)], loser[at(b0):], loser[at(ch0):at(ch0 + 4 * bar)]
    xf = int(0.04 * SR)
    def join(a, b):
        a = a.copy()
        a[-xf:] = a[-xf:] * np.linspace(1, 0, xf) + b[:xf] * np.linspace(0, 1, xf)
        return np.concatenate([a, b[xf:]])
    t = drop - (ch0 - b0)
    track = body
    while t > 0:
        t -= 4 * bar
        track = join(verse, track)
    while t + len(track) / SR < dance0 + 1.0:
        track = join(track, loop)
    song = np.zeros(n, np.float32)
    i0 = at(t)
    x = track[max(0, -i0):]
    i0 = max(0, i0)
    m = min(len(x), n - i0)
    song[i0:i0 + m] = x[:m]
    from scipy.signal import butter, sosfiltfilt
    s1 = L["s1"][0]
    dark = sosfiltfilt(butter(4, 800, "low", fs=SR, output="sos"), song).astype(np.float32)
    w = np.clip((np.arange(n) / SR - (s1 - 1.0)) / 2.0, 0, 1).astype(np.float32)
    song = dark * (1 - w) + song * w
    # level it: a slow loudness follower so the bed stays put, then the target curve
    env = np.sqrt(uniform_filter1d(song ** 2, int(2.0 * SR))) + 1e-4
    target = ramp([(0, 0.02), (drop - 0.3, 0.02), (drop + 0.4, 0.10), (mont1 - 0.6, 0.10), (mont1, 0.02),
                   (dance0 - 0.3, 0.02), (dance0 + 0.05, 0.0), (999, 0.0)])
    song *= uniform_filter1d(np.clip(target / env, 0, 6), int(1.0 * SR))
    music = song
    k = at(CATS[0] - DANCE_IN)  # the cat song, from his first dance step, in sync with the cats when they appear
    cs = cat[k:k + n - at(dance0)].copy()
    cs *= 0.11 / (np.sqrt(np.mean(cs ** 2)) + 1e-6)
    f = int(0.12 * SR); cs[:f] *= np.linspace(0, 1, f)
    music[at(dance0):at(dance0) + len(cs)] += cs

    hush = np.ones(n, np.float32)
    q = int(0.012 * SR)
    for h0, h1 in tl.get("hush", []):
        i0, i1 = at(h0), at(h1)
        hush[i0:i1] = 0.0
        hush[max(0, i0 - q):i0] = np.linspace(1, 0, i0 - max(0, i0 - q))
        hush[i1:i1 + q] = np.linspace(0, 1, len(hush[i1:i1 + q]))
    music *= hush
    # the world's own sound: each B-roll clip's natural audio, low under him, fuller in the montage
    amb = np.zeros(n, np.float32)
    for it in tl["items"]:
        if it["kind"] != "broll" or "childhood" in it.get("src", ""):
            continue
        a_ = audio(Path(it["src"]))
        dur = it["t1"] - it["t0"]
        x = a_[at(it["src_in"]):at(it["src_in"] + dur * it["speed"])].copy()
        if it["speed"] != 1.0:
            x = stretch(x, it["speed"], False)
        x = x[: at(dur)]
        if len(x) < 400:
            continue
        x *= 0.06 / (np.sqrt(np.mean(x ** 2)) + 1e-6)  # same level for every clip
        f = min(len(x) // 3, int(0.12 * SR)); x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
        i = at(it["t0"])
        amb[i:i + len(x)] += x[: max(0, n - i)]
    amb *= ramp([(0, 0.35), (drop - 0.3, 0.35), (drop + 0.3, 1.0), (mont1 - 0.4, 1.0), (mont1, 0.35), (999, 0.35)]) * hush

    # sound design (Vish, 22 Oct v9: crisp, on every beat of the picture): the plan's sound map, one sound per graphic,
    # cut and transition; short and bright, under his voice, never on top of it
    fx = np.zeros(n, np.float32)
    for name, t_, g, o in tl["sfx"]:
        x, hit = sound(name, o)
        i = at(max(0.0, t_)) - hit
        if i < 0:
            x, i = x[-i:], 0
        e = min(n, i + len(x))
        fx[i:e] += g * x[: e - i]
    end = at(tl["dur"])
    np.savez(W / "stems.npz", voice=voice[:end], fx=fx[:end], music=music[:end], amb=amb[:end])  # for level checks
    out = (voice + fx + music + amb)[: end]
    import soundfile as sf
    wav = W / "mix.wav"
    sf.write(wav, np.stack([out, out], 1), SR, subtype="FLOAT")
    return wav


def mux(picture: Path, wav: Path) -> Path:
    OUT.mkdir(exist_ok=True)
    out = OUT / "week1-intro-9x16.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(picture), "-i", str(wav), "-filter_complex",
                    "[1:a]alimiter=limit=0.8:attack=4:release=60:level=disabled,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000,alimiter=limit=0.84:attack=2:release=50:level=disabled[a]", "-map", "0:v", "-map", "[a]", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "prep"
    opt = dict(a[2:].split("=", 1) for a in sys.argv[2:] if a.startswith("--"))
    if cmd == "prep":
        prep()
    elif cmd == "stills":
        stills([float(x) for x in sys.argv[2].split(",")])
    elif cmd == "render":
        pic = render(int(opt.get("jobs", 3)))
        print("->", mux(pic, mix()))
    elif cmd == "mix":
        print("->", mux(W / "picture.mp4", mix()))
