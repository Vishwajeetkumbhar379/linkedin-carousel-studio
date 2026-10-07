"""Minimal MCP server over stdio (newline-delimited JSON-RPC), standard library only.

Register with Claude Code:  claude mcp add free-helper -s user -- python3 -m freellm mcp
"""
from __future__ import annotations

import json
import sys
import traceback

from . import __version__, tasks
from .providers import LLMError, available
from .safety import Blocked, allowed_dirs

PROTOCOL = "2025-06-18"
SRC = {"type": "array", "items": {"type": "string"},
       "description": "Files, folders, globs (src/**/*.py) or public URLs. Local paths must be inside FREELLM_ALLOW_DIRS."}
TOOLS = [
    {"name": "free_summarize",
     "description": "Read large files/folders/logs/URLs with a FREE model and return a short summary, so the raw text "
                    "never enters your context. Use for anything over ~200 lines you only need the gist of.",
     "inputSchema": {"type": "object", "properties": {"sources": SRC, "focus": {"type": "string"},
                                                       "max_words": {"type": "integer", "default": 250}},
                     "required": ["sources"]}},
    {"name": "free_ask",
     "description": "Answer a question from large files/folders/URLs with a FREE model; returns a cited answer. "
                    "Verify anything you will act on, the free model can be wrong.",
     "inputSchema": {"type": "object", "properties": {"question": {"type": "string"}, "sources": SRC},
                     "required": ["question", "sources"]}},
    {"name": "free_find",
     "description": "Locate where something is handled in a codebase (returns path:symbol lines) using a FREE model. "
                    "Then open only those files yourself.",
     "inputSchema": {"type": "object", "properties": {"question": {"type": "string"},
                                                       "path": {"type": "string", "default": "."}},
                     "required": ["question"]}},
    {"name": "free_draft",
     "description": "Write a first draft (README, post, email, docs) with a FREE model, optionally from source files. "
                    "Polish the result yourself.",
     "inputSchema": {"type": "object", "properties": {"instructions": {"type": "string"}, "sources": SRC,
                                                       "max_words": {"type": "integer", "default": 400}},
                     "required": ["instructions"]}},
    {"name": "free_bulk",
     "description": "Apply one instruction to every line of a file (classify, translate, extract) with a FREE model "
                    "and write one result per line to output_path.",
     "inputSchema": {"type": "object", "properties": {"instruction": {"type": "string"},
                                                       "input_path": {"type": "string"},
                                                       "output_path": {"type": "string"}},
                     "required": ["instruction", "input_path", "output_path"]}},
    {"name": "free_status",
     "description": "Show configured free providers, allowed folders, and how many tokens have been kept out of Claude.",
     "inputSchema": {"type": "object", "properties": {}}},
]


def call(name: str, a: dict) -> str:
    if name == "free_summarize":
        return tasks.summarize(a["sources"], a.get("focus", ""), int(a.get("max_words", 250)))
    if name == "free_ask":
        return tasks.ask(a["question"], a["sources"])
    if name == "free_find":
        return tasks.find(a["question"], a.get("path", "."))
    if name == "free_draft":
        return tasks.draft(a["instructions"], a.get("sources") or [], int(a.get("max_words", 400)))
    if name == "free_bulk":
        return tasks.bulk(a["instruction"], a["input_path"], a["output_path"])
    if name == "free_status":
        ps = available()
        return ("Providers: " + (", ".join(f"{p.name} ({p.model})" for p in ps) or "none") +
                "\nAllowed folders: " + (", ".join(map(str, allowed_dirs())) or "none (set FREELLM_ALLOW_DIRS)") +
                "\n" + tasks.stats())
    raise ValueError(f"Unknown tool {name}")


def handle(msg: dict) -> dict | None:
    mid, method = msg.get("id"), msg.get("method")
    if mid is None:  # notification
        return None
    if method == "initialize":
        result = {"protocolVersion": msg.get("params", {}).get("protocolVersion", PROTOCOL),
                  "capabilities": {"tools": {}}, "serverInfo": {"name": "free-llm-helper", "version": __version__}}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        p = msg.get("params", {})
        try:
            result = {"content": [{"type": "text", "text": call(p.get("name"), p.get("arguments") or {})}]}
        except (LLMError, Blocked, KeyError, ValueError, OSError) as e:
            result = {"content": [{"type": "text", "text": f"free-llm-helper error: {e}"}], "isError": True}
    elif method == "ping":
        result = {}
    else:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"Method not found: {method}"}}
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def serve(stdin=sys.stdin, stdout=sys.stdout):
    for line in stdin:
        if not line.strip():
            continue
        try:
            reply = handle(json.loads(line))
        except Exception:  # noqa: BLE001 - never kill the server on one bad message
            traceback.print_exc(file=sys.stderr)
            continue
        if reply is not None:
            stdout.write(json.dumps(reply) + "\n")
            stdout.flush()
