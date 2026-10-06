"""Studio templates: the locked carousel system plus 3D hero art, the mascot and themes.

Themes
- studio: light paper, tinted cards, violet accent (Direction A, the evolution of the locked style)
- night:  near-black, iris violet, aurora teal (Direction B, Build with Vish cinematic)
- field:  bone paper, deep teal, Syne display (Direction C, the portfolio voice)

The 1.x `templates.py` stays untouched so existing decks keep rendering exactly as before.
"""
from __future__ import annotations

import base64
import mimetypes
from functools import lru_cache
from html import escape
from pathlib import Path

W, H = 1080, 1350
ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "templates" / "node_modules" / "@fontsource"

THEMES = {
    "studio": {
        "bg": "#FBFAF8", "wash": "rgba(127,119,221,.11)", "ink": "#17141C", "muted": "#5F5967", "body": "#3A3542",
        "line": "#E2E0EE", "accent": "#7F77DD", "accent_ink": "#4A44C4", "on_accent": "#FFFFFF",
        "tints": {"purple": "#F5F4FF", "teal": "#F0FBF6", "coral": "#FEF6F3"},
        "inks": {"purple": "#534AB7", "teal": "#0F7A55", "coral": "#B4502A"},
        "badge_bg": "#EEEDFD", "badge_line": "#D6D3F7", "pill_bg": "#FFFFFF",
        "display": "Geist", "text": "Geist", "mono": "Geist Mono", "grain": .055, "shadow": "rgba(74,68,196,.16)",
    },
    "night": {
        "bg": "#08070D", "wash": "rgba(169,156,255,.16)", "ink": "#F5F5F7", "muted": "#A1A1A6", "body": "#CFCDD6",
        "line": "#2A2A2E", "accent": "#A99CFF", "accent_ink": "#A99CFF", "on_accent": "#0A0A14",
        "tints": {"purple": "#15142B", "teal": "#0E2322", "coral": "#261816"},
        "inks": {"purple": "#C9C1FF", "teal": "#86E6D8", "coral": "#F5B49C"},
        "badge_bg": "#1B1A33", "badge_line": "#2E2C55", "pill_bg": "#121214",
        "display": "Geist", "text": "Geist", "mono": "Geist Mono", "grain": .07, "shadow": "rgba(0,0,0,.5)",
    },
    "field": {
        "bg": "#ECE7DC", "wash": "rgba(14,75,72,.08)", "ink": "#142220", "muted": "#56645F", "body": "#2C3A37",
        "line": "#CFC8B8", "accent": "#7F77DD", "accent_ink": "#4A44C4", "on_accent": "#FFFFFF",
        "tints": {"purple": "#F5F4FF", "teal": "#E3EEEA", "coral": "#F6E9E2"},
        "inks": {"purple": "#534AB7", "teal": "#0E4B48", "coral": "#8A3A1A"},
        "badge_bg": "#0E4B48", "badge_line": "#0E4B48", "pill_bg": "#F5F2EA",
        "display": "Syne", "text": "Public Sans", "mono": "Geist Mono", "grain": .06, "shadow": "rgba(20,34,32,.16)",
    },
}

_FACES = [
    ("Geist", "geist-sans", (400, 500, 600, 700, 800)),
    ("Geist Mono", "geist-mono", (400, 500)),
    ("Syne", "syne", (600, 700, 800)),
    ("Public Sans", "public-sans", (400, 500, 600)),
    ("Newsreader", "newsreader", (400, 500, 600)),
]


@lru_cache(maxsize=1)
def font_css() -> str:
    out = []
    for fam, pkg, weights in _FACES:
        for w in weights:
            for style in ("normal", "italic"):
                f = FONTS / pkg / "files" / f"{pkg}-latin-{w}-{style}.woff2"
                if f.exists():
                    b64 = base64.b64encode(f.read_bytes()).decode()
                    out.append(f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:{style};font-display:block;src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
    return "".join(out)


@lru_cache(maxsize=64)
def data_uri(path: str) -> str:
    p = Path(path)
    mime = mimetypes.guess_type(p.name)[0] or "image/png"
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


GRAIN = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'>"
         "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/>"
         "<feColorMatrix values='0 0 0 0 .5 0 0 0 0 .5 0 0 0 0 .5 0 0 0 1 0'/></filter>"
         "<rect width='100%25' height='100%25' filter='url(%23n)'/></svg>")


