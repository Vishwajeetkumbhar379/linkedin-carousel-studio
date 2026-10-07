"""Optional: ask an LLM (Claude, or a chain of free providers) to draft a deck as structured JSON the renderer accepts."""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request

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


UA = "linkedin-carousel-studio/0.1"  # some APIs sit behind Cloudflare, which blocks the default Python-urllib agent


class LLMError(RuntimeError):
    pass


class OpenAICompatClient:
    """Speaks the OpenAI-style chat API (Mistral, Groq, NVIDIA, Cloudflare, LLM7 all use it) but answers like
    anthropic.Anthropic().messages.create, so draft() stays provider-agnostic."""

    def __init__(self, name: str, base_url: str, api_key: str, model: str, tool_choice: str = "required",
                 timeout: int = 120):
        self.name, self.base_url, self.api_key, self.model = name, base_url.rstrip("/"), api_key, model
        self.tool_choice, self.timeout = tool_choice, timeout
        self.messages = self

    def create(self, *, system, tools, messages, max_tokens, model=None, tool_choice=None):
        body = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "system", "content": system}, *messages],
            "tools": [{"type": "function", "function": {"name": t["name"], "description": t["description"],
                                                        "parameters": t["input_schema"]}} for t in tools],
            "tool_choice": self.tool_choice,
        }
        req = urllib.request.Request(f"{self.base_url}/chat/completions", data=json.dumps(body).encode(), method="POST",
                                     headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json",
                                              "User-Agent": UA})
        for wait in (2, 5, 15, 0):  # free tiers are rate-limited: back off on 429
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    message = json.load(r)["choices"][0]["message"]
                break
            except urllib.error.HTTPError as e:
                if e.code != 429 or not wait:
                    raise LLMError(f"{self.name} {e.code}: {e.read().decode(errors='replace')[:300]}") from e
                time.sleep(wait)
            except (urllib.error.URLError, TimeoutError) as e:
                raise LLMError(f"{self.name}: {e}") from e
            except (ValueError, KeyError, IndexError) as e:
                raise LLMError(f"{self.name}: unexpected reply ({e})") from e
        try:
            args = message["tool_calls"][0]["function"]["arguments"]
            data = json.loads(args) if isinstance(args, str) else args
        except (KeyError, IndexError, TypeError, ValueError) as e:
            raise LLMError(f"{self.name}: no usable tool call in the reply") from e
        return _Msg([_Block("tool_use", data)])


class FallbackClient:
    """Tries each client in order and moves on when one fails (rate limit, no credit, timeout, bad reply)."""

    def __init__(self, clients: list, log=print):
        if not clients:
            raise LLMError("No LLM API key found. Set one of: " + ", ".join(k for p in PROVIDERS.values() for k in p["keys"][:1]))
        self.clients, self.log = list(clients), log
        self.last = None
        self.messages = self

    def drop_last(self) -> bool:
        """Give up on the provider that answered last (its drafts keep breaking the rules). True if others remain."""
        if self.last in self.clients:
            self.clients.remove(self.last)
            self.log(f"{self.last.name} keeps breaking the style rules, switching provider")
        return bool(self.clients)

    def create(self, **kw):
        errors = []
        for c in list(self.clients):
            try:
                msg = c.messages.create(**kw)
                self.last = c
                self.log(f"Drafted with {getattr(c, 'name', 'anthropic')} ({getattr(c, 'model', MODEL)})")
                return msg
            except Exception as e:  # noqa: BLE001 - any failure means: try the next provider
                errors.append(str(e))
                self.log(f"{getattr(c, 'name', c)} failed, trying next: {str(e)[:120]}")
                self.clients.remove(c)  # don't retry a broken provider on the next validation round
        raise LLMError("All providers failed:\n- " + "\n- ".join(errors))


class _Block:
    def __init__(self, type, input):
        self.type, self.input = type, input


class _Msg:
    def __init__(self, content):
        self.content = content


def _env(*names: str) -> str | None:
    return next((os.environ[n] for n in names if os.environ.get(n)), None)


