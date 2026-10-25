# buildwithvish/tools

Generate, lint, merge, and manage long‑form tutorial pages for AI content pipeline.

- `tools/longform/STYLE.md`: Specifies style and hard rules for rewriting long‑form pages into complete AI tutorials.
- `tools/longform/check.js`: Node linter for long‑form pages, enforcing dash, banned words, tag, and length rules. (uses slugs.txt)
- `tools/longform/merge.py`: Copies validated long‑form pages from out/ to src/long after linting. (uses check.js, slugs.txt)
- `tools/longform/out/creator-campaign-hq-in-claude.html`: html file
- `tools/longform/out/creator-campaign-hq-in-claude.meta.json`: JSON: title, excerpt
- `tools/longform/out/get-cited-by-ai-answers.html`: html file
- `tools/longform/out/get-cited-by-ai-answers.meta.json`: JSON: title, excerpt
- `tools/longform/out/youtube-research-with-claude.html`: html file
- `tools/longform/out/youtube-research-with-claude.meta.json`: JSON: title, excerpt
- `tools/longform/seed/creator-campaign-hq-in-claude.json`: JSON: type
- `tools/longform/seed/get-cited-by-ai-answers.json`: JSON: type
- `tools/longform/seed/youtube-research-with-claude.json`: JSON: type
- `tools/longform/slugs.txt`: List of long‑form page slugs with types for build pipeline.
