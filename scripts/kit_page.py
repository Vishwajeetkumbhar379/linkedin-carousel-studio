"""The posting kit: every finished post in posting order, with media, caption, first comment and download links.

    python scripts/kit_page.py <out_dir>        # writes <out_dir>/index.html, <out_dir>/img/*, <out_dir>/media/*

Media files that are not ready yet (a video still being voiced) show as "voice in progress".
"""
from __future__ import annotations

import datetime as dt
import html
import json
import shutil
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GH = "https://github.com/vishwajeetkumbhar379/linkedin-carousel-studio/blob/claude/content-engine-test-gate/"
ORDER = [
    "flagship/claude-instagram", "flagship/manus-video-editor", "flagship/claude-skills",
    "batch-03/ltk-auto-draft-apple-intelligence", "batch-03/claude-connectors-marketers-step-by-step",
    "batch-03/stop-influencers-target-kids", "batch-03/chatgpt-apps-connectors-marketers-step-by-step",
    "batch-02/free-llm-token-repos", "batch-02/claude-startups-free-year",
    "batch-02/claude-sonnet-5-5-slide-decks", "batch-03/unpaid-influencer-network-governor-race",
    "batch-02/mistral-large-4-le-chonk", "batch-02/faceless-ai-video-pipeline-free-tools",
    "batch-01/ai-creators-cheap-trust-isnt", "batch-02/ad-platforms-draft-ads-from-url",
    "2026-10-06-chatgpt-image-ads", "2026-10-06-eu-ai-text-watermark",
    "batch-01/openai-dots-always-on-agents", "2026-10-06-meta-creator-hub",
    "batch-01/meta-muse-small-business", "batch-01/campaign-report-three-decisions",
    "batch-01/tiktok-buy-direct-ad-network", "batch-01/creator-brief-mistakes-that-burn-budget",
    "batch-01/what-predicts-good-creator-partnership", "batch-01/frontier-deployed-engineers-carousel",
    "batch-01/frontier-deployed-engineers-ai-ops", "batch-01/google-ai-max-ai-brief-languages",
    "batch-01/instagram-edits-ai-assistant", "batch-01/made-on-youtube-creator-tools",
    "batch-01/youtube-custom-feeds", "batch-01/ai-creator-rule-out-pass",
    "batch-01/ai-wont-replace-content-team-bad-brief-will", "batch-01/make-ai-brief-you-back",
    "batch-01/linkedin-post-proofreader",
]
START = dt.date(2026, 10, 8)


def weekdays(n: int) -> list[dt.date]:
    d, out = START, []
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def jpg(src: Path, dst: Path, w: int) -> None:
    if not dst.exists():
        im = Image.open(src).convert("RGB")
        im.resize((w, round(im.height * w / im.width))).save(dst, quality=82)


def voiced_ok(d: Path) -> bool:
    """A video counts as ready only when its voice is the locked #25 voice (or #25 itself)."""
    if d.name == "ai-creators-cheap-trust-isnt" or d.parent.name == "flagship":
        return (d / "video.mp4").exists()
    try:
        v = json.loads((d / "video.json").read_text()).get("voice") or {}
    except Exception:  # noqa: BLE001
        return False
    return v.get("engine", "").startswith("chatterbox-clone") and (d / "video.mp4").exists()


def collect(out: Path) -> list[dict]:
    (out / "img").mkdir(parents=True, exist_ok=True)
    (out / "media").mkdir(exist_ok=True)
    items = []
    for key, day in zip(ORDER, weekdays(len(ORDER))):
        d = ROOT / "out" / key
        slug = d.name
        meta = json.loads((d / "meta.json").read_text()) if (d / "meta.json").exists() else {}
        cap = (d / "caption.md").read_text().strip() if (d / "caption.md").exists() else ""
        fc = (d / "first-comment.md").read_text().strip() if (d / "first-comment.md").exists() else ""
        hook = (meta.get("hook") or cap.split("\n")[0]).replace("*", "")
        it = {"key": key, "slug": slug, "day": day, "hook": hook, "caption": cap, "first": fc, "slides": [], "video": None, "ready": True}
        guide = d / "guide.md"
        it["guide"] = guide.read_text().strip() if guide.exists() else ""
        if (d / "video.json").exists() or (d / "video.mp4").exists():
            it["fmt"] = "Video"
            it["ready"] = voiced_ok(d)
            if it["ready"]:
                dst = out / "media" / f"{slug}.mp4"
                if not dst.exists() or dst.stat().st_mtime < (d / "video.mp4").stat().st_mtime:
                    shutil.copy(d / "video.mp4", dst)
                it["video"] = f"media/{slug}.mp4"
                it["dl"] = GH + f"out/{key}/video.mp4?raw=true"
            frames = d / "frames"
            poster = next((p for p in [frames / "b01.png", frames / "l1b.png"] if p.exists()), None)
            if poster:
                jpg(poster, out / "img" / f"{slug}-poster.jpg", 540)
                it["poster"] = f"img/{slug}-poster.jpg"
        else:
            slides = sorted((d / "slides").glob("slide-*.png"))
            if not slides and (d / "image.png").exists():
                slides = [d / "image.png"]
            it["fmt"] = "Carousel" if len(slides) > 1 else "Image"
            for s in slides:
                name = f"{slug}-{s.stem}.jpg"
                jpg(s, out / "img" / name, 720)
                it["slides"].append(f"img/{name}")
            f = "carousel.pdf" if (d / "carousel.pdf").exists() else "image.png"
            it["dl"] = GH + f"out/{key}/{f}?raw=true"
            it["dlname"] = "PDF" if f.endswith(".pdf") else "PNG"
            if (d / "slides.zip").exists():
                it["zip"] = GH + f"out/{key}/slides.zip?raw=true"
        items.append(it)
    return items