def _cloudflare_url(key: str) -> str:
    account = _env("CLOUDFLARE_ACCOUNT_ID", "CLOUDFARE_ACCOUNT_ID")
    if not account:  # an account-scoped token can look its own account up
        req = urllib.request.Request("https://api.cloudflare.com/client/v4/accounts",
                                     headers={"Authorization": f"Bearer {key}", "User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            account = json.load(r)["result"][0]["id"]
    return f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/v1"


# Free providers, best quality first. "keys" lists accepted env var names (common misspellings included).
PROVIDERS = {
    "nvidia": {"keys": ["NVIDIA_API_KEY"], "url": "https://integrate.api.nvidia.com/v1", "model": "moonshotai/kimi-k3"},
    "github": {"keys": ["GITHUB_MODELS_TOKEN", "GITHUB_API_KEY"], "url": "https://models.github.ai/inference",
               "model": "openai/gpt-4.1"},
    "openrouter": {"keys": ["OPENROUTER_API_KEY"], "url": "https://openrouter.ai/api/v1",
                   "model": "nvidia/nemotron-3-super-120b-a12b:free"},
    "groq": {"keys": ["GROQ_API_KEY", "GROG_API_KEY"], "url": "https://api.groq.com/openai/v1", "model": "openai/gpt-oss-120b"},
    "cloudflare": {"keys": ["CLOUDFLARE_API_TOKEN", "CLOUDFLARE_API_KEY", "CLOUDFARE_API_KEY"], "url": _cloudflare_url,
                   "model": "@cf/meta/llama-3.3-70b-instruct-fp8-fast"},
    "zai": {"keys": ["ZAI_API_KEY", "Z_AI_API_KEY", "ZHIPU_API_KEY", "GLM_API_KEY"], "url": "https://api.z.ai/api/paas/v4",
            "model": "glm-4.5-flash"},
    "llm7": {"keys": ["LLM7_API_KEY"], "url": "https://api.llm7.io/v1", "model": "deepseek-v4-pro"},
    "mistral": {"keys": ["MISTRAL_API_KEY"], "url": "https://api.mistral.ai/v1", "model": "ministral-14b-latest",
                "tool_choice": "any"},
    "sambanova": {"keys": ["SAMBANOVA_API_KEY"], "url": "https://api.sambanova.ai/v1", "model": "gpt-oss-120b"},
}

def provider_client(name: str, model: str | None = None) -> OpenAICompatClient | None:
    p = PROVIDERS[name]
    key = _env(*p["keys"])
    if not key:
        return None
    url = p["url"](key) if callable(p["url"]) else p["url"]
    return OpenAICompatClient(name, url, key, model or p["model"], p.get("tool_choice", "required"))


def make_client(provider: str = "auto", log=print):
    """auto: Claude if ANTHROPIC_API_KEY is set, else every free provider that has a key, as a fallback chain."""
    if provider == "auto" and os.environ.get("ANTHROPIC_API_KEY"):
        provider = "anthropic"
    if provider == "anthropic":
        import anthropic

        return anthropic.Anthropic()
    if provider == "auto":
        clients = []
        for name in PROVIDERS:
            try:
                if c := provider_client(name):
                    clients.append(c)
            except Exception as e:  # noqa: BLE001 - e.g. Cloudflare account lookup failed
                log(f"Skipping {name}: {e}")
        return FallbackClient(clients, log)
    client = provider_client(provider, os.environ.get("CAROUSEL_MODEL"))
    if client is None:
        raise LLMError(f"No key for {provider}: set {PROVIDERS[provider]['keys'][0]}")
    return client


STAT = re.compile(r"(\d+(?:[.,]\d+)?)\s*(%|x\b|×|percent)", re.I)


def invented_numbers(deck: dict, notes: str) -> list[str]:
    """Percentages and multipliers (43%, 2x) in the draft whose number never appears in the notes."""
    known = set(re.findall(r"\d+(?:[.,]\d+)?", notes))
    text = json.dumps({k: deck.get(k) for k in ("caption", "slides")}, ensure_ascii=False)
    return sorted({n + u for n, u in STAT.findall(text) if n not in known})


def draft(topic: str, notes: str, author: dict, client=None, retries: int = 2, provider: str = "auto") -> dict:
    if client is None:
        client = make_client(provider)
    while True:
        try:
            return _draft_once(topic, notes, author, client, retries)
        except ValueError:
            if not (isinstance(client, FallbackClient) and client.drop_last()):
                raise


def _draft_once(topic: str, notes: str, author: dict, client, retries: int) -> dict:
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