def css(t: dict) -> str:
    return f"""
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:{W}px;height:{H}px;background:{t['bg']};font-family:'{t['text']}',system-ui,sans-serif;color:{t['ink']};overflow:hidden;-webkit-font-smoothing:antialiased;text-rendering:geometricPrecision}}
.bgwash{{position:absolute;inset:0;background:radial-gradient(70% 50% at 88% 12%,{t['wash']},transparent 70%),radial-gradient(60% 40% at 0% 100%,{t['wash']},transparent 70%)}}
.grain{{position:absolute;inset:0;background-image:url("{GRAIN}");opacity:{t['grain']};mix-blend-mode:{'overlay' if t is THEMES['night'] else 'multiply'};pointer-events:none;z-index:9}}
.slide{{position:absolute;inset:0;padding:84px 84px 96px;display:flex;flex-direction:column;z-index:2}}
.top{{display:flex;justify-content:space-between;align-items:center;position:relative;z-index:5}}
.handle{{display:flex;align-items:center;gap:16px;font-size:24px;font-weight:600;letter-spacing:-.01em}}
.avatar{{width:54px;height:54px;border-radius:50%;background:#7F77DD;color:#fff;display:grid;place-items:center;font-size:24px;font-weight:700;letter-spacing:-.01em}}
.handle small{{display:block;font-size:19px;font-weight:400;color:{t['muted']};letter-spacing:0;margin-top:2px}}
.pill{{font:500 20px '{t['mono']}',monospace;border:.5px solid {t['line']};border-radius:999px;padding:10px 20px;color:{t['muted']};background:{t['pill_bg']}}}
.mid{{flex:1;display:flex;flex-direction:column;justify-content:center;position:relative;z-index:3}}
.badge{{align-self:flex-start;font:600 19px '{t['text']}';letter-spacing:.08em;text-transform:uppercase;color:{t['accent_ink'] if t is not THEMES['field'] else '#F5F2EA'};background:{t['badge_bg']};border:.5px solid {t['badge_line']};border-radius:8px;padding:9px 14px;margin-bottom:34px}}
h1{{font-family:'{t['display']}';font-size:98px;line-height:1.0;letter-spacing:-.042em;font-weight:{800 if t['display']=='Syne' else 700};text-wrap:balance}}
h1 em,h2 em{{font-style:normal;color:{t['accent']}}}
h2{{font-family:'{t['display']}';font-size:62px;line-height:1.05;letter-spacing:-.034em;font-weight:{700};margin-bottom:26px;text-wrap:balance}}
.sub{{font-size:34px;line-height:1.42;color:{t['muted']};margin-top:34px;max-width:780px;text-wrap:pretty}}
.card{{border:.5px solid {t['line']};border-radius:30px;padding:54px 56px;box-shadow:0 40px 80px -48px {t['shadow']};position:relative}}
.card p,.bodytext{{font-size:33px;line-height:1.46;color:{t['body']};text-wrap:pretty}}
p em,li em{{font-style:normal;font-weight:600;color:{t['accent_ink']}}}
.label{{font:500 22px '{t['mono']}',monospace;margin-bottom:24px;letter-spacing:.01em}}
.stat{{font-family:'{t['display']}';font-size:200px;font-weight:700;letter-spacing:-.06em;line-height:.9;margin-bottom:22px}}
.rows{{list-style:none;display:flex;flex-direction:column;margin-top:8px;border-top:.5px solid {t['line']}}}
.rows li{{display:flex;gap:28px;align-items:baseline;padding:28px 0;border-bottom:.5px solid {t['line']};font-size:33px;line-height:1.38;color:{t['body']}}}
.rows li b{{font:500 22px '{t['mono']}',monospace;color:{t['accent_ink']};min-width:40px}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:6px}}
.cols .card{{padding:40px 38px}}
.cols h3{{font:600 22px '{t['text']}';letter-spacing:.07em;text-transform:uppercase;margin-bottom:24px}}
.cols ul{{list-style:none;display:flex;flex-direction:column;gap:22px;font-size:30px;line-height:1.36;color:{t['body']}}}
.cols li{{padding-left:30px;position:relative}}
.cols li::before{{content:"";position:absolute;left:0;top:.55em;width:12px;height:12px;border-radius:3px;transform:rotate(45deg);background:currentColor;opacity:.55}}
.foot{{display:flex;justify-content:flex-end;align-items:center;position:relative;z-index:5;min-height:40px}}
.swipe{{font:500 22px '{t['mono']}',monospace;color:{t['accent_ink']}}}
.hero{{position:absolute;pointer-events:none;z-index:1}}
.mascot{{position:absolute;left:58px;bottom:44px;width:176px;z-index:6}}
.cta{{display:flex;flex-direction:column}}
.cta h1{{font-size:84px}}
.q{{margin-top:44px;border:.5px solid {t['line']};border-radius:24px;padding:30px 34px;font-size:32px;line-height:1.4;background:{t['tints']['purple']};color:{t['body']}}}
.q b{{display:block;font:500 20px '{t['mono']}',monospace;color:{t['accent_ink']};margin-bottom:10px;letter-spacing:.02em}}
.save{{display:inline-flex;align-items:center;gap:14px;margin-top:40px;font-size:30px;font-weight:600;background:{t['accent_ink'] if t is not THEMES['night'] else t['accent']};color:{t['on_accent']};border-radius:999px;padding:22px 34px;align-self:flex-start}}
.src{{font:400 22px '{t['mono']}',monospace;color:{t['muted']};margin-top:26px;letter-spacing:.01em}}
"""