def page(items: list[dict]) -> str:
    e = html.escape
    ready = sum(1 for i in items if i["ready"])
    cards = []
    for n, it in enumerate(items, 1):
        if it["fmt"] == "Video":
            if it["ready"]:
                media = f'<video controls playsinline preload="none" poster="{it.get("poster", "")}" src="{it["video"]}"></video>'
            else:
                media = (f'<div class="pending"><img src="{it.get("poster", "")}" alt="" loading="lazy"><span>Voice in progress</span></div>'
                         if it.get("poster") else '<div class="pending"><span>Voice in progress</span></div>')
            dl = (f'<a href="{it["dl"]}" target="_blank" rel="noopener">LinkedIn MP4 (4:5)</a>'
                  f'<a href="{it["dl"].replace("video.mp4", "video-9x16.mp4")}" target="_blank" rel="noopener">Reel / Short MP4 (9:16)</a>') if it["ready"] else ""
        else:
            media = '<div class="deck" tabindex="0">' + "".join(f'<img src="{s}" alt="Slide {k + 1}" loading="lazy">' for k, s in enumerate(it["slides"])) + "</div>"
            dl = f'<a href="{it["dl"]}" target="_blank" rel="noopener">LinkedIn {it["dlname"]}</a>'
            if it.get("zip"):
                dl += f'<a href="{it["zip"]}" target="_blank" rel="noopener">Instagram slides (ZIP)</a>'
        guide = (f'<details><summary>Guide to send when people comment</summary><div class="copy"><div class="ch"><span>Guide</span>'
                 f'<button type="button" data-copy="g{n}">Copy</button></div><pre id="g{n}">{e(it["guide"])}</pre></div></details>') if it["guide"] else ""
        state = '<span class="st ok">Ready</span>' if it["ready"] else '<span class="st wait">Voice in progress</span>'
        cards.append(f'''<article class="post" id="p{n}">
  <div class="media">{media}</div>
  <div class="side">
    <div class="row"><span class="n">{n:02d}</span><span class="day">{it["day"]:%a %d %b}</span><span class="fmt">{it["fmt"]}</span>{state}</div>
    <h2>{e(it["hook"])}</h2>
    <div class="copy"><div class="ch"><span>Caption</span><button type="button" data-copy="c{n}">Copy</button></div><pre id="c{n}">{e(it["caption"])}</pre></div>
    <div class="copy"><div class="ch"><span>First comment</span><button type="button" data-copy="f{n}">Copy</button></div><pre id="f{n}">{e(it["first"])}</pre></div>
    {guide}
    <div class="dl">{dl}</div>
  </div>
</article>''')
    return f'''<title>Build with Vish Posting Kit</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&family=Newsreader:ital,opsz,wght@0,6..72,500;1,6..72,500&display=swap">
<style>
/* Layout: a posting queue. One row per post in the order to post it: media left, copy-ready text right. */
:root{{--bg:#F6F4F2;--panel:#FFFFFF;--ink:#17141C;--muted:#5F5967;--line:#E2DDE6;--accent:#4A44C4;--soft:#ECEAFB;--ok:#0F7A55;--wait:#B4502A;
--display:"Newsreader",Georgia,serif;--body:"Geist",system-ui,sans-serif;--mono:"Geist Mono",ui-monospace,monospace}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#0E0D12;--panel:#17161D;--ink:#F2F0F5;--muted:#A6A0B0;--line:#2C2A34;--accent:#A99CFF;--soft:#221F3A;--ok:#6FE0B5;--wait:#F09A75;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#0E0D12;--panel:#17161D;--ink:#F2F0F5;--muted:#A6A0B0;--line:#2C2A34;--accent:#A99CFF;--soft:#221F3A;--ok:#6FE0B5;--wait:#F09A75;color-scheme:dark}}
body{{background:var(--bg);color:var(--ink);font:400 16px/1.55 var(--body)}}
.wrap{{max-width:1120px;margin:0 auto;padding-inline:20px;padding-block:36px 64px;display:grid;gap:28px}}
h1,h2{{font-family:var(--display);font-weight:500;letter-spacing:-.02em;text-wrap:balance;margin:0}}
h1{{font-size:clamp(32px,5vw,48px);line-height:1.05}} h1 em{{color:var(--accent)}}
h2{{font-size:clamp(22px,2.6vw,28px);line-height:1.15}}
.lead{{max-width:68ch;color:var(--muted);margin:10px 0 0}}
.eyebrow{{font:500 12px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}}
.post{{display:grid;grid-template-columns:minmax(0,380px) minmax(0,1fr);gap:28px;padding-top:28px;border-top:1px solid var(--line)}}
@media (max-width:820px){{.post{{grid-template-columns:minmax(0,1fr)}}}}
video{{width:100%;max-width:100%;aspect-ratio:4/5;border-radius:16px;background:#000;display:block}}
.deck{{display:flex;gap:8px;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:6px}}
.deck img{{flex:0 0 100%;max-width:100%;height:auto;aspect-ratio:4/5;object-fit:cover;border-radius:16px;scroll-snap-align:start;border:1px solid var(--line)}}
.pending{{position:relative;aspect-ratio:4/5;border-radius:16px;overflow:hidden;background:var(--soft);display:grid;place-items:center}}
.pending img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.35}}
.pending span{{position:relative;font:500 13px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--wait);background:var(--panel);padding:8px 14px;border-radius:999px}}
.side{{display:grid;gap:14px;align-content:start;min-width:0}}
.row{{display:flex;flex-wrap:wrap;gap:10px;align-items:center;font:500 13px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}}
.n{{color:var(--accent);font-variant-numeric:tabular-nums}}
.fmt{{border:1px solid var(--line);border-radius:999px;padding:3px 10px}}
.st{{border-radius:999px;padding:3px 10px}} .st.ok{{color:var(--ok);background:var(--soft)}} .st.wait{{color:var(--wait);background:var(--soft)}}
.copy{{border:1px solid var(--line);border-radius:12px;background:var(--panel);overflow:hidden;min-width:0}}
.ch{{display:flex;justify-content:space-between;align-items:center;padding:8px 12px;border-bottom:1px solid var(--line);font:500 12px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}}
.copy pre{{margin:0;padding:12px 14px;white-space:pre-wrap;word-break:break-word;font:400 14.5px/1.55 var(--body);max-height:240px;overflow:auto}}
details summary{{cursor:pointer;font:500 14px var(--body);color:var(--accent);margin-bottom:8px}}
button{{font:500 13px var(--body);color:var(--accent);background:var(--soft);border:0;border-radius:999px;padding:5px 12px;cursor:pointer}}
button:focus-visible,a:focus-visible,summary:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
a{{color:var(--accent);font-weight:500}}
.dl{{display:flex;flex-wrap:wrap;gap:8px 16px;font-size:14px}}
</style>
<main class="wrap">
<header>
  <div class="eyebrow">Posting kit · {len(items)} posts · {ready} ready now</div>
  <h1>Everything to post, <em>in order.</em></h1>
  <p class="lead">One post per weekday from Thursday 8 October. Newest news first, evergreen tutorials later. Copy the caption, post the media natively, then add the first comment with the sources. LinkedIn gets the 4:5 video or PDF; Instagram Reels and YouTube Shorts get the 9:16 video; Instagram carousels get the slides ZIP. Videos marked "voice in progress" get the #25 voice and appear here as they finish.</p>
</header>
{"".join(cards)}
</main>
<script>
document.querySelectorAll("[data-copy]").forEach(b => b.addEventListener("click", () => {{
  const pre = document.getElementById(b.dataset.copy), t = pre.innerText;
  const sel = () => {{ const r = document.createRange(); r.selectNodeContents(pre); const s = getSelection(); s.removeAllRanges(); s.addRange(r); b.textContent = "Selected"; }};
  try {{ navigator.clipboard.writeText(t).then(() => {{ b.textContent = "Copied"; setTimeout(() => b.textContent = "Copy", 1600); }}, sel); }} catch (e) {{ sel(); }}
}}));
</script>
'''


if __name__ == "__main__":
    out = Path(sys.argv[1])
    items = collect(out)
    (out / "index.html").write_text(page(items))
    print(f"{len(items)} posts, {sum(i['ready'] for i in items)} ready -> {out / 'index.html'}")
