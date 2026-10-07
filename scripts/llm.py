"""One LLM call for the engine, on free tokens first.

    from llm import chat
    text = chat("Write 5 hooks about ...", system="You write for Vish ...")

    python scripts/llm.py "prompt"     # one answer (stderr says which backend answered)
    python scripts/llm.py --check      # test every backend, print the free monthly token budget that is live

Order of attempts (first that answers wins):
  1. Free-token routers with an OpenAI-compatible /v1 endpoint, from LLM_BASE_URL (comma-separated):
       OmniRoute   github.com/diegosouzapw/OmniRoute    http://localhost:20128/v1   (scripts/router_setup.sh)
       FreeLLMAPI  github.com/tashfeenahmed/freellmapi  http://localhost:3001/v1    (needs LLM_API_KEY = its unified key)
  2. Free-tier providers called directly, for every key present in the environment (see PROVIDERS below and
     docs/llm-router.md). Keys live only in the cloud environment settings or your shell, never in this repo.
  3. Gemini through the environment's GEMINI_API_KEY credential.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

ROUTERS = [u.strip().rstrip("/") for u in os.environ.get("LLM_BASE_URL", "http://localhost:20128/v1,http://localhost:3001/v1").split(",") if u.strip()]
MODEL = os.environ.get("LLM_MODEL", "auto")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"

# Free tiers, biggest first. budget = documented recurring free tokens a month (OmniRoute FREE_TIERS.md,
# re-audited 2 Sep 2026; 0 = free but rate-limited with no published token cap). model = preferred model;
# if it is retired the client picks a capable one from the provider's /models list.
PROVIDERS = [
    {"id": "mistral", "env": "MISTRAL_API_KEY", "base": "https://api.mistral.ai/v1", "model": "open-mistral-nemo", "alts": ["ministral-8b-latest", "mistral-small-latest"], "budget": 1_000_000_000,
     "signup": "https://console.mistral.ai (Experiment plan, free, phone check)"},
    {"id": "llm7", "env": "LLM7_API_KEY", "base": "https://api.llm7.io/v1", "model": "default", "budget": 150_000_000,
     "signup": "https://token.llm7.io (free token)"},
    {"id": "groq", "env": "GROQ_API_KEY", "aliases": ["GROG_API_KEY"], "base": "https://api.groq.com/openai/v1", "model": "openai/gpt-oss-120b", "budget": 30_000_000,
     "signup": "https://console.groq.com/keys"},
    {"id": "cloudflare", "env": "CLOUDFLARE_API_TOKEN", "aliases": ["CLOUDFARE_API_KEY", "CLOUDFLARE_API_KEY", "CLOUDFARE_API_TOKEN"], "base": "https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/v1",
     "model": "@cf/meta/llama-3.3-70b-instruct-fp8-fast", "budget": 30_000_000,
     "signup": "https://dash.cloudflare.com > AI > Workers AI > Use REST API (token + account ID)"},
    {"id": "sambanova", "env": "SAMBANOVA_API_KEY", "base": "https://api.sambanova.ai/v1", "model": "Meta-Llama-3.3-70B-Instruct", "budget": 6_000_000,
     "signup": "https://cloud.sambanova.ai/apis"},
    {"id": "openrouter", "env": "OPENROUTER_API_KEY", "base": "https://openrouter.ai/api/v1", "model": ":free", "budget": 1_000_000,
     "signup": "https://openrouter.ai/settings/keys"},
    {"id": "cohere", "env": "COHERE_API_KEY", "base": "https://api.cohere.ai/compatibility/v1", "model": "command-a-03-2025", "budget": 800_000,
     "signup": "https://dashboard.cohere.com/api-keys (trial key)"},
    {"id": "huggingface", "env": "HF_TOKEN", "base": "https://router.huggingface.co/v1", "model": "openai/gpt-oss-120b", "budget": 200_000,
     "signup": "https://huggingface.co/settings/tokens (read token, Inference Providers on)"},
    {"id": "cerebras", "env": "CEREBRAS_API_KEY", "base": "https://api.cerebras.ai/v1", "model": "gpt-oss-120b", "budget": 0,
     "signup": "https://cloud.cerebras.ai"},
    {"id": "nvidia", "env": "NVIDIA_API_KEY", "base": "https://integrate.api.nvidia.com/v1", "model": "nvidia/nemotron-3-super-120b-a12b", "alts": ["openai/gpt-oss-20b"], "budget": 0,
     "signup": "https://build.nvidia.com (Get API key)"},
    {"id": "zai", "env": "ZAI_API_KEY", "aliases": ["Z_AI_API_KEY", "ZHIPU_API_KEY", "GLM_API_KEY", "ZAI_KEY"], "base": "https://api.z.ai/api/paas/v4", "model": "glm-4.5-flash", "budget": 0,
     "signup": "https://z.ai/manage-apikey/apikey-list"},
    {"id": "github", "env": "GITHUB_MODELS_TOKEN", "aliases": ["GITHUB_API_KEY"], "base": "https://models.github.ai/inference", "model": "openai/gpt-4.1", "budget": 0,
     "signup": "https://github.com/settings/personal-access-tokens (fine-grained, Models: read)"},
]
GOOD = re.compile(r"large|70b|120b|405b|glm|deepseek|qwen.*(32|72|235)|gpt-oss|command-a|llama-4|kimi", re.I)


UA = {"User-Agent": "Mozilla/5.0 (compatible; buildwithvish-llm/1.0)"}  # Groq's firewall rejects Python's default agent (error 1010)


def _post(url: str, body: dict, headers: dict, timeout: int) -> dict:
    for wait in (2, 5, 0):  # free tiers allow about 1 request a second: back off on 429 and try again
        req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST", headers={"Content-Type": "application/json", **UA, **headers})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code != 429 or not wait or e.headers.get("x-ratelimit-limit-req-minute") == "0":
                raise  # limit 0 = model not in this free tier: retrying will not help
            time.sleep(wait)


def _get(url: str, headers: dict, timeout: int = 20) -> dict:
    with urllib.request.urlopen(urllib.request.Request(url, headers={**UA, **headers}), timeout=timeout) as r:
        return json.loads(r.read())


def _openai(base: str, key: str | None, model: str, messages: list[dict], temperature: float, timeout: int) -> str:
    resp = _post(f"{base}/chat/completions", {"model": model, "messages": messages, "temperature": temperature},
                 {"Authorization": f"Bearer {key}"} if key else {}, timeout)
    return resp["choices"][0]["message"]["content"]


def _key(p: dict) -> str | None:
    """The provider's key from its variable or a common misspelling of it (GROG, CLOUDFARE), stripped of quotes."""
    for name in [p["env"], *p.get("aliases", [])]:
        v = os.environ.get(name, "").strip().strip("'\"")
        if v:
            return v
    return None


