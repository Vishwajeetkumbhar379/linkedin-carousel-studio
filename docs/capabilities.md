# Capabilities inventory

Checked 6 Oct 2026 from the Claude Code cloud session that built this engine. Each connector was tested with one harmless, read-only call.

## Connectors

| Connector | Status | Test call | Used for in the pipeline |
|---|---|---|---|
| GitHub (MCP) | ✅ works | `get_me`, repo search | Inspiration sweep, reading Vish's site repos, PRs |
| Netlify | ✅ works | `get-projects` → 5 sites (`buildwithvish`, `vishkumbhar`, …) | Deploy Build with Vish pages (draft previews first) |
| Notion | ⚠️ works, wrong workspace | search returns nothing; the public Inspiration Libraries page is in another workspace | Optional approval queue. Fetched the public page via Crustdata instead |
| Gmail | ✅ works | `list_labels` | Review notifications (drafts only, never auto-send) |
| Google Drive | ✅ works | `list_recent_files` | Storing review packs, LinkedIn exports |
| Google Sheets | ✅ (same Google auth) | not called separately | Approval queue + analytics log option |
| Google Calendar | ✅ works | `list_calendars` (timezone Europe/Berlin) | Posting-slot holds |
| Todoist | ✅ works (Free plan, Europe/Brussels) | `user-info` | "Approve post X" tasks |
| Slack | ⚠️ connected, no channels found | `search_channels` → 0 results | Not useful until Vish has a workspace channel; use Gmail + Todoist |
| MailerLite | ✅ works | `get_auth_status` (account 2688960) | Resource delivery for comment/DM requests, newsletter repeat |
| Zapier | ✅ connected | not executed (needs per-app actions enabled) | LinkedIn post-with-approval, MailerLite hand-offs |
| Canva | ✅ works, no brand kit | `list-brand-kits` → empty | Optional: Vish edits a slide by hand. Not in the main path |
| Figma | ✅ works (view seat, starter) | `whoami` | Moodboard boards; read-only design context |
| Gamma | ✅ works | `get_themes` | Not needed (our own renderer is better on brand) |
| Hugging Face | ✅ works (free, `vishjarvisai`) | `hf_whoami` | Trending models/papers for research; TTS models later |
| Crustdata | ✅ works, **84 → ~60 credits left, expire 14 Oct** | `credits_check`, web fetch, social post search | LinkedIn post search (competitor scan), fetching pages this container can't reach |
| Typefully | ❌ "connect incomplete" | — | Possible scheduler (see automation options) |
| HubSpot, Vercel, Microsoft 365 | ❌ not connected | — | Not needed |
| Apollo, Asana, Indeed, Zoom, Spotify, Gemini (crypto) | connected | not tested | Not relevant to content |

## Skills

| Skill | Status | How the engine uses it |
|---|---|---|
| vish-linkedin-content | ✅ enabled | Positioning, voice, CTA bank (read; its dark palette became Direction B) |
| application-humanizer | ✅ enabled | Humanizer pass rules (adapted into `scripts/qa.py` banned list + manual pass) |
| deep-research | ✅ enabled | Weekly deep topic research (spawns sub-agents; run on Sundays) |
| canvas-design, algorithmic-art, theme-factory | ✅ enabled | Reference for generative backgrounds; not needed in the core path |
| frontend-design | ⚠️ not in this account | Replaced by **impeccable** (which started from it) + **taste-skill**, both installed in `.claude/skills/` |
| brand-guidelines | ✅ enabled, **not used** | It applies Anthropic's brand, which Vish must not imitate |
| web-artifacts-builder, pdf, pptx, docx, xlsx | ✅ enabled | PDF merge/checks; review pages |
| slack-gif-creator | ✅ enabled | Mascot GIF stickers later |
| skill-creator | ✅ enabled | Turn this pipeline into a `build-with-vish-post` skill after the go-ahead |
| SearchSkills | — | No "taste" or "impeccable" skill in the claude.ai library; found and verified on GitHub instead |

## Built-in tools

| Tool | Status | Note |
|---|---|---|
| Bash, Python 3.13, Node 22, ffmpeg 6.1 | ✅ | |
| Playwright + Chromium (headless, WebGL via SwiftShader) | ✅ | Python Playwright pinned to 1.56 to match the preinstalled Chromium 1194 |
| Three.js r186, Geist/Syne/Public Sans fonts | ✅ installed via npm into `templates/` | All MIT/OFL |
| WebSearch | ✅ | US results only |
| WebFetch | ❌ blocked for almost every host | This container's network policy. Workaround: Crustdata web fetch (costs credits) |
| curl to most sites (netlify.app, instagram, openai.com…) | ❌ 403 from egress proxy | Fix: widen the environment's network access (see below) |
| Instagram | ❌ for images | Captions and engagement came through Crustdata; slide images need screenshots from Vish |
| Scheduled routines (`create_trigger`, `send_later`) | ✅ available | Weekly research etc., after approval |
| GitHub Actions | ✅ (repo has CI) | Free cron with open network: the research fetcher runs there |

## Gaps and what I recommend

| Gap | Best option found | Cost | Status |
|---|---|---|---|
| Network blocked for research sites | Allow more hosts in this environment (Settings → environment → Network access → Custom, keep package managers) **or** run `scripts/research/fetch.py` in GitHub Actions | Free | Workflow added: `.github/workflows/research.yml` |
| Video rendering | Current: deterministic HTML/Three.js frames → ffmpeg (works, ~2 s/frame on software GPU). Option: Remotion | Remotion is free for individuals and companies of up to 3 people; flag before any team use | Using our own renderer; Remotion optional |
| Voiceover | Kokoro-82M (Apache-2.0) or Piper (MIT) open TTS | Free | Not installed yet; needs a quality review sample first |
| Design taste | `impeccable` (Apache-2.0, ~77k★) + `taste-skill` (MIT, ~93k★) | Free | Installed in `.claude/skills/` |
| Remotion-style motion recipes | `video-shotcraft` (Apache-2.0, ~10k★) | Free | Studied, patterns logged, not installed |
| Posting automation | See `docs/automation-options.md` | Free paths exist | Waiting on Vish |
| Instagram reference images | Vish sends screenshots, or connect Claude in Chrome on his machine | Free | Waiting on Vish |
