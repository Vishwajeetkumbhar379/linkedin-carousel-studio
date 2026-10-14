"""Delivery report for one raw take: what to keep doing and what to fix before the next recording.

    python scripts/reel_edit/coach.py video-projects/<slug> [--sheet=EDIT]

Reads work/edl.json (cutplan.py) and, if given or set in work/overrides.json ("sheet"), the shoot sheet line by line.
Writes out/delivery.md. Numbers come from this take only.
"""
from __future__ import annotations

import difflib
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def words(t: str) -> list[str]:
    t = re.sub(r"\[[^\]]*\]|\((up|down)\)", " ", t)
    return [w for w in re.sub(r"[^a-z0-9' ]", " ", t.lower()).split() if w]


def sheet_lines(key: str) -> list[str]:
    for f in sorted(glob.glob(str(ROOT / "content" / "shoot-sheets" / "*.json"))):
        for s in json.loads(Path(f).read_text()).get("sheets", []):
            if s.get("key", "").upper() == key.upper():
                return [s["hook"]] + [l["say"] for l in s["lines"]]
    return []


def main(proj: Path, key: str | None) -> Path:
    w = proj / "work"
    edl = json.loads((w / "edl.json").read_text())
    ov = json.loads((w / "overrides.json").read_text()) if (w / "overrides.json").exists() else {}
    key = key or ov.get("sheet")
    K = edl["keeps"]
    said = [x["text"] for k in K for x in k["w"]]
    speech = sum(k["src_end"] - k["src_start"] for k in K)
    wpm = len(said) / speech * 60
    isl = json.loads((w / "islands.json").read_text()) if (w / "islands.json").exists() else \
        [{"s": k["src_start"], "e": k["src_end"], "words": k["words"].split()} for k in K]
    # silence between any two things he said (kept or not), measured on the raw take
    gaps = [(isl[i + 1]["s"] - isl[i]["e"], "", " ".join(isl[i + 1]["words"])) for i in range(len(isl) - 1)]
    long_gaps = sorted([g for g in gaps if g[0] > 1.5], reverse=True)
    retakes = [c for c in edl["cut"] if c["why"].startswith("retake")]
    fillers = [c for c in edl["cut"] if not c["why"].startswith("retake")]
    dead = edl["raw_duration"] - edl["duration"]
    L = [f"# Delivery report: {proj.name}", "",
         f"Raw take {edl['raw_duration']:.0f} s, finished edit {edl['duration']:.0f} s. {dead:.0f} s cut ({dead / edl['raw_duration']:.0%}).", "",
         "## Numbers", "",
         f"- Pace while talking: {wpm:.0f} words a minute (target 150 to 170; @kallawaymarketing runs about 170).",
         f"- Pauses over 1.5 s: {len(long_gaps)}" + (f", longest {long_gaps[0][0]:.1f} s (before \"{long_gaps[0][2][:40]}\")." if long_gaps else "."),
         f"- Retakes: {len(retakes)}" + ("".join(f"\n  - \"{c['words']}\"" for c in retakes)),
         f"- Fillers cut: {len(fillers)}" + (": " + ", ".join(f"\"{c['words'].strip('. ')}\"" for c in fillers) if fillers else ""), ""]
    tips = []
    if any(c["why"] == "opening filler" for c in fillers) or (fillers and fillers[0]["src"][0] < 2):
        tips.append("Start on the hook's first word. Count 3 in your head with your mouth closed, then go. No \"hey\" or \"you know\".")
    if long_gaps and long_gaps[0][0] > 3:
        tips.append(f"Your longest pauses ({', '.join(f'{g[0]:.0f} s' for g in long_gaps[:3])}) are reading time. Read the next line on the teleprompter while you finish the current one, or film line by line and keep the camera rolling.")
    if wpm < 145:
        tips.append("Speed up a little inside sentences. Keep the pauses between lines, just tighten the words within one.")
    elif wpm > 185:
        tips.append("Slow down slightly; captions and graphics need a beat to land.")
    if retakes:
        tips.append("Retakes are fine: say the whole line again from its first word, like you did. The edit keeps the last clean take.")
    if key:
        lines = sheet_lines(key)
        heard = [re.sub(r"[^a-z0-9']", "", x.lower()) for x in said]
        miss = []
        for ln in lines:
            ws = words(ln)
            if not ws:
                continue
            best = max((difflib.SequenceMatcher(None, ws, heard[i:i + len(ws)]).ratio() for i in range(max(1, len(heard) - len(ws) + 1))), default=0)
            if best < 0.7:
                miss.append((best, re.sub(r"\s*/+\s*|\*", " ", ln).strip()))
        L += [f"## Against the shoot sheet ({key})", ""]
        L += [f"- Changed or skipped: \"{m[1]}\" (match {m[0]:.0%})" for m in miss] or ["- Every scripted line is in the take."]
        L.append("")
    L += ["## For the next take", ""] + [f"{i + 1}. {t}" for i, t in enumerate(tips or ["Same again: clean take."])] + [""]
    out = proj / "out"
    out.mkdir(exist_ok=True)
    (out / "delivery.md").write_text("\n".join(L))
    return out / "delivery.md"


if __name__ == "__main__":
    a = dict(x[2:].split("=", 1) for x in sys.argv[2:] if x.startswith("--"))
    print(main(Path(sys.argv[1]), a.get("sheet")).read_text())
