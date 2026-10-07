"""The jobs Claude hands off: read big inputs here, send only a short answer back."""
from __future__ import annotations

import glob
import html
import json
import os
import re
import time
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from .providers import UA, Chain
from .safety import SKIP_DIRS, Blocked, check_path, check_url, is_secret_file, scrub

MAX_FILE_BYTES = 1_000_000
MAX_TOTAL_CHARS = int(os.environ.get("FREELLM_MAX_CHARS", 2_000_000))
LOG = Path(os.environ.get("FREELLM_LOG", "~/.freellm/usage.jsonl")).expanduser()

SYSTEM = ("You are a precise assistant doing bulk reading for another AI. Be terse and factual. Quote file paths, "
          "function names, numbers and errors exactly. Never invent anything that is not in the input; say "
          "'not found' instead.")


@dataclass
class Bundle:
    text: str = ""
    sources: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    redactions: int = 0


def _fetch_url(url: str) -> str:
    req = urllib.request.Request(check_url(url), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read(5_000_000).decode(r.headers.get_content_charset() or "utf-8", errors="replace")
    if "<html" in raw[:2000].lower() or "<body" in raw.lower():
        raw = re.sub(r"(?is)<(script|style|noscript|svg|nav|footer|header)[^>]*>.*?</\1>", " ", raw)
        raw = re.sub(r"(?s)<[^>]+>", " ", raw)
        raw = html.unescape(raw)
    return re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n\n", raw)).strip()


def _iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
        for name in sorted(filenames):
            yield Path(dirpath) / name


def _read_file(path: Path) -> str | None:
    if path.stat().st_size > MAX_FILE_BYTES:
        return None
    data = path.read_bytes()
    if b"\0" in data[:4096]:
        return None  # binary
    return data.decode("utf-8", errors="replace")


def gather(sources: list[str]) -> Bundle:
    """Read files, folders, globs and URLs. Local paths must be inside FREELLM_ALLOW_DIRS; all text is scrubbed."""
    b = Bundle()
    parts: list[str] = []
    total = 0

    def add(label: str, text: str):
        nonlocal total
        if total >= MAX_TOTAL_CHARS:
            b.skipped.append(f"{label} (size cap)")
            return
        clean, n = scrub(text)
        b.redactions += n
        clean = clean[: MAX_TOTAL_CHARS - total]
        total += len(clean)
        parts.append(f"===== {label} =====\n{clean}")
        b.sources.append(label)

    for src in sources:
        if re.match(r"https?://", src):
            try:
                add(src, _fetch_url(src))
            except Exception as e:  # noqa: BLE001
                b.skipped.append(f"{src} ({e})")
            continue
        matches = glob.glob(os.path.expanduser(src), recursive=True) if any(c in src for c in "*?[") else [src]
        if not matches:
            b.skipped.append(f"{src} (not found)")
        for m in matches:
            try:
                p = check_path(m)
            except Blocked as e:
                b.skipped.append(str(e))
                continue
            files = list(_iter_files(p)) if p.is_dir() else [p]
            for f in files:
                if is_secret_file(f):
                    b.skipped.append(f"{f} (secrets file)")
                    continue
                try:
                    text = _read_file(f)
                except OSError as e:
                    b.skipped.append(f"{f} ({e})")
                    continue
                if text is None:
                    b.skipped.append(f"{f} (binary or >1MB)")
                elif text.strip():
                    add(str(f), text)
    b.text = "\n\n".join(parts)
    return b


def chunks(text: str, size: int) -> list[str]:
    """Split on file boundaries, then blank lines, then hard cuts, keeping each piece under `size`."""
    out, cur = [], ""
    for block in re.split(r"(?=\n===== )|\n\n", text):
        while len(block) > size:
            if cur:
                out.append(cur)
                cur = ""
            out.append(block[:size])
            block = block[size:]
        if len(cur) + len(block) + 2 > size:
            out.append(cur)
            cur = block
        else:
            cur = f"{cur}\n\n{block}" if cur else block
    if cur.strip():
        out.append(cur)
    return [c for c in out if c.strip()]


def _log(task: str, chars_in: int, chars_out: int, chain: Chain, b: Bundle):
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a") as f:
            f.write(json.dumps({"t": int(time.time()), "task": task, "chars_in": chars_in, "chars_out": chars_out,
                                "providers": sorted(set(chain.used)), "sources": b.sources[:50],
                                "redactions": b.redactions}) + "\n")
    except OSError:
        pass


def _footer(chain: Chain, b: Bundle, chars_out: int) -> str:
    bits = [f"via {', '.join(sorted(set(chain.used))) or 'none'}",
            f"read {len(b.text):,} chars -> returned {chars_out:,} (~{max(0, len(b.text) - chars_out) // 4:,} tokens kept out of Claude)"]
    if b.redactions:
        bits.append(f"{b.redactions} secret(s) redacted")
    if b.skipped:
        bits.append(f"skipped {len(b.skipped)}: " + "; ".join(b.skipped[:5]) + (" ..." if len(b.skipped) > 5 else ""))
    return "\n\n[free-llm-helper: " + " | ".join(bits) + "]"


def _map_reduce(chain: Chain, b: Bundle, map_prompt: str, reduce_prompt: str, max_tokens: int) -> str:
    pieces = chunks(b.text, chain.chunk_chars)
    if not pieces:
        return "Nothing readable in the given sources."
    if len(pieces) == 1:
        return chain.chat(SYSTEM, f"{map_prompt}\n\n{pieces[0]}", max_tokens)
    notes = [chain.chat(SYSTEM, f"{map_prompt}\n\nThis is part {i} of {len(pieces)}.\n\n{p}", max_tokens)
             for i, p in enumerate(pieces, 1)]
    joined = "\n\n".join(f"--- notes from part {i} ---\n{n}" for i, n in enumerate(notes, 1))
    while len(joined) > chain.chunk_chars:  # very large inputs: reduce in rounds
        groups = chunks(joined, chain.chunk_chars)
        joined = "\n\n".join(chain.chat(SYSTEM, f"Merge these notes, keep every concrete fact:\n\n{g}", max_tokens)
                             for g in groups)
    return chain.chat(SYSTEM, f"{reduce_prompt}\n\n{joined}", max_tokens)


def _run(task: str, sources: list[str], map_prompt: str, reduce_prompt: str, max_tokens: int = 1500,
         chain: Chain | None = None) -> str:
    chain = chain or Chain()
    b = gather(sources)
    if not b.text:
        return "Nothing could be read." + _footer(chain, b, 0)
    out = _map_reduce(chain, b, map_prompt, reduce_prompt, max_tokens)
    _log(task, len(b.text), len(out), chain, b)
    return out + _footer(chain, b, len(out))


def summarize(sources: list[str], focus: str = "", max_words: int = 250, chain: Chain | None = None) -> str:
    f = f" Focus on: {focus}." if focus else ""
    return _run("summarize", sources,
                f"Summarize this input for a developer in bullet points.{f} Keep names, paths, numbers, errors.",
                f"Combine these partial notes into one summary of at most {max_words} words.{f}", chain=chain)


def ask(question: str, sources: list[str], chain: Chain | None = None) -> str:
    return _run("ask", sources,
                f"Question: {question}\nExtract everything in this input that helps answer it, with file paths and "
                f"quotes. If nothing is relevant, reply exactly: NOTHING RELEVANT.",
                f"Question: {question}\nAnswer it from these notes only. Cite file paths. Say 'not found in the "
                f"sources' if the notes do not answer it.", chain=chain)


def find(question: str, path: str = ".", chain: Chain | None = None) -> str:
    return _run("find", [path],
                f"Where in this code is the following handled: {question}\nList matches as `path:line-or-symbol - "
                f"one-line reason`. Reply exactly NONE if nothing matches.",
                f"Merge these match lists for: {question}\nRank by relevance, drop NONE entries, max 15 lines.",
                max_tokens=1000, chain=chain)


def draft(instructions: str, sources: list[str] | None = None, max_words: int = 400, chain: Chain | None = None) -> str:
    chain = chain or Chain()
    b = gather(sources or [])
    clean_instr, n = scrub(instructions)
    b.redactions += n
    if len(b.text) > chain.chunk_chars // 2:
        context = _map_reduce(chain, b, f"Extract facts useful for this writing task: {clean_instr}",
                              "Merge these facts, keep every concrete detail.", 1500)
    else:
        context = b.text
    out = chain.chat("You are a skilled writer. Write exactly what is asked, no preamble.",
                     f"Task: {clean_instr}\nMax {max_words} words.\n\nContext:\n{context or '(none)'}", 2500)
    _log("draft", len(b.text) + len(instructions), len(out), chain, b)
    return out + _footer(chain, b, len(out))


def bulk(instruction: str, input_path: str, output_path: str, chain: Chain | None = None) -> str:
    """Apply one instruction to every non-empty line of a file; write one result per line."""
    chain = chain or Chain()
    src = check_path(input_path)
    dst = check_path(Path(output_path).expanduser().resolve().parent) / Path(output_path).name
    lines = [l for l in src.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()]
    results, redactions = [], 0
    for line in lines:
        clean, n = scrub(line)
        redactions += n
        res = chain.chat(SYSTEM + " Reply with the result only, on one line.", f"{instruction}\n\nInput: {clean}", 300)
        results.append(" ".join(res.split()))
    dst.write_text("\n".join(results) + "\n", encoding="utf-8")
    b = Bundle(text="\n".join(lines), sources=[str(src)], redactions=redactions)
    _log("bulk", len(b.text), sum(map(len, results)), chain, b)
    return f"Wrote {len(results)} results to {dst}" + _footer(chain, b, 0)


def stats() -> str:
    if not LOG.exists():
        return "No usage logged yet."
    rows = [json.loads(l) for l in LOG.read_text().splitlines() if l.strip()]
    cin, cout = sum(r["chars_in"] for r in rows), sum(r["chars_out"] for r in rows)
    by: dict[str, int] = {}
    for r in rows:
        for p in r["providers"]:
            by[p] = by.get(p, 0) + 1
    top = ", ".join(f"{k} x{v}" for k, v in sorted(by.items(), key=lambda kv: -kv[1]))
    return (f"{len(rows)} calls | read {cin:,} chars, returned {cout:,} | ~{max(0, cin - cout) // 4:,} tokens kept out "
            f"of Claude | {sum(r['redactions'] for r in rows)} secrets redacted | providers: {top or '-'}\nLog: {LOG}")
