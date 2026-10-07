"""Optional: ask an LLM (Claude, or Mistral's free tier) to draft a deck as structured JSON the renderer accepts."""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request

from .templates import validate

MODEL = os.environ.get("CAROUSEL_MODEL", "claude-sonnet-4-5")
MISTRAL_MODEL = os.environ.get("CAROUSEL_MODEL", "ministral-14b-latest")  # strongest model on the free tier
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"

SLIDE = {
    "type": "object",
    "properties": {
        "type": {"enum": ["cover", "point", "stat", "list", "compare", "cta"]},
        "badge": {"type": "string"},
        "title": {"type": "string", "description": "Wrap one key word in *asterisks* for the accent colour"},
        "subtitle": {"type": "string"},
        "body": {"type": "string", "description": "Max 45 words"},
        "label": {"type": "string"},
        "value": {"type": "string"},
        "emoji": {"type": "string"},
        "items": {"type": "array", "items": {"type": "string"}},
        "left": {"type": "object", "properties": {"label": {"type": "string"}, "items": {"type": "array", "items": {"type": "string"}}}},
        "right": {"type": "object", "properties": {"label": {"type": "string"}, "items": {"type": "array", "items": {"type": "string"}}}},
    },
    "required": ["type", "title"],
}
TOOL = {
    "name": "build_deck",
    "description": "Return a LinkedIn carousel as slides.",
    "input_schema": {
        "type": "object",
        "properties": {"slug": {"type": "string"}, "caption": {"type": "string"}, "slides": {"type": "array", "items": SLIDE}},
        "required": ["slug", "caption", "slides"],
    },
}
SYSTEM = """You write LinkedIn carousels for a creator-marketing professional.
Rules: 6-9 slides. Slide 1 is a cover with a hook under 10 words. Last slide is a CTA asking people to save the post.
One idea per slide, max 45 words of body. Rare, high-signal knowledge, not generic advice.
At most 2 emojis in the whole deck. Never invent statistics: if you use a number, it must come from the notes provided.
Caption: punchy first line, a short arrow list (→), then a save CTA and one open question."""


class MistralClient:
    """Speaks Mistral's chat API but answers like anthropic.Anthropic().messages.create, so draft() stays provider-agnostic."""

    def __init__(self, api_key: str | None = None, model: str = MISTRAL_MODEL):
        self.api_key = api_key or os.environ["MISTRAL_API_KEY"]
        self.model = model
        self.messages = self

    def create(self, *, system, tools, messages, max_tokens, model=None, tool_choice=None):
        body = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "system", "content": system}, *messages],
            "tools": [{"type": "function", "function": {"name": t["name"], "description": t["description"],
                                                        "parameters": t["input_schema"]}} for t in tools],
            "tool_choice": "any",
        }
        req = urllib.request.Request(MISTRAL_URL, data=json.dumps(body).encode(), method="POST",
                                     headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"})
        for wait in (2, 5, 15, 0):  # free tier is rate-limited: back off on 429
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    call = json.load(r)["choices"][0]["message"]["tool_calls"][0]["function"]
                break
            except urllib.error.HTTPError as e:
                if e.code != 429 or not wait:
                    raise RuntimeError(f"Mistral API {e.code}: {e.read().decode(errors='replace')}") from e
                time.sleep(wait)
        args = call["arguments"]
        return _Msg([_Block("tool_use", json.loads(args) if isinstance(args, str) else args)])


class _Block:
    def __init__(self, type, input):
        self.type, self.input = type, input


class _Msg:
    def __init__(self, content):
        self.content = content


def make_client(provider: str = "auto"):
    if provider == "auto":
        provider = "anthropic" if os.environ.get("ANTHROPIC_API_KEY") or not os.environ.get("MISTRAL_API_KEY") else "mistral"
    if provider == "mistral":
        return MistralClient()
    import anthropic

    return anthropic.Anthropic()


STAT = re.compile(r"(\d+(?:[.,]\d+)?)\s*(%|x\b|×|percent)", re.I)


def invented_numbers(deck: dict, notes: str) -> list[str]:
    """Percentages and multipliers (43%, 2x) in the draft whose number never appears in the notes."""
    known = set(re.findall(r"\d+(?:[.,]\d+)?", notes))
    text = json.dumps({k: deck.get(k) for k in ("caption", "slides")}, ensure_ascii=False)
    return sorted({n + u for n, u in STAT.findall(text) if n not in known})


def draft(topic: str, notes: str, author: dict, client=None, retries: int = 2, provider: str = "auto") -> dict:
    if client is None:
        client = make_client(provider)
    prompt = f"Topic: {topic}\n\nMy notes and real numbers (use only these):\n{notes}"
    for _ in range(retries + 1):
        msg = client.messages.create(model=MODEL, max_tokens=3000, system=SYSTEM, tools=[TOOL],
                                     tool_choice={"type": "tool", "name": "build_deck"},
                                     messages=[{"role": "user", "content": prompt}])
        deck = dict(next(b for b in msg.content if getattr(b, "type", "") == "tool_use").input)
        deck["author"] = author
        problems = validate(deck)
        if fake := invented_numbers(deck, notes):
            problems.append(f"These statistics are not in my notes, remove them: {', '.join(fake)}")
        if not problems:
            return deck
        prompt += "\n\nYour last draft broke these rules, fix them:\n- " + "\n- ".join(problems)
    raise ValueError("Draft still breaks the style rules: " + "; ".join(problems))
