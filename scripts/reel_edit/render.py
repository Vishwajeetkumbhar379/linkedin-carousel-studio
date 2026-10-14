"""Render a talking-head reel (Vish on camera) in two vertical layouts from the same layers (16:9 still available).

    python scripts/reel_edit/render.py video-projects/<slug> [--page=edit-reel] [--layouts=9x16,4x5] [--stills=12.0,20.5]

Layers: the real shot (work/frames), the cut-out (work/cut, prep.py), graphics and captions
(templates/video/talking/<page>.html). Each layout is laid out from the layers, never cropped from another.
Writes video-projects/<slug>/out/<slug>-<layout>.mp4 (+ mix.wav, spec.json, stills/*.jpg).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from render3d import serve  # noqa: E402
import sfx  # noqa: E402
from prep import src_times  # noqa: E402

FPS = 30
SIZES = {"9x16": (1080, 1920), "4x5": (1080, 1350), "16x9": (1920, 1080)}
KEYS = {"edit", "claude", "phone", "take", "mistakes", "coffee", "pause", "um", "twice", "captions", "zoom", "graphic",
        "three", "versions", "reels", "youtube", "linkedin", "free", "open", "source", "film", "setup"}


def norm(w: str) -> str:
    return re.sub(r"[^a-z0-9']", "", w.lower())


def words_fixed(edl: dict, fixes: dict) -> list[dict]:
    ws = [dict(x, k=n) for n, k in enumerate(edl["keeps"]) for x in k["w"]]
    for i, x in enumerate(ws):
        x["start"] = max(0.0, x["start"])
        x["end"] = max(x["end"], x["start"] + 0.08)
    for src, dst in fixes.items():
        a, b = src.split(), dst.split()
        for i in range(len(ws) - len(a) + 1):
            if [norm(x["text"]) for x in ws[i:i + len(a)]] == [norm(t) for t in a]:
                punct = re.sub(r"[\w']", "", ws[i + len(a) - 1]["text"])[-1:]
                if len(a) == len(b):
                    for j, t in enumerate(b):
                        ws[i + j]["text"] = t
                else:
                    ws[i]["text"] = dst
                    for j in range(1, len(a)):
                        ws[i + j]["text"] = ""
                if punct and not ws[i + len(a) - 1]["text"].endswith(punct):
                    ws[i + len(a) - 1]["text"] += punct
    return [x for x in ws if x["text"]]


BREAK_BEFORE = {"in", "and", "which", "where", "is", "on", "to", "the", "every", "i", "these", "with"}
NO_END = {"every", "a", "the", "my", "i", "this", "these", "your", "to"}


def captions(ws: list[dict], dur: float) -> list[dict]:
    """1-3 word chunks inside one phrase: break before function words, never end on one, never leave a word alone."""
    chunks = []
    for k in sorted({x["k"] for x in ws}):
        isl = [x for x in ws if x["k"] == k]
        cur: list[dict] = []
        for j, x in enumerate(isl):
            left = len(isl) - j  # words still to place, this one included
            n = norm(x["text"])
            chars = len(" ".join(y["text"] for y in cur))
            if cur and left > 1 or (cur and left == 1 and len(cur) > 3):
                if len(cur) >= 2 and n in BREAK_BEFORE and not (n == "in" and left == 1):
                    chunks.append(cur); cur = []
                elif (len(cur) >= 3 or chars >= 14) and norm(cur[-1]["text"]) not in NO_END:
                    chunks.append(cur); cur = []
            cur.append(x)
            if x["text"].endswith((",", ".", "?", "!")) and left > 1:
                chunks.append(cur); cur = []
        if cur:
            chunks.append(cur)
    out = []
    for i, c in enumerate(chunks):
        t0 = max(0.0, c[0]["start"] - 2 / FPS)
        t1 = chunks[i + 1][0]["start"] - 2 / FPS if i + 1 < len(chunks) else dur
        if t1 - c[-1]["end"] > 0.5:  # long pause after: clear the caption
            t1 = c[-1]["end"] + 0.25
        text = re.sub(r"[.,!?]+$", "", " ".join(y["text"] for y in c)).replace(",", "")
        out.append({"t0": round(t0, 3), "t1": round(t1, 3), "text": text,
                    "key": any(norm(y["text"]) in KEYS for y in c),
                    "w": [{"t": round(y["start"], 3), "x": re.sub(r"[.,!?]+$", "", y["text"])} for y in c]})
    return out


def person_box(w: Path, n: int) -> dict:
    tops, cxs, faces = [], [], []
    for k in np.linspace(0, n - 1, 24).astype(int):
        im = cv2.imread(str(w / "cut" / f"c_{k:05d}.webp"), cv2.IMREAD_UNCHANGED)
        if im is None:
            continue
        a = im[:, :, 3] > 128
        rows = np.where(a.any(1))[0]
        top = int(rows[0])
        band = a[top:top + 300]
        cols = np.where(band.any(0))[0]
        tops.append(top)
        cxs.append(int((cols[0] + cols[-1]) / 2))
        faces.append(top + 230)
    return {"top": int(np.median(tops)), "cx": int(np.median(cxs)), "face": int(np.median(faces)), "w": 1080, "h": 1920}


def waveform(proj: Path, edl: dict) -> dict:
    a, sr = sf.read(proj / "work" / "audio16k.wav", dtype="float32")
    hop = sr // 2
    rms = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a) - hop, hop)])
    rms = np.clip(rms / (np.percentile(rms, 98) + 1e-9), 0, 1)
    kept = [[k["src_start"], k["src_end"]] for k in edl["keeps"]]
    return {"bars": [round(float(x), 3) for x in rms], "bar_s": 0.5, "kept": kept,
            "retakes": [c["src"] for c in edl["cut"] if c["why"].startswith("retake")],
            "fillers": [c for c in edl["cut"] if not c["why"].startswith("retake")]}


def build_spec(proj: Path, work: str = "work") -> dict:
    w = proj / work
    edl = json.loads((proj / "work" / "edl.json").read_text())
    ov = json.loads((proj / "work" / "overrides.json").read_text()) if (proj / "work" / "overrides.json").exists() else {}
    meta = json.loads((w / "prep.json").read_text())
    n = meta["frames"]
    dur = n / FPS
    ws = words_fixed(edl, ov.get("fix", {}))
    retake_words = sum(c["src"][1] - c["src"][0] for c in edl["cut"])
    spec = {
        "slug": proj.name, "frames": n, "fps": FPS, "duration": dur,
        "base": f"/video-projects/{proj.name}/{work}", "work": work,
        "words": [{"t": round(x["start"], 3), "e": round(x["end"], 3), "x": x["text"]} for x in ws],
        "captions": captions(ws, dur),
        "src": [round(t, 3) for t in src_times(edl)],
        "person": person_box(w, n),
        "keeps": [k["out_start"] for k in edl["keeps"]],
        "wave": waveform(proj, edl),
        "raw_s": edl["raw_duration"], "final_s": round(dur, 1),
        "cut_s": round(edl["raw_duration"] - dur, 1), "retake_s": round(retake_words, 1),
    }
    fx = ov.get("fix", {})
    def clean(t: str) -> str:
        for a, b in fx.items():
            t = re.sub(rf"\b{re.escape(a)}\b", b, t)
        t = t.strip().rstrip(".")
        return t[0].upper() + t[1:]
    spec["wave"]["retakeText"] = [clean(c["words"]) for c in edl["cut"] if c["why"].startswith("retake")]
    # B-roll (broll_prep.py), real page captures, the real pipeline log and this page's own source for the "graphics" line
    bi = proj / "work" / "broll" / "index.json"
    if bi.exists():
        spec["broll"] = json.loads(bi.read_text())
        spec["brollBase"] = f"/video-projects/{proj.name}/work/broll"
    bc = proj / "broll.json"
    if bc.exists():
        spec["pages"] = {k: "/" + v for k, v in json.loads(bc.read_text()).get("pages", {}).items()}
    tr = json.loads((proj / "work" / "transcript.json").read_text())
    fill = [c for c in edl["cut"] if not c["why"].startswith("retake")]
    spec["term"] = [f"$ python scripts/reel_edit/make.py video-projects/{proj.name}",
                    f"› transcribe (local Whisper): {len(tr['words'])} words, {edl['raw_duration']:.1f} s",
                    f"› retakes: {len(spec['wave']['retakes'])} · fillers: {len(fill)} · pauses: {round(spec['cut_s'] - spec['retake_s'])} s",
                    f"› cut: {edl['raw_duration']:.1f} s → {dur:.1f} s",
                    f"› cut-out: {n:,} frames",
                    "› render 9:16 + 4:5",
                    "✓ done"]
    (proj / "out").mkdir(exist_ok=True)
    (proj / "out" / f"spec-{work}.json").write_text(json.dumps(spec))
    return spec


SFX_DIR = ROOT / ".claude" / "skills" / "media-use" / "audio" / "assets" / "sfx"  # Pixabay licence, see CREDITS.md
SFX_GAIN = {"whoosh-short": .35, "whoosh": .3, "whoosh-cinematic": .3, "pop": .35, "click": .3, "click-soft": .35, "key-press": .25,
            "typing": .18, "impact-bass-1": .45, "impact-bass-2": .45, "riser": .25, "ping": .25, "chime": .25, "sparkle": .25, "notification": .25}


def load_audio(path: Path, sr: int) -> np.ndarray:
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32).copy()


def mix(proj: Path, spec: dict, events: list[dict]) -> Path:
    v, sr = sf.read(proj / spec["work"] / "voice.wav", dtype="float32")
    assert sr == sfx.SR
    n = len(v)
    vr = np.sqrt(np.mean(v[np.abs(v) > 1e-4] ** 2))
    fx = np.zeros(n, np.float32)
    real = [e for e in events if (SFX_DIR / f"{e['s']}.mp3").exists()]
    events = [e for e in events if e not in real]
    cache: dict[str, np.ndarray] = {}
    for e in real:
        if e["s"] not in cache:
            y = load_audio(SFX_DIR / f"{e['s']}.mp3", sr)
            cache[e["s"]] = y / (np.abs(y).max() + 1e-9)
        y = cache[e["s"]] * SFX_GAIN.get(e["s"], .3) * e.get("g", 1.0) * vr / 0.1
        s = int(e["t"] * sr)
        m = max(0, min(len(y), n - s))
        fx[s:s + m] += y[:m]
    lib = {"whoosh": lambda: sfx.whoosh(0.45, 4) * 0.22, "zoom": lambda: (sfx.whoosh(0.35, 7) * 0.16 + np.pad(sfx.thump(0.3), (0, int(0.05 * sr)))[:int(0.35 * sr)] * 0.25),
           "click": lambda: sfx.click(3) * 0.12, "click2": lambda: sfx.click(11) * 0.10, "pop": lambda: sfx.pop() * 0.16,
           "tap": lambda: sfx.thump(0.18) * 0.22}
    for e in events:
        y = lib.get(e["s"], lib["click"])().astype(np.float32) * (vr / 0.1) * 0.6
        s = int(e["t"] * sr)
        m = max(0, min(len(y), n - s))
        fx[s:s + m] += y[:m]
    bc = proj / "broll.json"
    mus = json.loads(bc.read_text()).get("music") if bc.exists() else None
    if mus and (proj / mus["src"]).exists():
        bed = load_audio(proj / mus["src"], sr)[int(mus.get("in", 0) * sr):]
        bed = np.tile(bed, int(np.ceil(n / len(bed))))[:n]
        f = int(0.4 * sr)
        bed[:f] *= np.linspace(0, 1, f)
        bed[-int(1.2 * sr):] *= np.linspace(1, 0, int(1.2 * sr))
        bed_db, duck_k = -8, 0.7  # references: music only ~4 to 6 dB under the voice
    else:
        bed = sfx.bed(n / sr + 0.1, bpm=84)[:n].astype(np.float32)
        bed = np.pad(bed, (0, max(0, n - len(bed))))
        bed_db, duck_k = -17, 0.55
    # duck the bed under speech
    env = np.abs(v)
    k = int(0.25 * sr)
    sm = np.convolve(env, np.ones(k) / k, mode="same")
    duck = np.where(sm > 0.01, duck_k, 1.0).astype(np.float32)
    duck = np.convolve(duck, np.ones(k) / k, mode="same")
    br = np.sqrt(np.mean(bed ** 2)) + 1e-9
    bed = bed / br * vr * 10 ** (bed_db / 20) * duck
    out = v + fx + bed
    st = np.stack([out, out], 1)
    raw = proj / "out" / f"mix_raw-{spec['work']}.wav"
    sf.write(raw, st, sr)
    dst = proj / "out" / ("mix.wav" if spec["work"] == "work" else f"mix-{spec['work']}.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", str(dst)], check=True)
    return dst


def render(proj: Path, spec: dict, page: str, layout: str, stills: list[float] | None = None) -> tuple[Path, list[dict]]:
    from playwright.sync_api import sync_playwright

    W, H = SIZES[layout]
    out = proj / "out"
    tag = "" if spec["work"] == "work" else "-" + spec["work"].replace("work-", "")
    vid = out / f"{proj.name}{tag}-{layout}-video.mp4"
    with serve(ROOT) as base, sync_playwright() as p:
        b = p.chromium.launch(args=["--disable-web-security"])
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        errs: list[str] = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append("console: " + m.text) if m.type == "error" else None)
        pg.goto(f"{base}/templates/video/talking/{page}.html?layout={layout}")
        pg.wait_for_function("window.STAGE_LOADED === true", timeout=60000)
        pg.evaluate("s => window.setup(s)", spec)
        pg.wait_for_function("window.READY === true")
        if errs:
            raise RuntimeError(errs)
        events = pg.evaluate("window.SFX || []")
        if stills is not None:
            (out / "stills").mkdir(exist_ok=True)
            for t in stills:
                pg.evaluate("i => window.frame(i)", int(t * FPS))
                pg.screenshot(path=str(out / "stills" / f"{layout}{tag}-{t:05.2f}.jpg"), type="jpeg", quality=85)
            b.close()
            return out / "stills", events
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                               "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-r", str(FPS), str(vid)],
                              stdin=subprocess.PIPE)
        for i in range(spec["frames"]):
            pg.evaluate("i => window.frame(i)", i)
            ff.stdin.write(pg.screenshot(type="jpeg", quality=92))
            if i % 150 == 0:
                print(f"{layout}: {i}/{spec['frames']}", flush=True)
        ff.stdin.close()
        ff.wait()
        if errs:
            print("page errors:", errs[:5])
        b.close()
    return vid, events


def mux(proj: Path, layout: str, vid: Path, wav: Path) -> Path:
    dst = proj / "out" / vid.name.replace("-video.mp4", ".mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(vid), "-i", str(wav), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(dst)], check=True)
    vid.unlink()
    return dst


if __name__ == "__main__":
    proj = Path(sys.argv[1])
    args = dict(a[2:].split("=", 1) for a in sys.argv[2:] if a.startswith("--") and "=" in a)
    page = args.get("page", "edit-reel")
    spec = build_spec(proj, args.get("work", "work"))
    spec["keyWords"] = ["claude", "coffee", "twice", "captions", "zoom", "graphic", "versions", "free", "film", "setup", "um"]
    spec["pageName"] = f"templates/video/talking/{page}.html"
    import html as _h
    src = (ROOT / spec["pageName"]).read_text().splitlines()
    a = next((i for i, l in enumerate(src) if "function timeline()" in l), 0)
    code = []
    for l in src[a:a + 70]:
        l = _h.escape(l[:92])
        l = re.sub(r"(&#x27;[^&]*?&#x27;|&quot;.*?&quot;)", r"<u>\1</u>", l)
        l = re.sub(r"\b(const|function|return|if|for|let)\b", r"<i>\1</i>", l)
        l = re.sub(r"\b(T\.[a-z0-9]+)\b", r"<b>\1</b>", l)
        code.append(l)
    spec["code"] = "\n".join(code)
    stills = [float(x) for x in args["stills"].split(",")] if "stills" in args else None
    if "mix-only" in sys.argv:
        _, ev = render(proj, spec, page, "9x16", [])
        print("mixed", mix(proj, spec, ev))
        sys.exit(0)
    for lay in args.get("layouts", "9x16,4x5").split(","):
        vid, events = render(proj, spec, page, lay, stills)
        if stills is None:
            wav = proj / "out" / ("mix.wav" if spec["work"] == "work" else f"mix-{spec['work']}.wav")
            if not wav.exists() or args.get("remix"):
                wav = mix(proj, spec, events)
            print("wrote", mux(proj, lay, vid, wav))
        else:
            print("stills in", vid)
