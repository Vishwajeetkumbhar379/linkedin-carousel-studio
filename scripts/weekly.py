"""The whole weekly batch in one command, with the heavy work on free tokens and local tools.

    python scripts/weekly.py                 # research -> write -> build -> voice -> covers -> render -> QA -> site -> calendar -> page
    python scripts/weekly.py --no-voice      # skip Gemini TTS (quota) and rendering of videos
    python scripts/weekly.py --write-only    # stop after content/batch-NN/posts.json

Who does what:
  research   scripts/research/fetch.py (RSS and pages, no LLM)
  writing    scripts/llm.py free providers (Groq gpt-oss-120b first, then NVIDIA, OpenRouter, Mistral, Cloudflare, LLM7)
  voice      Gemini TTS free tier (scripts/voiceover.py), one request per video
  graphics   Three.js props in headless Chromium, screen recordings via scripts/screen_record.py
  video      motion template + ffmpeg (scripts/render_ready.py), SFX via scripts/sfx.py
Claude only reviews the summary this prints and commits. Facts are restricted to the fetched research items:
every fact URL must be one of them and its date is taken from the item, so nothing can be invented or misdated.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import llm  # noqa: E402

PY = sys.executable
TODAY = dt.date.today()
MIX = ["carousel-tutorial", "carousel-tutorial", "carousel", "video", "video", "video-tutorial"]
BANNED = ["delve", "game-changer", "game changer", "unlock", "unleash", "supercharge", "seamless", "leverage", "robust", "elevate",
          "harness", "empower", "revolutionise", "revolutionize", "cutting-edge", "landscape", "realm", "tapestry", "synergy",
          "circle back", "fast-paced world", "let's dive in", "buckle up", "secret sauce", "it's important to note", "whether you're a"]
HEROES = {  # rendered 3D story props in out/_samples/3d (generic, no logos)
    "cv-report-funnel": "charts pouring into a funnel, three decision tiles come out (reports, analytics, decisions)",
    "cv-burning-brief": "a clipboard brief on fire with gold coins flying off (wasted budget, mistakes)",
    "cv-laptop-cap": "a laptop with a graduation cap (careers, learning, new roles)",
    "cv-brief-bot": "a friendly chat robot holding an ad card next to a speech bubble (AI assistants, chatbots)",
    "cv-hook-sticker": "a social post card with a yellow hook sticker and a cursor (hooks, posts, creators)",
    "cv-pipeline-chain": "script page, voice, play and spark tiles flowing by an arrow into a finished video post (workflows, pipelines, automation)",
    "cv-gift-year": "a gift box with a 12 month calendar (free offers, credits, programmes)",
    "cv-url-to-ads": "a browser URL bar with a cursor arrowing into two ad cards (ads, websites, generation)",
    "c-click-v6": "a big glossy button being clicked (launches, new features, one-click tools)",
    "a-cover-v6": "abstract glass tiles and a chat bubble (general AI news)",
}
SH = "filter:drop-shadow(0 24px 30px rgba(40,20,90,.28))"
MASK = "-webkit-mask-image:linear-gradient(#000 70%,transparent 98%);mask-image:linear-gradient(#000 70%,transparent 98%);"
SYSTEM = ("You write LinkedIn content for Vishwajeet 'Vish' Kumbhar: MBA (IBC, Hochschule Offenburg, Germany), 850+ creator deals in "
          "influencer marketing, works on AI x marketing, pivoting to AI Ops. Hub: Build with Vish (https://buildwithvish.netlify.app). "
          "British English. No em dashes or en dashes. Plain, punchy, human, short sentences, admits limits. Never invent numbers, quotes, "
          "results or clients. You return only valid JSON, no commentary.")


def log(*a):
    print("[weekly]", *a, flush=True)


def run(*cmd, check=True, **kw):
    log("$", " ".join(map(str, cmd)))
    return subprocess.run([str(c) for c in cmd], cwd=ROOT, check=check, **kw)


def ask_json(prompt: str, tries: int = 3):
    """Ask the free LLMs for JSON; strip code fences; retry with the parse error."""
    msg = prompt
    for i in range(tries):
        out = llm.chat(msg + "\nReturn a single JSON object (wrap lists as {\"items\": [...]}).", system=SYSTEM, temperature=0.6, timeout=240, json=True)
        txt = re.sub(r"^```(?:json)?|```$", "", out.strip(), flags=re.M).strip()
        m = re.search(r"[\[{].*[\]}]", txt, re.S)
        try:
            return json.loads(m.group(0) if m else txt)
        except Exception as e:  # noqa: BLE001
            log(f"JSON parse failed ({e}); asking again")
            msg = prompt + f"\n\nYour last reply was not valid JSON ({e}). Return ONLY the JSON."
    raise RuntimeError("LLM did not return valid JSON")


def next_batch() -> str:
    nums = [int(m.group(1)) for p in (ROOT / "out").glob("batch-*") if (m := re.match(r"batch-(\d+)$", p.name))]
    return f"batch-{(max(nums) + 1 if nums else 1):02d}"


def used_titles() -> list[str]:
    t = [json.loads(m.read_text()).get("title", "") for m in (ROOT / "out").glob("batch-*/*/meta.json")]
    posted = ROOT / "topics" / "posted.json"
    if posted.exists():
        t += [x.get("title", "") if isinstance(x, dict) else str(x) for x in json.loads(posted.read_text())]
    return [x for x in t if x]


_USED: set | None = None


def used_urls() -> set:
    """Source URLs already used by earlier batches, so a topic is never repeated."""
    global _USED
    if _USED is None:
        _USED = {u for f in (ROOT / "out").glob("batch-*/*/sources.md") for u in re.findall(r"https?://[^\s|)]+", f.read_text())}
    return _USED


def page_text(url: str, limit: int = 3500) -> str:
    try:
        raw = urllib.request.urlopen(urllib.request.Request(url, headers=llm.UA), timeout=20).read().decode("utf-8", "ignore")
    except Exception:  # noqa: BLE001
        return ""
    raw = re.sub(r"(?is)<(script|style|nav|footer|header)[^>]*>.*?</\1>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw))).strip()[:limit]


# ---------- seed topics (Vish's hype list) + free web search ----------
OFFICIAL = ("claude.com", "anthropic.com", "support.claude.com", "openai.com", "help.openai.com", "developers.facebook.com",
            "about.instagram.com", "blog.youtube", "developers.google.com", "support.google.com", "github.com", "modelcontextprotocol.io")


def search(q: str, n: int = 4) -> list[dict]:
    """Free web search (DuckDuckGo HTML). Official pages first."""
    import urllib.parse
    t = ""
    for wait in (0, 4, 10):
        time.sleep(wait)
        try:
            req = urllib.request.Request("https://html.duckduckgo.com/html/", data=urllib.parse.urlencode({"q": q}).encode(), headers=llm.UA)
            t = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
            break
        except Exception as e:  # noqa: BLE001
            log("search retry:", e)
    if not t:
        return []
    res = []
    for m in re.finditer(r'class="result__a" href="([^"]+)"[^>]*>(.*?)</a>', t):
        u = urllib.parse.parse_qs(urllib.parse.urlparse(m.group(1)).query).get("uddg", [m.group(1)])[0]
        if u.startswith("http") and "duckduckgo" not in u:
            res.append({"title": html.unescape(re.sub("<[^>]+>", "", m.group(2))), "url": u, "date": TODAY.isoformat(),
                        "source": urllib.parse.urlparse(u).netloc.replace("www.", "") + f" (page read {TODAY.isoformat()})", "summary": ""})
    res.sort(key=lambda r: 0 if any(r["url"].split("/")[2].endswith(d) for d in OFFICIAL) else 1)
    return res[:n]


def seed_picks(slots: list[str]) -> list[dict]:
    """Next unused seed topics for the tutorial slots; their sources come from live search, dated the day they were read."""
    f, used_f = ROOT / "topics" / "seeds.json", ROOT / "topics" / "seeds_used.json"
    if not f.exists():
        return []
    used = set(json.loads(used_f.read_text())) if used_f.exists() else set()
    out = []
    for slot in slots:
        seed = next((x for x in json.loads(f.read_text()) if x["id"] not in used and x["slot"] == slot), None)
        if not seed:
            continue
        items, seen = [], set()
        for q in seed["queries"]:
            for r in search(q):
                if r["url"] not in seen:
                    seen.add(r["url"]); items.append(r)
        if items:
            used.add(seed["id"])  # in-memory only, so two slots never take the same seed
            out.append({"slot": slot, "items": items[:4], "angle": seed["angle"], "seed": seed["id"]})
    return out


def mark_seeds_used(ids: list[str]) -> None:
    used_f = ROOT / "topics" / "seeds_used.json"
    used = set(json.loads(used_f.read_text())) if used_f.exists() else set()
    used_f.write_text(json.dumps(sorted(used | set(ids)), indent=1))


# ---------- research + planning ----------
def research() -> list[dict]:
    run(PY, "scripts/research/fetch.py", check=False)
    f = ROOT / "research" / "daily" / f"{TODAY.isoformat()}.json"
    items = json.loads(f.read_text())["items"] if f.exists() else []
    for p in (ROOT / "research" / "daily").glob("*.json"):  # also keep recent days still inside the news window
        if p != f and (TODAY - dt.date.fromisoformat(p.stem)).days <= 3:
            items += json.loads(p.read_text()).get("items", [])
    seen, out = set(), []
    for it in items:
        try:
            age = (TODAY - dt.date.fromisoformat(str(it.get("date"))[:10])).days
        except ValueError:
            continue  # undated items cannot back a claim
        if it.get("url") and it["url"] not in seen and it["url"] not in used_urls() and age <= 14:
            seen.add(it["url"]); out.append(it)
    log(f"{len(out)} fresh research items")
    return out


def _words(t: str) -> set:
    return {w for w in re.findall(r"[a-z0-9]+", t.lower()) if len(w) > 3}


def fresh_only(items: list[dict]) -> list[dict]:
    """Drop items whose title overlaps a topic we already covered (shared key words)."""
    done = [_words(t) for t in used_titles()]
    keep = []
    for it in items:
        w = _words(it["title"])
        if not any(len(w & d) >= 3 or (w and len(w & d) / len(w) >= 0.5) for d in done):
            keep.append(it)
    log(f"{len(items) - len(keep)} items dropped as already covered")
    return keep


def plan(items: list[dict], mix: list[str] = MIX) -> list[dict]:
    items = fresh_only(items)
    menu = "\n".join(f"{i}. [{it['date'][:10]}] {it.get('source', '')}: {it['title']} :: {(it.get('summary') or '')[:220]}" for i, it in enumerate(items[:120]))
    avoid = "\n".join(f"- {t}" for t in used_titles()[-60:])
    prompt = f"""Pick {len(mix)} LinkedIn post topics from these fresh research items (today is {TODAY}).
