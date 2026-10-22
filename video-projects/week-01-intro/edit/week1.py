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
DROP, BEAT = 24.60, 0.46440  # music: the drop's onset (s into the track) and the beat period (129 bpm)

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
    ("n1", "IMG_1597", [(0.0, 4.3)], {"Rish,": "Vish,"}, "45", "night", {}),
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
LAND = {"h4": .3, "h5": .3, "h6": .45, "n1": .35, "c1": .4, "g3": .55, "r2": .5, "r3": .6, "r4": .45,
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
                  "look": sh["runs"][0]["look"], "cut": any(r["lay"] == "cut" for r in sh["runs"]),
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

    def B(t0, t1, rel, src_in, geom, look="day", kb=(1.0, 1.08), speed=1.0, size=None, name=None, fy=0.5):
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

    def title(t0, t1, words=None, html=None, font="serif", size=96, y=None, band=False, z=45, **k):
        cues.append({"type": "title", "t0": round(t0, 3), "t1": round(t1, 3), "words": words, "html": html, "font": font, "size": size,
                     "y": y, "band": band, "z": z, **k})

    END = L["e1"]["t1"]
    cues.append({"type": "week", "t0": L["n1"]["t0"] + 0.5, "t1": END, "z": 46, "hide": [[L["c1"]["t0"], L["c1"]["t1"]]]})

    # ---- HOOK: his real room, softened behind him; the words tuck behind his head as he says them
    for lid in ("h1", "h2", "h3", "h4", "h5"):  # one slow push across the whole hook take
        zoom(lid, 1.0, 1.06, L["h1"]["t0"], L["h5"]["t1"])
    title(-0.6, L["h1"]["t1"], html="I just<br><i>broke up.</i>", size=250, y=170, z=20)  # on screen from frame one
    title(L["h2"]["t0"], L["h2"]["t1"], html="<span class=am>40K</span>", font="sans", size=430, y=130, z=20, din=0.35)
    title(T("h2", "in"), L["h2"]["t1"], seq("h2", "*in* *debt.*"), size=170, y=1400, z=40)
    B(T("h3", "moved") - 0.04, T("h3", "where"), "travel/cities/IMG_8516.MOV", 0.6, "full", kb=(1.0, 1.04))
    title(T("h3", "moved"), T("h3", "where"), html="New country.", font="sans", size=140, y=1400, z=40)
    title(T("h3", "speak"), L["h3"]["t1"], html="<span class=am>0%</span>", font="sans", size=360, y=70, z=20)
    title(T("h3", "language"), L["h3"]["t1"], html="<i>German.</i>", size=170, y=1400, z=40)
    title(L["h4"]["t0"], L["h4"]["t1"], seq("h4", "No / job."), font="sans", size=300, y=160, z=20)
    title(L["h5"]["t0"], T("h5", "to") - 0.04, seq("h5", "Booked a / *flight.*"), size=230, y=170, z=20)
    B(T("h5", "to") - 0.04, L["h5"]["t1"], "travel/planes/IMG_1110.MOV", 4.0, "full", kb=(1.04, 1.0))
    cues.append({"type": "pass", "t0": T("h5", "to"), "t1": L["h5"]["t1"] + 0.05, "z": 40})
    zoom("h6", 1.0, 1.08, L["h6"]["t0"], L["h6"]["t1"] + 0.3)
    title(L["h6"]["t0"], L["h6"]["t1"] + 0.3, seq("h6", "*What* *am* *I* / *doing?*"), size=170, y=1250, z=40)
    nocap += [[0, L["h6"]["t1"] + 0.3]]

    # ---- the 4:5 frame from "Hey, I'm Vish"
    geoms.append([L["n1"]["t0"] - 0.1, "f45", 0.6])
    bgs.append([0, L["n1"]["t1"], "ink"])
    title(T("n1", "Vish"), L["n1"]["t1"], seq("n1", "Vish, ^27.^"), font="sans", size=96, band=True)
    B(T("n1", "27") - 0.03, T("n1", "my"), "childhood/IMG_5300.MOV", 0.0, "f45", look="soft", kb=(1.0, 1.0), speed=4.0)
    cues.append({"type": "age", "t0": T("n1", "27") - 0.03, "t1": T("n1", "my"), "z": 40})

    # ---- the soft middle: paper
    bgs.append([L["c1"]["t0"], L["r2"]["t0"] + 0.5, "paper"])
    title(L["c1"]["t0"], L["c1"]["t1"], seq("c1", "I always wanted to start this. / But I never had the *confidence* / or the discipline."),
          size=70, band=True, shadow=0, lh=1.08)
    nocap += [[L["c1"]["t0"], L["c1"]["t1"]]]
    zoom("c1", 1.25, 1.25)
    title(L["g1"]["t0"], T("g1", "moved") - 0.04, seq("g1", "Quit my job."), font="sans", size=96, band=True, shadow=0)
    title(T("g1", "moved"), L["g1"]["t1"] + 0.3, seq("g1", "Germany."), font="sans", size=96, band=True, shadow=0)
    B(T("g1", "moved") - 0.03, L["g1"]["t1"] + 0.3, "travel/cities/IMG_7352.MOV", 1.0, "f45", kb=(1.0, 1.04))
    title(L["g3"]["t0"], L["g3"]["t1"], seq("g3", "I doubted my / *whole* *life.*"), size=96, band=True, shadow=0)
    nocap += [[L["g3"]["t0"], L["g3"]["t1"]]]
    zoom("g3", 1.0, 1.04)
    title(L["r1"]["t0"], T("r1", "220") - 0.05, seq("r1", "No friends. / No family."), font="sans", size=88, band=True, shadow=0)
    wall_end = L["r2"]["t0"] + 0.6  # stays up across the cut into the next take, then fades
    cues.append({"type": "wall", "t0": T("r1", "220") - 0.1, "t1": wall_end, "z": 42, "count_t": T("r1", "220"),
                 "count_d": max(0.9, T("r1", "rejections") - T("r1", "220") + 0.3), "stamp_t": T("r1", "rejections") + 0.2})
    nocap += [[T("r1", "220") - 0.1, wall_end]]
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
    cues.append({"type": "stats", "t0": L["s1"]["t0"] + 0.2, "t1": L["l1"]["t0"] + 0.1, "z": 40, "fills": [
        ["Social media", 8, "", T("s2", "social")], ["Influencer marketing", 9, "", T("s3", "influencer")],
        ["Yoga", 7, "", T("s4", "yoga")], ["Master's", 9, "thesis · Feb", T("s5", "master")],
        ["German", 1, "1 / 10", T("s5", "master") + 0.25], ["Job offers", 0, "0 of 220", T("s5", "master") + 0.45],
        ["Remote income", 0, "0", T("s5", "master") + 0.65]]})
    B(T("s4", "taught") - 0.03, L["s4"]["t1"], "travel/yoga/IMG_2362.MOV", 22.6, "split", kb=(1.0, 1.03))
    geoms.append([L["l1"]["t0"] - 0.1, "f45", 0.6])

    # ---- life is all over the place
    title(L["l1"]["t0"], L["l1"]["t1"], seq("l1", "Life is all over / the place right now."), size=88, band=True)
    nocap += [[L["l1"]["t0"], L["l1"]["t1"]]]
    c0 = T("l1b", "so")
    chaos = [("travel/friends/IMG_2758.MOV", 2.5), ("travel/friends/IMG_3348.MOV", 4.5), ("travel/friends/IMG_6353.MOV", 4.0),
             ("travel/mountains/IMG_2099.MOV", 5.5), ("travel/cafes/IMG_0516.MOV", 4.0), ("travel/planes/IMG_6250.MOV", 3.0),
             ("travel/friends/IMG_2783.MOV", 2.0)]
    step = (T("l1b", "debt") - 0.3 - c0) / len(chaos)
    for i, (rel, s) in enumerate(chaos):
        B(c0 + i * step, c0 + (i + 1) * step, rel, s, "f45", kb=(1.0, 1.03))
        items[-1]["dx"] = 0.14
    # the turn: music out, black, his words alone
    bgs.append([L["l2"]["t0"], L["l3"]["t0"], "black"])
    title(L["l2"]["t0"], L["l3"]["t0"] + 0.2, seq("l2", "But one thing / is *sure,*"), size=96, band=True)
    nocap += [[L["l2"]["t0"], L["l3"]["t1"]]]
    bgs.append([L["l3"]["t0"], L["m1"]["t0"], "ink"])
    B(T("l3", "work") - 0.03, T("l3", "travel") - 0.02, "travel/cafes/IMG_3995.MOV", 0.2, "f45", kb=(1.0, 1.04))
    title(T("l3", "work"), T("l3", "travel") - 0.02, seq("l3", "Work remotely."), font="sans", size=96, band=True)
    # the drop: the frame opens to full screen, the montage cuts on the music's beat
    drop = T("l3", "travel") - 0.02
    geoms.append([drop, "full", 0.5])
    mont = [("travel/ocean/IMG_5708.MOV", 3.5, 2), ("travel/bike/IMG_1754.MOV", 9.4, 2), ("travel/ocean/IMG_4594.MOV", 4.0, 2),
            ("travel/friends/IMG_5615.MOV", 7.0, 2), ("travel/ocean/IMG_3547.mov", 5.0, 2), ("travel/ocean/IMG_5676.MOV", 22.6, 2),
            ("travel/ocean/IMG_1503.MOV", 10.5, 99)]
    t, end = drop, L["m1"]["t0"]
    for i, (rel, s, beats) in enumerate(mont):
        t1 = min(end, t + beats * BEAT) if beats < 99 else end
        if t1 - t > 0.05:
            B(t, t1, rel, s, "full", kb=(1.0, 1.04))
            items[-1]["dx"] = 0.35 if i == 0 else 0.0
        t = t1
    title(drop + 0.05, L["l3"]["t1"] + 1.2, seq("l3", "*travel* / *the* *world.*"), size=200, y=700, z=45)
    geoms.append([L["m1"]["t0"] - 0.1, "f45", 0.6])

    # ---- max out every stat (push-ups)
    bgs.append([L["m1"]["t0"], END, "ink"])
    title(T("m1", "max"), L["m1b"]["t1"], seq("m1", "Max out / ^every^ ^skill.^"), font="sans", size=96, band=True)
    cues.append({"type": "chips", "t0": T("m1", "max") + 0.6, "t1": L["m1b"]["t0"] + 2.6, "step": 0.75, "z": 40,
                 "items": ["confidence", "discipline", "German", "courage"]})
    title(L["m2"]["t0"], L["m2"]["t1"] + 0.2, seq("m2", "I have to / make this *happen.*"), size=88, band=True)
    nocap += [[L["m2"]["t0"], L["m2"]["t1"] + 0.2]]
    zoom("m2", 1.0, 1.05)
    # week one
    title(L["w1"]["t0"], T("w1", "week") - 0.05, seq("w1", "I don't know / *how* yet,"), size=88, band=True)
    cues.append({"type": "weekcard", "t0": T("w1", "week") - 0.1, "t1": L["w1"]["t1"] + 0.6, "z": 44})
    nocap += [[L["w1"]["t0"], L["w1"]["t1"] + 0.6]]
    title(L["w2"]["t0"], L["w7"]["t1"], seq("w2", "Every week, / ^everything.^"), font="sans", size=96, band=True)
    nocap += [[L["w2"]["t0"], L["w7"]["t1"]]]
    # fresh footage for the promise (nothing seen earlier in the reel), Vish 22 Oct
    flashes = [("w3", "The trials.", "travel/bike/IMG_4167.MOV", 3.3, 1.0, (1.03, 1.0), 0.5),
               ("w4", "The fails.", "travel/mountains/IMG_1452.MOV", 6.0, 1.6, (1.45, 1.52), 0.9),  # the flop onto the grass
               ("w5", "The work.", "travel/cafes/IMG_7358.MOV", 3.0, 1.0, (1.03, 1.0), 0.5),
               ("w6", "The travel.", "travel/planes/IMG_6726.MOV", 2.1, 1.0, (1.03, 1.0), 0.5)]
    for lid, lab, rel, s, sp, kb, fy in flashes:
        t0, t1 = L[lid]["t0"] - 0.02, L[lid]["t1"]
        if rel:
            B(t0, t1, rel, s, "f45", kb=kb, speed=sp, fy=fy)
            items[-1]["dx"] = 0.16
        else:
            cues.append({"type": "mail", "t0": t0, "t1": t1, "z": 38})
        cues.append({"type": "label", "t0": t0, "t1": t1, "text": lab, "z": 44})
    # come with me, the dance, the cats
    title(L["e1"]["t0"], L["e1"]["t1"] + 0.2, seq("e1", "So come with me / and join my *journey.*"), size=88, band=True)
    d0, d1 = tl["dance"]
    title(d0 + 0.05, d1 + 0.3, html="<i>me, trying to max out<br>my dance stat:</i>", size=80, band=True)
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
    geoms.append([c0 - 0.1, "none", M])
    return {"items": items, "cues": cues, "geoms": geoms, "bgs": bgs, "nocap": nocap}


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
    pl["caps"] = captions(tl, pl["nocap"])
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
        for s0, s1, o0, r in sh["segs"]:
            x = a[int((sh["a"] + s0) * SR): int((sh["a"] + s1) * SR)].copy()
            sp = True
            if sp:
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
    amb *= ramp([(0, 0.35), (drop - 0.3, 0.35), (drop + 0.3, 1.0), (mont1 - 0.4, 1.0), (mont1, 0.35), (999, 0.35)])

    # sound design: soft, faded in, on the real transitions only
    fx = np.zeros(n, np.float32)
    def put(name, t, g, cut=None, fin=0.04):
        x = sfx(name).copy()
        if cut:
            x = x[: int(cut * SR)]
            x[-int(0.1 * SR):] *= np.linspace(1, 0, int(0.1 * SR))
        fi = int(fin * SR); x[:fi] *= np.linspace(0, 1, fi)
        i = at(max(0, t)); e = min(n, i + len(x))
        fx[i:e] += g * x[: e - i]
    for it in tl["items"]:
        if it["kind"] == "broll" and it.get("dx", 0.32) >= 0.14 and it["t0"] > 1:
            put("whoosh-fast", it["t0"] - 0.22, 0.05)
    put("jet-whoosh", T("h5", "to") - 0.5, 0.08, 2.4, fin=0.3)
    put("airport-ding", T("h5", "booked") - 0.05, 0.05, 1.8)
    for k_ in range(4):
        put("paper-slide", T("r1", "220") + k_ * 0.22, 0.07)
    for lid, s_ in (("s2", "social"), ("s3", "influencer"), ("s4", "yoga"), ("s5", "master")):
        put("pop-light", T(lid, s_) + 0.1, 0.04)
    rs = sfx("riser-drama")
    x = rs[-at(1.6):].copy(); x[:at(0.4)] *= np.linspace(0, 1, at(0.4))
    i = at(drop - 1.6); fx[i:i + len(x)] += 0.05 * x[: n - i]
    put("type-bell", T("w1", "week") + 0.15, 0.05)
    put("whoosh-fast", cats0 - 0.25, 0.07)
    end = at(tl["dur"])
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
