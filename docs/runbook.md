# Runbook

## One-time setup (Vish's machine or a cloud session)
```bash
make setup            # Python deps (Playwright pinned to 1.56) + Node deps (three.js, fonts)
```
No secrets are stored in the repo. Env vars, only when you turn the feature on:
| Variable | Needed for | Where to set |
|---|---|---|
| `ANTHROPIC_API_KEY` | `carousel draft` (Claude drafting outside Claude Code) | shell / GitHub Actions secret |
| `MAILERLITE_API_TOKEN`, `MAILERLITE_GROUP_ID` | already set on the Build with Vish Netlify site | Netlify env |

## Make one post (today's manual flow, before the go-ahead)
1. `make research` (or read `topics/backlog.json`).
2. Create `out/YYYY-MM-DD-slug/` with `deck.json` (carousel / single image) or `video.json` (video), plus `caption.md`, `first-comment.md`, `alt-text.md`, `sources.md`, `hooks.md`. Copy one of the three samples as a starting point.
3. `make post POST=out/YYYY-MM-DD-slug` → renders slides/PDF or MP4, runs QA, writes `qa-report.md`.
4. Fix every FAIL. WARNs need a human look.
5. Build the matching Build with Vish page first (`site-page/` in the post folder → `buildwithvish/src/long/guides/` + an entry in `content-guides.js`), deploy a **draft preview** on Netlify, check the link.
6. Notify: Gmail draft + Todoist "Approve: <title>". Vish posts.

## Scheduled jobs (proposed; nothing is scheduled yet)
| When | Job | How |
|---|---|---|
| Sunday 06:17 UTC | Weekly research fetch | `.github/workflows/research.yml` (enable by merging) |
| Sunday | Deep topic research + backlog rescoring | Claude routine using deep-research |
| Monday | Batch of 5 to 7 posts (`make week`) | Claude routine, after the go-ahead |
| Daily 08:00 CET | Breaking-news check (score ≥ 9 only) | Claude routine |
| Weekly | Analytics review from Vish's export | Claude routine |
| Monthly | Algorithm + inspiration refresh | Claude routine |

## Known environment limits (this cloud container)
- Most sites are blocked by the environment's network policy (netlify.app, instagram.com, openai.com, techcrunch.com…). Either widen Network access in the environment settings or rely on GitHub Actions for fetching.
- WebGL runs on SwiftShader (software). Stills: ~5 s each. Video: ~0.9 s/frame at 60% 3D resolution (30 s video ≈ 14 min).
