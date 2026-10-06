"""Build the review page Vish approves from: out/_review/index.html + compressed images.

    python scripts/review_page.py out/2026-10-06-eu-ai-text-watermark out/2026-10-06-chatgpt-image-ads out/2026-10-06-meta-creator-hub
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from html import escape
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
REVIEW = ROOT / "out" / "_review"

WHY = {
    "studio": "Instantly reads as your existing carousels, now with depth. The safest bet for saves.",
    "night": "Dark covers stand out on LinkedIn's light feed, and video is where dwell time grows fastest.",
    "field": "Looks like nobody else in AI x marketing. Operator voice, good for opinion and creator posts.",
}


def jpg(src: Path, name: str, width: int = 1080) -> str:
    im = Image.open(src).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    out = REVIEW / "img" / name
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, quality=86, optimize=True, progressive=True)
    return f"img/{name}"


def md_inline(s: str) -> str:
    s = escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return re.sub(r"(https?://[^\s|<)]+)", r'<a href="\1" target="_blank" rel="noopener">\1</a>', s)


def sources_rows(p: Path) -> list[list[str]]:
    rows = []
    for line in p.read_text().splitlines():
        if line.startswith("|") and not line.startswith("|---") and "Claim" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            rows.append(cells)
    return rows


def qa_summary(p: Path) -> tuple[str, list[str]]:
    if not p.exists():
        return "not run", []
    t = p.read_text()
    head = re.search(r"\*\*(PASS|FAIL)\*\* · ([^\n]+)", t)
    warns = [re.sub(r"^\| WARN \| (\w+) \| ", r"\1: ", l).rstrip(" |") for l in t.splitlines() if l.startswith("| WARN")]
    return (f"{head.group(1)} · {head.group(2)}" if head else "?"), warns


def post_section(post: Path, idx: int) -> str:
    spec_f = post / "deck.json" if (post / "deck.json").exists() else post / "video.json"
    spec = json.loads(spec_f.read_text())
    theme = spec.get("theme", "night")
    caption = (post / "caption.md").read_text().strip()
    hook = caption.splitlines()[0]
    first = (post / "first-comment.md").read_text().strip() if (post / "first-comment.md").exists() else ""
    qa, warns = qa_summary(post / "qa-report.md")
    slug = post.name
    if (post / "video.mp4").exists():
        vid = REVIEW / "media" / f"{slug}.mp4"
        vid.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(post / "video.mp4", vid)
        poster = jpg(post / "frames" / "cover.png", f"{slug}-poster.jpg")
        stills = "".join(f'<img loading="lazy" src="{jpg(f, f"{slug}-{f.stem}.jpg", 540)}" alt="Video frame {f.stem}">' for f in sorted((post / "frames").glob("*.png")))
        visual = (f'<div class="media"><video controls playsinline muted loop preload="metadata" poster="{poster}" src="media/{slug}.mp4"></video></div>'
                  f'<p class="cap">30 s · 1080 x 1350 · H.264. Frames:</p><div class="strip">{stills}</div>')
        fmt = "Video"
    else:
        slides = sorted((post / "slides").glob("slide-*.png"))
        imgs = "".join(f'<img loading="lazy" src="{jpg(f, f"{slug}-{f.stem}.jpg")}" alt="Slide {i}">' for i, f in enumerate(slides, 1))
        visual = f'<div class="strip {"single" if len(slides) == 1 else ""}">{imgs}</div>'
        fmt = "Carousel PDF" if len(slides) > 1 else "Single image + text post"
    rows = "".join("<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in r[:3]) + "</tr>" for r in sources_rows(post / "sources.md"))
    warn_html = "".join(f"<li>{md_inline(w)}</li>" for w in warns)
    return f"""
<section class="dir" id="{'abc'[idx]}">
  <header class="dh"><span class="letter">{'ABC'[idx]}</span><div><h2>{escape(spec.get('direction', ''))}</h2>
  <p class="meta">{fmt} · {escape(spec.get('pillar', 'AI tools that change marketing work'))} · QA {escape(qa)}</p></div></header>
  <p class="why"><b>Why it could work:</b> {escape(WHY.get(theme, ''))}</p>
  {visual}
  <div class="cols">
    <div class="col"><h3>Hook</h3><p class="hook">{escape(hook)}</p>
      <h3>Caption <button class="copy" type="button" data-copy="cap-{idx}">Copy</button></h3><pre id="cap-{idx}" class="caption">{escape(caption)}</pre>
      <h3>First comment</h3><pre class="caption small">{md_inline(first)}</pre></div>
    <div class="col"><h3>Sources</h3><div class="tw"><table><tr><th>Claim</th><th>Source</th><th>Date</th></tr>{rows}</table></div>
      <h3>QA warnings to look at</h3><ul class="warn">{warn_html or '<li>None</li>'}</ul></div>
  </div>
