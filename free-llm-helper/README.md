# free-llm-helper

Make Claude cheaper by letting **free LLMs do the bulk reading**. Claude Code (and Claude chat) call a tool that reads
big files, folders, logs and web pages with a free model and returns a short answer, so the raw text never enters
Claude's context. Claude keeps the thinking, the code and the final word.

```
Claude ──"summarize src/, focus auth"──▶ free-llm-helper ──chunks──▶ Groq → NVIDIA → Cloudflare → OpenRouter → ...
       ◀── 15-line summary + "[via groq | read 80,000 chars -> returned 900 (~19,775 tokens kept out of Claude)]"
```

Every reply says which provider answered and how many tokens it kept out of Claude; `freellm stats` adds them up.

## What gets sent where (read this)

The helper sends the content of files you point it at to third-party free providers, which may log it or use it for
training. Guards:

- **Folder allowlist.** Nothing local is read unless it is inside `FREELLM_ALLOW_DIRS`. Symlinks are resolved first,
  so a link cannot escape the allowlist.
- **Secret files are never read:** `.env*`, `*.pem`, `*.key`, `id_rsa*`, `credentials*`, `*secret*`, `.npmrc`,
  `.netrc`, `*.tfstate`, and folders like `.git`, `.ssh`, `.aws`, `node_modules`.
- **Secret scrubbing.** Before anything leaves the machine, API keys (Anthropic, OpenAI, Groq, NVIDIA, GitHub, AWS,
  Google, Slack, ...), private keys, JWTs, `password=...`-style assignments, credentials in URLs, and the literal values
  of your `*_KEY`/`*_TOKEN`/`*_SECRET` env vars are replaced by `[REDACTED]`.
- **No private URLs.** localhost, private ranges and cloud metadata endpoints are refused.
- **Audit log.** Every call is logged to `~/.freellm/usage.jsonl` (sources, providers, sizes, redaction count).

Don't allowlist folders holding client data or anything under NDA.

## Setup for Claude Code (2 minutes)

```bash
pip install -e .                                  # or just run with: python3 -m freellm
export FREELLM_ALLOW_DIRS=~/projects:~/notes      # folders the helper may read (colon-separated)
export GROQ_API_KEY=... NVIDIA_API_KEY=...        # any subset of the providers below
freellm providers                                 # check keys + allowed folders

# register the MCP server for all your projects
claude mcp add free-helper -s user \
  -e FREELLM_ALLOW_DIRS="$FREELLM_ALLOW_DIRS" -- python3 -m freellm mcp

# teach Claude when to use it
mkdir -p ~/.claude/skills && cp -r skills/free-helper ~/.claude/skills/
```

Provider keys are read from your environment, so `claude mcp add` doesn't need to copy them. If Claude Code is
started without them in its environment, add `-e GROQ_API_KEY=...` and the others to the command.

Tools Claude gets: `free_summarize`, `free_ask`, `free_find`, `free_draft`, `free_bulk`, `free_status`.

## Setup for Claude chat (claude.ai): Cloudflare Worker

Claude chat can't reach your machine, so this is a small hosted MCP server that reads **public URLs and text you
pass it** (no local files). It runs on the Cloudflare free tier and also uses Workers AI as a keyless fallback.

```bash
cd worker
# one-time: open https://dash.cloudflare.com -> Workers & Pages once, so your workers.dev subdomain exists
export CLOUDFLARE_API_TOKEN=...                   # needs "Workers Scripts: Edit" + "Workers AI: Read"
npx wrangler deploy
openssl rand -hex 24 | npx wrangler secret put MCP_SECRET
npx wrangler secret put GROQ_API_KEY              # repeat for NVIDIA_API_KEY, OPENROUTER_API_KEY, MISTRAL_API_KEY
```

Then in claude.ai: **Settings → Connectors → Add custom connector** with the URL
`https://free-llm-helper.<your-subdomain>.workers.dev/mcp/<MCP_SECRET>`. The secret in the path is the password, so
keep the URL private. Tools: `free_summarize_url`, `free_ask`, `free_draft`.

## CLI

```bash
freellm summarize src/ --focus "auth flow" --words 150
freellm ask "where are retries configured?" src/ config/
freellm find "rate limiting" .
freellm draft "LinkedIn post about creator contracts" --from notes.md
freellm bulk "Classify sentiment: positive/negative/neutral" reviews.txt out.txt
freellm stats
```

## Providers

Tried in this order. A rate limit or timeout skips a provider for that one call; a bad key, missing credit or a
retired model benches it for the rest of the run.

| Provider | Env var | Default model |
|---|---|---|
| Groq | `GROQ_API_KEY` | `openai/gpt-oss-120b` (fastest; 8k tokens/min, so chunks stay small) |
| NVIDIA | `NVIDIA_API_KEY` | `moonshotai/kimi-k3` |
| Cloudflare Workers AI | `CLOUDFLARE_API_TOKEN` (+ `CLOUDFLARE_ACCOUNT_ID`, auto-detected if missing) | `@cf/meta/llama-3.3-70b-instruct-fp8-fast` |
| OpenRouter | `OPENROUTER_API_KEY` | `nvidia/nemotron-3-super-120b-a12b:free` |
| GitHub Models | `GITHUB_MODELS_TOKEN` | `openai/gpt-4.1` |
| Mistral | `MISTRAL_API_KEY` | `ministral-14b-latest` |
| Z.AI | `ZAI_API_KEY` | `glm-4.5-flash` |
| LLM7 | `LLM7_API_KEY` | `deepseek-v4-pro` |
| SambaNova | `SAMBANOVA_API_KEY` | `gpt-oss-120b` (needs a payment method on file) |

Change the order with `FREELLM_ORDER=nvidia,groq,...`, a model with `FREELLM_MODEL_GROQ=...`, parallel chunk calls
with `FREELLM_PARALLEL=4`, and see provider failures with `FREELLM_VERBOSE=1`.

## Where it saves, and where it doesn't

It saves the most on reading-heavy work: big logs, unfamiliar codebases, long docs and research pages, bulk text jobs,
where 20-80k characters come back as a few hundred. It saves nothing on short files and shouldn't be used for hard
reasoning or code you'll commit. Free models can be wrong, so check what they cite before acting on it.

## Tests

```bash
python3 -m pytest -q          # Python package (offline, fake providers)
cd worker && npm test         # Worker (offline)
```
