"""Capture a real web page as B-roll (full-page screenshot the video template scrolls like a screen recording).

    python scripts/screen_record.py https://github.com/tashfeenahmed/freellmapi [name]
    -> templates/video/broll/<name>.png  (1200 px wide, up to 7000 px tall)

Video beats use it with  {"look": "clip", "clip": {"url": "...", "scroll": true}}; make_batch.py records
missing clips automatically. Only record public pages; GitHub, docs and official blogs work best.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "templates" / "video" / "broll"


def name_for(url: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", url.lower().split("://", 1)[-1]).strip("-")[:80]


CSS = """body{margin:0;background:#fff;color:#1f2328;font:16px/1.6 -apple-system,'Segoe UI',Helvetica,Arial,sans-serif}
.top{background:#f6f8fa;border-bottom:1px solid #d1d9e0;padding:22px 40px 0}
.repo{font-size:22px;color:#0969da}.repo b{font-weight:600}
.tabs{display:flex;gap:26px;margin-top:18px;font-size:14px;color:#59636e}.tabs span{padding-bottom:10px}
.tabs span:first-child{color:#1f2328;font-weight:600;border-bottom:2px solid #fd8c73}
.wrap{padding:28px 40px}.box{border:1px solid #d1d9e0;border-radius:8px}
.bh{padding:10px 16px;border-bottom:1px solid #d1d9e0;font-size:14px;font-weight:600}
.md{padding:24px 32px}.md h1,.md h2{border-bottom:1px solid #d1d9e0;padding-bottom:.3em}
.md code{background:#eff1f3;border-radius:6px;padding:.2em .4em;font:85% ui-monospace,Menlo,monospace}
.md pre{background:#f6f8fa;border-radius:6px;padding:16px;overflow:hidden}.md pre code{background:none;padding:0}
.md img{max-width:100%}.md table{border-collapse:collapse}.md td,.md th{border:1px solid #d1d9e0;padding:6px 13px}
.md a{color:#0969da;text-decoration:none}"""


def github_html(url: str) -> str | None:
    """github.com/<owner>/<repo>: the real README, laid out like GitHub (its CSS host is blocked in the cloud)."""
    import urllib.request

    import markdown

    m = re.match(r"https?://github\.com/([^/]+)/([^/#?]+)/?$", url)
    if not m:
        return None
    owner, repo = m.groups()
    raw = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/"
    try:
        md = urllib.request.urlopen(raw + "README.md", timeout=30).read().decode()
    except Exception:  # noqa: BLE001
        return None
    md = re.sub(r"<(div|p)([^>]*)>", r'<\1\2 markdown="1">', md)
    body = markdown.markdown(md, extensions=["fenced_code", "tables", "md_in_html"])
    body = re.sub(r'src="(?!https?:|data:)/?', f'src="{raw}', body)
    body = re.sub(r'<a[^>]*>\s*<img[^>]*(shields\.io|badge)[^>]*>\s*</a>|<img[^>]*(shields\.io|badge)[^>]*>', "", body)  # badges add noise
    return (f"<!doctype html><meta charset=utf-8><style>{CSS}</style><div class=top><div class=repo>{owner} / <b>{repo}</b></div>"
            f"<div class=tabs><span>Code</span><span>Issues</span><span>Pull requests</span><span>Actions</span></div></div>"
            f"<div class=wrap><div class=box><div class=bh>README.md</div><div class=md>{body}</div></div></div>")


def record(url: str, name: str | None = None) -> Path:
    from PIL import Image
    from playwright.sync_api import sync_playwright

    OUT.mkdir(parents=True, exist_ok=True)
    dst = OUT / f"{name or name_for(url)}.png"
    if dst.exists():
        return dst
    px = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    with sync_playwright() as p:
        b = p.chromium.launch(proxy={"server": px} if px else None)
        pg = b.new_page(viewport={"width": 1200, "height": 1500}, device_scale_factor=1, color_scheme="light")
        html = github_html(url)
        if html:
            pg.set_content(html, wait_until="load", timeout=60000)
        else:
            pg.goto(url, timeout=60000, wait_until="domcontentloaded")
        pg.wait_for_timeout(2500)
        for sel in ["[aria-label='Close']", "button:has-text('Accept')", "button:has-text('Dismiss')"]:
            try:
                pg.locator(sel).first.click(timeout=800)
            except Exception:  # noqa: BLE001
                pass
        pg.screenshot(path=str(dst), full_page=True)
        b.close()
    im = Image.open(dst)
    if im.height > 7000:
        im.crop((0, 0, im.width, 7000)).save(dst)
    return dst


if __name__ == "__main__":
    print(record(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None))
