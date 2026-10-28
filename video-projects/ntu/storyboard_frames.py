"""Storyboard frames for every episode: the hook, then each new shot a second after it lands. -> work/<key>_<t>.jpg + work/<key>_frames.json"""
import json, re, subprocess, sys
from pathlib import Path
H = Path(__file__).resolve().parent; CR = H.parents[1] / "scripts/canvas_reel.py"
for k in (sys.argv[1:] or ["e1", "e2", "e3", "e4", "e5", "e6", "e7"]):
    subprocess.run(["python3", str(CR), ".", k, "--stills", "0.6"], cwd=H, check=True, capture_output=True)
    D = json.loads(re.search(r"const D = (\{.*?\});  //", (H / "work" / f"{k}.html").read_text(), re.S).group(1))
    def done(e):  # the moment a beat has fully played out: last row, last pin or route, counter or bar filled
        ends = [e["at"] + 1.1] + [r["at"] + 0.7 for r in e.get("rows", []) + e.get("lines", []) if isinstance(r, dict) and "at" in r]
        ends += [p["at"] + p.get("delay", 0) + 0.8 for p in e.get("pins", [])] + [r["at"] + r.get("dur", 1.4) + 0.3 for r in e.get("routes", [])]
        ends += [e[f] + 1.0 for f in ("fill", "until") if f in e] + [e["at"] + len(e.get("items", [])) * e.get("gap", 0.14) + 0.6]
        if "press" in e: return round(e["press"] + 0.2, 2)  # a dialog: catch it as the button is pressed
        return round(max(ends), 2)
    blocks = [e for e in D["els"] if e["type"] not in ("stamp", "chip")]
    ts = [0.6] + [done(e) for e in blocks if not e.get("beside")]
    ts = sorted(set(min(t, D["end"] - 0.3) for t in ts))
    ts = [t for i, t in enumerate(ts) if i == 0 or t - ts[i - 1] > 0.8] + [round(D["end"] - 0.6, 2)]
    subprocess.run(["python3", str(CR), ".", k, "--stills", ",".join(map(str, ts))], cwd=H, check=True, capture_output=True)
    (H / "work" / f"{k}_frames.json").write_text(json.dumps({"times": ts, "end": D["end"]}))
    print(k, len(ts), "frames", f"{D['end']:.0f}s")
