"""Free OpenAI-compatible providers, tried in order until one answers."""
from __future__ import annotations

import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

UA = "free-llm-helper/0.1"  # several APIs sit behind Cloudflare, which blocks the default Python-urllib agent


class LLMError(RuntimeError):
    def __init__(self, msg: str, transient: bool = False):
        super().__init__(msg)
        self.transient = transient  # rate limit / timeout: worth trying this provider again later


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


# Fastest/most generous first. "keys" lists accepted env var names (common misspellings included).
# Override the order with FREELLM_ORDER=groq,nvidia,... and a model with FREELLM_MODEL_<NAME>=...
PROVIDERS: dict[str, dict] = {
    "groq": {"keys": ["GROQ_API_KEY", "GROG_API_KEY"], "url": "https://api.groq.com/openai/v1",
             "model": "openai/gpt-oss-120b", "max_chars": 16_000},  # 8k tokens/min on the free tier
    "nvidia": {"keys": ["NVIDIA_API_KEY"], "url": "https://integrate.api.nvidia.com/v1", "model": "moonshotai/kimi-k3"},
    "cloudflare": {"keys": ["CLOUDFLARE_API_TOKEN", "CLOUDFLARE_API_KEY", "CLOUDFARE_API_KEY"], "url": _cloudflare_url,
                   "model": "@cf/meta/llama-3.3-70b-instruct-fp8-fast", "max_chars": 60_000},
    "openrouter": {"keys": ["OPENROUTER_API_KEY"], "url": "https://openrouter.ai/api/v1",
                   "model": "nvidia/nemotron-3-super-120b-a12b:free"},
    "github": {"keys": ["GITHUB_MODELS_TOKEN", "GITHUB_API_KEY"], "url": "https://models.github.ai/inference",
               "model": "openai/gpt-4.1", "max_chars": 24_000},
    "mistral": {"keys": ["MISTRAL_API_KEY"], "url": "https://api.mistral.ai/v1", "model": "ministral-14b-latest"},
    "zai": {"keys": ["ZAI_API_KEY", "Z_AI_API_KEY", "ZHIPU_API_KEY", "GLM_API_KEY"], "url": "https://api.z.ai/api/paas/v4",
            "model": "glm-4.5-flash"},
    "llm7": {"keys": ["LLM7_API_KEY"], "url": "https://api.llm7.io/v1", "model": "deepseek-v4-pro"},
    "sambanova": {"keys": ["SAMBANOVA_API_KEY"], "url": "https://api.sambanova.ai/v1", "model": "gpt-oss-120b"},
}
DEFAULT_MAX_CHARS = 80_000
THINK = re.compile(r"<think>.*?</think>", re.S)


@dataclass
class Provider:
    name: str
    url: str
    key: str
    model: str
    max_chars: int = DEFAULT_MAX_CHARS
    timeout: int = 180

    def chat(self, system: str, user: str, max_tokens: int = 2000) -> str:
        body = {"model": self.model, "max_tokens": max_tokens,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        req = urllib.request.Request(f"{self.url.rstrip('/')}/chat/completions", data=json.dumps(body).encode(),
                                     method="POST", headers={"Authorization": f"Bearer {self.key}",
                                                             "Content-Type": "application/json", "User-Agent": UA})
        for wait in (3, 0):  # one short retry on 429, then let the chain move on
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    text = json.load(r)["choices"][0]["message"].get("content") or ""
                break
            except urllib.error.HTTPError as e:
                if e.code != 429 or not wait:
                    raise LLMError(f"{self.name} {e.code}: {e.read().decode(errors='replace')[:200]}",
                                   transient=e.code in (429, 500, 502, 503, 504)) from e
                time.sleep(wait)
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                raise LLMError(f"{self.name}: {e}", transient=True) from e
            except (ValueError, KeyError, IndexError, TypeError) as e:
                raise LLMError(f"{self.name}: unexpected reply ({e})") from e
        text = THINK.sub("", text).strip()
        if not text:
            raise LLMError(f"{self.name}: empty reply")
        return text


def available(log=lambda m: None) -> list[Provider]:
    order = [n.strip() for n in os.environ.get("FREELLM_ORDER", ",".join(PROVIDERS)).split(",") if n.strip() in PROVIDERS]
    out = []
    for name in order:
        p = PROVIDERS[name]
        key = _env(*p["keys"])
        if not key:
            continue
        try:
            url = p["url"](key) if callable(p["url"]) else p["url"]
        except Exception as e:  # noqa: BLE001 - e.g. Cloudflare account lookup failed
            log(f"skipping {name}: {e}")
            continue
        model = os.environ.get(f"FREELLM_MODEL_{name.upper()}", p["model"])
        out.append(Provider(name, url, key, model, p.get("max_chars", DEFAULT_MAX_CHARS)))
    return out


class Chain:
    """Calls providers in order. Rate limits and timeouts skip a provider for one call; hard failures bench it."""

    def __init__(self, providers: list[Provider] | None = None, log=None):
        if log is None:
            log = (lambda m: print(f"freellm: {m}", file=sys.stderr)) if os.environ.get("FREELLM_VERBOSE") else (lambda m: None)
        self.providers = providers if providers is not None else available(log)
        self.log = log
        self.used: list[str] = []
        self._lock = threading.Lock()
        if not self.providers:
            raise LLMError("No free LLM key found. Set e.g. GROQ_API_KEY, NVIDIA_API_KEY, OPENROUTER_API_KEY "
                           "or MISTRAL_API_KEY (see README).")

    @property
    def chunk_chars(self) -> int:
        return min(p.max_chars for p in self.providers[:2])  # chunks must fit the first fallback too

    def chat(self, system: str, user: str, max_tokens: int = 2000) -> str:
        errors = []
        for p in list(self.providers):
            if len(user) > p.max_chars * 1.2:
                errors.append(f"{p.name}: input too large")
                continue
            try:
                text = p.chat(system, user, max_tokens)
                with self._lock:
                    self.used.append(f"{p.name}/{p.model}")
                return text
            except LLMError as e:
                errors.append(str(e))
                self.log(f"{p.name} failed, trying next: {str(e)[:120]}")
                if not e.transient:  # bad key, no credit, model gone: bench it for this run
                    with self._lock:
                        if p in self.providers:
                            self.providers.remove(p)
        raise LLMError("All free providers failed:\n- " + "\n- ".join(errors))
