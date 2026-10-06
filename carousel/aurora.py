"""Aurora Glass: the premium, seamless carousel system (direction chosen with Vish on 6 Oct 2026).

What makes it seamless: every deck shares ONE wide panorama of soft light sources. Slide i shows the
window [i*1080, (i+1)*1080] of it, so a glow that leaves slide 2 on the right enters slide 3 on the left.

Variants
- galaxy:   near-black with violet/indigo/plum light, the default for covers, video and dark decks
- daylight: airy lavender, sky and peach, for long-read carousels

Locked rules kept from the original system: handle top-left, pill counter top-right, #7F77DD accent,
hairline borders, tinted (now glass) cards, save CTA with one question on the last slide.
"""
from __future__ import annotations

import math
import random
from html import escape

from .studio import GRAIN, H, W, _e, _img, font_css

VARIANTS = {
    "galaxy": {
        "base": "#07060C", "ink": "#F4F2FA", "muted": "#A9A4B8", "body": "#D9D5E6", "accent": "#B3A9FF", "accent_ink": "#B3A9FF",
        "lights": ["#4B3FD6", "#211C78", "#6D62E8", "#2E2790", "#5446D9"], "light_alpha": [0.62, 0.7, 0.42, 0.6, 0.38],
        "glass": "rgba(255,255,255,.055)", "glass_line": "rgba(255,255,255,.13)", "glass_hi": "rgba(255,255,255,.22)",
        "chip": "rgba(20,18,32,.72)", "chip_line": "rgba(255,255,255,.14)", "ghost": "rgba(255,255,255,.035)",
        "grain": .10, "blend": "overlay", "btn": "#F4F2FA", "btn_ink": "#0B0A12",
        "tints": {"purple": "rgba(127,119,221,.14)", "teal": "rgba(127,119,221,.09)", "coral": "rgba(180,170,255,.08)"},
        "inks": {"purple": "#C9C1FF", "teal": "#C9C1FF", "coral": "#DCD6FF"},
    },
    "daylight": {
        "base": "#EEEEF6", "ink": "#121018", "muted": "#5E5970", "body": "#2F2B3D", "accent": "#5B4FE0", "accent_ink": "#4A44C4",
        "lights": ["#C9D9F7", "#D9D2FA", "#F6E2D2", "#BFE8E1", "#E7D7F7"], "light_alpha": [0.95, 0.9, 0.85, 0.7, 0.8],
        "glass": "rgba(255,255,255,.55)", "glass_line": "rgba(255,255,255,.85)", "glass_hi": "rgba(255,255,255,.95)",
        "chip": "rgba(28,26,40,.82)", "chip_line": "rgba(255,255,255,.2)", "ghost": "rgba(40,30,90,.045)",
        "grain": .07, "blend": "soft-light", "btn": "#17141C", "btn_ink": "#FFFFFF",
        "tints": {"purple": "rgba(255,255,255,.62)", "teal": "rgba(240,251,246,.7)", "coral": "rgba(254,246,243,.72)"},
        "inks": {"purple": "#534AB7", "teal": "#0F7A55", "coral": "#B4502A"},
    },
}


def panorama(n: int, v: dict, seed: int = 7) -> list[dict]:
    """Soft light sources across the whole deck, in panorama pixel coordinates."""
    rnd = random.Random(seed)
    out = []
    for k in range(int(n * 1.15) + 2):
        x = (k + 0.5) * (n * W) / (n * 1.15 + 1) + rnd.uniform(-180, 180)
        y = rnd.choice([rnd.uniform(-150, 380), rnd.uniform(950, 1500)])
        r = rnd.uniform(520, 860)
        i = k % len(v["lights"])
        out.append({"x": x, "y": y, "r": r, "c": v["lights"][i], "a": v["light_alpha"][i]})
    return out


