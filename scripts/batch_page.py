"""Build the batch page: every post ready to publish (video or slides, caption, article link, schedule).

    python scripts/batch_page.py out/batch-01    # -> out/_batch/index.html + media/
"""
from __future__ import annotations

import datetime as dt
import json
import shutil
import sys
from html import escape
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out" / "_batch"
SITE = "https://buildwithvish.netlify.app"


def jpg(src: Path, name: str, width: int = 720) -> str:
    im = Image.open(src).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    (OUT / "img").mkdir(parents=True, exist_ok=True)
    im.save(OUT / "img" / name, quality=84, optimize=True, progressive=True)
    return f"img/{name}"


def posts(batch: Path) -> list[Path]:
    ps = [p for p in batch.iterdir() if (p / "meta.json").exists()]
    ps += [ROOT / "out" / s for s in ("2026-10-06-chatgpt-image-ads", "2026-10-06-eu-ai-text-watermark", "2026-10-06-meta-creator-hub")]
    import re

    def newest(p: Path) -> str:  # most recent ISO or "5 Oct 2026" style date in sources.md ("" = evergreen)
        t = (p / "sources.md").read_text() if (p / "sources.md").exists() else ""
        iso = re.findall(r"20\d\d-\d\d-\d\d", t)
        mon = {m: i for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}
        iso += [f"{y}-{mon[m]:02d}-{int(d):02d}" for d, m, y in re.findall(r"\b(\d{1,2}) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* (20\d\d)", t)]
        return max(iso) if iso else ""
    # news first (freshest first, it goes stale), evergreen after (best score first)
    return sorted(ps, key=lambda p: (0, "~" + "".join(chr(255 - ord(c)) for c in newest(p))) if newest(p) else (1, -float(json.loads((p / "meta.json").read_text()).get("score") or 8.5)))


def schedule(ps: list[Path]) -> list[str]:
    # weekdays, 08:30 Berlin; videos and carousels alternate so the feed never repeats a format twice in a row
    order, d = list(ps), dt.date(2026, 10, 7)
    # keep the same topic family apart: the FDE carousel repeats the FDE video, so push it to the end
    order.sort(key=lambda p: 1 if json.loads((p / "meta.json").read_text()).get("site_slug") else 0)
    days = []
    for _ in order:
        while d.weekday() > 4:
            d += dt.timedelta(days=1)
        days.append(d.strftime("%a %d %b"))
        d += dt.timedelta(days=1)
    return list(zip(order, days))


def card(p: Path, day: str, n: int) -> str:
    meta = json.loads((p / "meta.json").read_text())
    slug, cap = meta["slug"], (p / "caption.md").read_text().strip()
    first = (p / "first-comment.md").read_text().strip() if (p / "first-comment.md").exists() else ""
    site_slug = meta.get("site_slug") or slug
    qa = (p / "qa-report.md").read_text().splitlines()[2] if (p / "qa-report.md").exists() else ""
    if (p / "video.mp4").exists():
        (OUT / "media").mkdir(parents=True, exist_ok=True)
        shutil.copy(p / "video.mp4", OUT / "media" / f"{slug}.mp4")
        frames = sorted((p / "frames").glob("b*.png"))
        poster = jpg(frames[0], f"{slug}-poster.jpg") if frames else ""
        media = f'<video controls playsinline preload="none" poster="{poster}" src="media/{slug}.mp4"></video>'
        kind = "Video"
    elif (p / "video.json").exists():
        media = '<div class="pending">Video rendering. It will appear here on the next update.</div>'
        kind = "Video"
    else:
        slides = sorted((p / "slides").glob("slide-*.png"))
        imgs = "".join(f'<img loading="lazy" src="{jpg(s, f"{slug}-{s.stem}.jpg", 540)}" alt="Slide {i}">' for i, s in enumerate(slides, 1))
        media = f'<div class="strip">{imgs}</div>'
        kind = "Carousel" if len(slides) > 1 else "Image"
    hook = escape(meta.get("hook", "")).replace("*", "")
    return f"""<article class="post" id="{slug}">
  <header><span class="n">{n:02d}</span><div><p class="meta">{escape(day)} · {kind} · {escape(meta.get('pillar') or '')}</p><h2>{hook}</h2></div></header>
  <div class="body"><div class="m">{media}</div>
  <div class="t"><h3>Caption <button class="copy" type="button" data-copy="c-{slug}">Copy</button></h3><pre id="c-{slug}">{escape(cap)}</pre>
  {f'<h3>First comment</h3><pre class="small">{escape(first)}</pre>' if first else ''}
  <p class="links"><a href="{SITE}/#read-{site_slug}" target="_blank" rel="noopener">Article on Build with Vish</a> · <span class="qa">{escape(qa.replace('*', ''))}</span></p></div></div>
</article>"""


