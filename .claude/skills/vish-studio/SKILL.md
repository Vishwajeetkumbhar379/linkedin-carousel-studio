---
name: vish-studio
description: Vish's full content system for @buildwith.vish and buildwithvvish.com. Use when asked for "the week", "next week's content", "a full package", "run the pipeline", or any single stage of it (topic, hook, script, storyboard, edit, captions, carousel, cover, publish, comment-to-DM, lead magnet, website, sales, analytics) for Vish. Runs the stages in order and names the exact skill and script for each.
---

# vish-studio: the master workflow

Read `PLAYBOOK.md` first (single source of truth). Facts about Vish only from `brand-profile.md`. Writing rules from `voice.md`. Never post, DM or charge anyone without Vish's approval for that week.

## Full week = run 1 to 14 in order, one theme for all three posts (playbook §2)

| # | Stage | Do | Skills / scripts | Output |
|---|---|---|---|---|
| 1 | Research | **Viral first:** rank candidate reels by likes and comments (`ig_fetch.py --meta-only`) and keep only 50K+ likes, 20K+ comments, or more comments than likes (PLAYBOOK §12). Then trends from the last 30 days and Vish's comments | `last30days`, `competitor-teardown`, `comment-mining`, `reel-analyzer`; `scripts/research/ig_fetch.py` + `reel_teardown.py`; `agent-reach` when the built-in fetch fails | 5 to 10 candidate themes with sources |
| 2 | Topic validation | Start from a winning pattern (named framework, tool giveaway, big-claim tool hook), then score each theme: fits a pillar, has a real proof from Vish, has a free resource, isn't a repeat (`topics/posted.json`), episode can deliver it | `niche-research`, `series-planner` | One weekly theme: episode + carousel A + carousel B |
| 3 | Hook | 3 hooks per post, 12 words or fewer, 3+ levers, true facts only | `viral-hook-creator`, `hook-generator`, `yt-script` (hook score) | Hook + 2 alternates |
| 4 | Script | Shoot sheet: hook, lock-in, body, re-hooks, CTA with keyword; 80 to 100 words; delivery marks; on-screen cue per line; SlopMonster | `short-form-video-script`, `reels-script`; `python3 .claude/skills/slopmonster/tools/deslop.py` | `content/shoot-sheets/<week>.json` + teleprompter page update |
| 5 | Storyboard | **70/30 style (PLAYBOOK §4): pick the 3D world, place the portal card, perform the tempo marks.** Per line: layout (cut-out, 4:5 frame, split, full B-roll), graphic, sound, transition. Mark the freeze-frame beat, silences, montage | `video-storytelling`, `on-screen-text-writer`, `style-library` | Storyboard table in the shoot sheet |
| 6 | Visual edit | v12 standard. Captions at 58 to 66% height. **Safe-zone and face gate: `scripts/reel_edit/safe_zones.py check` must PASS before render (no text under Instagram's UI, nothing drawn on his face; titles and stickers go behind him), and `preview` goes with the review copy.** ElevenLabs "Next week" card. Check the disk first | `video-projects/<slug>/edit/*.py` + `comp.html` (copy from week-01-intro), `hyperframes`, `huashu-motion`, `openfilm`, `gsap-*`, `media-use` | 9:16 master + 4:5 LinkedIn + review copy |
| 7 | Captions | Post text (playbook §6), 5 hashtags, alt text, first comment | `ig-caption-writer`, `hashtag-strategy`, SlopMonster | Caption block in the post kit |
| 8 | Carousel | 7 to 10 slides, 1080x1350, real screenshots, keyword on the last slide | `viral-carousel`, `ig-carousel-planner`; `templates/carousel/<name>.html`, `scripts/render_slides.py` | PNG slides + ZIP + caption |
| 9 | Cover | Framed-print template, week colour, 3 stickers, 3:4-safe | `video-projects/week-01-intro/work/cover12/cover.html` | `out/week<N>-cover.jpg` |
| 10 | Publish | Post kit per post: file, cover, caption, alt text, location, audio name, pinned comment, time. Vish posts (or approved scheduling) | `instagram-reels-publishing`, `scheduling-and-queue` | `content/instagram/week-NN-post-kit.md` |
| 11 | Comment automation | Add every keyword to `buildwithvish/lib/ig-autodm/config.json` with its resource, reply set and tier; run the tests | `dm-script-writer`; `node --test` in buildwithvish | Keyword live after push |
| 12 | Lead magnet | Free resource in the 8-section guide format, plus a PDF version. Optional €1 template | `lead-magnet-generator`, `mkt-lead-magnets`, `anthropic-skills:pdf`; `templates/guide/implementation-guide.md` | Guide page + PDF |
| 13 | Website | Publish the resource page in the library and link it from `/resources` and `/go/KEY` | `seo-audit`, `ai-seo`, `frontend-design`; `buildwithvish/src/build.py` | Live page (after approval) |
| 14 | Sales and analytics | Products and checkout (no live charges until approved); weekly report: keep / test / change / stop | `stripe-best-practices`, `social-analytics-report`, `utm-campaign-plan`; `docs/monetisation.md` | Weekly report + next week's adjustments |

## Single stages
Jump straight to the row. Still read the playbook section it names, and still run SlopMonster on any text.

## Guardrails
- Never post, DM, comment on others' posts, or charge money without Vish's approval for that week.
- Never invent numbers, results or quotes. Never mention his past relationship. No "Edited by AI" card.
- Keep token use low: reuse transcripts and teardowns in `research/`. Batch renders. Load only the stage you need.
- Report what was done, tested, blocked and pending, and keep them separate.