def _base(p: dict) -> str | None:
    try:
        env = dict(os.environ)
        env.setdefault("CLOUDFLARE_ACCOUNT_ID", os.environ.get("CLOUDFARE_ACCOUNT_ID", ""))
        return p["base"].format(**env) if "{CLOUDFLARE_ACCOUNT_ID}" not in p["base"] or env["CLOUDFLARE_ACCOUNT_ID"] else None
    except KeyError:
        return None  # e.g. Cloudflare without CLOUDFLARE_ACCOUNT_ID


def configured() -> list[dict]:
    return [p for p in PROVIDERS if _key(p) and _base(p)]


def _pick_model(p: dict, key: str) -> str:
    """Preferred model, or the most capable-looking one the provider lists today (free tiers change weekly)."""
    try:
        ids = [m.get("id", "") for m in _get(f"{_base(p)}/models", {"Authorization": f"Bearer {key}"}).get("data", [])]
    except Exception:  # noqa: BLE001
        return p["model"]
    if p["model"] == ":free":
        ids = [i for i in ids if i.endswith(":free")]
    elif p["model"] in ids:
        return p["model"]
    return next((i for i in ids if GOOD.search(i)), ids[0] if ids else p["model"])


def _provider(p: dict, messages: list[dict], temperature: float, timeout: int) -> str:
    key = _key(p)
    model = p.get("_model") or p["model"]
    try:
        if model == ":free":
            raise urllib.error.HTTPError(p["base"], 404, "pick", None, None)
        return _openai(_base(p), key, model, messages, temperature, timeout)
    except urllib.error.HTTPError as e:
        if e.code not in (400, 403, 404, 410, 429):  # 410 = model retired
            raise
        for alt in p.get("alts", []):  # e.g. a model the free tier does not include (403 tier_not_allowed)
            time.sleep(1.2)
            try:
                out = _openai(_base(p), key, alt, messages, temperature, timeout)
                p["_model"] = alt
                return out
            except urllib.error.HTTPError:
                continue
        p["_model"] = _pick_model(p, key)  # model retired or renamed: choose again, once
        return _openai(_base(p), key, p["_model"], messages, temperature, timeout)


GEMINI_MODELS = [m.strip() for m in os.environ.get("GEMINI_TEXT_MODELS", "gemini-3.8-flash,gemini-3.7-flash,gemini-3.5-flash,gemini-flash-latest").split(",")]


