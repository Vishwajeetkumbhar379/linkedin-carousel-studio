"""Plan the cuts for a talking-head clip: drop dead air, retakes and filler, keep natural beats.

    python scripts/reel_edit/cutplan.py video-projects/<slug>

Needs work/audio16k.wav and work/transcript.json (scripts/reel_edit/transcribe.py).
Writes work/edl.json: keeps [{src_start, src_end, out_start, words}] plus what was cut and why.
Rules (edit-kit-docs/EDITING-PLAYBOOK.md): cut between phrases at real silence, never inside a phrase;
keep the last clean take of a repeated line; gaps between phrases ~0.2 s, a little longer at sentence ends.
Optional work/overrides.json: {"drop": [[s, e], ...], "head": seconds} to force extra cuts.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

FILLERS = {"hey", "yeah", "so", "um", "uh", "okay", "ok", "like", "you", "know", "right", "and"}
PRE, POST = 0.05, 0.11          # pad before onset, after offset (consonant decay)
GAP_PHRASE, GAP_SENT = 0.10, 0.20  # silence added between islands (on top of pads)


def norm(w: str) -> str:
    return re.sub(r"[^a-z']", "", w.lower())


def islands(a: np.ndarray, sr: int, thr_db: float = -52, min_sil: float = 0.30, min_len: float = 0.08):
    hop = sr // 100
    n = len(a) // hop
    db = np.array([20 * np.log10(np.sqrt(np.mean(a[i * hop:(i + 1) * hop] ** 2)) + 1e-9) for i in range(n)])
    on = db > thr_db
    out, i = [], 0
    while i < n:
        if on[i]:
            j = i
            while j < n and (on[j] or (j + int(min_sil * 100) < n and on[j:j + int(min_sil * 100)].any())):
                j += 1
            if (j - i) / 100 >= min_len:
                out.append([i / 100, j / 100])
            i = j
        else:
            i += 1
    return out, db


def island_words(a, sr, isl, w: Path) -> list[dict]:
    """Transcribe each speech island on its own: whisper's word times drift across long silences, per-island they don't."""
    cache = w / "islands.json"
    if cache.exists():
        c = json.loads(cache.read_text())
        if [g["s"] for g in c] == [s for s, _ in isl]:
            return c
    from faster_whisper import WhisperModel
    m = WhisperModel("small.en", device="cpu", compute_type="int8")
    out = []
    for s, e in isl:
        s0 = max(0.0, s - 0.15)
        seg = a[int(s0 * sr):int((e + 0.2) * sr)]
        r, _ = m.transcribe(seg, word_timestamps=True, beam_size=5, condition_on_previous_text=False)
        ws = [{"text": x.word.strip(), "start": round(x.start + s0, 3), "end": round(x.end + s0, 3)} for y in r for x in y.words]
        out.append({"s": s, "e": e, "words": [x["text"] for x in ws], "w": ws})
    cache.write_text(json.dumps(out, indent=1))
    return out


def dip_after(db: np.ndarray, t0: float, t1: float) -> float | None:
    """Deepest 10 ms frame between t0 and t1 if it is a real dip (>= 15 dB under the phrase)."""
    a, b = int(t0 * 100), int(t1 * 100)
    if b <= a:
        return None
    k = a + int(np.argmin(db[a:b]))
    return k / 100 if db[k] < np.median(db[a:b]) - 15 else None


def plan(proj: Path) -> dict:
    w = proj / "work"
    a, sr = sf.read(w / "audio16k.wav", dtype="float32")
    ov = json.loads((w / "overrides.json").read_text()) if (w / "overrides.json").exists() else {}
    isl, db = islands(a, sr)
    groups = island_words(a, sr, isl, w)
    cut = []
    # 1. lone filler blips ("yeah", "hey") and islands with no words
    keep = []
    for g in groups:
        t = [norm(x) for x in g["words"]]
        near = [o for o in groups if o is not g and min(abs(o["s"] - g["e"]), abs(g["s"] - o["e"])) < 0.6]
        if not t or (g["e"] - g["s"] < 1.0 and all(x in FILLERS for x in t)) or (g["e"] - g["s"] < 0.4 and len(t) <= 1 and not near):
            cut.append({"src": [g["s"], g["e"]], "why": "filler or noise", "words": " ".join(g["words"])})
        else:
            keep.append(g)
    # 2. retakes: a sentence restarted within 25 s (same first 3 words, or same first 2 + similar length) -> keep the last
    def sent_starts(i):
        prev_end = keep[i - 1]["words"][-1] if i else "."
        return prev_end.endswith((".", "?", "!")) or i == 0
    drop = set()
    for i, g in enumerate(keep):
        hi = [norm(x) for x in g["words"]][:3]
        for j in range(i + 1, len(keep)):
            if keep[j]["s"] - g["e"] > 25:
                break
            hj = [norm(x) for x in keep[j]["words"]][:3]
            if len(hi) >= 2 and hi[:2] == hj[:2]:
                drop.add(i)
                break
            # "comment edit" said as "come and edit": same 2nd/3rd word and same island shape
            if len(hi) >= 3 and hi[1:3] == hj[1:3] and hi[0][:3] == hj[0][:3]:
                drop.add(i)
                break
    for i in sorted(drop):
        cut.append({"src": [keep[i]["s"], keep[i]["e"]], "why": "retake (kept the later take)", "words": " ".join(keep[i]["words"])})
    keep = [g for i, g in enumerate(keep) if i not in drop]
    # 3. leading filler ("hey, you know, I didn't...") -> start at the first real word if there is a clean dip
    g0 = keep[0]
    lead = []
    for x in g0["w"]:
        if norm(x["text"]) in FILLERS:
            lead.append(x)
        else:
            break
    if lead:
        t = dip_after(db, max(g0["s"], lead[-1]["end"] - 0.35), lead[-1]["end"] + 0.4)
        if t:
            cut.append({"src": [g0["s"], t], "why": "opening filler", "words": " ".join(x["text"] for x in lead)})
            g0["s"] = t + PRE  # PRE is added back below
            g0["w"] = g0["w"][len(lead):]
            g0["words"] = [x["text"] for x in g0["w"]]
    if "head" in ov:
        keep[0]["s"] = ov["head"] + PRE
    for s, e in ov.get("drop", []):
        keep = [g for g in keep if not (g["s"] >= s - 0.05 and g["e"] <= e + 0.05)]
        cut.append({"src": [s, e], "why": "manual", "words": ""})
    # 4. lay out: pads, gaps; never let pads overlap the neighbour
    out, t = [], 0.0
    for i, g in enumerate(keep):
        s = max(0.0, g["s"] - PRE)
        e = g["e"] + POST
        if i + 1 < len(keep):
            e = min(e, keep[i + 1]["s"] - PRE - 0.02)
        if i:
            prev = out[-1]
            gap = GAP_SENT if keep[i - 1]["words"] and keep[i - 1]["words"][-1].endswith((".", "?", "!")) else GAP_PHRASE
            natural = g["s"] - keep[i - 1]["e"]
            if natural < 0.45:  # short natural beat: keep it whole, it is part of the phrase
                s = prev["src_end"]
            else:
                t += gap
        out.append({"src_start": round(s, 3), "src_end": round(e, 3), "out_start": round(t, 3), "words": " ".join(g["words"]),
                    "w": [{**x, "start": round(x["start"] - s + t, 3), "end": round(x["end"] - s + t, 3)} for x in g["w"]]})
        t += e - s
    edl = {"source": "raw", "duration": round(t, 3), "keeps": out, "cut": cut,
           "raw_duration": round(len(a) / sr, 2)}
    (w / "edl.json").write_text(json.dumps(edl, indent=1))
    return edl


if __name__ == "__main__":
    e = plan(Path(sys.argv[1]))
    for k in e["keeps"]:
        print(f'{k["out_start"]:6.2f}  [{k["src_start"]:6.2f}-{k["src_end"]:6.2f}]  {k["words"]}')
    print("CUT:")
    for c in e["cut"]:
        print(f'  {c["src"][0]:6.2f}-{c["src"][1]:6.2f} {c["why"]}: {c["words"]}')
    print(f'raw {e["raw_duration"]} s -> edit {e["duration"]} s')
