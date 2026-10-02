"""Optional: ask Claude to draft a deck from a topic, as structured JSON that the renderer accepts."""
from __future__ import annotations

import os

from .templates import validate

MODEL = os.environ.get("CAROUSEL_MODEL", "claude-sonnet-4-5")

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


def draft(topic: str, notes: str, author: dict, client=None, retries: int = 1) -> dict:
    if client is None:
        import anthropic

        client = anthropic.Anthropic()
    prompt = f"Topic: {topic}\n\nMy notes and real numbers (use only these):\n{notes}"
    for _ in range(retries + 1):
        msg = client.messages.create(model=MODEL, max_tokens=3000, system=SYSTEM, tools=[TOOL],
                                     tool_choice={"type": "tool", "name": "build_deck"},
                                     messages=[{"role": "user", "content": prompt}])
        deck = dict(next(b for b in msg.content if getattr(b, "type", "") == "tool_use").input)
        deck["author"] = author
        problems = validate(deck)
        if not problems:
            return deck
        prompt += "\n\nYour last draft broke these rules, fix them:\n- " + "\n- ".join(problems)
    raise ValueError("Draft still breaks the style rules: " + "; ".join(problems))
