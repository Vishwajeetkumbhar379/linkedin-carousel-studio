"""Pull fresh items from every feed in sources.json into research/daily/YYYY-MM-DD.json.

Stdlib only so it runs anywhere (GitHub Actions, a laptop, a Claude routine).
Every item keeps its source URL and publish date; anything older than its window is dropped here.
"""
from __future__ import annotations

import datetime as dt
import email.utils
import html
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((Path(__file__).parent / "sources.json").read_text())
WINDOW = {"news": 14, "tool": 30}
UA = {"User-Agent": "build-with-vish-research/0.1 (+https://github.com/Vishwajeetkumbhar379)"}


def get(url: str) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25).read()


def parse_date(s: str | None) -> dt.date | None:
    if not s:
        return None
    try:
        return email.utils.parsedate_to_datetime(s).date()
    except (TypeError, ValueError):
        pass
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return dt.date(*map(int, m.groups()))
    m = re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* (\d{1,2}), (20\d\d)", s)
    if m:
        return dt.datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)}", "%b %d %Y").date()
    return None


def rss(feed: dict) -> list[dict]:
    root = ET.fromstring(get(feed["url"]))
    out = []
    for it in root.iter():
        tag = it.tag.split("}")[-1]
        if tag not in ("item", "entry"):
            continue
        f = {c.tag.split("}")[-1]: (c.text or c.attrib.get("href", "")) for c in it}
        link = f.get("link") or next((c.attrib.get("href") for c in it if c.tag.endswith("link")), "")
        out.append({"title": html.unescape((f.get("title") or "").strip()), "url": link,
                    "date": str(parse_date(f.get("pubDate") or f.get("published") or f.get("updated") or f.get("date"))),
                    "summary": re.sub("<[^>]+>", "", html.unescape(f.get("description") or f.get("summary") or ""))[:400]})
    return out


def hn(feed: dict, since: dt.date) -> list[dict]:
    q = urllib.parse.quote(feed["query"])
    ts = int(dt.datetime.combine(since, dt.time()).timestamp())
    data = json.loads(get(f"https://hn.algolia.com/api/v1/search?query={q}&tags=story&numericFilters=created_at_i>{ts},points>50"))
    return [{"title": h["title"], "url": h.get("url") or f"https://news.ycombinator.com/item?id={h['objectID']}",
             "date": h["created_at"][:10], "summary": f"{h['points']} points, {h.get('num_comments', 0)} comments on HN"} for h in data["hits"]]


def reddit(feed: dict) -> list[dict]:
    data = json.loads(get(f"https://www.reddit.com/r/{feed['sub']}/top.json?t=week&limit=15"))
    return [{"title": c["data"]["title"], "url": "https://www.reddit.com" + c["data"]["permalink"],
             "date": str(dt.datetime.fromtimestamp(c["data"]["created_utc"], dt.timezone.utc).date()),
             "summary": f"{c['data']['score']} upvotes"} for c in data["data"]["children"]]


def github(feed: dict, since: dt.date) -> list[dict]:
    q = urllib.parse.quote(feed["query"].format(since=since.isoformat()))
    data = json.loads(get(f"https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page=15"))
    return [{"title": f"{r['full_name']}: {r.get('description') or ''}", "url": r["html_url"], "date": r["created_at"][:10],
             "summary": f"{r['stargazers_count']} stars, licence {(r.get('license') or {}).get('spdx_id')}"} for r in data["items"]]


def html_links(feed: dict) -> list[dict]:
    page = get(feed["url"]).decode("utf-8", "ignore")
    out = []
    for href, text in re.findall(r'<a[^>]+href="([^"]*' + re.escape(feed["match"]) + r'[^"]+)"[^>]*>(.*?)</a>', page, re.S)[:30]:
        title = re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", text)).strip()
        if title:
            d = parse_date(title)
            out.append({"title": title, "url": urllib.parse.urljoin(feed["url"], href), "date": str(d), "summary": "" if d else "date: open the page (listing has none)"})
    return out


def main(today: dt.date) -> Path:
    items, errors = [], []
    for f in CFG["feeds"]:
        since = today - dt.timedelta(days=WINDOW[f["kind"]])
        try:
            got = {"rss": lambda: rss(f), "hn": lambda: hn(f, since), "reddit": lambda: reddit(f),
                   "github": lambda: github(f, since), "html_links": lambda: html_links(f)}[f["type"]]()
        except Exception as e:  # noqa: BLE001 - one dead feed must not stop the run
            errors.append({"feed": f["name"], "error": str(e)[:160]})
            continue
        for it in got:
            d = dt.date.fromisoformat(it["date"]) if it["date"] not in ("None", "") else None
            if d and d < since:
                continue
            text = (it["title"] + " " + it["summary"]).lower()
            if any(k.lower() in text for k in CFG["keywords_drop"]):
                continue
            it.update(source=f["name"], kind=f["kind"], fresh=bool(d), boost=sum(k.lower() in text for k in CFG["keywords_boost"]))
            items.append(it)
    items.sort(key=lambda x: (x["boost"], x["date"]), reverse=True)
    out = ROOT / "research" / "daily" / f"{today}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"date": str(today), "items": items, "errors": errors}, indent=1, ensure_ascii=False))
    print(f"{len(items)} fresh items, {len(errors)} feeds failed -> {out}")
    return out


if __name__ == "__main__":
    main(dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date.today())
