"""Free stock B-roll from Mixkit (no key; Mixkit Stock Video Free License: free in videos, no credit needed,
don't resell the clips themselves).

    python scripts/broll/stock.py "pouring coffee" [--n=6] [--out=video-projects/<slug>/broll]   # list + download
    python scripts/broll/stock.py --id=1730 --out=...                                             # one clip

Writes <out>/mixkit-<id>.mp4 (720p vertical-friendly source) and <out>/stock.json with title, id, page and licence.
Pick clips that act the spoken line out; never use stock to fake a result.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

import requests

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}


def search(q: str) -> list[dict]:
    slug = re.sub(r"[^a-z0-9]+", "-", q.lower()).strip("-")
    h = requests.get(f"https://mixkit.co/free-stock-video/{slug}/", headers=UA, timeout=30).text
    out, seen = [], set()
    for m in re.finditer(r'data-algolia-analytics-object-id="video-(\d+)"(.*?)</a>', h, re.S):
        vid, body = m.group(1), m.group(2)
        if vid in seen:
            continue
        seen.add(vid)
        alt = re.search(r'alt="([^"]*)"', body)
        page = re.search(r'href="(/free-stock-video/[^"]+)"', body)
        out.append({"id": vid, "title": html.unescape(alt.group(1)) if alt else "", "page": "https://mixkit.co" + page.group(1) if page else ""})
    return out


def download(vid: str, out: Path) -> Path | None:
    out.mkdir(parents=True, exist_ok=True)
    dst = out / f"mixkit-{vid}.mp4"
    if dst.exists():
        return dst
    for q in ("1080", "720", "360"):
        r = requests.get(f"https://assets.mixkit.co/videos/{vid}/{vid}-{q}.mp4", headers=UA, timeout=120)
        if r.ok and len(r.content) > 50000:
            dst.write_bytes(r.content)
            return dst
    return None


if __name__ == "__main__":
    a = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    q = " ".join(x for x in sys.argv[1:] if not x.startswith("--"))
    out = Path(a.get("out", "broll"))
    meta_f = out / "stock.json"
    meta = json.loads(meta_f.read_text()) if meta_f.exists() else {}
    items = [{"id": a["id"], "title": "", "page": ""}] if "id" in a else search(q)[: int(a.get("n", 6))]
    for it in items:
        p = download(it["id"], out)
        if p:
            meta[it["id"]] = {**it, "file": p.name, "query": q, "licence": "Mixkit Stock Video Free License"}
            print(f'{it["id"]}: {it["title"]} -> {p}')
    out.mkdir(parents=True, exist_ok=True)
    meta_f.write_text(json.dumps(meta, indent=1))
