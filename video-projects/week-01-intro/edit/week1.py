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

import json
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
MUSIC = P / "assets" / "music" / "a-new-life.mp3"
DROP, BEAT = 24.60, 0.46440  # music: the drop's onset (s into the track) and the beat period (129 bpm)

# ---------------------------------------------------------------- the cut (his words, in order)
# id, clip, runs of (from, to) word-start times kept, caption fixes, layout, look, flags
LINES = [
    ("h1", "IMG_1578", [(1.1, 2.4)], {}, "cut", "night", {}),
    ("h2", "IMG_1578", [(2.8, 4.1)], {}, "cut", "night", {}),
    ("h3", "IMG_1578", [(4.25, 7.3)], {"to.": "too."}, "cut", "night", {}),
    ("h4", "IMG_1578", [(7.7, 8.3)], {}, "cut", "night", {}),
    ("h5", "IMG_1578", [(9.2, 11.3)], {}, "cut", "night", {}),
    ("h6", "IMG_1578", [(13.4, 14.3)], {}, "full", "night", {"gap": 0.12}),
    ("n1", "IMG_1597", [(0.0, 1.6), (2.9, 4.3)], {"Rish,": "Vish,"}, "45", "night", {}),
    ("c1", "IMG_1581", [(0.0, 1.9), (3.3, 7.0)], {"a": "the"}, "45", "soft", {}),
    ("g1", "IMG_1582", [(1.0, 4.0)], {}, "45", "soft", {}),
    ("g2", "IMG_1582", [(7.3, 7.5), (8.5, 9.8)], {}, "45", "soft", {}),
    ("r1", "IMG_1583", [(1.7, 3.5), (3.9, 7.0)], {}, "45", "soft", {}),
    ("r2", "IMG_1583", [(12.5, 13.0), (13.9, 14.3), (18.4, 19.6)], {"breaker,": "breakup,"}, "45", "night", {}),
    ("s1", "IMG_1585", [(0.0, 1.0)], {}, "split", "night", {}),
    ("s2", "IMG_1585", [(1.7, 3.0)], {}, "split", "night", {}),
    ("s3", "IMG_1585", [(3.4, 4.9)], {}, "split", "night", {}),
    ("s4", "IMG_1585", [(5.8, 7.2)], {}, "split", "night", {}),
    ("s5", "IMG_1585", [(7.6, 9.3)], {}, "split", "night", {"gap": 1.0}),
    ("l1", "IMG_1586", [(0.0, 2.0)], {}, "45", "night", {}),
    ("l2", "IMG_1586", [(10.1, 11.3)], {}, "45", "night", {"gap": 0.45}),
    ("l3", "IMG_1586", [(12.2, 15.5)], {}, "45", "night", {"gap": 2.8}),
    ("m1", "IMG_1588", [(0.0, 0.1), (0.7, 3.2)], {}, "45", "night", {}),
    ("m2", "IMG_1588", [(9.6, 10.95)], {}, "45", "night", {}),
    ("w1", "IMG_1593", [(0.0, 1.1), (1.7, 2.9)], {"the": ""}, "45", "night", {}),
    ("w2", "IMG_1593", [(3.8, 6.1)], {}, "45", "night", {}),
    ("w3", "IMG_1593", [(7.2, 7.4)], {}, "45", "night", {}),
    ("w4", "IMG_1593", [(8.7, 8.9)], {}, "45", "night", {}),
    ("w5", "IMG_1593", [(10.3, 10.4)], {}, "45", "night", {}),
    ("w6", "IMG_1593", [(11.3, 11.4)], {}, "45", "night", {}),
    ("w7", "IMG_1593", [(12.6, 12.7)], {}, "45", "night", {}),
    ("e1", "IMG_1594", [(0.0, 2.8)], {}, "45", "night", {}),
]
DANCE = ("IMG_1594", 4.75, 2.0)  # src, in, seconds: his dance attempt, picture only
CATS = (4.0, 3.6)                # cats clip in, seconds (two cats on screen from 3.5 s)


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
def build() -> dict:
    t = 0.0
    runs, words, lines = [], [], {}
    for lid, clip, rr, fix, lay, look, fl in LINES:
        L = {"t0": t, "runs": []}
        prev_b = -1.0
        for k, (A, B) in enumerate(rr):
            a, b, sel = snap(clip, A, B)
            if a < prev_b:  # never replay audio inside a line
                a = prev_b
                b = a + max(1, round((b - a) * FPS)) / FPS
            prev_b = b
            d = b - a
            runs.append({"line": lid, "clip": clip, "a": a, "b": b, "t0": t, "t1": t + d, "lay": lay, "look": look, "k": k,
                         "hold": fl.get("gap", 0.0) if k == len(rr) - 1 else 0.0})
            for w in sel:
                x = fix.get(w["x"], w["x"])
                if x:
                    words.append({"line": lid, "x": x, "t0": t + max(0, w["t"] - a), "t1": t + min(d, w["e"] - a)})
            L["runs"].append((t, t + d))
            t += d
        L["t1"] = t
        lines[lid] = L
        t += fl.get("gap", 0.0)
    dance_t0 = t
    t += DANCE[2]
    cats_t0 = t
    t += CATS[1]
    return {"runs": runs, "words": words, "lines": lines, "dance": (dance_t0, cats_t0), "cats": (cats_t0, t), "dur": round(t * FPS) / FPS}