</section>"""


def build(posts: list[Path]) -> Path:
    REVIEW.mkdir(parents=True, exist_ok=True)
    mascot = jpg(ROOT / "brand" / "mascot" / "sheet.png", "mascot-sheet.jpg", 1200)
    backlog = json.loads((ROOT / "topics" / "backlog.json").read_text())["topics"]
    blrows = "".join(f'<tr class="{"ship" if t["ships"] else ""}"><td class="num">{t["score"]}</td><td>{escape(t["title"])}</td><td>{escape(t["pillar"])}</td><td>{escape(t["status"])}</td></tr>' for t in backlog)
    reviewer = ROOT / "out" / "_review" / "reviewer-report.md"
    rev_html = ""
    if reviewer.exists():
        rev_html = f'<section class="plain"><h2>Independent reviewer</h2><p class="meta">A separate agent that didn\'t make the samples checked facts against the saved sources and looked at every image. Its report, unedited:</p><pre class="caption">{escape(reviewer.read_text())}</pre><h3>What I changed after the review</h3><pre class="caption">{escape((ROOT / "out" / "_review" / "fixes-applied.md").read_text())}</pre></section>'
    html = f"""<title>Test Gate Review</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@500;600&display=swap">
<style>
/* Layout: one long review sheet; each direction is a band with the work first, then copy and sources side by side. */
:root{{--bg:#F4F2F6;--paper:#FFFFFF;--ink:#17141C;--muted:#5F5967;--line:#DDD8E3;--accent:#4A44C4;--brand:#7F77DD;--good:#0E7A6E;--warn:#9A5B0C;--tint:#EEEDFD;
--f-d:"Geist","SF Pro Display","Helvetica Neue",Arial,sans-serif;--f-b:"Geist","Segoe UI",system-ui,sans-serif;--f-m:"Geist Mono",ui-monospace,Menlo,monospace}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#0B0A10;--paper:#15141B;--ink:#F2F1F5;--muted:#A6A2AE;--line:#2B2934;--accent:#A99CFF;--brand:#A99CFF;--good:#6FE0D2;--warn:#F3C584;--tint:#1B1A2E;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#0B0A10;--paper:#15141B;--ink:#F2F1F5;--muted:#A6A2AE;--line:#2B2934;--accent:#A99CFF;--brand:#A99CFF;--good:#6FE0D2;--warn:#F3C584;--tint:#1B1A2E;color-scheme:dark}}
body{{background:var(--bg);color:var(--ink);font:16px/1.55 var(--f-b);padding-inline:clamp(16px,4vw,48px);padding-block:32px 80px;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1180px;margin:0 auto;display:flex;flex-direction:column;gap:40px}}
h1{{font:700 clamp(2rem,5vw,3.2rem)/1.02 var(--f-d);letter-spacing:-.035em;text-wrap:balance;margin:0}}
h2{{font:700 1.6rem/1.1 var(--f-d);letter-spacing:-.02em;margin:0}}
h3{{font:600 .78rem/1 var(--f-m);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:22px 0 10px;display:flex;align-items:center;gap:10px}}
.lead{{font-size:1.12rem;color:var(--muted);max-width:62ch;margin:12px 0 0}}
.ask{{background:var(--tint);border:1px solid var(--line);border-radius:18px;padding:20px 22px}}
.ask ol{{margin:8px 0 0;padding-left:20px;display:flex;flex-direction:column;gap:6px}}
.dir,.plain{{background:var(--paper);border:1px solid var(--line);border-radius:22px;padding:clamp(18px,3vw,32px);display:flex;flex-direction:column;gap:14px;min-width:0}}
.dh{{display:flex;gap:16px;align-items:center}}
.letter{{flex:none;width:52px;height:52px;border-radius:14px;background:var(--brand);color:#fff;display:grid;place-items:center;font:700 1.5rem var(--f-d)}}
.meta{{color:var(--muted);font:500 .86rem/1.4 var(--f-m);margin:4px 0 0}}
.why{{margin:0;max-width:75ch}}
.strip{{display:flex;gap:12px;overflow-x:auto;padding-bottom:8px;scroll-snap-type:x mandatory}}
.strip img{{width:min(300px,70vw);flex:none;border-radius:10px;border:1px solid var(--line);scroll-snap-align:start;max-width:100%}}
.strip.single img{{width:min(460px,100%)}}
.media video{{width:min(460px,100%);border-radius:12px;border:1px solid var(--line);display:block;background:#08070D}}
.cap{{margin:0;color:var(--muted);font:500 .8rem var(--f-m)}}
.cols{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:28px}}
.col{{min-width:0}}
.hook{{font:700 1.3rem/1.2 var(--f-d);letter-spacing:-.02em;margin:0}}
pre.caption{{white-space:pre-wrap;font:15px/1.55 var(--f-b);background:var(--bg);border:1px solid var(--line);border-radius:14px;padding:16px;margin:0;max-height:420px;overflow:auto}}
pre.small{{font-size:14px}}
.tw{{overflow-x:auto}}
table{{border-collapse:collapse;width:100%;font-size:.86rem}}
th,td{{text-align:left;vertical-align:top;padding:8px 10px;border-bottom:1px solid var(--line)}}
th{{font:600 .72rem var(--f-m);letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}}
td a{{color:var(--accent);word-break:break-all}}
td.num{{font:600 1rem var(--f-m);font-variant-numeric:tabular-nums}}
tr.ship td.num{{color:var(--good)}}
.warn{{margin:0;padding-left:18px;color:var(--warn);font-size:.9rem;display:flex;flex-direction:column;gap:4px}}
.copy{{font:600 .72rem var(--f-m);letter-spacing:.04em;border:1px solid var(--line);background:var(--paper);color:var(--ink);border-radius:999px;padding:5px 10px;cursor:pointer}}
.copy:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
.mascot img{{border-radius:14px;max-width:100%;border:1px solid var(--line)}}
a{{color:var(--accent)}}
</style>
<div class="wrap">
<header><p class="meta">Build with Vish content engine · test-first gate · 6 Oct 2026</p>
<h1>Three directions. Pick one, mix, or send it back.</h1>
<p class="lead">Each sample is a real post on a topic from this week, researched, written, designed in 3D, rendered and run through the QA gate. Nothing has been posted, emailed or deployed.</p></header>
<div class="ask"><b>What I need from you</b><ol>
<li>Which direction (A, B, C, or a mix like "A for carousels, B for video")?</li>
<li>What to change and what to drop: type, colour, 3D objects, the mascot "Dot", copy tone.</li>
<li>Confirm the flagged line in C ("the hard part was the brief and the rights") is true for you.</li>
<li>Screenshots of the 7 Instagram posts you liked (Instagram blocked images here).</li>
</ol></div>
{''.join(post_section(p, i) for i, p in enumerate(posts))}
<section class="plain mascot"><h2>Dot, the sidekick</h2><p class="meta">Original character in your violet. Antenna carries the Build with Vish logo mark. Six expressions, five poses, rendered from code so it never drifts.</p><img src="{mascot}" alt="Mascot sheet with six expressions"></section>
<section class="plain"><h2>Topic backlog</h2><p class="meta">Scored 1 to 10 on freshness, usefulness, shareability, comment potential, brand fit. Only 8+ ships.</p>
<div class="tw"><table><tr><th>Score</th><th>Topic</th><th>Pillar</th><th>Status</th></tr>{blrows}</table></div></section>
{rev_html}
</div>
<script>
document.querySelectorAll(".copy").forEach(b => b.addEventListener("click", () => {{
  const el = document.getElementById(b.dataset.copy);
  navigator.clipboard.writeText(el.textContent).then(() => {{ b.textContent = "Copied"; setTimeout(() => b.textContent = "Copy", 1500); }})
    .catch(() => {{ const r = document.createRange(); r.selectNodeContents(el); const s = getSelection(); s.removeAllRanges(); s.addRange(r); }});
}}));
</script>
"""
    out = REVIEW / "index.html"
    out.write_text(html)
    return out


if __name__ == "__main__":
    print(build([Path(a) for a in sys.argv[1:]]))
