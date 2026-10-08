"""Add finished long-form guides to the Build with Vish site (clone at /home/user/buildwithvish).

    python scripts/site_guide.py <slug> [...] [--tools=claude,multi]

Each guide must already pass `node tools/longform/check.js <slug>` in the site repo (written to tools/longform/out).
Copies the page and its meta into src/long/guides, adds a GUIDES entry (stub body; build.py swaps in the long page)
and rebuilds site/. Commit and push the site repo afterwards. The guide's public link is #read-<slug>.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SITE = Path("/home/user/buildwithvish")
LF = SITE / "tools" / "longform"
TOOLS = {"youtube-research-with-claude": ["claude"], "creator-campaign-hq-in-claude": ["claude"], "get-cited-by-ai-answers": ["claude", "multi"]}


def add(slug: str) -> str:
    r = subprocess.run(["node", str(LF / "check.js"), slug], capture_output=True, text=True)
    if "PASS" not in r.stdout:
        return f"{slug}: check.js did not pass, not added\n{r.stdout[-600:]}"
    for ext in (".html", ".meta.json"):
        shutil.copy(LF / "out" / f"{slug}{ext}", SITE / "src" / "long" / "guides" / f"{slug}{ext}")
    meta = json.loads((LF / "out" / f"{slug}.meta.json").read_text())
    typ = json.loads((LF / "seed" / f"{slug}.json").read_text())["type"]
    f = SITE / "src" / "content-guides.js"
    js = f.read_text()
    if f'slug: "{slug}"' in js:
        return f"{slug}: page updated (entry already listed)"
    ranks = [int(x) for p in (SITE / "src").glob("content-*.js") for x in re.findall(r"rank: (\d+)", p.read_text())]
    start = js.index("const GUIDES = [")
    end = js.index("\n];", start)
    q = lambda s: json.dumps(s, ensure_ascii=False)  # noqa: E731
    entry = (f'\n\n{{ slug: {q(slug)}, type: {q(typ)}, tools: {q(TOOLS.get(slug, ["claude"]))}, level: "Intermediate", mins: 15, rank: {max(ranks) + 1},\n'
             f'  title: {q(meta["title"])},\n  excerpt: {q(meta["excerpt"])},\n  body: `<p>{meta["excerpt"].replace("`", "")}</p>` }},')
    f.write_text(js[:end].rstrip().rstrip(",") + "," + entry.rstrip(",") + js[end:])
    return f"{slug}: added -> https://buildwithvish.netlify.app/#read-{slug}"


if __name__ == "__main__":
    for s in [a for a in sys.argv[1:] if not a.startswith("--")]:
        print(add(s))
    r = subprocess.run([sys.executable, str(SITE / "src" / "build.py")], capture_output=True, text=True, cwd=SITE)
    print("build:", "ok" if r.returncode == 0 else r.stderr[-800:])