def _bg(lights: list[dict], i: int, v: dict, ghost: str) -> str:
    off = (i - 1) * W
    blobs = "".join(
        f'<div class="light" style="left:{L["x"] - off - L["r"]:.0f}px;top:{L["y"] - L["r"]:.0f}px;width:{2 * L["r"]:.0f}px;height:{2 * L["r"]:.0f}px;'
        f'background:radial-gradient(circle at 50% 50%,{L["c"]} 0%,transparent 68%);opacity:{L["a"]}"></div>'
        for L in lights if -L["r"] * 1.2 < L["x"] - off < W + L["r"] * 1.2)
    g = f'<div class="ghost">{escape(ghost)}</div>' if ghost else ""
    return f'<div class="bg">{blobs}</div>{g}'


def css(v: dict) -> str:
    return f"""
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:{W}px;height:{H}px;background:{v['base']};font-family:'Geist',system-ui,sans-serif;color:{v['ink']};overflow:hidden;-webkit-font-smoothing:antialiased;text-rendering:geometricPrecision}}
.bg{{position:absolute;inset:-60px;filter:blur(70px) saturate(1.1)}}
.light{{position:absolute;border-radius:50%}}
.ghost{{position:absolute;left:0;right:0;top:50%;transform:translateY(-54%);text-align:center;font:700 600px/1 'Geist';letter-spacing:-.07em;color:{v['ghost']};pointer-events:none}}
.grain{{position:absolute;inset:0;background-image:url("{GRAIN}");background-size:180px;opacity:{v['grain']};mix-blend-mode:{v['blend']};pointer-events:none;z-index:9}}
.slide{{position:absolute;inset:0;padding:80px 84px 84px;display:flex;flex-direction:column;z-index:3}}
.top{{display:flex;justify-content:space-between;align-items:center}}
.handle{{display:flex;align-items:center;gap:14px;font-size:24px;font-weight:600;letter-spacing:-.01em}}
.mark{{width:46px;height:46px;border-radius:14px;background:linear-gradient(160deg,#9C94F0,#5B4FE0);position:relative;box-shadow:inset 0 1px 0 rgba(255,255,255,.35),0 8px 24px -10px rgba(91,79,224,.8)}}
.mark::before{{content:"";position:absolute;inset:12px;border:3px solid #fff;border-radius:4px;transform:rotate(45deg)}}
.mark::after{{content:"";position:absolute;left:50%;top:50%;width:7px;height:7px;margin:-3.5px;border-radius:50%;background:#fff}}
.handle small{{display:block;font-size:19px;font-weight:400;color:{v['muted']};margin-top:1px}}
.pill{{font:500 20px 'Geist Mono',monospace;border:1px solid {v['glass_line']};border-radius:999px;padding:10px 20px;color:{v['muted']};background:{v['glass']};backdrop-filter:blur(14px)}}
.mid{{flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;position:relative}}
.chip{{display:inline-flex;align-items:center;gap:0;border-radius:999px;background:{v['chip']};border:1px solid {v['chip_line']};padding:6px;margin-bottom:38px;backdrop-filter:blur(16px);box-shadow:0 20px 40px -24px rgba(0,0,0,.6)}}
.chip span{{font:500 25px 'Geist';color:#F4F2FA;padding:8px 18px 8px 14px;display:flex;align-items:center;gap:10px}}
.chip svg{{width:22px;height:22px}}
.chip b{{font:600 25px 'Geist';background:#7F77DD;color:#fff;border-radius:999px;padding:9px 22px;box-shadow:inset 0 1px 0 rgba(255,255,255,.35)}}
h1{{font-size:92px;line-height:1.02;letter-spacing:-.04em;font-weight:600;text-wrap:balance;max-width:900px}}
h1 em,h2 em{{font-style:normal;color:{v['accent']}}}
h2{{font-size:60px;line-height:1.06;letter-spacing:-.035em;font-weight:600;text-wrap:balance;margin-bottom:24px}}
.sub{{font-size:36px;line-height:1.35;color:{v['muted']};margin-top:24px;max-width:820px;text-wrap:balance;font-weight:400}}
.glass{{background:{v['glass']};border:1px solid {v['glass_line']};border-radius:40px;padding:56px 58px;backdrop-filter:blur(26px) saturate(1.2);box-shadow:inset 0 1px 0 {v['glass_hi']},0 50px 90px -50px rgba(0,0,0,.55);text-align:left;width:100%;position:relative}}
.glass p,.bodytext{{font-size:33px;line-height:1.46;color:{v['body']};text-wrap:pretty}}
p em,li em{{font-style:normal;font-weight:600;color:{v['accent_ink']}}}
.label{{font:500 22px 'Geist Mono',monospace;margin-bottom:26px;letter-spacing:.01em}}
.stat{{font-size:230px;font-weight:600;letter-spacing:-.065em;line-height:.88;margin-bottom:18px}}
.rows{{list-style:none;display:flex;flex-direction:column;gap:16px;width:100%;margin-top:10px}}
.rows li{{display:flex;gap:26px;align-items:center;text-align:left;padding:28px 34px;border-radius:28px;background:{v['glass']};border:1px solid {v['glass_line']};backdrop-filter:blur(20px);font-size:31px;line-height:1.36;color:{v['body']};box-shadow:inset 0 1px 0 {v['glass_hi']}}}
.rows li b{{flex:none;width:52px;height:52px;border-radius:16px;display:grid;place-items:center;font:600 22px 'Geist Mono',monospace;color:#fff;background:linear-gradient(160deg,#9C94F0,#5B4FE0)}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:20px;width:100%;margin-top:6px;text-align:left}}
.cols .glass{{padding:40px 36px;border-radius:32px}}
.cols h3{{font:600 22px 'Geist';letter-spacing:.07em;text-transform:uppercase;margin-bottom:24px}}
.cols ul{{list-style:none;display:flex;flex-direction:column;gap:20px;font-size:29px;line-height:1.36;color:{v['body']}}}
.cols li{{padding-left:28px;position:relative}}
.cols li::before{{content:"";position:absolute;left:0;top:.5em;width:11px;height:11px;border-radius:3px;transform:rotate(45deg);background:currentColor;opacity:.6}}
.foot{{display:flex;justify-content:space-between;align-items:center;font:400 21px 'Geist';color:{v['muted']}}}
.foot b{{font-weight:500;color:{v['ink']};display:flex;align-items:center;gap:10px}}
.hero{{position:absolute;pointer-events:none;z-index:1}}
.hero.dof{{filter:blur(10px);opacity:.8;z-index:0}}
.mascot{{position:absolute;z-index:6}}
.src{{font:400 22px 'Geist Mono',monospace;color:{v['muted']};margin-top:22px}}
.q{{margin-top:36px;border-radius:30px;padding:30px 36px;font-size:32px;line-height:1.4;background:{v['glass']};border:1px solid {v['glass_line']};backdrop-filter:blur(20px);color:{v['body']};text-align:left;width:100%}}
.q b{{display:block;font:500 20px 'Geist Mono',monospace;color:{v['accent_ink']};margin-bottom:10px;letter-spacing:.04em}}
.save{{display:inline-flex;align-items:center;gap:14px;margin-top:36px;font-size:29px;font-weight:600;background:{v['btn']};color:{v['btn_ink']};border-radius:999px;padding:22px 36px;box-shadow:0 24px 50px -24px rgba(0,0,0,.6)}}
.save svg{{width:24px;height:24px}}
"""


