"""Build the posting-kit page (one card per post, copy buttons) from content/posting-kit/<file>.md and the post kits.

    python scripts/posting_kit_page.py content/posting-kit/2026-10-27-to-11-09.md <out.html>
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MONTHS = {"Oct": 10, "Nov": 11, "Dec": 12}


def code_after(s, anchor):
    i = s.index(anchor)
    return re.search(r"```\n(.*?)```", s[i:], re.S).group(1).strip()


def posts(kit_path: Path) -> list:
    kit = kit_path.read_text()
    w2 = (ROOT / "content/instagram/week-02-post-kit.md").read_text()
    w3 = (ROOT / "content/instagram/week-03-post-kit.md").read_text()
    other = {"CHECK": code_after(w2, "## Sat 1 Nov · Carousel B (CHECK)"), "EDIT": code_after(w2, "## Mon 27 Oct · Carousel A (EDIT)"),
             "FRICTION": code_after(w3, "## Tue 4 Nov · Carousel: reduce friction (FRICTION)")}
    out, plat = [], None
    for sec in re.split(r"\n(?=## |### )", kit):
        if sec.startswith("## Instagram"):
            plat = "Instagram"
            continue
        if sec.startswith("## LinkedIn"):
            plat = "LinkedIn"
            continue
        if sec.startswith("## YouTube"):
            for name, title, desc in re.findall(r"^\| (?!Short|---)(.+?) \| (.+?) \| (.+?) \|$", sec, re.M):
                out.append({"plat": "YouTube", "day": "", "sort": 99, "title": f"Short: {name}", "meta": ["Same day as the Instagram reel, the -9x16.mp4 file (with music)"],
                            "caption": f"{title}\n\n{desc}"})
            continue
        if not sec.startswith("### ") or not plat:
            continue
        head = sec.split("\n")[0][4:]
        day, _, title = head.partition(" · ")
        meta = [re.sub(r"\*\*|`", "", b.strip()[2:]) for b in sec.split("\n")[1:] if b.strip().startswith("- ")]
        m = re.search(r"```\n(.*?)```", sec, re.S)
        cap = m.group(1).strip() if m else ""
        if not cap:
            key = next(k for k in other if f"({k})" in title)
            cap = other[key]
            meta = [x for x in meta if not x.startswith("Caption:")]
        d = day.split()
        out.append({"plat": plat, "day": day, "sort": MONTHS[d[2]] * 100 + int(d[1]) + (0.5 if plat == "LinkedIn" else 0), "title": title,
                    "meta": meta, "caption": cap})
    return sorted(out, key=lambda p: p["sort"])


def page(items: list) -> str:
    cards = []
    for i, p in enumerate(items):
        meta = "".join(f"<li>{html.escape(m)}</li>" for m in p["meta"])
        cards.append(f'''<article class="post" data-plat="{p["plat"]}" id="p{i}">
  <header><span class="day">{html.escape(p["day"] or "Shorts")}</span><span class="chip {p["plat"].lower()}">{p["plat"]}</span>
  <label class="done"><input type="checkbox" id="done-{i}" data-i="{i}"> Posted</label></header>
  <h2>{html.escape(p["title"])}</h2>
  {f'<ul class="meta">{meta}</ul>' if meta else ''}
  <div class="cap"><pre id="cap-{i}">{html.escape(p["caption"])}</pre><button type="button" class="copy" data-for="cap-{i}">Copy</button></div>
</article>''')
    return f'''<title>Build with Vish Posting Kit</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter+Tight:wght@400;500;600;700&family=Geist+Mono:wght@500&display=swap">
<style>
/* One column of post cards in posting order; a sticky filter bar; captions in copyable blocks. */
:root {{
  --bg: #F3EEE5; --surface: #FFFDF8; --fg: #1A1712; --muted: #6E665A; --line: #DED5C4; --accent: #A85A12;
  --ig: #A3367A; --li: #1E5BA8; --yt: #B3261E; --code: #F7F2E8;
  --display: "Instrument Serif", Georgia, serif; --body: "Inter Tight", system-ui, sans-serif; --mono: "Geist Mono", ui-monospace, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #14161B; --surface: #1C1F26; --fg: #F2EEE6; --muted: #A39C90; --line: #2E323B; --accent: #E7A15A;
  --ig: #E07AB8; --li: #7FB0EE; --yt: #F08A80; --code: #171A20; color-scheme: dark }} }}
:root[data-theme="dark"] {{ --bg: #14161B; --surface: #1C1F26; --fg: #F2EEE6; --muted: #A39C90; --line: #2E323B; --accent: #E7A15A;
  --ig: #E07AB8; --li: #7FB0EE; --yt: #F08A80; --code: #171A20; color-scheme: dark }}
body {{ background: var(--bg); color: var(--fg); font: 16px/1.5 var(--body); }}
body::before {{ content: ""; position: fixed; inset: 0 0 auto; height: env(safe-area-inset-top, 0px); z-index: 10; background: var(--bg); }}
.wrap {{ max-width: 720px; margin: 0 auto; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 28px 64px; }}
h1 {{ font: 400 clamp(40px, 8vw, 58px)/1 var(--display); margin: 0; text-wrap: balance; }}
h1 em {{ color: var(--accent); }}
.lede {{ color: var(--muted); max-width: 60ch; margin: 12px 0 0; }}
.rules {{ display: grid; gap: 6px; margin: 18px 0 0; padding: 14px 16px; border: 1px solid var(--line); border-radius: 14px; background: var(--surface); font-size: 14px; }}
.rules b {{ font-weight: 600; }}
.bar {{ position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5; background: var(--bg); display: flex; flex-wrap: wrap; gap: 8px; padding-block: 14px; margin-top: 18px; border-bottom: 1px solid var(--line); }}
.bar button {{ font: 600 14px var(--body); border: 1px solid var(--line); background: var(--surface); color: var(--fg); border-radius: 999px; padding: 7px 14px; cursor: pointer; }}
.bar button[aria-pressed="true"] {{ background: var(--fg); color: var(--bg); border-color: var(--fg); }}
.bar .count {{ margin-left: auto; align-self: center; font: 500 12px var(--mono); color: var(--muted); letter-spacing: .06em; }}
.list {{ display: grid; gap: 14px; margin-top: 18px; }}
.post {{ background: var(--surface); border: 1px solid var(--line); border-radius: 18px; padding: 16px 16px 14px; display: grid; gap: 10px; min-width: 0; }}
.post.is-done {{ opacity: .55; }}
.post header {{ display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }}
.day {{ font: 500 13px var(--mono); letter-spacing: .08em; text-transform: uppercase; color: var(--accent); }}
.chip {{ font: 600 12px var(--body); border-radius: 999px; padding: 2px 10px; border: 1px solid currentColor; }}
.chip.instagram {{ color: var(--ig); }} .chip.linkedin {{ color: var(--li); }} .chip.youtube {{ color: var(--yt); }}
.done {{ margin-left: auto; font-size: 14px; color: var(--muted); display: flex; gap: 6px; align-items: center; cursor: pointer; }}
.post h2 {{ font: 400 26px/1.15 var(--display); margin: 0; text-wrap: balance; }}
.meta {{ margin: 0; padding-left: 18px; color: var(--muted); font-size: 14px; display: grid; gap: 4px; overflow-wrap: anywhere; }}
.cap {{ position: relative; min-width: 0; }}
.cap pre {{ margin: 0; white-space: pre-wrap; overflow-wrap: anywhere; font: 15px/1.5 var(--body); background: var(--code); border: 1px solid var(--line); border-radius: 12px; padding: 14px 14px 46px; }}
.copy {{ position: absolute; right: 10px; bottom: 10px; font: 600 14px var(--body); background: var(--fg); color: var(--bg); border: 0; border-radius: 10px; padding: 8px 16px; cursor: pointer; }}
.copy:focus-visible, .bar button:focus-visible, .done input:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
@media (prefers-reduced-motion: no-preference) {{ .post {{ transition: opacity .2s; }} }}
</style>
<main class="wrap">
  <h1>Posting kit, <em>27 Oct to 9 Nov</em></h1>
  <p class="lede">Every post in order. Tap Copy, paste into the app, tick Posted. Instagram at 18:30, LinkedIn at 08:30 (Berlin).</p>
  <div class="rules">
    <div><b>Instagram files</b> end in -instagram-9x16.mp4 and have no music: add the song named on the card in the app (Original audio 100, Music 15).</div>
    <div><b>LinkedIn and YouTube files</b> end in -9x16.mp4 and already have music.</div>
    <div><b>AI info label</b> on for every reel with a clone line. The caption already says which lines.</div>
    <div><b>Keywords</b> (EDIT, FRICTION) send the guide only after "merge". On LinkedIn, send the link yourself.</div>
  </div>
  <nav class="bar" aria-label="Filter posts">
    <button type="button" data-f="all" aria-pressed="true">All</button><button type="button" data-f="Instagram" aria-pressed="false">Instagram</button>
    <button type="button" data-f="LinkedIn" aria-pressed="false">LinkedIn</button><button type="button" data-f="YouTube" aria-pressed="false">YouTube</button>
    <span class="count" id="count"></span>
  </nav>
  <section class="list">
{chr(10).join(cards)}
  </section>
</main>
<script>
const KEY = "vish-kit-done";
let done = {{}};
try {{ done = JSON.parse(localStorage.getItem(KEY) || "{{}}"); }} catch (e) {{ done = {{}}; }}
const posts = [...document.querySelectorAll(".post")];
function paint() {{
  posts.forEach((p, i) => {{ const on = !!done[i]; p.classList.toggle("is-done", on); p.querySelector("input").checked = on; }});
  const vis = posts.filter(p => !p.hidden);
  document.getElementById("count").textContent = vis.filter(p => !p.classList.contains("is-done")).length + " to post";
}}
document.querySelectorAll(".done input").forEach(cb => cb.addEventListener("change", () => {{
  done[cb.dataset.i] = cb.checked; try {{ localStorage.setItem(KEY, JSON.stringify(done)); }} catch (e) {{}} paint(); }}));
document.querySelectorAll(".bar button").forEach(b => b.addEventListener("click", () => {{
  document.querySelectorAll(".bar button").forEach(x => x.setAttribute("aria-pressed", String(x === b)));
  posts.forEach(p => {{ p.hidden = b.dataset.f !== "all" && p.dataset.plat !== b.dataset.f; }}); paint(); }}));
document.querySelectorAll(".copy").forEach(b => b.addEventListener("click", () => {{
  const pre = document.getElementById(b.dataset.for), txt = pre.textContent;
  const ok = () => {{ b.textContent = "Copied"; setTimeout(() => b.textContent = "Copy", 1600); }};
  const sel = () => {{ const r = document.createRange(); r.selectNodeContents(pre); const s = getSelection(); s.removeAllRanges(); s.addRange(r); b.textContent = "Selected"; setTimeout(() => b.textContent = "Copy", 1600); }};
  if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).then(ok, sel); else sel();
}}));
paint();
</script>
'''


if __name__ == "__main__":
    Path(sys.argv[2]).write_text(page(posts(Path(sys.argv[1]))))
    print(sys.argv[2])