Slots, in this order: {json.dumps(mix)}.
Style Vish wants: big-claim tool hooks ("Opus 5.5 is crazy", "X just killed Y") ONLY when the item supports it, then a practical
step-by-step "how to use or automate it" angle (tools, prompts, B-roll, motion graphics, sound design). Free AI resources
(free tokens, GitHub repos, open-source tools) are great. AI x marketing, creator economy, social platforms, AI careers.
Tutorial slots must be step-by-step how-tos. Vary the hook shapes across the 6 (a number, a question, a "stop doing X",
a before/after, at most ONE "X just killed Y" and at most one "X is crazy"). Never stretch a claim beyond what the item says. Do not repeat these already-covered topics:
{avoid}

Research items:
{menu}

Return JSON: [{{"slot": "...", "items": [item numbers, 1-3 that back the post], "angle": "one line: the hook idea and the step-by-step payoff"}}] with {len(mix)} entries."""
    picks = []
    for _ in range(3):  # models sometimes return one pick, or wrap the list oddly; ask again until we have enough
        r = ask_json(prompt)
        if isinstance(r, dict):
            r = [r] if "slot" in r else next((v for v in r.values() if isinstance(v, list) and v and isinstance(v[0], dict)), [])
        picks = [x for x in (r if isinstance(r, list) else []) if isinstance(x, dict)]
        if len(picks) >= len(mix) - 1:
            break
        log(f"planner returned {len(picks)} picks; asking again")
    out = []
    for p, slot in zip(picks, mix):
        idx = [i for i in p.get("items", []) if isinstance(i, int) and 0 <= i < len(items)]
        if idx:
            out.append({"slot": slot, "items": [items[i] for i in idx], "angle": p.get("angle", "")})
    log("plan:", [(p["slot"], p["angle"][:60]) for p in out])
    return out


# ---------- writing ----------
def example(fmt: str) -> str:
    for f in sorted((ROOT / "content").glob("batch-*/posts.json"), reverse=True):
        for p in json.loads(f.read_text()):
            if p["format"] == fmt:
                p = dict(p); p["article"] = p["article"][:700] + " ..."
                return json.dumps(p, ensure_ascii=False)[:9000]
    return ""


def write_post(pick: dict) -> dict:
    fmt = "video" if pick["slot"].startswith("video") else "carousel"
    tutorial = pick["slot"].endswith("tutorial")
    src = "\n\n".join(f"SOURCE {k + 1}: {it['title']} ({it.get('source', '')}, {it['date'][:10]})\nURL: {it['url']}\n"
                      f"SUMMARY: {it.get('summary', '')[:600]}\nPAGE TEXT: {page_text(it['url'])}" for k, it in enumerate(pick["items"]))
    brief = (ROOT / "content" / "batch-01" / "BRIEF.md").read_text()
    rules = ("VIDEO RULES: narration 60 to 80 words total (30 to 40 s at a calm pace); 6 to 9 scenes, ONE phrase per scene, each phrase "
             "at least 6 words; exactly one beat per phrase, same order; vary looks (hook first, cta last; also text, stamp, chips, stat, "
             "chat, feed, versus); every beat gets an 'avatar' from surprised, smirk, laugh, stressed, thinking, focused, pleased, wink, "
             "point, explaining, thumbs, crossed (first beat), wave (cta); add 'trans' (whip|zoom|click|pop|rise) to every beat but the first. "
             "For any how-to step inside an AI app (Claude, ChatGPT, Gemini), use a screen walkthrough beat: {\"look\":\"ui\",\"bg\":\"ivory\","
             "\"title\":\"short line\",\"app\":\"Claude\",\"screen\":\"Connectors\",\"steps\":[{\"click\":\"Settings\"},{\"click\":\"Connectors\"},"
             "{\"click\":\"<item to add>\"},{\"result\":\"connected\"}],\"button\":\"Connect\",\"toast\":\"<item> connected\"} or a prompt flow "
             "{\"look\":\"ui\",\"app\":\"Claude\",\"screen\":\"New chat\",\"steps\":[{\"type\":\"<the exact prompt>\"},{\"result\":\"site\"}],"
             "\"siteTitle\":\"...\",\"siteSub\":\"...\"} (result can be site, connected or reply with \"reply\":\"...\"). Only click names the source "
             "actually describes; use 2 to 4 ui beats in a tutorial video. "
             "If a source is a GitHub repo or docs page, add a beat {\"look\":\"clip\",\"bg\":\"ivory\",\"title\":\"...\",\"clip\":{\"url\":\"<that url>\",\"scrollPx\":1600}}."
             if fmt == "video" else
             "CAROUSEL RULES: 8 to 10 slides, cover first, cta last. " + ("TUTORIAL: one step per slide, labels '01 · Step name', with copy-paste prompts or commands in the body." if tutorial else ""))
    prompt = f"""Write ONE post as a JSON object in exactly the schema of the brief below (format "{fmt}").