def build(batch: Path) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    plan = schedule(posts(batch))
    cards = "".join(card(p, day, i) for i, (p, day) in enumerate(plan, 1))
    nv = sum(1 for p, _ in plan if (p / "video.json").exists())
    html = f"""<title>Content Batch 01</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@500&family=Newsreader:ital,wght@0,500;1,500&display=swap">
<style>
:root{{--bg:#F4F0E8;--paper:#FFFDFA;--ink:#1F1C24;--muted:#6B6572;--line:#E4DDD2;--accent:#4A44C4;--tint:#EEEAFB}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#0E0C14;--paper:#17151E;--ink:#F2F0F6;--muted:#A8A3B3;--line:#2A2733;--accent:#B3A9FF;--tint:#1C1A2B;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#0E0C14;--paper:#17151E;--ink:#F2F0F6;--muted:#A8A3B3;--line:#2A2733;--accent:#B3A9FF;--tint:#1C1A2B;color-scheme:dark}}
body{{background:var(--bg);color:var(--ink);font:16px/1.55 Geist,system-ui,sans-serif;margin:0;padding:32px 16px 80px}}
.wrap{{max-width:1180px;margin:0 auto;display:flex;flex-direction:column;gap:28px}}
h1{{font:500 clamp(2.1rem,5vw,3.4rem)/1.04 Newsreader,Georgia,serif;letter-spacing:-.02em;margin:0}} h1 em{{color:var(--accent)}}
.lead{{color:var(--muted);max-width:68ch;margin:10px 0 0}}
.box{{background:var(--tint);border:1px solid var(--line);border-radius:18px;padding:18px 20px}} .box ul{{margin:6px 0 0;padding-left:20px}}
.post{{background:var(--paper);border:1px solid var(--line);border-radius:22px;padding:clamp(16px,3vw,28px);min-width:0}}
.post header{{display:flex;gap:14px;align-items:flex-start;margin-bottom:14px}}
.n{{flex:none;font:500 .9rem 'Geist Mono',monospace;background:var(--ink);color:var(--paper);border-radius:10px;padding:6px 9px}}
.meta{{margin:0;color:var(--muted);font:500 .8rem 'Geist Mono',monospace}}
h2{{font:500 1.6rem/1.15 Newsreader,Georgia,serif;margin:4px 0 0}}
h3{{font:600 .72rem 'Geist Mono',monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0 0 8px;display:flex;gap:10px;align-items:center}}
.body{{display:grid;grid-template-columns:minmax(0,360px) minmax(0,1fr);gap:24px}}
@media (max-width:760px){{.body{{grid-template-columns:1fr}}}}
video{{width:100%;border-radius:14px;background:#0E0C14;display:block}}
.strip{{display:flex;gap:10px;overflow-x:auto;scroll-snap-type:x mandatory}} .strip img{{width:min(300px,78vw);flex:none;border-radius:10px;scroll-snap-align:start}}
.pending{{border:1px dashed var(--line);border-radius:14px;padding:40px 16px;text-align:center;color:var(--muted)}}
pre{{white-space:pre-wrap;font:14.5px/1.55 Geist,sans-serif;background:var(--bg);border:1px solid var(--line);border-radius:12px;padding:14px;margin:0 0 14px;max-height:340px;overflow:auto}}
pre.small{{font-size:13px;max-height:140px}}
.links{{margin:0;font-size:.9rem}} a{{color:var(--accent)}} .qa{{color:var(--muted);font:500 .78rem 'Geist Mono',monospace}}
.copy{{font:600 .7rem 'Geist Mono',monospace;border:1px solid var(--line);background:var(--paper);color:var(--ink);border-radius:999px;padding:4px 10px;cursor:pointer}}
</style>
<div class="wrap">
<header><p class="meta">Build with Vish · content batch 01 · made 6 Oct 2026</p>
<h1>20 posts, <em>ready to go</em>.</h1>
<p class="lead">{nv} videos and {len(plan) - nv} carousels or images, in posting order. Each one has a caption to copy, a first comment with sources, and its full article live on Build with Vish. Voice: one natural designed voice. Your avatar reacts in context.</p></header>
<div class="box"><b>How to post</b><ul>
<li>One post per weekday, around 08:30 Berlin time. Videos and carousels alternate.</li>
<li>Upload the video or PDF natively to LinkedIn (no link in the post body). Paste the caption, then add the first comment right after posting.</li>
<li>Reply to every comment in the first hour. It's the strongest reach signal you control.</li>
<li>Downloads: the MP4s are in the GitHub repo under <code>out/batch-01/&lt;slug&gt;/video.mp4</code>, carousels as <code>carousel.pdf</code>.</li>
</ul></div>
{cards}
</div>
<script>
document.querySelectorAll(".copy").forEach(b => b.addEventListener("click", () => {{
  const el = document.getElementById(b.dataset.copy);
  navigator.clipboard.writeText(el.textContent).then(() => {{ b.textContent = "Copied"; setTimeout(() => b.textContent = "Copy", 1500); }}).catch(() => {{}});
}}));
</script>
"""
    (OUT / "index.html").write_text(html)
    return OUT / "index.html"


if __name__ == "__main__":
    print(build(Path(sys.argv[1])))
