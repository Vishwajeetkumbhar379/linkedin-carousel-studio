# engine/(root)

Define brand assets, content rules, and CLI tools for generating LinkedIn carousel posts.

- `.mcp.json`: JSON: mcpServers
- `CLAUDE.md`: Specifies locked assets (aurora paper carousel, video motion template), voice API key, British English hooks ≤12 words, sourced claims. (uses tokens.json, aurora.py, cover-psychology.md, kit.js, motion.html, sfx.py)
- `PLAYBOOK.md`: Defines 3‑post weekly system (Reel, Carousel A, Carousel B), theme buckets, metric goals, calendar location, updated rules. (uses 2026-weeks-02-05.md, week-series.css, attention-playbook-2026-10-15.md, edit-recipe-v9-2026-10-22.md, render_slides.py, monetisation.md)
- `README.md`: CLI renders LinkedIn carousel from JSON deck, enforces style rules, outputs PNG slides and PDF; can draft via Claude. (uses creator-contract-checks.json, studio.py, runbook.md, tokens.json, posted.json, build_post.py)
- `brand-profile.md`: Locks Vish brand profile: positioning, proof points, audience, content pillars, prohibits invented stats, personal contacts, past employer names.
- `content-pillars.md`: Defines five content pillar series with formats and target topics for LinkedIn posts. (uses brand-profile.md)
- `package.json`: JSON: name, version, private, type, description, scripts, engines, devDependencies (uses transcribe-elevenlabs.mjs, validate-beat-sync.mjs, preflight.mjs, sync-codex-skills.mjs, setup.mjs, new-video.mjs)
- `pyproject.toml`: Defines project metadata, dependencies, optional AI dev tools, and CLI entry point 'carousel'.
- `skills-lock.json`: JSON: version, skills
- `voice.md`: Defines Vish's voice guidelines, banned words, style, and editing rules for scripts and captions.