def wt(tl: dict, lid: str, sub: str, end: bool = False, nth: int = 0) -> float:
    m = [w for w in tl["words"] if w["line"] == lid and sub.lower() in w["x"].lower()]
    return m[nth]["t1" if end else "t0"]


# ---------------------------------------------------------------- frame extraction + film grade
# extract() only registers a job; run_jobs() does them in parallel: ffmpeg cut + film LUT, then per frame the matte
# (speaker shots), the head track, and film.finish() (light pool, lens defocus, halation, diffusion).
JOBS: list[dict] = []
LUTS = W / "luts"


def extract(src: Path, a: float, n: int, look: str | None, size: str, name: str, speed: float = 1.0,
            matte: bool = False, cut: bool = False) -> Path:
    d = FR / name
    if not (d / "finished").exists() and not any(j["d"] == str(d) for j in JOBS):
        JOBS.append(dict(src=str(src), a=a, n=n, look=look, size=size, d=str(d), speed=speed, matte=matte, cut=cut))
    return d


def count(d: Path) -> int:
    return len(list(d.glob("*.jpg")))


def run_job(j: dict) -> str:
    import cv2
    from scipy.ndimage import gaussian_filter1d
    d, src, look = Path(j["d"]), Path(j["src"]), j["look"]
    d.mkdir(parents=True, exist_ok=True)
    if not (d / "done").exists():
        pts = f"setpts=PTS/{j['speed']}," if j["speed"] != 1 else ""
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
        sig = 5 if j["cut"] else 9
        xs, ys = gaussian_filter1d(xs, sig, mode="nearest"), gaussian_filter1d(ys, sig, mode="nearest")
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

    def B(t0, t1, rel, src_in, geom, look="day", kb=(1.0, 1.08), speed=1.0, size=None, name=None):
        src = RAW / rel
        n = max(1, round((t1 - t0) * FPS))
        pr = probe(src)
        w, h = int(pr.get("width", 1080)), int(pr.get("height", 1920))
        rot = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream_side_data=rotation",
                              "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout.strip()
        if rot in ("90", "-90", "270", "-270"):
            w, h = h, w
        size = size or ("1080:-2" if h > w else "-2:1080")
        nm = name or f"b_{Path(rel).stem}_{src_in:.2f}_{n}_{speed}"
        d = extract(src, src_in, n, look, size, nm, speed)
        items.append({"t0": round(t0, 4), "t1": round(t1, 4), "dir": str(d), "n": n, "kind": "broll", "geom": geom, "kb": kb})

    # talking runs
    for r in tl["runs"]:
        n = round((r["b"] - r["a"] + r["hold"]) * FPS)  # the picture holds through a designed pause
        d = extract(RAW / "intro" / f"{r['clip']}.MOV", r["a"], n, r["look"], "1920:1080", f"t_{r['clip']}_{r['a']:.3f}_{n}",
                    matte=True, cut=r["lay"] == "cut")
        tr = None  # filled in after the grade jobs run
        z = 1.0 if r["k"] % 2 == 0 else 1.13  # alternate framing on jump cuts
        items.append({"t0": round(r["t0"], 4), "t1": round(r["t1"] + r["hold"], 4), "dir": str(d), "n": n, "kind": "cut" if r["lay"] == "cut" else "talk",
                      "geom": {"cut": "full", "full": "full", "45": "f45", "split": "split"}[r["lay"]], "track": tr, "z": z})

    def run_items(lid):
        return [i for i in items if i["kind"] in ("talk", "cut") and L[lid]["t0"] - 1e-3 <= i["t0"] < L[lid]["t1"] - 1e-3]

    def zoom(lid, z0, z1, t0=None, t1=None):
        for i in run_items(lid):
            i["zk"] = [[t0 if t0 is not None else L[lid]["t0"], z0], [t1 if t1 is not None else L[lid]["t1"], z1]]

    # ---- HOOK (0 to ~11 s): cut-out Vish in a loud graphic world, text behind him
    h = L["h1"]
    bgs.append([0, L["h5"]["t1"], "hook"])
    cues.append({"type": "speed", "t0": 0, "t1": L["h2"]["t1"], "z": 1})
    cues.append({"type": "big", "t0": -0.08, "t1": L["h1"]["t1"], "html": "I JUST<br>BROKE UP.", "y": 250, "size": 250, "z": 20, "rot": -5,
                 "color": "#F5F3EE", "shadow": 1})
    cues.append({"type": "big", "t0": L["h2"]["t0"], "t1": L["h2"]["t1"], "html": "40K", "y": 300, "size": 560, "z": 20, "rot": -6, "color": "#E8231C"})
    cues.append({"type": "big", "t0": T("h2", "in"), "t1": L["h2"]["t1"], "html": "IN DEBT.", "y": 1330, "size": 250, "z": 40, "rot": -4,
                 "color": "#F5F3EE", "shadow": 1})
    zoom("h1", 1.0, 1.06)
    zoom("h2", 1.08, 1.16)
    # moved to a country (B-roll), then back on him for the language
    B(T("h3", "moved") - 0.04, T("h3", "where"), "travel/cities/IMG_8516.MOV", 0.6, "full")
    cues.append({"type": "big", "t0": T("h3", "moved"), "t1": T("h3", "where"), "html": "NEW<br>COUNTRY.", "y": 1180, "size": 230, "z": 40,
                 "rot": -4, "color": "#F5F3EE", "shadow": 1})
    cues.append({"type": "big", "t0": T("h3", "where"), "t1": L["h3"]["t1"], "html": "0%", "y": 250, "size": 470, "z": 20, "rot": -5, "color": "#E8231C"})
    cues.append({"type": "big", "t0": T("h3", "speak"), "t1": L["h3"]["t1"], "html": "GERMAN.", "y": 1330, "size": 250, "z": 40, "rot": -4,
                 "color": "#F5F3EE", "shadow": 1})
    zoom("h3", 1.12, 1.2)
    cues.append({"type": "stamp", "t0": T("h4", "no"), "t1": L["h4"]["t1"], "text": "NO JOB.", "y": 1250, "size": 230, "rot": -8, "z": 40})
    cues.append({"type": "speed", "t0": L["h4"]["t0"], "t1": L["h4"]["t1"], "z": 1})
    zoom("h4", 1.18, 1.3)
    # booked a flight: the boarding pass
    B(T("h5", "flight") - 0.04, L["h5"]["t1"], "travel/planes/IMG_1110.MOV", 4.0, "full", kb=(1.06, 1.0))
    cues.append({"type": "big", "t0": L["h5"]["t0"], "t1": T("h5", "flight") - 0.04, "html": "BOOKED<br>A FLIGHT.", "y": 230, "size": 230, "z": 20,
                 "rot": -5, "color": "#F5F3EE", "shadow": 1})
    cues.append({"type": "pass", "t0": T("h5", "flight"), "t1": L["h5"]["t1"] + 0.05, "stamp_t": T("h5", "Sri"), "z": 40})
    cues.append({"type": "plane", "t0": T("h5", "flight") - 0.1, "t1": L["h5"]["t1"], "z": 41})
    nocap += [[0, L["h5"]["t1"]]]
    # what am I doing? the real room, anime punch-in
    zoom("h6", 1.0, 1.45, L["h6"]["t0"], L["h6"]["t1"])
    cues.append({"type": "speed", "t0": L["h6"]["t0"] + 0.25, "t1": L["h6"]["t1"] + 0.12, "z": 35, "light": 1})
    cues.append({"type": "big", "t0": L["h6"]["t0"], "t1": L["h6"]["t1"] + 0.12, "html": "WHAT AM<br>I DOING?", "y": 1240, "size": 200, "z": 40,
                 "rot": -3, "color": "#F5F3EE", "shadow": 1})
    nocap += [[L["h6"]["t0"], L["h6"]["t1"] + 0.12]]
    cues.append({"type": "tag", "t0": 0, "t1": L["h6"]["t1"] + 0.12, "text": "WEEK 01 / 52", "y": 150, "z": 45})

    # ---- 4:5 world from "Hey, I'm Vish"
    geoms.append([L["n1"]["t0"] - 0.05, "f45", 0.32])
    bgs.append([L["h5"]["t1"], L["n1"]["t1"], "ink"])
    band = lambda t0, t1, html, **k: cues.append({"type": "band", "t0": t0, "t1": t1, "html": html, "z": 45, **k})  # noqa: E731
    cues.append({"type": "week", "t0": L["n1"]["t0"], "t1": L["e1"]["t1"], "z": 46, "hide": [[L["c1"]["t0"], L["c1"]["t1"]]]})
    band(T("n1", "Vish"), L["n1"]["t1"], "VISH, <span class=r>27.</span>", style="bc")
    B(T("n1", "27") - 0.03, T("n1", "my"), "childhood/IMG_5300.MOV", 0.0, "f45", look="soft", kb=(1.0, 1.0), speed=4.0)
    cues.append({"type": "age", "t0": T("n1", "27") - 0.03, "t1": T("n1", "my"), "z": 40})
    cues.append({"type": "rec", "t0": T("n1", "first"), "t1": L["n1"]["t1"], "z": 40})
    zoom("n1", 1.0, 1.0)

    # ---- the soft middle: paper world
    bgs.append([L["c1"]["t0"], L["r1"]["t1"] + 0.25, "paper"])
    cues.append({"type": "typer", "t0": L["c1"]["t0"], "t1": L["c1"]["t1"], "z": 45, "lines": [
        {"html": "i always wanted to start this.", "t0": T("c1", "always"), "t1": T("c1", "this", end=True)},
        {"html": "never had the <span class=circ>confidence</span>", "t0": T("c1", "never"), "t1": T("c1", "confidence", end=True), "circ": T("c1", "confidence")},
        {"html": "or the discipline.", "t0": T("c1", "or"), "t1": T("c1", "discipline", end=True)}]})
    nocap += [[L["c1"]["t0"], L["c1"]["t1"]]]
    zoom("c1", 1.3, 1.4)
    band(L["g1"]["t0"], T("g1", "moved"), "QUIT MY JOB.", style="bc", strike=T("g1", "job"))
    band(T("g1", "moved"), L["g1"]["t1"], "&rarr; GERMANY", style="bc")
    B(T("g1", "moved") - 0.03, L["g1"]["t1"], "travel/cities/IMG_7352.MOV", 1.0, "f45")
    band(L["g2"]["t0"], L["g2"]["t1"], "i doubted my <i>whole</i> life.", style="serif")
    zoom("g2", 1.0, 1.12)
    band(L["r1"]["t0"], T("r1", "220") - 0.05, "FRIENDS <span class=r>0</span>|FAMILY <span class=r>0</span>", style="mono",
         steps=[T("r1", "friends"), T("r1", "family")])
    cues.append({"type": "wall", "t0": T("r1", "220") - 0.05, "t1": L["r1"]["t1"] + 0.25, "z": 42, "count_t": T("r1", "220"),
                 "count_d": max(0.6, T("r1", "rejections") - T("r1", "220")), "stamp_t": T("r1", "rejections")})
    nocap += [[T("r1", "220") - 0.05, L["r1"]["t1"] + 0.25]]
    bgs.append([L["r1"]["t1"] + 0.25, L["s1"]["t0"], "ink"])
    band(T("r2", "breakup"), T("r2", "this"), "the breakup?", style="serif")
    band(T("r2", "this"), L["r2"]["t1"] + 0.1, "good <i>distraction.</i>", style="serif")

    # ---- what I've got: Kallaway split, the stat card on top
    geoms.append([L["s1"]["t0"] - 0.05, "split", 0.3])
    bgs.append([L["s1"]["t0"], L["l1"]["t0"], "ink"])
    s5e = L["s5"]["t1"]
    cues.append({"type": "stats", "t0": L["s1"]["t0"], "t1": L["l1"]["t0"], "z": 40, "fills": [
        ["SOCIAL MEDIA", 8, "", T("s2", "social")], ["INFLUENCER MKTG", 9, "", T("s3", "influencer")],
        ["YOGA", 7, "", T("s4", "yoga")], ["MASTER'S", 9, "thesis: feb", T("s5", "master")],
        ["GERMAN", 1, "", s5e + 0.08], ["JOB OFFERS", 0, "0 of 220", s5e + 0.38],
        ["REMOTE INCOME", 0, "", s5e + 0.68]]})
    B(T("s4", "taught") - 0.03, L["s4"]["t1"], "travel/yoga/IMG_2362.MOV", 22.6, "split", kb=(1.0, 1.06))
    geoms.append([L["l1"]["t0"] - 0.05, "f45", 0.3])

    # ---- life is all over the place: chaos montage in the frame
    bgs.append([L["l1"]["t0"], L["l2"]["t0"], "ink"])
    c0 = T("l1", "all")
    chaos = [("travel/friends/IMG_2758.MOV", 2.5), ("travel/friends/IMG_3348.MOV", 4.5), ("travel/friends/IMG_6353.MOV", 4.0),
             ("travel/mountains/IMG_2099.MOV", 5.5), ("travel/cafes/IMG_0516.MOV", 4.0), ("travel/planes/IMG_6250.MOV", 3.0),
             ("travel/friends/IMG_2783.MOV", 2.0)]
    step = (L["l1"]["t1"] + 0.02 - c0) / len(chaos)
    for i, (rel, s) in enumerate(chaos):
        B(c0 + i * step, c0 + (i + 1) * step, rel, s, "f45", kb=(1.1, 1.0))
    band(L["l1"]["t0"], L["l1"]["t1"], "ALL OVER<br>THE PLACE.", style="bc", jitter=1)
    cues.append({"type": "glitch", "t0": c0, "t1": L["l1"]["t1"], "z": 39})
    # the turn: music out, black, serif
    bgs.append([L["l2"]["t0"], L["l3"]["t0"], "black"])
    band(L["l2"]["t0"], L["l3"]["t0"], "but one thing<br>is <i>sure.</i>", style="serif")
    zoom("l2", 1.0, 1.1)
    # work remotely
    bgs.append([L["l3"]["t0"], L["m1"]["t0"], "ink"])
    B(T("l3", "work") - 0.03, T("l3", "travel") - 0.02, "travel/cafes/IMG_3995.MOV", 0.2, "f45", kb=(1.0, 1.08))
    band(T("l3", "work"), T("l3", "travel") - 0.02, "WORK REMOTELY", style="wide")
    # the drop: full frame, montage on the beat
    drop = T("l3", "travel") - 0.02
    geoms.append([drop, "full", 0.22])
    mont = [("travel/ocean/IMG_5708.MOV", 3.5, 2), ("travel/bike/IMG_1754.MOV", 9.4, 1), ("travel/ocean/IMG_4594.MOV", 4.0, 1),
            ("travel/friends/IMG_5615.MOV", 7.0, 2), ("travel/ocean/IMG_3547.mov", 5.0, 1), ("travel/mountains/IMG_4616.MOV", 4.0, 1),
            ("travel/ocean/IMG_5676.MOV", 22.6, 2), ("travel/ocean/IMG_1503.MOV", 10.5, 99)]
    t, end = drop, L["m1"]["t0"] - 0.0
    for rel, s, beats in mont:
        t1 = min(end, t + beats * BEAT) if beats < 99 else end
        if t1 - t > 0.05:
            B(t, t1, rel, s, "full", kb=(1.0, 1.07))
        t = t1
    cues.append({"type": "serif", "t0": drop, "t1": L["l3"]["t1"] + 0.5, "html": "travel<br>the world.", "y": 700, "size": 190, "z": 45})
    cues.append({"type": "flash", "t0": drop, "t1": drop + 0.18, "z": 60})
    nocap += [[drop, L["m1"]["t0"]]]
    geoms.append([L["m1"]["t0"] - 0.02, "f45", 0.28])

    # ---- max out every stat (push-ups)
    bgs.append([L["m1"]["t0"], L["e1"]["t1"], "ink"])
    band(T("m1", "max"), L["m2"]["t1"], "MAX OUT<br><span class=r>EVERY STAT.</span>", style="bc")
    cues.append({"type": "plus", "t0": T("m1", "max"), "t1": L["m1"]["t1"], "z": 40})
    zoom("m2", 1.05, 1.22)
    # week one
    band(L["w1"]["t0"], T("w1", "week") - 0.02, "i don't know <i>how</i> yet.", style="serif")
    cues.append({"type": "weekstamp", "t0": T("w1", "week"), "t1": L["w1"]["t1"] + 0.25, "z": 44})
    nocap += [[T("w1", "week"), L["w1"]["t1"] + 0.25]]
    band(L["w2"]["t0"], L["w7"]["t1"], "EVERY WEEK.<br><span class=r>EVERYTHING.</span>", style="bc")
    flashes = [("w3", "THE TRIALS", "travel/mountains/IMG_2099.MOV", 7.0), ("w4", "THE FAILS", None, 0),
               ("w5", "THE WORK", "travel/cafes/IMG_3995.MOV", 1.4), ("w6", "THE TRAVEL", "travel/planes/IMG_3569.MOV", 14.0)]
    for lid, lab, rel, s in flashes:
        t0, t1 = L[lid]["t0"] - 0.02, L[lid]["t1"] + 0.0
        if rel:
            B(t0, t1, rel, s, "f45", kb=(1.12, 1.0))
        else:
            cues.append({"type": "mail", "t0": t0, "t1": t1, "z": 38})
        cues.append({"type": "label", "t0": t0, "t1": t1, "text": lab, "z": 44})
        nocap += [[t0, t1]]
    # come with me + the dance + the cats
    band(T("e1", "come"), L["e1"]["t1"], "COME<br><span class=r>WITH ME.</span>", style="bc")
    d0, d1 = tl["dance"]
    dd = extract(RAW / "intro" / f"{DANCE[0]}.MOV", DANCE[1], round(DANCE[2] * FPS), "night", "1920:1080", "dance", matte=True)
    items.append({"t0": d0, "t1": d1, "dir": str(dd), "n": round(DANCE[2] * FPS), "kind": "talk", "geom": "f45", "track": None, "z": 1.0})
    band(d0, d1, "me, trying to<br><span class=r>max out dancing:</span>", style="bc")
    nocap += [[d0, tl["dur"]]]
    c0, c1 = tl["cats"]
    cd = key_cats(round(CATS[1] * FPS))
    cues.append({"type": "cats", "t0": c0, "t1": c1 + 1, "dir": str(cd / "cut"), "n": round(CATS[1] * FPS), "z": 30})
    bgs.append([c0, c1 + 1, "paper"])
    geoms.append([c0, "none", 0.0])
    return {"items": items, "cues": cues, "geoms": geoms, "bgs": bgs, "nocap": nocap}


