# Free-token LLM router (OmniRoute + FreeLLMAPI)

The engine's writing and research calls go through `scripts/llm.py`. It tries, in order:
1. the free-token routers in `LLM_BASE_URL` (default `http://localhost:20128/v1` OmniRoute, then `http://localhost:3001/v1` FreeLLMAPI),
2. every free provider whose key is in the environment, called directly (OpenAI-compatible),
3. Gemini through the environment credential.

Check what is live: `bash scripts/router_setup.sh && python scripts/llm.py --check`. It prints each backend and the documented free monthly budget unlocked.

## What Vish sets up once (cloud environment > Edit)
1. **Network access: Full.** On 7 Oct 2026 every provider host (api.mistral.ai, api.groq.com, openrouter.ai, api.llm7.io, api.cloudflare.com, api.sambanova.ai, api.cohere.ai, router.huggingface.co, api.cerebras.ai, integrate.api.nvidia.com, api.z.ai, models.github.ai, opencode.ai) was blocked under the Trusted level.
2. **Environment variables**, one per line `NAME=value` (never in chat, never in this repo):

| Variable | Provider | Free tokens a month (OmniRoute FREE_TIERS.md, 2 Sep 2026) | Get it |
|---|---|---|---|
| `MISTRAL_API_KEY` | Mistral | ~1.00B | console.mistral.ai, Experiment plan (free, phone check), API Keys |
| `LLM7_API_KEY` | LLM7 | ~150M | token.llm7.io |
| `GROQ_API_KEY` | Groq | ~30M | console.groq.com/keys |
| `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` | Workers AI | ~30M | dash.cloudflare.com > AI > Workers AI > Use REST API |
| `SAMBANOVA_API_KEY` | SambaNova | ~6M, **now needs a payment method on file** (checked 7 Oct 2026) | cloud.sambanova.ai/apis |
| `OPENROUTER_API_KEY` | OpenRouter | ~1M (50 free requests a day) | openrouter.ai/settings/keys |
| `COHERE_API_KEY` | Cohere | ~0.8M | dashboard.cohere.com/api-keys |
| `HF_TOKEN` | Hugging Face | ~0.2M | huggingface.co/settings/tokens |
| `NVIDIA_API_KEY` | NVIDIA NIM | no cap, about 40 requests a minute | build.nvidia.com |
| `ZAI_API_KEY` | Z.ai GLM Flash | no cap, rate-limited | z.ai API keys |
| `GITHUB_MODELS_TOKEN` (or `GITHUB_API_KEY`) | GitHub Models | rate-limited; in the cloud the GitHub proxy intercepts models.github.ai, so it only works on the Mac | fine-grained token with Models: read |
| `CEREBRAS_API_KEY` | Cerebras | one-time $5 credit, **needs a card** | cloud.cerebras.ai |

All keys together: about **1.22B documented tokens a month** in the cloud, plus the uncapped tiers.
3. Optional **setup script** line: `npm install -g omniroute >/dev/null 2>&1 || true`.

`scripts/router_setup.sh` starts OmniRoute and pipes the Mistral, Groq and OpenRouter keys into it (`omniroute keys add <p> --stdin`), never printing them.

## On the Mac (optional, the full dashboards)
- **FreeLLMAPI** (the "7.4B" figure, a sum of rate limits across 34 providers): desktop app from github.com/tashfeenahmed/freellmapi/releases/latest (`.dmg`, arm64 for Apple Silicon). Tray > Open Dashboard > Keys: add keys; copy the unified key. Endpoint `http://localhost:3001/v1`, model `auto`.
- **OmniRoute** (the audited "~1.62B" figure): Node 22, then `npm install -g omniroute && omniroute`, open `http://localhost:20128`, Providers: connect OpenCode Free, Kiro, Nara and xKiro (dashboard sign-in flows) and add the same keys. Free tiers page shows the live budget.

## Rules
- Free tiers can use prompts for training (Mistral Experiment, Google free). Send public content drafts only, never private data.
- Two paid upgrades exist and are not needed: Cerebras (card for $5 credit) and an OpenRouter $10 top-up.

## Verified live, 7 Oct 2026
Mistral (open-mistral-nemo), LLM7, Groq, Cloudflare Workers AI, OpenRouter (:free), NVIDIA (Nemotron 3 Super) and Gemini: about **1.21B documented free tokens a month**. Variable names `GROG_API_KEY` and `CLOUDFARE_API_KEY` are accepted as typed.
