# engine/docs

Document processes, policies, and configurations for content automation, monetization, hosting, and social media.

- `docs/automation-options.md`: Lists LinkedIn publishing options, approval steps, costs, and recommends Gmail+Todoist for zero-setup posting.
- `docs/backfill-plan.md`: Specifies backfill workflow: verify facts, upgrade pages, draft Netlify preview, redesign carousel, QA, review pack. (uses posted.json)
- `docs/capabilities.md`: Catalogs available API connectors, test status, and pipeline usage for content automation. (uses qa.py, fetch.py, automation-options.md)
- `docs/cover-psychology.md`: Defines cover image rules: hero action, context symbol, face emotion, focal point, curiosity gap.
- `docs/growth-playbook.md`: Defines LinkedIn posting strategy, timing, hooks, comments, analytics loop, and default formats based on 2026 research. (uses backlog.json)
- `docs/hosting-cloudflare.md`: Migrates buildwithvish site to Cloudflare Workers, sets up API routes, secrets, and custom domain. (uses instagram-autodm.md, wrangler.toml)
- `docs/impressum-template.md`: Template for German legal Impressum, requires real address, email, tax info, and contact details.
- `docs/instagram-autodm.md`: Automates DM replies to Instagram comment keywords, tracks stats, enforces rate limits, and serves resource links.
- `docs/llm-router.md`: Routes LLM requests through free-token routers, environment keys, and Gemini, checking backend availability and token budgets. (uses llm.py, router_setup.sh)
- `docs/monetisation.md`: Outlines German e‑commerce rules, Stripe fees, Lemon Squeezy costs, and tax registration steps for digital product sales. (uses impressum-template.md)
- `docs/reference-study.md`: Analyzes Instagram posts Vish likes, listing hooks, formats, structures, and why they perform well.
- `docs/runbook.md`: Runbook (uses backlog.json, content-guides.js)
- `docs/skills.md`: Skills installed for the content engine (7 Oct 2026, approved by Vish) (uses .mcp.json)
- `docs/voice.md`: Voiceover (uses voiceover.py)