def captions(tl: dict, nocap: list) -> list:
    caps, cur = [], []
    def flush():
        if cur:
            caps.append({"t0": cur[0]["t0"], "t1": cur[-1]["t1"], "w": [[w["x"].upper(), round(w["t0"], 3), round(w["t1"], 3)] for w in cur]})
    for w in tl["words"]:
        if any(a - 1e-3 <= w["t0"] < b for a, b in nocap):
            flush(); cur = []
            continue
        if cur and (len(cur) >= 3 or len(" ".join(x["x"] for x in cur + [w])) > 16 or cur[-1]["x"][-1] in ",.?" or cur[-1]["line"] != w["line"]):
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


def mix() -> Path:
    tl = json.loads((W / "timeline.json").read_text())
    L = tl["lines"]
    n = int(tl["dur"] * SR) + SR
    voice = np.zeros(n, np.float32)
    speech = np.zeros(n, np.float32)
    fade = int(0.012 * SR)
    for r in tl["runs"]:
        a = audio(RAW / "intro" / f"{r['clip']}.MOV")
        seg = a[int(r["a"] * SR): int(r["a"] * SR) + int(round((r["b"] - r["a"]) * SR))].copy()
        rms = np.sqrt(np.mean(seg ** 2)) + 1e-6
        seg *= min(4.0, 0.085 / rms)  # even out the takes
        seg[:fade] *= np.linspace(0, 1, fade)
        seg[-fade:] *= np.linspace(1, 0, fade)
        i = int(r["t0"] * SR)
        voice[i:i + len(seg)] += seg
        speech[i:i + len(seg)] = 1
    def at(t):
        return int(t * SR)
    words = tl["words"]
    def T(lid, s, end=False):
        m = [w for w in words if w["line"] == lid and s.lower() in w["x"].lower()]
        return m[0]["t1" if end else "t0"]
    fx = np.zeros(n, np.float32)
    def put(name, t, g, cut=None):
        s = sfx(name)
        if cut:
            s = s[: int(cut * SR)].copy()
            s[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))
        i = at(max(0, t))
        e = min(n, i + len(s))
        fx[i:e] += g * s[: e - i]
    # hook
    put("impact-big", T("h1", "broke") - 0.02, 0.55, 1.6)
    put("whoosh-fast", L["h2"][0] - 0.12, 0.35)
    put("impact-deep", T("h2", "40k") - 0.02, 0.7, 1.5)
    put("whoosh-rocket", T("h3", "moved") - 0.25, 0.3, 1.0)
    put("pop-light", T("h3", "where"), 0.25)
    put("wood-hit", T("h4", "no"), 0.8)
    put("type-hit", T("h4", "no") + 0.02, 0.5)
    put("airport-ding", T("h5", "booked") - 0.1, 0.25, 1.8)
    put("jet-whoosh", T("h5", "flight") - 0.3, 0.45, 2.4)
    put("shutter-old", T("h5", "Sri"), 0.5)
    put("riser-drama", L["h6"][0] - 0.6, 0.25, 1.7)
    put("vinyl-stop", L["h6"][1] - 0.15, 0.4, 0.9)
    put("pop-light", T("n1", "Vish"), 0.22)
    put("shutter-old", T("n1", "first"), 0.5)
    # soft middle
    put("paper-slide", L["c1"][0] - 0.1, 0.5)
    for w in [w for w in words if w["line"] == "c1"]:
        put("type-soft", w["t0"], 0.5)
    put("pencil-scribble", T("c1", "confidence"), 0.45)
    put("whoosh-fast", T("g1", "moved") - 0.15, 0.3)
    for k in range(4):
        put("paper-slide" if k % 2 else "wood-hit", T("r1", "220") + k * 0.18, 0.45)
    put("impact-big", T("r1", "rejections") + 0.05, 0.5, 1.4)
    hb = sfx("heartbeat-slow")[: at(L["r2"][1] - L["c1"][0])].copy()
    hb[-SR // 2:] *= np.linspace(1, 0, SR // 2)
    fx[at(L["c1"][0]): at(L["c1"][0]) + len(hb)] += 0.07 * hb
    # stats
    for lid, s in (("s2", "social"), ("s3", "influencer"), ("s4", "yoga"), ("s5", "master")):
        put("pop-light", T(lid, s) + 0.1, 0.25)
        put("type-hit", T(lid, s) + 0.1, 0.25)
    for k in range(3):
        put("glitch-text", L["l1"][0] - 0.05 + k * 0.2, 0.18, 0.25)
    put("glitch-text", T("l1", "all"), 0.3, 1.2)
    # the drop
    drop = T("l3", "travel") - 0.02
    put("water-jump", drop + 0.25, 0.5)
    put("whoosh-rocket", drop - 0.35, 0.35, 0.9)
    for k in range(4):
        put("pop-light", T("m1", "max") + 0.3 + k * 0.42, 0.22)
    put("impact-trailer", T("w1", "week") - 0.02, 0.6, 2.2)
    put("type-bell", T("w1", "week") + 0.3, 0.35)
    for lid in ("w3", "w4", "w5", "w6"):
        put("whoosh-fast", L[lid][0] - 0.1, 0.3)
    s5e = L["s5"][1]
    for k in range(3):
        put("glitch-text", s5e + 0.08 + k * 0.3, 0.22, 0.22)
    put("whoosh-fast", tl["cats"][0] - 0.12, 0.4)
    put("pop-light", tl["cats"][0] + 0.5, 0.25)
    # music: the drop lands on "travel"
    m = audio(MUSIC)
    start = drop - DROP
    mus = np.zeros(n, np.float32)
    i0 = at(start)
    seg = m[max(0, -i0):]
    mus[max(0, i0): max(0, i0) + len(seg)] = seg[: n - max(0, i0)]
    # duck under speech (smoothed): about 15 dB under the voice while he talks, up for the montage; silence for the turn
    from scipy.ndimage import uniform_filter1d
    sp = uniform_filter1d(speech, int(0.12 * SR))
    g = 0.7 - 0.52 * sp
    turn0, turn1 = at(L["l2"][0] - 0.15), at(drop - 0.01)
    g[turn0:turn1] = 0.0
    ramp = int(0.25 * SR)
    g[turn0 - ramp:turn0] *= np.linspace(1, 0, ramp)
    g = uniform_filter1d(g, int(0.03 * SR))
    mus *= g
    # the cats: music keeps going, end with a short fade so the loop back to frame 1 feels intended
    end = at(tl["dur"])
    mus[end - int(0.35 * SR):end] *= np.linspace(1, 0.2, int(0.35 * SR))
    out = voice + 0.75 * fx + mus
    out = out[: end]
    import soundfile as sf
    wav = W / "mix.wav"
    sf.write(wav, np.stack([out, out], 1), SR, subtype="FLOAT")
    return wav


def mux(picture: Path, wav: Path) -> Path:
    OUT.mkdir(exist_ok=True)
    out = OUT / "week1-intro-9x16.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(picture), "-i", str(wav), "-filter_complex",
                    "[1:a]alimiter=limit=0.8:attack=4:release=60:level=disabled,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[a]", "-map", "0:v", "-map", "[a]", "-c:v", "copy",
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
