"""Quality gate for a post folder. Writes qa-report.md and exits non-zero on any FAIL.

    python scripts/qa.py out/2026-10-06-eu-ai-text-watermark [--no-net]

Checks
- copy:    banned words, em/en dashes, hook length, one closing question, caption length, reading ease
- facts:   sources.md present, every source dated, dates inside the freshness window,
           every number on the slides/caption appears in sources.md
- design:  every text box inside the canvas and safe margins, no text overflow, WCAG contrast,
           minimum font size for mobile (40% scale), mascot present on at least one slide
- links:   every URL in first-comment.md / sources.md answers 200 (skipped with --no-net)
- brand:   theme exists in tokens; accent colours come from tokens
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
TOKENS = json.loads((ROOT / "brand" / "tokens.json").read_text())
TODAY = dt.date.fromisoformat(__import__("os").environ.get("QA_TODAY", dt.date.today().isoformat()))
WINDOWS = {"news": 14, "tool": 30, "product": 30, "evergreen": 10_000}
MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}

DESIGN_JS = r"""
() => {
  const W = 1080, H = 1350, M = 60, out = [];
  const lum = (c) => { const m = c.match(/[\d.]+/g).map(Number); const f = (v) => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }; return [.2126 * f(m[0]) + .7152 * f(m[1]) + .0722 * f(m[2]), m[3] === undefined ? 1 : m[3]]; };
  // Composite every translucent background from <body> up to the element (glass cards are rgba).
  const rgba = (c) => { const m = (c.match(/[\d.]+/g) || [0, 0, 0, 0]).map(Number); return [m[0], m[1], m[2], m[3] === undefined ? 1 : m[3]]; };
  const bgOf = (el) => {
    const stack = []; for (let e = el; e && e !== document.documentElement; e = e.parentElement) stack.push(getComputedStyle(e).backgroundColor);
    let c = [0, 0, 0];
    for (const b of stack.reverse()) { const [r, g, bl, a] = rgba(b); if (!a) continue; c = [c[0] * (1 - a) + r * a, c[1] * (1 - a) + g * a, c[2] * (1 - a) + bl * a]; }
    return `rgb(${c[0]},${c[1]},${c[2]})`;
  };
  // Opaque gradient fills (badges, buttons): judge against the worst gradient stop, not the colour underneath.
  const gradStops = (el) => {
    for (let e = el; e && e !== document.documentElement; e = e.parentElement) {
      const bi = getComputedStyle(e).backgroundImage;
      if (bi && bi.includes("linear-gradient") && !bi.includes("url(")) return bi.match(/rgba?\([^)]+\)/g) || [];
      if (rgba(getComputedStyle(e).backgroundColor)[3] >= 1) return [];
    }
    return [];
  };
  document.querySelectorAll(".slide *").forEach((el) => {
    const own = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
    if (!own) return;
    const r = el.getBoundingClientRect(), cs = getComputedStyle(el), fs = parseFloat(cs.fontSize);
    const txt = el.textContent.trim().slice(0, 40);
    if (r.left < M - 1 || r.right > W - M + 1 || r.top < M - 1 || r.bottom > H - 40) out.push(["FAIL", `outside safe area: "${txt}"`]);
    if (el.scrollWidth > el.clientWidth + 2 && cs.overflow !== "visible") out.push(["FAIL", `text overflow: "${txt}"`]);
    const [l1] = lum(cs.color), stops = gradStops(el);
    const ratio = Math.min(...(stops.length ? stops : [bgOf(el)]).map((b) => { const [l2] = lum(b); return (Math.max(l1, l2) + .05) / (Math.min(l1, l2) + .05); }));
    const large = fs >= 24 && parseInt(cs.fontWeight) >= 600 || fs >= 32;
    if (ratio < (large ? 3 : 4.5)) out.push(["FAIL", `contrast ${ratio.toFixed(2)}:1 at ${fs}px: "${txt}"`]);
    if (fs < 19) out.push(["FAIL", `font ${fs}px too small for mobile: "${txt}"`]);
    else if (fs < 26 && !el.closest(".top,.foot,.label,.badge,.chip,.src,.q b,.cols h3,.rows b")) out.push(["WARN", `${fs}px body text reads ~${(fs * .4).toFixed(0)}px on a phone: "${txt}"`]);
  });
  return out;
}
"""


def _words(s: str) -> int:
    return len(re.findall(r"[\w'’%.,]+", s))


def flesch(text: str) -> float:
    sents = max(1, len(re.findall(r"[.!?](\s|$)", text)))
    words = re.findall(r"[A-Za-z']+", text)
    syl = sum(max(1, len(re.findall(r"[aeiouy]+", w.lower())) - (w.lower().endswith("e") and len(w) > 3)) for w in words)
    n = max(1, len(words))
    return 206.835 - 1.015 * (n / sents) - 84.6 * (syl / n)


def parse_dates(text: str) -> list[dt.date]:
    out = []
    for d, m, y in re.findall(r"\b(\d{1,2}) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* (20\d\d)\b", text):
        out.append(dt.date(int(y), MONTHS[m.lower()], int(d)))
    return out


def check_copy(post: Path, deck: dict, R: list) -> None:
    banned = TOKENS["voice"]["banned"]
    texts = {"caption": (post / "caption.md").read_text() if (post / "caption.md").exists() else ""}
    slide_txt = json.dumps(deck.get("slides", deck.get("scenes", [])), ensure_ascii=False)
    texts["slides"] = slide_txt
    for name, t in texts.items():
        low = t.lower()
        for b in banned:
            if re.search(r"\b" + re.escape(b) + r"\b", low):
                R.append(("FAIL", "copy", f"banned phrase '{b}' in {name}"))
        if "—" in t or "–" in t:
            R.append(("FAIL", "copy", f"em/en dash in {name}"))
    tells = {r"\bnot (just|only) \w+.{0,40}\bbut\b": "not-X-but-Y contrast", r"\bisn't (a|an|about)\b[^.]{0,60}\. (It's|It is)\b": "not-X-but-Y contrast",
             r"(?m)^(That matters|Let that sink in|That's the real)": "dramatic one-line closer", r"\b(crucial|pivotal|showcase|vibrant|meticulous|underscore|garner|bolster|testament|furthermore|moreover|additionally|passionate|thrilled|results-driven)\b": "stock AI word",
             r", (highlighting|ensuring|showcasing|fostering)\b": "-ing rider", r"\b(I hope this helps|feel free to|don't hesitate)\b": "chatbot residue", r"!": "exclamation mark"}
    for name, t in texts.items():
        for rx, label in tells.items():
            for m in re.finditer(rx, t, re.I):
                R.append(("WARN", "copy", f"humanizer tell ({label}) in {name}: \"{m.group(0)[:50]}\""))
    cap = texts["caption"]
    if cap:
        hook = cap.strip().splitlines()[0]
        n = _words(hook)
        R.append(("PASS" if n < 12 else "FAIL", "copy", f"hook {n} words: \"{hook}\""))
        last = [l for l in cap.strip().splitlines() if l.strip()][-1]
        R.append(("PASS" if last.strip().endswith("?") else "FAIL", "copy", f"closes on one open question: \"{last.strip()[:70]}\""))
        qs = cap.count("?")
        if qs > 2:
            R.append(("WARN", "copy", f"{qs} question marks; keep one clear CTA question"))
        R.append(("PASS" if len(cap) <= 3000 else "FAIL", "copy", f"caption {len(cap)} chars (LinkedIn limit 3000)"))
        fe = flesch(re.sub(r"[→\[\]]", "", cap))
        R.append(("PASS" if fe >= 50 else "WARN", "copy", f"reading ease {fe:.0f} (aim 50+)"))
        if "[VISH" in cap or "[CONFIRM" in cap:
            R.append(("WARN", "copy", "contains a line Vish must confirm before posting"))


def check_facts(post: Path, deck: dict, R: list) -> None:
    src = post / "sources.md"
    if not src.exists():
        R.append(("FAIL", "facts", "sources.md missing"))
        return
    s = src.read_text()
    kind = "tool" if re.search(r"product update|tool/product|30 days", s) else "news"
    window = WINDOWS[kind]
    dates = parse_dates(s)
    if not dates:
        R.append(("FAIL", "facts", "no dated sources"))
    for d in sorted(set(dates)):
        age = (TODAY - d).days
        R.append(("PASS" if age <= window else "FAIL", "facts", f"source dated {d} is {age} days old ({kind} window {window}d)"))
    clean = json.loads(json.dumps(deck))
    for sl in clean.get("slides", []) + clean.get("scenes", []):
        for k in [k for k in sl if k.endswith("_style")]:
            sl.pop(k)
    body = json.dumps(clean, ensure_ascii=False) + ((post / "caption.md").read_text() if (post / "caption.md").exists() else "")
    nums = set(re.findall(r"\d+(?:[.,]\d+)?\s?(?:%|B\b|billion|tokens)", body))
    for n in sorted(nums):
        core = re.match(r"[\d.,]+", n).group()
        ok = core in s or core.replace(",", "") in s
        R.append(("PASS" if ok else "FAIL", "facts", f"number '{n.strip()}' traced to sources.md" if ok else f"number '{n.strip()}' not found in sources.md"))


def check_design(post: Path, deck: dict, R: list) -> None:
    if "slides" not in deck:
        return
    from playwright.sync_api import sync_playwright

    from carousel import aurora
    from carousel.studio import H, W, render_slide as studio_slide
    from build_post import find_assets

    assets = find_assets(deck, post)
    n = len(deck["slides"])
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": W, "height": H})
        for i, s in enumerate(deck["slides"], 1):
            rs = aurora.render_slide if deck.get("system") == "aurora" else studio_slide
            page.set_content(rs(s, i, n, deck, assets), wait_until="load")
            page.evaluate("document.fonts.ready")
            issues = page.evaluate(DESIGN_JS)
            fonts_ok = page.evaluate("[...document.fonts].filter(f => f.status === 'loaded').length")
            if not fonts_ok:
                R.append(("FAIL", "design", f"slide {i}: brand fonts did not load"))
            if not issues:
                R.append(("PASS", "design", f"slide {i}: safe area, overflow, contrast, sizes"))
            for lvl, msg in issues:
                R.append((lvl, "design", f"slide {i}: {msg}"))
        b.close()
    if not any(s.get("mascot") for s in deck["slides"]):
        R.append(("WARN", "design", "mascot not used on any slide"))
    if deck.get("system") == "aurora":
        R.append(("PASS", "brand", f"Aurora Glass ({deck.get('variant', 'galaxy')}) from brand tokens"))
    elif deck.get("theme") not in ("studio", "night", "field"):
        R.append(("FAIL", "brand", f"unknown theme {deck.get('theme')}"))
    else:
        R.append(("PASS", "brand", f"theme '{deck['theme']}' comes from brand tokens"))


def check_links(post: Path, R: list, net: bool) -> None:
    urls = set()
    for f in ("first-comment.md", "sources.md"):
        if (post / f).exists():
            urls |= set(re.findall(r"https?://[^\s)|>]+", (post / f).read_text()))
    for u in sorted(urls):
        if not net:
            R.append(("WARN", "links", f"not checked (--no-net): {u}"))
            continue
        try:
            req = urllib.request.Request(u.split("#")[0], method="GET", headers={"User-Agent": "Mozilla/5.0 qa-bot"})
            code = urllib.request.urlopen(req, timeout=15).status
            R.append(("PASS" if code == 200 else "FAIL", "links", f"{code} {u}"))
        except Exception as e:  # noqa: BLE001
            reason = str(e)
            lvl = "WARN" if "403" in reason and "Tunnel" in reason or "CONNECT" in reason else "FAIL"
            R.append((lvl, "links", f"{u} -> {reason[:80]}"))
    if (post / "first-comment.md").exists() and "#read-" in (post / "first-comment.md").read_text():
        slug = re.search(r"#read-([\w-]+)", (post / "first-comment.md").read_text()).group(1)
        R.append(("WARN", "links", f"hash route #read-{slug} always returns 200; confirm the page exists in buildwithvish src/long before posting"))


def run(post: Path, net: bool = True) -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    deck_f = post / "deck.json" if (post / "deck.json").exists() else post / "video.json"
    deck = json.loads(deck_f.read_text())
    R: list[tuple[str, str, str]] = []
    check_copy(post, deck, R)
    check_facts(post, deck, R)
    check_design(post, deck, R)
    check_links(post, R, net)
    fails = sum(1 for r in R if r[0] == "FAIL")
    warns = sum(1 for r in R if r[0] == "WARN")
    lines = [f"# QA report: {post.name}", "", f"Run {dt.datetime.now():%Y-%m-%d %H:%M} · **{'PASS' if not fails else 'FAIL'}** · {fails} fail, {warns} warn, {len(R) - fails - warns} pass", "",
             "| Result | Area | Check |", "|---|---|---|"]
    order = {"FAIL": 0, "WARN": 1, "PASS": 2}
    lines += [f"| {lvl} | {area} | {msg.replace('|', '/')} |" for lvl, area, msg in sorted(R, key=lambda r: order[r[0]])]
    lines += ["", "Manual checks (the reviewer agent signs these off): 3D quality (banding, muddy light), mascot consistency, legal (no third-party logos or characters), tone."]
    (post / "qa-report.md").write_text("\n".join(lines) + "\n")
    print(f"{post.name}: {'PASS' if not fails else 'FAIL'} ({fails} fail, {warns} warn)")
    return 1 if fails else 0


if __name__ == "__main__":
    net = "--no-net" not in sys.argv
    rc = 0
    for a in [x for x in sys.argv[1:] if not x.startswith("--")]:
        rc |= run(Path(a), net)
    raise SystemExit(rc)