Angle: {pick['angle']}
{"This is a step-by-step tutorial." if tutorial else ""}
{rules}
FACTS: use ONLY the sources below. Every number or claim goes in "facts" with the source's exact URL and date. If a source does not say it, do not write it.
Hook max 12 words. Caption 700 to 1300 characters ending with one easy question, then 'Full breakdown: https://buildwithvish.netlify.app/#read-<slug>'.
Article 450 to 750 words in Markdown with H2s, a 'What I'd do' section and a 'Sources' list. No em or en dashes anywhere.

BRIEF:
{brief}

EXAMPLE OF A GOOD {fmt.upper()} POST (style and structure only; do not copy its facts):
{example(fmt)}

SOURCES:
{src}"""
    return ask_json(prompt)


def problems(p: dict, allowed: dict, tutorial: bool = False) -> list[str]:
    errs = []
    blob = json.dumps(p, ensure_ascii=False)
    if "—" in blob or "–" in blob:
        errs.append("contains em or en dashes")
    errs += [f"banned word: {w}" for w in BANNED if re.search(rf"\b{re.escape(w)}\b", blob, re.I)]
    if len(re.sub(r"[*]", "", p.get("hook", "")).split()) > 12:
        errs.append("hook longer than 12 words")
    for f in p.get("facts", []):
        if f.get("url") not in allowed:
            errs.append(f"fact URL not from the sources: {f.get('url')}")
    if p.get("format") == "video":
        phrases = [x for sc in p.get("narration", []) for x in sc]
        words = sum(len(x.split()) for x in phrases)
        if not 55 <= words <= 85:
            errs.append(f"narration is {words} words; needs 60 to 80")
        if len(p.get("beats", [])) != len(phrases):
            errs.append(f"{len(p.get('beats', []))} beats for {len(phrases)} phrases; needs one beat per phrase")
        if p.get("beats") and p["beats"][-1].get("look") != "cta":
            errs.append("last beat must be look cta")
        if tutorial and sum(b.get("look") == "ui" for b in p.get("beats", [])) < 2:
            errs.append("tutorial video needs 2 to 4 'ui' screen walkthrough beats (cursor clicks in the app, or the typed prompt and its result), "
                        "one per how-to step, using the ui beat format from the rules")
    else:
        if not 6 <= len(p.get("slides", [])) <= 10:
            errs.append(f"carousel has {len(p.get('slides', []))} slides; needs 8 to 10 (cover first, cta last)")
    if "?" not in p.get("caption", ""):
        errs.append("caption needs one closing question")
    return errs


def add_ui_beats(p: dict, items: list[dict]) -> dict:
    """Small focused call: turn 2 to 4 how-to lines of a tutorial video into screen walkthrough beats."""
    phrases = [sc[0] for sc in p.get("narration", [])]
    if len(phrases) < 4 or sum(b.get("look") == "ui" for b in p.get("beats", [])) >= 2:
        return p
    lines = "\n".join(f"{i}: {x}" for i, x in enumerate(phrases) if 0 < i < len(phrases) - 1)
    src = "\n\n".join(f"SOURCE {it['url']}\n{it.get('summary', '')[:400]}\n{page_text(it['url'], 3000)}" for it in items)
    try:
        r = ask_json(f"""A tutorial video shows the app screen while the voice explains each step. For 2 to 4 of these narration lines