def _e(s: str) -> str:
    out = escape(s or "")
    parts = out.split("*")
    return "".join(f"<em>{p}</em>" if i % 2 else p for i, p in enumerate(parts))


def _img(key: str | None, assets: dict, style: str, cls: str = "hero") -> str:
    if not key:
        return ""
    return f'<img class="{cls}" style="{style}" src="{data_uri(str(assets[key]))}" alt="">'


def render_slide(s: dict, i: int, n: int, deck: dict, assets: dict) -> str:
    t = THEMES[deck.get("theme", "studio")]
    kind = s.get("type", "point")
    tint = s.get("tint", ["purple", "teal", "coral"][(i - 2) % 3])
    bg, ink = t["tints"][tint], t["inks"][tint]
    badge = f'<div class="badge">{escape(s["badge"])}</div>' if s.get("badge") else ""
    src = f'<div class="src">{escape(s["source"])}</div>' if s.get("source") else ""
    hero = _img(s.get("hero"), assets, s.get("hero_style", "right:-40px;bottom:120px;width:640px"))
    mascot = _img(s.get("mascot"), assets, s.get("mascot_style", ""), "mascot")
    if kind == "cover":
        body = f'{badge}<h1 style="{s.get("title_style", "")}">{_e(s["title"])}</h1><p class="sub">{_e(s.get("subtitle", ""))}</p>'
    elif kind == "stat":
        body = (f'{badge}<div class="card" style="background:{bg}"><div class="label" style="color:{ink}">{escape(s.get("label", ""))}</div>'
                f'<div class="stat" style="color:{ink}">{escape(s["value"])}</div><h2>{_e(s["title"])}</h2><p>{_e(s.get("body", ""))}</p>{src}</div>')
        src = ""
    elif kind == "list":
        rows = "".join(f"<li><b>{k:02d}</b><span>{_e(x)}</span></li>" for k, x in enumerate(s["items"], 1))
        body = f'{badge}<h2>{_e(s["title"])}</h2><ul class="rows">{rows}</ul>'
    elif kind == "compare":
        col = lambda c, tn: (f'<div class="card" style="background:{t["tints"][tn]}"><h3 style="color:{t["inks"][tn]}">{escape(c["label"])}</h3>'
                             f'<ul style="color:{t["inks"][tn]}">{"".join(f"<li><span style=\"color:{t["body"]}\">{_e(x)}</span></li>" for x in c["items"])}</ul></div>')
        body = f'{badge}<h2>{_e(s["title"])}</h2><div class="cols">{col(s["left"], "coral")}{col(s["right"], "teal")}</div>'
    elif kind == "cta":
        q = f'<div class="q"><b>YOUR TURN</b>{_e(s["question"])}</div>' if s.get("question") else ""
        body = (f'<div class="cta">{badge}<h1>{_e(s["title"])}</h1><p class="sub">{_e(s.get("subtitle", ""))}</p>{q}'
                f'<div class="save">{escape(s.get("button", "Save this for later"))}</div></div>')
    else:  # point
        body = (f'{badge}<div class="card" style="background:{bg}"><div class="label" style="color:{ink}">{escape(s.get("label", ""))}</div>'
                f'<h2>{_e(s["title"])}</h2><p>{_e(s.get("body", ""))}</p></div>')
    a = deck["author"]
    initials = "".join(w[0] for w in a["name"].split()[:2]).upper()
    foot = "" if kind == "cta" else '<div class="foot"><span class="swipe">swipe →</span></div>'
    counter = f"{i} / {n}"
    if deck.get("single"):
        counter = escape(deck.get("tag", ""))
        foot = f'<div class="foot"><span class="swipe" style="color:{t["muted"]}">{escape(deck.get("site_label", ""))}</span></div>'
    if kind == "cta":
        foot = f'<div class="foot"><span class="swipe" style="color:{t["muted"]}">{escape(deck.get("site_label", "buildwithvish.netlify.app"))}</span></div>'
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{font_css()}{css(t)}</style></head><body>"
            f'<div class="bgwash"></div>{hero}'
            f'<div class="slide"><div class="top"><div class="handle"><div class="avatar">{initials}</div>'
            f'<div>{escape(a["name"])}<small>{escape(a["handle"])}</small></div></div><div class="pill">{counter}</div></div>'
            f'<div class="mid" style="{s.get("mid_style", "")}">{body}{src}</div>{foot}</div>{mascot}<div class="grain"></div></body></html>')


def render_html_page(html: str, out_png: Path, out_pdf_parts: list | None = None, page=None) -> None:
    page.set_content(html, wait_until="load")
    page.evaluate("document.fonts.ready")
    page.screenshot(path=str(out_png))
    if out_pdf_parts is not None:
        out_pdf_parts.append(page.pdf(width=f"{W}px", height=f"{H}px", print_background=True, page_ranges="1"))