def _gemini(messages: list[dict], timeout: int) -> str:
    text = "\n\n".join(f"{m['role'].upper()}: {m['content']}" if m["role"] != "user" else m["content"] for m in messages)
    key = os.environ.get("GEMINI_API_KEY")
    last = None
    for attempt in range(2):
        for model in GEMINI_MODELS:  # busy (503) or capped (429) models fall through to the next one
            try:
                resp = _post(GEMINI_URL, {"model": model, "input": [{"type": "user_input", "content": [{"type": "text", "text": text}]}]},
                             {"x-goog-api-key": key} if key else {}, timeout)
                break
            except urllib.error.HTTPError as e:
                last = e
                if e.code not in (400, 429, 500, 502, 503, 404):  # a one-off 400 falls through to the next model
                    raise
        else:
            time.sleep(10)
            continue
        break
    else:
        raise RuntimeError(f"all Gemini models busy: {last}")

    def texts(o):
        if isinstance(o, dict):
            if o.get("type") == "text" and isinstance(o.get("text"), str):
                yield o["text"]
            for v in o.values():
                yield from texts(v)
        elif isinstance(o, list):
            for v in o:
                yield from texts(v)
    out = list(texts(resp.get("outputs", resp))) or list(texts(resp))
    if not out:
        raise RuntimeError(f"no text in Gemini response: {str(resp)[:200]}")
    return out[-1]


def _router_up(base: str) -> bool:
    try:
        key = os.environ.get("LLM_API_KEY")
        _get(f"{base}/models", {"Authorization": f"Bearer {key}"} if key else {}, timeout=4)
        return True
    except Exception:  # noqa: BLE001
        return False


def _err(e: Exception) -> str:
    if isinstance(e, urllib.error.HTTPError):
        try:
            body = e.read().decode()[:160]
        except Exception:  # noqa: BLE001
            body = ""
        return f"HTTP {e.code} {body}".strip()
    return str(e)[:160]


def chat(prompt: str, system: str | None = None, temperature: float = 0.7, timeout: int = 180) -> str:
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    errors = []
    for base in ROUTERS:
        if not _router_up(base):
            continue
        try:
            out = _openai(base, os.environ.get("LLM_API_KEY"), MODEL, messages, temperature, timeout)
            print(f"[llm] answered by router {base} ({MODEL})", file=sys.stderr)
            return out
        except Exception as e:  # noqa: BLE001
            errors.append(f"{base}: {_err(e)}")
    for p in configured():
        try:
            out = _provider(p, messages, temperature, timeout)
            print(f"[llm] answered by {p['id']} ({p.get('_model') or p['model']})", file=sys.stderr)
            return out
        except Exception as e:  # noqa: BLE001
            errors.append(f"{p['id']}: {_err(e)}")
    try:
        out = _gemini(messages, timeout)
        print("[llm] answered by Gemini", file=sys.stderr)
        return out
    except Exception as e:  # noqa: BLE001
        errors.append(f"gemini: {_err(e)}")
    raise RuntimeError("no LLM backend answered: " + " | ".join(errors))


def check() -> int:
    """Ping every backend with a tiny prompt; print what works and the free monthly budget that is live."""
    msg = [{"role": "user", "content": "Reply with the single word: ok"}]
    live, rows = 0, []
    for base in ROUTERS:
        if not _router_up(base):
            rows.append((base, "not running", ""))
            continue
        try:
            out = _openai(base, os.environ.get("LLM_API_KEY"), MODEL, msg, 0, 90)
            rows.append((base, "OK", out.strip()[:30]))
        except Exception as e:  # noqa: BLE001
            rows.append((base, "running, no provider answered", _err(e)[:90]))
    for p in PROVIDERS:
        if not _key(p):
            rows.append((p["id"], f"no key ({p['env']})", p["signup"]))
            continue
        if not _base(p):
            rows.append((p["id"], "key found, CLOUDFLARE_ACCOUNT_ID missing", "copy Account ID from the Workers AI REST API page"))
            continue
        try:
            _provider(p, msg, 0, 60)
            live += p["budget"]
            rows.append((p["id"], "OK", f"{p.get('_model') or p['model']} · {p['budget'] / 1e6:,.0f}M tokens/mo" if p["budget"] else f"{p.get('_model') or p['model']} · free, rate-limited"))
        except Exception as e:  # noqa: BLE001
            blocked = not isinstance(e, urllib.error.HTTPError) or (e.code in (403, 407) and "proxy" in _err(e).lower())
            hint = "blocked: Network access must be Full" if blocked else ""
            if isinstance(e, urllib.error.HTTPError) and e.code == 402:
                hint = "provider now asks for a payment method (no free use without a card)"
            rows.append((p["id"], "FAILED", hint or _err(e)[:90]))
    try:
        _gemini(msg, 60)
        rows.append(("gemini", "OK", "environment credential"))
    except Exception as e:  # noqa: BLE001
        rows.append(("gemini", "FAILED", _err(e)[:90]))
    w = max(len(r[0]) for r in rows)
    for r in rows:
        print(f"{r[0]:<{w}}  {r[1]:<34} {r[2]}")
    print(f"\nLive documented free budget (direct keys): ~{live / 1e9:.2f}B tokens a month"
          + ("" if live else "  (add keys: docs/llm-router.md)"))
    return 0 if any(r[1] == "OK" for r in rows) else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--check"]:
        sys.exit(check())
    print(chat(" ".join(sys.argv[1:]) or "Say hello in five words."))