that describe a step inside an app, write a screen walkthrough beat. Use only screen, menu and button names the sources mention;
if a source does not name a menu, use the plain action (for example "New chat", "Search", "Connect").
Beat format A (clicks): {{"look":"ui","bg":"ivory","title":"short caption, max 6 words","app":"<app name>","screen":"<screen>","steps":[{{"click":"<name>"}},{{"click":"<name>"}},{{"result":"connected"}}],"button":"Connect","toast":"<thing> connected"}}
Beat format B (prompt): {{"look":"ui","bg":"ivory","title":"...","app":"<app name>","screen":"New chat","steps":[{{"type":"<the prompt to paste>"}},{{"result":"site"}}],"siteTitle":"...","siteSub":"..."}}
(result may be "site", "connected", or "reply" with "reply":"<short answer>").

NARRATION LINES (index: line):
{lines}

SOURCES:
{src}

Return JSON {{"ui": [{{"index": <line index>, "beat": {{...}}}}]}}""")
    except Exception as e:  # noqa: BLE001
        log("ui beats skipped:", e); return p
    beats = p.get("beats", [])
    for u in (r.get("ui") or [])[:4]:
        i, b = u.get("index"), u.get("beat")
        if isinstance(i, int) and 0 < i < len(beats) - 1 and isinstance(b, dict) and b.get("steps"):
            b.update(look="ui", trans=beats[i].get("trans", "whip"), avatar="point")
            b.setdefault("bg", "ivory")
            b["title"] = b.get("title") or beats[i].get("title", "")
            beats[i] = b
    return p


def fact_check(p: dict, items: list[dict]) -> list[str]:
    """Second free model reads the sources and lists any line the sources do not support (numbers, claims, clicks)."""
    text = "\n".join([p.get("hook", "")] + [x for sc in p.get("narration", []) for x in sc]
                     + [" ".join(str(s.get(k, "")) for k in ("title", "body", "label") if s.get(k)) for s in p.get("slides", [])])
    src = "\n\n".join(f"SOURCE {it['url']}\n{it.get('summary', '')[:500]}\n{page_text(it['url'], 5000)}" for it in items)
    try:
        r = ask_json(f"""You are a strict fact checker. Below are the lines of a LinkedIn post and the sources it may use.
