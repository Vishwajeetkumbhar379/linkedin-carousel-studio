"""carousel render examples/creator-contract-checks.json --out out/
carousel draft "topic" --notes notes.txt   (needs ANTHROPIC_API_KEY or MISTRAL_API_KEY)
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .render import load, render


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="carousel")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render", help="Render a deck JSON to PNGs and a PDF")
    r.add_argument("deck", type=Path)
    r.add_argument("--out", type=Path, default=Path("out"))
    d = sub.add_parser("draft", help="Let an LLM draft a deck JSON from a topic and your notes")
    d.add_argument("topic")
    d.add_argument("--notes", type=Path, required=True)
    d.add_argument("--name", default="Your Name")
    d.add_argument("--handle", default="@yourhandle")
    d.add_argument("--out", type=Path, default=Path("deck.json"))
    d.add_argument("--provider", choices=["auto", "anthropic", "mistral"], default="auto",
                   help="auto = Claude if ANTHROPIC_API_KEY is set, else Mistral")
    a = ap.parse_args(argv)
    if a.cmd == "render":
        pdf = render(load(a.deck), a.out)
        print(f"Rendered {pdf} and PNG slides in {a.out}/")
    else:
        from .ai import draft

        deck = draft(a.topic, a.notes.read_text(encoding="utf-8"), {"name": a.name, "handle": a.handle},
                     provider=a.provider)
        a.out.write_text(json.dumps(deck, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Draft saved to {a.out}. Review it, then: carousel render {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
