"""Slide templates. One locked visual system so every post is recognisably yours.

Style: light Claude-like UI, tinted cards (purple / teal / coral), #7F77DD accent,
hairline 0.5px borders, small badges, a pill counter and the handle top-left.
Canvas: 1080 x 1350 (4:5), the size LinkedIn shows best on mobile.
"""
from __future__ import annotations

from html import escape

W, H = 1080, 1350
TINTS = {"purple": "#F5F4FF", "teal": "#F0FBF6", "coral": "#FEF6F3"}
INKS = {"purple": "#534AB7", "teal": "#0F7A55", "coral": "#B4502A"}

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:%(W)dpx;height:%(H)dpx;background:#FBFAF8;font-family:Inter,system-ui,sans-serif;color:#1A1A1F;overflow:hidden}
.slide{position:absolute;inset:0;padding:84px 84px 96px;display:flex;flex-direction:column}
.top{display:flex;justify-content:space-between;align-items:center}
.mid{flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:40px}
.handle{display:flex;align-items:center;gap:14px;font-size:24px;font-weight:600}
.avatar{width:48px;height:48px;border-radius:50%%;background:#7F77DD;color:#fff;display:grid;place-items:center;font-size:20px;font-weight:700}
.handle small{display:block;font-size:19px;font-weight:400;color:#77778A}
.pill{font:500 20px 'JetBrains Mono',monospace;border:0.5px solid #D9D7E8;border-radius:999px;padding:10px 20px;color:#55556A;background:#fff}
.badge{align-self:flex-start;font:600 19px Inter;letter-spacing:.08em;text-transform:uppercase;color:#7F77DD;background:#EEEDFD;border:0.5px solid #D6D3F7;border-radius:8px;padding:9px 14px;margin-bottom:34px}
h1{font-size:104px;line-height:1.02;letter-spacing:-3px;font-weight:700}
h1 em{font-style:normal;color:#7F77DD}
h2{font-size:72px;line-height:1.06;letter-spacing:-2.5px;font-weight:700;margin-bottom:30px}
.sub{font-size:36px;line-height:1.45;color:#55556A;margin-top:36px;max-width:820px}
.card{border:0.5px solid #E2E0EE;border-radius:28px;padding:56px;margin-top:8px}
.card p{font-size:35px;line-height:1.5;color:#33333F}
p em,li em{font-style:normal;font-weight:600;color:#7F77DD}
.num{font:500 22px 'JetBrains Mono',monospace;margin-bottom:22px}
.emoji{font-size:56px;margin-bottom:20px}
.stat{font-size:200px;font-weight:700;letter-spacing:-8px;line-height:1;color:#7F77DD}
.list{list-style:none;display:flex;flex-direction:column;gap:22px;margin-top:12px}
.list li{font-size:33px;line-height:1.4;padding:26px 30px;border:0.5px solid #E2E0EE;border-radius:20px;background:#fff;display:flex;gap:18px}
.list li b{font:500 22px 'JetBrains Mono',monospace;color:#7F77DD;padding-top:6px}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:12px}
.cols .card{margin:0;padding:40px}
.cols h3{font-size:26px;letter-spacing:.06em;text-transform:uppercase;margin-bottom:20px}
.cols ul{list-style:none;display:flex;flex-direction:column;gap:22px;font-size:32px;line-height:1.4}
.foot{display:flex;justify-content:space-between;align-items:center;font-size:22px;color:#8A8A9C}
.swipe{font:500 22px 'JetBrains Mono',monospace;color:#7F77DD}
.cta h1{font-size:84px}
.save{display:inline-flex;margin-top:40px;font-size:30px;font-weight:600;background:#7F77DD;color:#fff;border-radius:16px;padding:22px 32px}
""" % {"W": W, "H": H}


def font_css() -> str:
    """Embed the bundled fonts so rendering is identical offline and in CI."""
    import base64
    from pathlib import Path

    d = Path(__file__).parent / "fonts"
    faces = [("Inter", w, f"inter-latin-{w}-normal.woff2") for w in (400, 500, 600, 700)]
    faces.append(("JetBrains Mono", 500, "jetbrains-mono-latin-500-normal.woff2"))
    out = []
    for fam, w, f in faces:
        b64 = base64.b64encode((d / f).read_bytes()).decode()
        out.append(f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
    return "".join(out)


_FONTS = None


def _e(s: str) -> str:
    """Escape, then allow *word* for the accent colour."""
    out = escape(s)
    parts = out.split("*")
    return "".join(f"<em>{p}</em>" if i % 2 else p for i, p in enumerate(parts))


def _chrome(author: dict, i: int, n: int, body: str, last: bool) -> str:
    initials = "".join(w[0] for w in author["name"].split()[:2]).upper()
    foot = "" if last else '<div class="foot"><span></span><span class="swipe">swipe →</span></div>'
    return f"""<div class="slide"><div class="top"><div class="handle"><div class="avatar">{initials}</div>
<div>{escape(author['name'])}<small>{escape(author['handle'])}</small></div></div>
<div class="pill">{i} / {n}</div></div><div class="mid">{body}</div>{foot}</div>"""


def render_slide(s: dict, i: int, n: int, author: dict) -> str:
    kind = s.get("type", "point")
    tint = s.get("tint", ["purple", "teal", "coral"][(i - 1) % 3])
    bg, ink = TINTS.get(tint, TINTS["purple"]), INKS.get(tint, INKS["purple"])
    badge = f'<div class="badge">{escape(s["badge"])}</div>' if s.get("badge") else ""
    if kind == "cover":
        body = f'{badge}<h1>{_e(s["title"])}</h1><p class="sub">{_e(s.get("subtitle", ""))}</p>'
    elif kind == "stat":
        body = (f'{badge}<div class="card" style="background:{bg}"><div class="stat" style="color:{ink}">{escape(s["value"])}</div>'
                f'<h2 style="margin-top:24px">{_e(s["title"])}</h2><p>{_e(s.get("body", ""))}</p></div>')
    elif kind == "list":
        items = "".join(f"<li><b>{k:02d}</b><span>{_e(t)}</span></li>" for k, t in enumerate(s["items"], 1))
        body = f'{badge}<h2>{_e(s["title"])}</h2><ul class="list">{items}</ul>'
    elif kind == "compare":
        col = lambda c, t: (f'<div class="card" style="background:{TINTS[t]}"><h3 style="color:{INKS[t]}">{escape(c["label"])}</h3>'
                            f'<ul>{"".join(f"<li>{_e(x)}</li>" for x in c["items"])}</ul></div>')
        body = f'{badge}<h2>{_e(s["title"])}</h2><div class="cols">{col(s["left"], "coral")}{col(s["right"], "teal")}</div>'
    elif kind == "cta":
        body = (f'<div class="cta">{badge}<h1>{_e(s["title"])}</h1><p class="sub">{_e(s.get("subtitle", ""))}</p>'
                f'<div class="save">{escape(s.get("button", "Save this for later"))}</div></div>')
    else:  # point
        emoji = f'<div class="emoji">{escape(s["emoji"])}</div>' if s.get("emoji") else ""
        body = (f'{badge}<div class="card" style="background:{bg}">{emoji}<div class="num" style="color:{ink}">{escape(s.get("label", ""))}</div>'
                f'<h2>{_e(s["title"])}</h2><p>{_e(s.get("body", ""))}</p></div>')
    global _FONTS
    if _FONTS is None:
        _FONTS = font_css()
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{_FONTS}{CSS}</style></head><body>{_chrome(author, i, n, body, kind == 'cta')}</body></html>"


def validate(deck: dict) -> list[str]:
    """Editorial rules from the style guide. Returns problems; empty means good to render."""
    errs = []
    slides = deck.get("slides", [])
    if not 5 <= len(slides) <= 12:
        errs.append(f"Use 5-12 slides (got {len(slides)})")
    if slides and slides[0].get("type") != "cover":
        errs.append("First slide must be a cover with the hook")
    if slides and slides[-1].get("type") != "cta":
        errs.append("Last slide must be a call to action")
    if slides and len(slides[0].get("title", "").split()) > 10:
        errs.append("Hook is longer than 10 words")
    emojis = sum(1 for s in slides if s.get("emoji"))
    if emojis > max(2, len(slides) // 3):
        errs.append("Too many emojis; use them sparingly as visual anchors")
    for k, s in enumerate(slides, 1):
        if len(s.get("body", "").split()) > 45:
            errs.append(f"Slide {k}: body over 45 words, split it")
        if s.get("type") == "list" and len(s.get("items", [])) > 5:
            errs.append(f"Slide {k}: more than 5 list items")
    return errs
