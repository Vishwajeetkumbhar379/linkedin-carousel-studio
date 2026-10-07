"""freellm summarize src/ --focus "auth flow"
freellm ask "where are retries configured?" src/ config/
freellm find "rate limiting" .
freellm draft "LinkedIn post about X" --from notes.md
freellm bulk "Classify sentiment: positive/negative/neutral" reviews.txt out.txt
freellm providers | stats | mcp
"""
from __future__ import annotations

import argparse
import sys

from . import tasks
from .providers import LLMError, available
from .safety import Blocked, allowed_dirs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="freellm", description="Offload bulk reading/drafting to free LLMs.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("summarize", help="Summarize files, folders, globs or URLs")
    s.add_argument("sources", nargs="+")
    s.add_argument("--focus", default="")
    s.add_argument("--words", type=int, default=250)
    a = sub.add_parser("ask", help="Answer a question from files, folders or URLs")
    a.add_argument("question")
    a.add_argument("sources", nargs="+")
    f = sub.add_parser("find", help="Locate where something is handled in a codebase")
    f.add_argument("question")
    f.add_argument("path", nargs="?", default=".")
    d = sub.add_parser("draft", help="Write a first draft")
    d.add_argument("instructions")
    d.add_argument("--from", dest="sources", nargs="*", default=[])
    d.add_argument("--words", type=int, default=400)
    b = sub.add_parser("bulk", help="Apply an instruction to every line of a file")
    b.add_argument("instruction")
    b.add_argument("input")
    b.add_argument("output")
    sub.add_parser("providers", help="Show which free providers have keys, and the allowed folders")
    sub.add_parser("stats", help="Show how much reading has been kept out of Claude")
    sub.add_parser("mcp", help="Run as an MCP server over stdio (for Claude Code)")
    x = ap.parse_args(argv)
    log = lambda m: print(m, file=sys.stderr)  # noqa: E731
    try:
        if x.cmd == "summarize":
            print(tasks.summarize(x.sources, x.focus, x.words))
        elif x.cmd == "ask":
            print(tasks.ask(x.question, x.sources))
        elif x.cmd == "find":
            print(tasks.find(x.question, x.path))
        elif x.cmd == "draft":
            print(tasks.draft(x.instructions, x.sources, x.words))
        elif x.cmd == "bulk":
            print(tasks.bulk(x.instruction, x.input, x.output))
        elif x.cmd == "providers":
            ps = available(log)
            print("Providers (in order):\n" + ("\n".join(f"  {p.name:<11} {p.model}" for p in ps) or "  none - set a key"))
            dirs = allowed_dirs()
            print("Allowed folders:\n" + ("\n".join(f"  {d}" for d in dirs) or "  none - set FREELLM_ALLOW_DIRS"))
        elif x.cmd == "stats":
            print(tasks.stats())
        else:
            from .mcp_server import serve
            serve()
    except (LLMError, Blocked) as e:
        print(f"freellm: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
