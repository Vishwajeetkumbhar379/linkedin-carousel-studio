"""Find B-roll for a line by describing the shot: movingimagearchive.com (public domain, free to reuse).

    python3 video-projects/week-02-talks/broll_search.py "query" [...]     -> broll/search/<slug>.json + a contact sheet
    python3 video-projects/week-02-talks/broll_search.py --get <clip id> <name>  -> broll/<name>.mp4 + credits.json

Each pick is credited (source film and year) in broll/credits.json.
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
API = "https://www.movingimagearchive.com/api/search"
OUT = HERE / "broll"


def search(q: str, n: int = 8) -> list:
    body = json.dumps({"query": q, "color": "all", "aspectRatio": "all", "offset": 0}).encode()
    req = urllib.request.Request(API, data=body, method="POST", headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    return json.load(urllib.request.urlopen(req, timeout=90))["clips"][:n]


def thumb(url: str) -> np.ndarray:
    data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
    im = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    return cv2.resize(im, (int(im.shape[1] * 180 / im.shape[0]), 180))


if __name__ == "__main__":
    a = sys.argv[1:]
    (OUT / "search").mkdir(parents=True, exist_ok=True)
    if a[0] == "--get":
        cid, name = a[1], a[2]
        hits = {c["id"]: c for f in (OUT / "search").glob("*.json") for c in json.loads(f.read_text())["clips"]}
        c = hits[cid]
        (OUT / f"{name}.mp4").write_bytes(urllib.request.urlopen(urllib.request.Request(c["videoUrl"], headers={"User-Agent": "Mozilla/5.0"}), timeout=120).read())
        cred = json.loads((OUT / "credits.json").read_text()) if (OUT / "credits.json").exists() else {}
        cred[name] = {"film": c["sourceTitle"], "year": c.get("sourceYear"), "clip": cid, "at": [c["startSeconds"], c["endSeconds"]],
                      "source": "movingimagearchive.com (public domain, free to reuse)"}
        (OUT / "credits.json").write_text(json.dumps(cred, indent=1))
        print(name, c["sourceTitle"], c.get("sourceYear"), round(c["durationSeconds"], 1), "s")
        sys.exit()
    for q in a:
        slug = re.sub(r"[^a-z0-9]+", "-", q.lower()).strip("-")[:40]
        clips = search(q)
        (OUT / "search" / f"{slug}.json").write_text(json.dumps({"query": q, "clips": clips}, indent=1))
        row = []
        for i, c in enumerate(clips):
            try:
                im = thumb(c["thumbnailUrl"])
            except Exception:
                continue
            cv2.putText(im, f"{i} {c.get('sourceYear') or ''} {c['durationSeconds']:.0f}s {c['colorMode'][:3]}", (4, 18), 0, 0.5, (0, 255, 255), 1)
            row.append(im)
        if row:
            cv2.imwrite(str(OUT / "search" / f"{slug}.jpg"), np.hstack(row))
        print(slug, len(clips))
