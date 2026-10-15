"""Fetch public Instagram posts and reels for study: caption, author, the video file, every carousel slide, a screenshot.

    python scripts/research/ig_fetch.py <shortcode or URL> [...] --out=/tmp/claude-0/refs

Uses the public embed page in headless Chromium (no login, no API). For research only: keep other creators'
media out of the repo and out of posts.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import requests
from playwright.sync_api import sync_playwright

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"


def code_of(s: str) -> str:
    m = re.search(r"instagram\.com/(?:p|reel|reels|tv)/([A-Za-z0-9_-]+)", s)
    return m.group(1) if m else s


def main(codes: list[str], out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    meta_f = out / "embeds.json"
    data = json.loads(meta_f.read_text()) if meta_f.exists() else {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 540, "height": 960}, user_agent=UA)
        seen: list[str] = []
        pg.on("request", lambda r: seen.append(r.url) if (r.resource_type in ("media", "image") or ".mp4" in r.url) else None)
        for c in codes:
            seen.clear()
            try:
                pg.goto(f"https://www.instagram.com/p/{c}/embed/captioned/", wait_until="networkidle", timeout=60000)
            except Exception as e:  # noqa: BLE001
                data[c] = {"err": str(e)[:160]}
                continue
            cap = pg.evaluate("() => (document.querySelector('.Caption')||{}).innerText || ''")
            user = pg.evaluate("() => (document.querySelector('.UsernameText, .Username')||{}).innerText || ''")
            # carousel: click through every slide so each image loads
            for _ in range(20):
                nxt = pg.query_selector("button[aria-label*='Next'], .coreSpriteRightChevron, [aria-label='Next']")
                if not nxt:
                    break
                try:
                    nxt.click(timeout=2000)
                    pg.wait_for_timeout(500)
                except Exception:  # noqa: BLE001
                    break
            for sel in [".EmbeddedMediaVideo", "video", "[aria-label*='Play']", ".Content"]:
                el = pg.query_selector(sel)
                if el:
                    try:
                        el.click(timeout=2000)
                    except Exception:  # noqa: BLE001
                        pass
            pg.wait_for_timeout(3000)
            v = pg.evaluate("() => { const v = document.querySelector('video'); return v ? (v.currentSrc || v.src) : null }")
            video = v if v and v.startswith("http") else next((u for u in seen if ".mp4" in u), None)
            imgs = list(dict.fromkeys(u for u in seen if re.search(r"(cdninstagram\.com|fbcdn\.net)/.+\.(jpg|webp|heic)", u) and "s150x150" not in u and "profile" not in u))
            pg.screenshot(path=str(out / f"{c}.png"))
            d = {"user": user.strip(), "caption": cap, "video_url": video, "images": imgs}
            if video:
                r = requests.get(video, headers={"User-Agent": UA}, timeout=120)
                if r.ok and len(r.content) > 50000:
                    (out / f"{c}.mp4").write_bytes(r.content)
                    d["video_file"] = f"{c}.mp4"
            saved = []
            for i, u in enumerate(imgs[:20]):
                r = requests.get(u, headers={"User-Agent": UA}, timeout=60)
                if r.ok and len(r.content) > 15000:
                    f = out / f"{c}_{i:02d}.jpg"
                    f.write_bytes(r.content)
                    saved.append(f.name)
            d["image_files"] = saved
            data[c] = d
            print(c, d["user"], "| video:", bool(d.get("video_file")), "| images:", len(saved), "|", cap[:160].replace("\n", " "))
        b.close()
    meta_f.write_text(json.dumps(data, indent=1, ensure_ascii=False))
    return data


if __name__ == "__main__":
    o = Path(next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--out=")), "/tmp/claude-0/refs"))
    main([code_of(a) for a in sys.argv[1:] if not a.startswith("--")], o)