List only lines that state a specific number, date, price, percentage, named product feature, or exact menu or button name
that the sources do NOT support. Ignore step numbers and labels like "01 · Connect", headings, general how-to instructions,
opinions, advice, hooks that frame the topic, and calls to action: those are fine. Return JSON {{"unsupported": [{{"line": "...", "why": "..."}}]}} (empty list if all fine).

POST LINES:
{text}

SOURCES:
{src}""")
    except Exception as e:  # noqa: BLE001
        log("fact check skipped:", e); return []
    bad = [x for x in (r.get("unsupported") or []) if isinstance(x, dict) and x.get("line")]
    return [f"unsupported by the sources, rewrite or remove: \"{x['line'][:140]}\" ({str(x.get('why', ''))[:120]})" for x in bad[:6]]


def _line(d) -> str:
    if not isinstance(d, dict):
        return str(d)
    for k in ("line", "text", "phrase", "narration", "voiceover", "vo", "script"):
        if isinstance(d.get(k), str):
            return d[k]
    return next((v for v in d.values() if isinstance(v, str) and len(v.split()) > 3), "")


def as_post(x) -> dict:
    """Models sometimes wrap the object in a list or nest it under a key."""
    while isinstance(x, list) and x:
        x = x[0]
    if isinstance(x, dict) and "slug" not in x and len(x) == 1 and isinstance(next(iter(x.values())), (dict, list)):
        x = as_post(next(iter(x.values())))
    if not isinstance(x, dict):
        raise ValueError("model did not return a post object")
    x["facts"] = [f for f in x.get("facts", []) if isinstance(f, dict)]
    for k in ("beats", "slides"):
        if k in x:
            x[k] = [b for b in x[k] if isinstance(b, dict)]
    if not x.get("narration") and isinstance(x.get("scenes"), list):  # {"scenes": [{"line": ..., "beat": {...}}]}
        sc = [c for c in x.pop("scenes") if isinstance(c, dict)]
        x["narration"] = [_line(c) for c in sc]
        if all(isinstance(c.get("beat"), dict) for c in sc):
            x["beats"] = [c["beat"] for c in sc]
    nar = x.get("narration")
    if isinstance(nar, str):
        nar = [p for p in re.split(r"(?<=[.!?])\s+", nar.strip()) if p]
    if isinstance(nar, list):
        flat = []
        for sc in nar:
            if isinstance(sc, dict):
                sc = [_line(sc)]
            flat += [sc] if isinstance(sc, str) else [_line(t) if isinstance(t, dict) else str(t) for t in sc if str(t).strip()]
        x["narration"] = [[p] for p in flat if p.strip()]
    return x


def repair(p: dict) -> dict:
    """Fix structure without another model call: beats match phrases, cta last, slide bounds, closing question."""
    if p.get("format") == "video" and p.get("narration"):
        phrases = [sc[0] for sc in p["narration"]]
        beats = p.get("beats", [])
        if not beats or beats[-1].get("look") != "cta":
            beats = [b for b in beats if b.get("look") != "cta"] + [{"look": "cta", "bg": "violet", "title": "More *AI x marketing* every week.", "button": "Follow Vish"}]
        while len(beats) < len(phrases):
            beats.insert(-1, {"look": "text", "bg": ["ivory", "peach", "cobalt"][len(beats) % 3], "title": phrases[len(beats) - 1][:60], "trans": "whip"})
        beats = beats[:len(phrases) - 1] + [beats[-1]] if len(beats) > len(phrases) else beats
        for i, b in enumerate(beats):
            b.setdefault("trans", "whip") if i else b.pop("trans", None)
        p["beats"] = beats
    if p.get("format") == "carousel" and p.get("slides"):
        sl = p["slides"]
        if sl[-1].get("type") != "cta":
            sl.append({"type": "cta", "title": "Save this for your next *build day*.", "subtitle": "Full breakdown on Build with Vish.",
                       "question": "Which step would you automate first?", "button": "Save · Follow for AI x marketing", "chip": "Free guide inside"})
        p["slides"] = sl[:10]
    cap = p.get("caption", "")
    if "?" not in cap:
        q = "\n\nWhich part would you try first?"
        p["caption"] = re.sub(r"(\n*Full breakdown:)", q + r"\1", cap, count=1) if "Full breakdown:" in cap else cap + q
    return p


SWAP = {"leverage": "use", "leveraging": "using", "robust": "solid", "seamless": "smooth", "seamlessly": "smoothly", "unlock": "open up",
        "unlocks": "opens up", "unleash": "release", "supercharge": "speed up", "elevate": "lift", "harness": "use", "empower": "help",
        "landscape": "market", "realm": "area", "game-changer": "big shift", "game changer": "big shift", "cutting-edge": "new",
        "delve": "dig", "synergy": "fit", "revolutionise": "change", "revolutionize": "change"}


def clean(p: dict, allowed: dict, slug_taken: set) -> dict:
    p = as_post(p)
    s = json.dumps(p, ensure_ascii=False).replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
    s = s.replace("\u2011", "-").replace("\u2011", "-").replace(" - ", ", ")
    for w, r in SWAP.items():  # banned words get a plain swap instead of a whole rewrite
        s = re.sub(rf"\b{re.escape(w)}\b", lambda m, r=r: r.capitalize() if m.group(0)[0].isupper() else r, s, flags=re.I)
    p = json.loads(s)
    p["slug"] = re.sub(r"[^a-z0-9]+", "-", p.get("slug") or p.get("title", "post").lower()).strip("-")[:60]
    while p["slug"] in slug_taken:
        p["slug"] += "-2"
    p["caption"] = re.sub(r"#read-[a-z0-9-]+", f"#read-{p['slug']}", p.get("caption", ""))
    for f in p.get("facts", []):  # dates come from the research item, never from the model
        if f.get("url") in allowed:
            f["date"] = allowed[f["url"]]["date"][:10]
            f.setdefault("source_name", allowed[f["url"]].get("source", ""))
    return p


def merge(old: dict | None, new) -> dict:
    """A fix reply may hold only the changed fields; keep everything it left out or emptied."""
    try:
        new = as_post(new)
    except ValueError:
        return old
    if not old:
        return new
    out = dict(old)
    out.update({k: v for k, v in new.items() if v not in (None, "", [], {})})
    nw = lambda d: sum(len(x.split()) for sc in d.get("narration") or [] for x in sc)  # noqa: E731
    if old.get("narration") and nw(out) < 40 <= nw(old):  # fix reply mangled the script: keep the old one
        out["narration"], out["beats"] = old["narration"], old.get("beats", out.get("beats"))
    if old.get("slides") and len(out.get("slides") or []) < 6 <= len(old["slides"]):
        out["slides"] = old["slides"]
    return out


def write_one(pick: dict, taken: set) -> tuple[dict | None, list[str]]:
    allowed = {it["url"]: it for it in pick["items"]}
    tutorial = pick["slot"] == "video-tutorial"
    post, errs, checked = None, [], False
    for attempt in range(4):
        try:
            post = write_post(pick) if post is None else merge(post, ask_json(
                "Fix these problems in the JSON post and return the FULL corrected JSON object (every field, not only the changed ones):\n- "
                + "\n- ".join(errs) + "\n\nAllowed source URLs: " + ", ".join(allowed) + "\n\nPOST:\n" + json.dumps(post, ensure_ascii=False)))
        except Exception as e:  # noqa: BLE001
            log("write failed:", e); continue
        try:
            post = repair(clean(post, allowed, taken))
        except Exception as e:  # noqa: BLE001
            log("bad post shape:", e); errs = [str(e)]; post = None; continue
        post["format"] = "video" if pick["slot"].startswith("video") else "carousel"
        post["facts"] = [f for f in post.get("facts", []) if f.get("url") in allowed]
        if tutorial:
            post = add_ui_beats(post, pick["items"])
        errs = problems(post, allowed, tutorial)
        if not errs and not checked:  # one fact-check round per post, on a structurally valid draft
            checked = True
            errs = fact_check(post, pick["items"])
        if not errs:
            return post, []
        log(f"{post.get('slug')}: {errs}")
    return None, errs


def write_all(picks: list[dict], spares: list[dict] | None = None) -> list[dict]:
    """Write each pick; if one fails, a spare for the same slot type takes its place so the batch stays at six."""
    posts, taken, spares = [], {p.name for p in (ROOT / "out").glob("batch-*/*")}, list(spares or [])
    for pick in picks:
        post, errs = write_one(pick, taken)
        while not post and spares:
            log("DROPPED", pick.get("seed") or pick["angle"][:60], errs, "-> trying a spare")
            alt = next((s for s in spares if s["slot"].split("-")[0] == pick["slot"].split("-")[0]), spares[0])
            spares.remove(alt); alt = dict(alt, slot=pick["slot"]); pick = alt
            post, errs = write_one(pick, taken)
        if post:
            post["_seed"] = pick.get("seed")
            taken.add(post["slug"]); posts.append(post)
        else:
            log("DROPPED a post, no spare left:", errs)
    return posts


# ---------- covers, build, voice, render ----------
def covers(out: Path, posts: list[dict]) -> None:
    menu = "\n".join(f"{k}: {v}" for k, v in HEROES.items() if (ROOT / "out/_samples/3d" / f"{k}.png").exists())
    for p in posts:
        if p["format"] != "carousel":
            continue
        pick = ask_json(f"Pick the 3D cover prop that best acts out this headline, and a 2 to 4 word pointer label.\nHeadline: {p['hook']}\n"
                        f"Concept: {p.get('cover', {}).get('concept', '')}\nProps:\n{menu}\nReturn JSON {{\"hero\": \"<prop id>\", \"label\": \"...\", \"face\": \"surprised|skeptical\"}}")
        hero = pick.get("hero") if pick.get("hero") in HEROES else "a-cover-v6"
        label = re.sub(r"[—–]", ",", pick.get("label") or p.get("cover", {}).get("label", ""))[:28]
        d = out / p["slug"] / "deck.json"
        deck = json.loads(d.read_text()); c = deck["slides"][0]
        c.update(hero=hero, hero_style="left:140px;bottom:40px;width:800px", mid_style="justify-content:flex-start;padding-top:56px",
                 layers=[{"asset": pick.get("face") if pick.get("face") in ("surprised", "skeptical") else "surprised",
                          "style": f"left:40px;top:700px;width:250px;{MASK}{SH}"},
                         {"html": label, "class": "tag dark", "style": "right:60px;top:690px;transform:rotate(3deg)"}])
        d.write_text(json.dumps(deck, indent=2, ensure_ascii=False))
        run(PY, "scripts/build_post.py", out / p["slug"], check=False)


def main() -> None:
    name = next_batch()
    tut = [m for m in MIX if m.endswith("tutorial")]
    seeds = seed_picks(tut + tut)  # Vish's hype list fills the tutorial slots first; the next seeds are spares
    seeds, spare_seeds = seeds[:len(tut)], seeds[len(tut):]
    rest = list(MIX)
    for sp in seeds:
        rest.remove(sp["slot"])
    news = plan(research(), rest + ["carousel", "video", "carousel"])  # three spare news picks
    picks = seeds + news[:len(rest)]
    posts = write_all(picks, spare_seeds + news[len(rest):])
    mark_seeds_used([p.pop("_seed") for p in posts if p.get("_seed")])
    for p in posts:
        p.pop("_seed", None)
    cdir = ROOT / "content" / name
    cdir.mkdir(parents=True, exist_ok=True)
    (cdir / "posts.json").write_text(json.dumps(posts, indent=1, ensure_ascii=False))
    log(f"wrote {len(posts)} posts to content/{name}/posts.json")
    if "--write-only" in sys.argv:
        return
    out = ROOT / "out" / name
    run(PY, "scripts/make_batch.py", f"content/{name}", f"--out={name}")
    covers(out, posts)
    voiced = []
    if "--no-voice" not in sys.argv:
        for p in posts:
            if p["format"] == "video":
                r = run(PY, "scripts/voiceover.py", out / p["slug"] / "video.json", "--engine", "gemini-oneshot", "--no-bed", check=False)
                (voiced if r.returncode == 0 else []).append(p["slug"])
                time.sleep(25)
        run(PY, "scripts/render_ready.py", out, "--jobs=3", check=False)
    qa = {}
    for p in posts:
        r = run(PY, "scripts/qa.py", out / p["slug"], "--no-net", check=False, capture_output=True, text=True)
        qa[p["slug"]] = (r.stdout.strip().splitlines() or ["?"])[-1]
    site = Path("/home/user/buildwithvish")
    if site.exists():
        run(PY, "scripts/publish_site.py", out, site, check=False)
    run(PY, "scripts/post_calendar.py", out, check=False)
    batches = sorted(p for p in (ROOT / "out").glob("batch-*") if p.is_dir())
    run(PY, "scripts/batch_page.py", *batches, check=False)
    summary = {"batch": name, "posts": [{"slug": p["slug"], "format": p["format"], "hook": p["hook"], "qa": qa.get(p["slug"]),
                                         "voiced": p["slug"] in voiced if p["format"] == "video" else None} for p in posts]}
    (out / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False))
    print(json.dumps(summary, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
