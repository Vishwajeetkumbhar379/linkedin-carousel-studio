"""Compact context graph of everything Vish's content engine touches, so a new session reads one small file.

Same idea and outputs as the graphify skill (.claude/skills/graphify): a knowledge graph with
EXTRACTED/INFERRED edges, communities (one per area), hub ("god") nodes, a short report and a per-area wiki.
Built without the graphify package so it runs anywhere, and every summary is written by the free LLMs in
scripts/llm.py, never by Claude.

    python scripts/context_graph.py build                 # sources from context/sources.json, writes context/
    python scripts/context_graph.py build --update        # only re-summarise files whose hash changed
    python scripts/context_graph.py build --source buildwithvish=/tmp/bwv   # point one source somewhere else
    python scripts/context_graph.py query "voice shorts"  # top matching nodes and their neighbours
    python scripts/context_graph.py path voice25.py qa.py # shortest path between two nodes

Outputs (context/): CONTEXT.md (the one file to read first), areas/<source>--<area>.md (one line per file),
graph.json (nodes + edges), cache.json (summaries keyed by content hash, makes --update cheap).
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm import chat  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "context"
TEXT = {".md", ".py", ".mjs", ".js", ".ts", ".sh", ".json", ".yml", ".yaml", ".toml", ".txt", ".html", ".css"}
SUMMARISE = {".md", ".py", ".mjs", ".js", ".ts", ".sh", ".yml", ".yaml", ".toml", ".txt"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "dist", "build", "graphify-out", "context", "frames"}
SKIP_FILES = {"package-lock.json", "LICENSE", ".gitignore", ".env", ".dev.vars"}
SKILL_DIRS = (".claude/skills", ".agents/skills")
BATCH, CHARS = 8, 2500  # files per LLM call, characters read per file
SYSTEM = ("You index a content-automation codebase for an AI agent that must find things fast. "
          "For each file give one plain line (max 22 words) saying what it does or decides, naming concrete "
          "commands, outputs and rules. No filler, no marketing words. Plus 2 to 5 lowercase topic tags.")


SECRET = re.compile(r"(sk-[\w-]{16,}|AIza[\w-]{30,}|gsk_\w{20,}|hf_\w{20,}|xox[bap]-[\w-]{10,}|gh[pousr]_\w{30,}|"
                    r"(?i:(?:api[_-]?key|token|secret|password)\s*[=:]\s*['\"]?)[\w./+-]{16,})")


def scrub(text: str) -> str:
    """Free LLMs are third parties: never send anything that looks like a credential."""
    return SECRET.sub("[REDACTED]", text)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()[:16]


def frontmatter(text: str) -> dict:
    m = re.match(r"---\s*\n(.*?)\n---", text, re.S)
    out = {}
    for line in (m.group(1).splitlines() if m else []):
        k, _, v = line.partition(":")
        if v.strip():
            out[k.strip()] = v.strip().strip("\"'")
    return out


def walk(src: dict) -> tuple[list[dict], list[dict], list[dict]]:
    """Files, skills and output folders of one source. Each file: rel path, area, text."""
    root, name = Path(src["path"]), src["name"]
    only, exclude = src.get("only_ext"), [re.compile(p) for p in src.get("exclude", [])]
    files, skills, outputs = [], [], []
    for sd in SKILL_DIRS:
        for sk in sorted((root / sd).glob("*/SKILL.md")) if (root / sd).is_dir() else []:
            fm = frontmatter(sk.read_text("utf-8", "replace"))
            skills.append({"name": sk.parent.name, "dir": sd, "desc": fm.get("description", "")[:220]})
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root).as_posix()
        parts = rel.split("/")
        if any(x in SKIP_DIRS for x in parts) or any(rel.startswith(sd + "/") for sd in SKILL_DIRS):
            continue
        if any(e.search(rel) for e in exclude):
            continue
        if src.get("outputs") and parts[0] == src["outputs"]:
            if p.is_dir() and len(parts) == 3 or (p.is_dir() and len(parts) == 2 and not any(c.is_dir() for c in p.iterdir())):
                outputs.append({"rel": rel})
            continue
        if not p.is_file() or p.name in SKIP_FILES or p.suffix not in TEXT or (only and p.suffix not in only):
            continue
        if p.stat().st_size > 400_000:
            continue
        area = parts[0] if len(parts) > 1 else "(root)"
        if area in src.get("deep", []) and len(parts) > 2:
            area = f"{parts[0]}/{parts[1]}"
        files.append({"id": f"{name}:{rel}", "source": name, "rel": rel, "area": area, "ext": p.suffix,
                      "text": p.read_text("utf-8", "replace")})
    return files, skills, outputs


def summarise(files: list[dict], cache: dict) -> None:
    todo = [f for f in files if f["ext"] in SUMMARISE and cache.get(f["id"], {}).get("h") != f["h"]]
    for f in files:  # data and markup files get a cheap structural line instead of an LLM call
        if f["ext"] not in SUMMARISE and cache.get(f["id"], {}).get("h") != f["h"]:
            cache[f["id"]] = {"h": f["h"], "s": structural(f), "t": [f["ext"].lstrip(".")]}
    batches = [todo[i:i + BATCH] for i in range(0, len(todo), BATCH)]
    print(f"[graph] {len(files)} files, {len(todo)} to summarise in {len(batches)} free-LLM calls", file=sys.stderr)

    def run(batch: list[dict]) -> None:
        body = "\n\n".join(f"### FILE {f['id']}\n{scrub(f['text'][:CHARS])}" for f in batch)
        prompt = (f"{body}\n\nReturn a JSON object mapping each FILE id exactly as written to "
                  '{"s": "<one line>", "t": ["tag", ...]}.')
        for _ in range(2):
            try:
                raw = chat(prompt, system=SYSTEM, temperature=0.2, json=True)
                data = json.loads(re.search(r"\{.*\}", raw, re.S).group(0))
                break
            except Exception as e:  # noqa: BLE001
                print(f"[graph] batch retry: {str(e)[:120]}", file=sys.stderr)
                data = {}
        for f in batch:
            d = data.get(f["id"]) or {}
            if isinstance(d, dict) and d.get("s"):
                cache[f["id"]] = {"h": f["h"], "s": str(d["s"]).strip(), "t": [str(t).lower() for t in d.get("t", [])][:5]}
            else:  # leave unstamped so the next --update retries it
                cache[f["id"]] = {"h": "", "s": structural(f), "t": []}

    with ThreadPoolExecutor(4) as ex:
        list(ex.map(run, batches))


def structural(f: dict) -> str:
    t = f["text"]
    if f["ext"] == ".json":
        try:
            d = json.loads(t)
            keys = list(d)[:8] if isinstance(d, dict) else [f"list of {len(d)}"]
            return "JSON: " + ", ".join(map(str, keys))
        except Exception:  # noqa: BLE001
            return "JSON data"
    m = re.search(r"<title>(.*?)</title>", t, re.S) or re.search(r"^#\s+(.+)$", t, re.M)
    return (m.group(1).strip()[:120] if m else f"{f['ext'].lstrip('.')} file")


def edges_for(files: list[dict]) -> list[dict]:
    """EXTRACTED: python/js imports and explicit path mentions. INFERRED: unique basename mentions."""
    by_rel = {(f["source"], f["rel"]): f["id"] for f in files}
    by_mod = {(f["source"], Path(f["rel"]).stem): f["id"] for f in files if f["ext"] == ".py"}
    names = Counter(Path(f["rel"]).name for f in files)
    by_name = {Path(f["rel"]).name: f["id"] for f in files if names[Path(f["rel"]).name] == 1}
    distinct = {n for n in by_name if len(n) >= 8 and n not in {"README.md", "SKILL.md", "index.html", "package.json"}}
    name_re = re.compile(r"(?<![\w/.-])(" + "|".join(sorted(map(re.escape, distinct), key=len, reverse=True)) + r")(?![\w-])") if distinct else None
    path_re = re.compile(r"[\w.-]+(?:/[\w.-]+)+\.\w{1,5}")
    out, seen = [], set()

    def add(a, b, rel, conf):
        if a != b and (a, b, rel) not in seen:
            seen.add((a, b, rel))
            out.append({"source": a, "target": b, "relation": rel, "confidence": conf})

    for f in files:
        if f["ext"] == ".py":
            try:
                for n in ast.walk(ast.parse(f["text"])):
                    mods = [a.name for a in n.names] if isinstance(n, ast.Import) else [n.module or ""] if isinstance(n, ast.ImportFrom) else []
                    for m in mods:
                        tgt = by_mod.get((f["source"], m.split(".")[-1])) or by_mod.get((f["source"], m.split(".")[0]))
                        if tgt:
                            add(f["id"], tgt, "imports", "EXTRACTED")
            except SyntaxError:
                pass
        if f["ext"] in {".js", ".mjs", ".ts"}:
            for m in re.findall(r"""(?:from|require\()\s*['"](\.{1,2}/[^'"]+)['"]""", f["text"]):
                p = (Path(f["rel"]).parent / m).as_posix()
                for cand in (p, p + ".js", p + ".mjs", p + ".ts"):
                    norm = Path(cand).as_posix()
                    while "/../" in norm:
                        norm = re.sub(r"[^/]+/\.\./", "", norm, count=1)
                    if (f["source"], norm.lstrip("./")) in by_rel:
                        add(f["id"], by_rel[(f["source"], norm.lstrip("./"))], "imports", "EXTRACTED")
        for m in path_re.findall(f["text"]):
            tgt = by_rel.get((f["source"], m.lstrip("./")))
            if tgt:
                add(f["id"], tgt, "references", "EXTRACTED")
        for m in re.findall(r"\[\[([\w-]+)\]\]", f["text"]):  # memory wikilinks
            tgt = by_rel.get((f["source"], m + ".md"))
            if tgt:
                add(f["id"], tgt, "links", "EXTRACTED")
        if name_re:
            for m in set(name_re.findall(f["text"][:60_000])):
                add(f["id"], by_name[m], "mentions", "INFERRED")
    return out


def area_summaries(areas: dict, cache: dict, old: dict) -> dict:
    """One line per area from its file lines (free LLM), reused when the file lines did not change."""
    res = {}

    def run(item):
        key, ids = item
        lines = "\n".join(f"- {i.split(':', 1)[1]}: {cache[i]['s']}" for i in ids[:60])
        h = sha(lines)
        if old.get(key, {}).get("h") == h:
            res[key] = old[key]
            return
        try:
            s = chat(f"Files in area '{key}':\n{lines}\n\nIn ONE line of at most 18 words say what this area is for. Start with a verb. No preamble, no hashtags, no area name.",
                     system=SYSTEM, temperature=0.2).strip().splitlines()[0]
        except Exception as e:  # noqa: BLE001
            print(f"[graph] area {key}: {str(e)[:100]}", file=sys.stderr)
            s, h = f"{len(ids)} files", ""
        res[key] = {"h": h, "s": re.sub(r"\s*(#\w+\s*)+$|\s*tags?:.*$", "", s.strip("-* "), flags=re.I)}

    with ThreadPoolExecutor(4) as ex:
        list(ex.map(run, areas.items()))
    return res


def build(update: bool, overrides: list[str]) -> None:
    cfg = json.loads((OUT / "sources.json").read_text())
    paths = dict(o.split("=", 1) for o in overrides)
    for src in cfg["sources"]:
        src["path"] = str((ROOT / paths.get(src["name"], src["path"])).expanduser().resolve())
    cache_path = OUT / "cache.json"
    cache = json.loads(cache_path.read_text()) if update and cache_path.exists() else {}
    files, skills, outputs = [], {}, {}
    for src in cfg["sources"]:
        if not Path(src["path"]).is_dir():
            print(f"[graph] skip {src['name']}: {src['path']} not found", file=sys.stderr)
            continue
        f, s, o = walk(src)
        files += f
        skills[src["name"]], outputs[src["name"]] = s, o
    for f in files:
        f["h"] = sha(f["text"])
    summarise(files, cache)
    ids = {f["id"] for f in files}
    cache = {k: v for k, v in cache.items() if k in ids or k.startswith("@area:")}
    edges = edges_for(files)
    deg = Counter()
    for e in edges:
        deg[e["source"]] += 1
        deg[e["target"]] += 2  # being pointed at matters more than pointing
    areas = defaultdict(list)
    for f in files:
        areas[f"{f['source']}/{f['area']}"].append(f["id"])
    for k in areas:
        areas[k].sort(key=lambda i: -deg[i])
    old = {k[6:]: v for k, v in cache.items() if k.startswith("@area:")}
    asum = area_summaries(areas, cache, old)
    for k, v in asum.items():
        cache["@area:" + k] = v

    nodes = [{"id": f["id"], "label": f["rel"], "type": "file", "source": f["source"], "community": f"{f['source']}/{f['area']}",
              "summary": cache[f["id"]]["s"], "tags": cache[f["id"]]["t"], "degree": deg[f["id"]]} for f in files]
    for src, sk in skills.items():
        for s in sk:
            nodes.append({"id": f"{src}:skill:{s['name']}", "label": s["name"], "type": "skill", "source": src,
                          "community": f"{src}/skills", "summary": s["desc"], "tags": ["skill"], "degree": 0})
    for src, os_ in outputs.items():
        for o in os_:
            nodes.append({"id": f"{src}:{o['rel']}", "label": o["rel"], "type": "output", "source": src,
                          "community": f"{src}/outputs", "summary": "", "tags": ["output"], "degree": 0})
    OUT.mkdir(exist_ok=True)
    (OUT / "graph.json").write_text(json.dumps({"built": date.today().isoformat(), "nodes": nodes, "edges": edges,
                                                 "communities": {k: v["s"] for k, v in asum.items()}}, indent=1, ensure_ascii=False))
    cache_path.write_text(json.dumps(cache, indent=0, ensure_ascii=False, sort_keys=True))
    write_markdown(cfg, files, skills, outputs, areas, asum, cache, deg, edges)
    print(f"[graph] {len(nodes)} nodes, {len(edges)} edges, {len(areas)} areas -> {OUT.relative_to(ROOT)}/CONTEXT.md", file=sys.stderr)


def slug(s: str) -> str:
    return re.sub(r"[^\w.-]+", "--", s).strip("-")


def write_markdown(cfg, files, skills, outputs, areas, asum, cache, deg, edges) -> None:
    (OUT / "areas").mkdir(exist_ok=True)
    for old in (OUT / "areas").glob("*.md"):
        old.unlink()
    out_edges = defaultdict(list)
    for e in edges:
        out_edges[e["source"]].append(e["target"])
    by_src = defaultdict(list)
    for k in sorted(areas):
        by_src[k.split("/", 1)[0]].append(k)
    hubs = [i for i, _ in deg.most_common(40) if not i.endswith(".json")][:12]
    L = [f"# Context map (built {date.today().isoformat()} by `scripts/context_graph.py`)", "",
         "Read this first instead of the repos. Each area links to a one-line-per-file page in `context/areas/`.",
         "Find anything: `python scripts/context_graph.py query \"<words>\"`. Rebuild after big changes: "
         "`python scripts/context_graph.py build --update` (free LLMs only).", ""]
    L += [cfg.get("preamble", "").strip(), ""] if cfg.get("preamble") else []
    L += ["## Sources", ""]
    for s in cfg["sources"]:
        if s["name"] in by_src:
            L.append(f"- **{s['name']}**: {s.get('about', '')} ({sum(len(areas[a]) for a in by_src[s['name']])} files, "
                     f"{len(skills.get(s['name'], []))} skills, {len(outputs.get(s['name'], []))} output folders)")
    L += ["", "## Hub files (most connected)", ""]
    L += [f"- `{h}`: {cache[h]['s']}" for h in hubs if h in cache]
    for src, keys in by_src.items():
        L += ["", f"## {src}", ""]
        for k in keys:
            ids, page = areas[k], f"areas/{slug(k)}.md"
            top = ", ".join(dict.fromkeys(f"`{Path(i.split(':', 1)[1]).name}`" for i in ids[:3]))
            L.append(f"- [{k.split('/', 1)[1]}]({page}) ({len(ids)}): {asum[k]['s']} Key: {top}")
            P = [f"# {k}", "", asum[k]["s"], ""]
            for i in sorted(ids, key=lambda i: i):
                links = ", ".join(Path(t.split(':', 1)[1]).name for t in out_edges[i][:6])
                P.append(f"- `{i.split(':', 1)[1]}`: {cache[i]['s']}" + (f" (uses {links})" if links else ""))
            (OUT / page).write_text("\n".join(P) + "\n")
        if skills.get(src):
            page = f"areas/{slug(src)}--installed-skills.md"
            names = ", ".join(s["name"] for s in skills[src])
            L.append(f"- [installed skills]({page}) ({len(skills[src])}, name + description per skill): {names[:300]}{'...' if len(names) > 300 else ''}")
            (OUT / page).write_text("\n".join([f"# {src} skills", ""] + [f"- **{s['name']}** ({s['dir']}): {s['desc']}" for s in skills[src]]) + "\n")
        if outputs.get(src):
            page = f"areas/{slug(src)}--outputs.md"
            groups = Counter(o["rel"].split("/")[1] for o in outputs[src])
            L.append(f"- [outputs]({page}) ({len(outputs[src])} folders): " + ", ".join(f"{g} ({n})" for g, n in groups.most_common(12)))
            (OUT / page).write_text("\n".join([f"# {src} rendered outputs", ""] + [f"- `{o['rel']}`" for o in outputs[src]]) + "\n")
    (OUT / "CONTEXT.md").write_text("\n".join(L) + "\n")


def load() -> dict:
    return json.loads((OUT / "graph.json").read_text())


def query(q: str, n: int = 12) -> None:
    g = load()
    words = [w for w in re.findall(r"\w+", q.lower()) if len(w) > 2]
    nbrs = defaultdict(set)
    for e in g["edges"]:
        nbrs[e["source"]].add(e["target"])
        nbrs[e["target"]].add(e["source"])

    def score(nd):
        hay = f"{nd['label']} {nd['summary']} {' '.join(nd['tags'])} {nd['community']}".lower()
        return sum(hay.count(w) * (3 if w in nd["label"].lower() else 1) for w in words) + (0.01 * nd["degree"] if words else 0)
    ranked = sorted((nd for nd in g["nodes"] if score(nd) >= 1), key=score, reverse=True)[:n]
    ids = {nd["id"]: nd for nd in g["nodes"]}
    for nd in ranked:
        print(f"{nd['id']}  [{nd['type']}]\n    {nd['summary']}")
        near = sorted(nbrs[nd["id"]], key=lambda i: -ids[i]["degree"])[:5]
        if near:
            print("    linked: " + ", ".join(i.split(":", 1)[1] for i in near))


def path(a: str, b: str) -> None:
    g = load()
    nbrs = defaultdict(set)
    for e in g["edges"]:
        nbrs[e["source"]].add(e["target"])
        nbrs[e["target"]].add(e["source"])
    find = lambda s: next((nd["id"] for nd in g["nodes"] if nd["label"].endswith(s) or nd["id"] == s), None)  # noqa: E731
    s, t = find(a), find(b)
    if not s or not t:
        sys.exit(f"not found: {a if not s else b}")
    prev, dq = {s: None}, deque([s])
    while dq:
        u = dq.popleft()
        if u == t:
            break
        for v in nbrs[u]:
            if v not in prev:
                prev[v] = u
                dq.append(v)
    if t not in prev:
        sys.exit("no path")
    chain = [t]
    while prev[chain[-1]]:
        chain.append(prev[chain[-1]])
    print(" -> ".join(reversed(chain)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "query", "path"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--update", action="store_true")
    ap.add_argument("--source", action="append", default=[], help="name=path, overrides a path in context/sources.json")
    a = ap.parse_args()
    if a.cmd == "build":
        build(a.update, a.source)
    elif a.cmd == "query":
        query(" ".join(a.args))
    else:
        path(*a.args[:2])
