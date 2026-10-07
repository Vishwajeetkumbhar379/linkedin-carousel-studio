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
        out = llm.chat(msg, system=SYSTEM, temperature=0.6, timeout=240)
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


def page_text(url: str, limit: int = 3500) -> str:
    try:
        raw = urllib.request.urlopen(urllib.request.Request(url, headers=llm.UA), timeout=20).read().decode("utf-8", "ignore")
    except Exception:  # noqa: BLE001
        return ""
    raw = re.sub(r"(?is)<(script|style|nav|footer|header)[^>]*>.*?</\1>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw))).strip()[:limit]


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
        if it.get("url") and it["url"] not in seen and age <= 14:
            seen.add(it["url"]); out.append(it)
    log(f"{len(out)} fresh research items")
    return out


def plan(items: list[dict]) -> list[dict]:
    menu = "\n".join(f"{i}. [{it['date'][:10]}] {it.get('source', '')}: {it['title']} :: {(it.get('summary') or '')[:220]}" for i, it in enumerate(items[:120]))
    avoid = "\n".join(f"- {t}" for t in used_titles()[-60:])
    prompt = f"""Pick 6 LinkedIn post topics from these fresh research items (today is {TODAY}).
Slots, in this order: {json.dumps(MIX)}.
Style Vish wants: big-claim tool hooks ("Opus 5.5 is crazy", "X just killed Y") ONLY when the item supports it, then a practical
step-by-step "how to use or automate it" angle (tools, prompts, B-roll, motion graphics, sound design). Free AI resources
(free tokens, GitHub repos, open-source tools) are great. AI x marketing, creator economy, social platforms, AI careers.
Tutorial slots must be step-by-step how-tos. Do not repeat these already-covered topics:
{avoid}

Research items:
{menu}

Return JSON: [{{"slot": "...", "items": [item numbers, 1-3 that back the post], "angle": "one line: the hook idea and the step-by-step payoff"}}] with 6 entries."""
    picks = ask_json(prompt)
    out = []
    for p, slot in zip(picks, MIX):
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


def problems(p: dict, allowed: dict) -> list[str]:
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
    else:
        if not 7 <= len(p.get("slides", [])) <= 10:
            errs.append("carousel needs 8 to 10 slides")
    if "?" not in p.get("caption", ""):
        errs.append("caption needs one closing question")
    return errs


def clean(p: dict, allowed: dict, slug_taken: set) -> dict:
    s = json.dumps(p, ensure_ascii=False).replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
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


def write_all(picks: list[dict]) -> list[dict]:
    posts, taken = [], {p.name for p in (ROOT / "out").glob("batch-*/*")}
    for pick in picks:
        allowed = {it["url"]: it for it in pick["items"]}
        post, errs = None, []
        for attempt in range(3):
            try:
                post = write_post(pick) if attempt == 0 or post is None else ask_json(
                    "Fix these problems in the JSON post and return the full corrected JSON object only:\n- " + "\n- ".join(errs)
                    + "\n\nAllowed source URLs: " + ", ".join(allowed) + "\n\nPOST:\n" + json.dumps(post, ensure_ascii=False))
            except Exception as e:  # noqa: BLE001
                log("write failed:", e); continue
            post = clean(post, allowed, taken)
            post["facts"] = [f for f in post.get("facts", []) if f.get("url") in allowed]
            errs = problems(post, allowed)
            if not errs:
                break
            log(f"{post.get('slug')}: {errs}")
        if post and not errs:
            post["format"] = "video" if pick["slot"].startswith("video") else "carousel"
            taken.add(post["slug"]); posts.append(post)
        else:
            log("DROPPED a post after 3 tries:", errs)
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
    picks = plan(research())
    posts = write_all(picks)
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