SAVE_ICON = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 3h12a1 1 0 0 1 1 1v17l-7-4.5L5 21V4a1 1 0 0 1 1-1z"/></svg>'
ARROW = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'


def render_slide(s: dict, i: int, n: int, deck: dict, assets: dict) -> str:
    v = VARIANTS[s.get("variant", deck.get("variant", "galaxy"))]
    lights = panorama(n, v, deck.get("seed", 7))
    kind = s.get("type", "point")
    tint = s.get("tint", ["purple", "teal", "coral"][(i - 2) % 3])
    chip = ""
    if s.get("chip"):
        chip = f'<div class="chip"><span>{SAVE_ICON}Save this</span><b>{escape(s["chip"])}</b></div>'
    src = f'<div class="src">{escape(s["source"])}</div>' if s.get("source") else ""
    heroes = ""
    if s.get("dof_hero") and not s.get("hero"):
        heroes += _img(s["dof_hero"], assets, s.get("dof_style", ""), "hero dof")
    if s.get("hero"):
        if s.get("dof"):
            heroes += _img(s.get("dof_hero", s["hero"]), assets, s.get("dof_style", "left:-120px;top:120px;width:520px;transform:rotate(-12deg)"), "hero dof")
        heroes += _img(s["hero"], assets, s.get("hero_style", "left:50%;transform:translateX(-50%);bottom:150px;width:720px"))
    mascot = _img(s.get("mascot"), assets, s.get("mascot_style", "right:70px;bottom:120px;width:170px"), "mascot")
    if kind == "cover":
        body = f'{chip}<h1 style="{s.get("title_style", "")}">{_e(s["title"])}</h1><p class="sub">{_e(s.get("subtitle", ""))}</p>'
    elif kind == "stat":
        ink = v["inks"][tint]
        body = (f'<div class="glass" style="background:{v["tints"][tint]}"><div class="label" style="color:{ink}">{escape(s.get("label", ""))}</div>'
                f'<div class="stat" style="color:{ink}">{escape(s["value"])}</div><h2>{_e(s["title"])}</h2><p>{_e(s.get("body", ""))}</p>{src}</div>')
        src = ""
    elif kind == "list":
        rows = "".join(f"<li><b>{k:02d}</b><span>{_e(x)}</span></li>" for k, x in enumerate(s["items"], 1))
        body = f'<h2>{_e(s["title"])}</h2><ul class="rows">{rows}</ul>'
    elif kind == "compare":
        def col(c, tn):
            items = "".join(f'<li><span style="color:{v["body"]}">{_e(x)}</span></li>' for x in c["items"])
            return f'<div class="glass" style="background:{v["tints"][tn]}"><h3 style="color:{v["inks"][tn]}">{escape(c["label"])}</h3><ul style="color:{v["inks"][tn]}">{items}</ul></div>'
        body = f'<h2>{_e(s["title"])}</h2><div class="cols">{col(s["left"], "coral")}{col(s["right"], "teal")}</div>'
    elif kind == "cta":
        q = f'<div class="q"><b>YOUR TURN</b>{_e(s["question"])}</div>' if s.get("question") else ""
        body = (f'{chip}<h1 style="font-size:82px">{_e(s["title"])}</h1><p class="sub">{_e(s.get("subtitle", ""))}</p>{q}'
                f'<div class="save">{SAVE_ICON}{escape(s.get("button", "Save this for later"))}</div>')
    else:
        ink = v["inks"][tint]
        body = (f'<div class="glass" style="background:{v["tints"][tint]}"><div class="label" style="color:{ink}">{escape(s.get("label", ""))}</div>'
                f'<h2>{_e(s["title"])}</h2><p>{_e(s.get("body", ""))}</p></div>')
    a = deck["author"]
    counter = escape(deck.get("tag", "")) if deck.get("single") else f"{i} / {n}"
    right = "" if kind == "cta" or deck.get("single") else f"<b>Swipe for more {ARROW}</b>"
    foot = f'<div class="foot"><span>{escape(deck.get("site_label", "buildwithvish.netlify.app"))}</span>{right}</div>'
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{font_css()}{css(v)}</style></head><body>"
            f'{_bg(lights, i, v, s.get("ghost", ""))}{heroes}'
            f'<div class="slide"><div class="top"><div class="handle"><div class="mark"></div>'
            f'<div>{escape(a["name"])}<small>{escape(a["handle"])}</small></div></div><div class="pill">{counter}</div></div>'
            f'<div class="mid" style="{s.get("mid_style", "")}">{body}{src}</div>{foot}</div>{mascot}<div class="grain"></div></body></html>')


__all__ = ["render_slide", "VARIANTS", "panorama", "math"]
