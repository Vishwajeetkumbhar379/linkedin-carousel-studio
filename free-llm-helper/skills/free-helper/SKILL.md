---
name: free-helper
description: Save Claude usage by handing bulk reading and first drafts to free LLMs through the free-llm-helper tools (free_summarize, free_ask, free_find, free_draft, free_bulk, free_summarize_url). Use whenever a task needs reading large files, folders, logs, long web pages or docs you only need the gist of, locating code in an unfamiliar repo, drafting boilerplate text, or applying one instruction to many rows.
---

# Free helper: delegate the reading, keep the thinking

The free-llm-helper tools read big inputs with free models (Groq, NVIDIA, Cloudflare, OpenRouter, ...) and return a
short answer, so the raw text never enters your context. Every reply ends with a `[free-llm-helper: ...]` line saying
which provider answered and how many tokens it kept out of Claude.

## Delegate (use the tool first)

| Situation | Tool |
|---|---|
| A file over ~200 lines, a folder, or a log you need the gist of | `free_summarize` (pass `focus`) |
| "Where is X handled?" in a repo you have not read | `free_find`, then open only the files it names |
| A question answerable from big files or docs | `free_ask` |
| A long web page, docs site, changelog, article | `free_summarize_url` / `free_summarize` with the URL |
| First draft of README, docs, post, email, release notes | `free_draft`, then edit it yourself |
| Same instruction over many lines (classify, translate, extract) | `free_bulk` |

## Keep on Claude (do not delegate)

- Writing or editing code you will commit, debugging, architecture, security decisions.
- Anything where a wrong answer is costly: verify free-model claims by opening the cited file/line before acting.
- Short files (under ~200 lines): reading them directly is cheaper than a round trip.
- Anything the user marked confidential, or files outside the allowed folders.

## Rules

- Local paths only work inside `FREELLM_ALLOW_DIRS`; secret files (.env, keys, credentials) are never sent and
  key-like strings are redacted. Do not try to work around a "Blocked" reply: tell the user instead.
- Pass paths and URLs, never paste file contents into the tool: pasting costs the tokens you are trying to save.
- If every provider fails, fall back to reading the material yourself and say so.
- `free_status` shows providers, allowed folders and total tokens saved.
