# Context map (built 2026-10-24 by `scripts/context_graph.py`)

Read this first instead of the repos. Each area links to a one-line-per-file page in `context/areas/`.
Find anything: `python scripts/context_graph.py query "<words>"`. Rebuild after big changes: `python scripts/context_graph.py build --update` (free LLMs only).

## Start here (rules that always apply)

- Goal: multi-agent content engine for Vish (AI x marketing). LinkedIn first, then Instagram and YouTube Shorts. Brand and voice are locked: `PLAYBOOK.md` is the single source of truth (23 Oct), then `brand-profile.md`, `voice.md`, `content-pillars.md`. `CLAUDE.md` is a stack of dated overrides: the newest section wins.
- Tokens: bulk reading, drafting and summarising go to free LLMs via `scripts/llm.py`. Claude directs and judges only.
- Never print or commit keys. Never post, DM or comment on Vish's behalf without his explicit go-ahead. Vish has no laptop and works from an iPad: cloud only, plain words, one question at a time.
- Branches: `claude/content-engine-test-gate` = main engine work; `claude/project-thread-k1b03i` = engine + Inside AI Shorts (latest). `main` is only the initial release.
- Shorts (Inside AI): faceless 9:16 explainers, ElevenLabs voice Drew v3, visual north star = reel De0BAl8B3mY (TEARDOWN.md, 12 three.js/GSAP rules). Ep 3+ = everyday-curiosity shock hooks.
- Project memory (`/tmp/claude/memory/team/silo`) holds the latest decisions; it is summarised under the `memory` source below.

## Sources

- **engine**: linkedin-carousel-studio: the content engine (scripts, brand, templates, research, content, skills) (389 files, 136 skills, 59 output folders)
- **buildwithvish**: website buildwithvvish.com on Cloudflare Workers, guides, Instagram auto-DM webhook (143 files, 0 skills, 0 output folders)
- **claude-skills**: Vish's public Agent Skills (job search, humanizer, carousel, creator marketing) (8 files, 7 skills, 0 output folders)
- **profile-pipeline**: profile repo, branch linkedin-pipeline: older 9-slide carousel builder (linkedin/build.py) (15 files, 11 skills, 0 output folders)
- **memory**: project memory: decisions, state, Vish's feedback (7 files, 0 skills, 0 output folders)
- **project-files**: shared deliverables: Shorts finals, research, LinkedIn profile kit (10 files, 0 skills, 0 output folders)

## Hub files (most connected)

- `engine:CLAUDE.md`: Specifies locked assets (aurora paper carousel, video motion template), voice API key, British English hooks ≤12 words, sourced claims.
- `buildwithvish:src/build.py`: Python build script compiles assets, generates site files, and handles local build mode.
- `engine:scripts/weekly.py`: Orchestrates weekly batch: research, write, voice, graphics, video, QA, site, calendar, page; supports skip‑voice, write‑only, fix.
- `engine:research/creators/style-guide-2026-10-14.md`: Defines pacing, sound, layout metrics for Kallaway and Justyn reel formats, used for style consistency.
- `engine:scripts/render3d.py`: Renders 3D scenes from JSON specs via headless Chromium; outputs PNG at 2x supersample.
- `engine:PLAYBOOK.md`: Defines 3‑post weekly system (Reel, Carousel A, Carousel B), theme buckets, metric goals, calendar location, updated rules.
- `engine:brand-profile.md`: Locks Vish brand profile: positioning, proof points, audience, content pillars, prohibits invented stats, personal contacts, past employer names.
- `engine:scripts/voice25.py`: Generates locked voice for video #25 with Gemini Flash‑Lite TTS, writes voice.wav/voice.json, aligns lines, supports realign and render, respects quota.
- `engine:scripts/make_batch.py`: Transforms batch topic JSONs into post folders, optionally adding voice or render steps.
- `engine:scripts/voiceover.py`: Creates voiceover for videos, outputs voice.wav/voice.json, rewrites scene timings, supports gemini, clone, kokoro engines.
- `engine:scripts/sfx.py`: Synthesizes transition sounds and music bed, outputs mix.wav from voice.wav using numpy and soundfile.
- `engine:scripts/llm.py`: Routes LLM calls to free-token routers, providers, or Gemini, selecting first successful backend.

## buildwithvish

- [(root)](areas/buildwithvish--root.md) (3): Configure, build, and deploy the Vish site using Cloudflare Workers and Netlify functions. Key: `wrangler.toml`, `README.md`, `netlify.toml`
- [emails](areas/buildwithvish--emails.md) (9): Generate and store welcome email templates and metadata for MailerLite automation. Key: `emails.json`, `welcome-series.md`, `make_emails.py`
- [functions](areas/buildwithvish--functions.md) (3): Handle external API endpoints for Instagram webhook, partner form, and newsletter subscription processing. Key: `ig-webhook.js`, `partner.js`, `newsletter.js`
- [lib](areas/buildwithvish--lib.md) (2): Automate Instagram direct messages and comment replies using keyword matching, DM templates, and HMAC verification. Key: `core.mjs`, `config.json`
- [site](areas/buildwithvish--site.md) (37): Host website pages, AI tutorials, privacy policy, and third‑party scripts for interactive visual effects. Key: `CopyShader.js`, `EffectComposer.js`, `LuminosityHighPassShader.js`
- [src](areas/buildwithvish--src.md) (12): Provide source code for building assets, managing content, and rendering interactive WebGL scenes for the Vish website. Key: `build.py`, `content-guides.js`, `sound.js`
- [src/legal](areas/buildwithvish--src--legal.md) (3): Provide legal pages for data deletion, links, and privacy policy. Key: `data-deletion.html`, `links.html`, `privacy.html`
- [src/long](areas/buildwithvish--src--long.md) (60): Provide long‑form guides and issue articles with metadata for content management. Key: `ad-performance-copilot.html`, `ad-performance-copilot.meta.json`, `ai-privacy-settings.html`
- [tools](areas/buildwithvish--tools.md) (13): Generate, lint, merge, and manage long‑form tutorial pages for AI content pipeline. Key: `check.js`, `slugs.txt`, `merge.py`
- [worker](areas/buildwithvish--worker.md) (1): Route API requests to newsletter, partner, and Instagram webhook handlers in a Cloudflare Worker. Key: `index.js`

## claude-skills

- [(root)](areas/claude-skills--root.md) (1): Provide Claude skill definitions for creator marketing and job search, with descriptions and reference links. Key: `README.md`
- [skills](areas/claude-skills--skills.md) (7): Automate job application, contract review, creator outreach, CV tailoring, and LinkedIn carousel creation for recruiters and creators. Key: `SKILL.md`
- [installed skills](areas/claude-skills--installed-skills.md) (7, name + description per skill): banner-design, brand, design, design-system, slides, ui-styling, ui-ux-pro-max

## engine

- [(root)](areas/engine--root.md) (10): Define brand assets, content rules, and CLI tools for generating LinkedIn carousel posts. Key: `CLAUDE.md`, `PLAYBOOK.md`, `brand-profile.md`
- [.claude](areas/engine--.claude.md) (1): Configure Claude AI settings, specifying environment, enabled plugins, and additional marketplaces. Key: `settings.json`
- [brand](areas/engine--brand.md) (2): Define brand tokens, colors, layout, and locked carousel visuals for consistent UI styling. Key: `tokens.json`, `identity.md`
- [brand/avatar](areas/engine--brand--avatar.md) (3): Create and manage Vish mascot avatars, prompts, and asset manifests for consistent brand representation. Key: `Vish_Mascot_Claude_Guide.md`, `README.md`, `asset_manifest.json`
- [brand/mascot](areas/engine--brand--mascot.md) (25): Define mascot animation specs for Dot v4, including expressions, camera, items, and rendering rules. Key: `README.md`, `dot-focused-cheer.json`, `dot-happy-wave.json`
- [carousel](areas/engine--carousel.md) (7): Generate, style, and render LinkedIn carousel decks as PNG/PDF using AI and Playwright. Key: `templates.py`, `studio.py`, `ai.py`
- [content](areas/engine--content.md) (1): Organize LinkedIn posting schedule, mapping file paths, hooks, and article links for automated publishing. Key: `calendar.md`
- [content/batch-01](areas/engine--content--batch-01.md) (3): Generate LinkedIn posts using brief rules, evergreen topics, and news items. Key: `BRIEF.md`, `evergreen.json`, `news.json`
- [content/batch-01e](areas/engine--content--batch-01e.md) (1): Provide evergreen content items for batch processing, supplying eight predefined JSON entries. Key: `evergreen.json`
- [content/batch-01n](areas/engine--content--batch-01n.md) (1): Provide a batch of nine news items for content generation pipelines. Key: `news.json`
- [content/batch-02](areas/engine--content--batch-02.md) (1): Store six pre‑generated post objects for batch processing and scheduled publishing. Key: `posts.json`
- [content/batch-03](areas/engine--content--batch-03.md) (1): Store six pre‑generated blog posts for batch processing and scheduled publishing. Key: `posts.json`
- [content/calendar](areas/engine--content--calendar.md) (1): Schedule weekly content production, allocate resources, track status, and plan filming for weeks 2‑5. Key: `2026-weeks-02-05.md`
- [content/instagram](areas/engine--content--instagram.md) (3): Organize Instagram content: profile details, weekly post kits, reels, carousels, captions, and scheduling. Key: `profile.md`, `week-02-post-kit.md`, `week-01-post-kit.md`
- [content/shoot-sheets](areas/engine--content--shoot-sheets.md) (5): Generate weekly content shoot plans with legends, defaults, and sheet configurations for October 2026. Key: `2026-10-week-2.json`, `2026-10-week-6-viral.json`, `2026-10-weeks-1-5.json`
- [content/shorts](areas/engine--content--shorts.md) (5): Define, generate, and render animated short scripts with voice, hooks, facts, and publishing metadata. Key: `README.md`, `guide.md`, `script.json`
- [docs](areas/engine--docs.md) (14): Document processes, policies, and configurations for content automation, monetization, hosting, and social media. Key: `llm-router.md`, `instagram-autodm.md`, `monetisation.md`
- [docs/design-library](areas/engine--docs--design-library.md) (148): Provide design tokens and brand guidelines for multiple product design systems. Key: `README-source.md`, `DESIGN.md`, `README.md`
- [edit-kit-docs](areas/engine--edit-kit-docs.md) (5): Document editing guidelines, tools, philosophy, design assets, and third‑party notices for Nate’s AI video workflow. Key: `EDITING-PLAYBOOK.md`, `MOTION_PHILOSOPHY.md`, `TOOLS-AND-API-KEYS.md`
- [examples](areas/engine--examples.md) (1): Demonstrate sample configurations like creator-contract-checks.json for testing slide generation and metadata handling. Key: `creator-contract-checks.json`
- [inspiration](areas/engine--inspiration.md) (5): Collect, document, and analyze external design inspirations to inform style rules and content generation. Key: `log.md`, `style-directions.md`, `README.md`
- [research](areas/engine--research.md) (1): Analyze competitor LinkedIn posts to identify top reactions and extract recurring content patterns. Key: `competitors.md`
- [research/2026-10-06](areas/engine--research--2026-10-06.md) (1): Capture daily backlog snapshot for research tasks, storing generated rules and topic metadata. Key: `backlog-snapshot.json`
- [research/creators](areas/engine--research--creators.md) (24): Provide style guidelines, edit recipes, reference reels, and teardown data for creators. Key: `style-guide-2026-10-14.md`, `edit-recipe-v9-2026-10-22.md`, `references-2026-10-23.md`
- [research/daily](areas/engine--research--daily.md) (2): Collects daily research logs with date, items, and errors for tracking and analysis. Key: `2026-10-06.json`, `2026-10-07.json`
- [research/shorts](areas/engine--research--shorts.md) (1): Define retention rules, hook templates, frame timing, and visual style for faceless animated Shorts series. Key: `viral-animated-explainers-2026-10-23.md`
- [research/viral](areas/engine--research--viral.md) (3): Analyze viral content patterns, hooks, timing, and comment strategies to inform high‑engagement post creation. Key: `attention-playbook-2026-10-15.md`, `teardown-2026-10-07.md`, `day1-intros-2026-10-21.md`
- [scripts](areas/engine--scripts.md) (37): Automate content pipeline tasks: batch creation, rendering, voice, QA, publishing, and asset validation. Key: `weekly.py`, `render3d.py`, `voice25.py`
- [scripts/broll](areas/engine--scripts--broll.md) (1): Download Mixkit stock videos, generate metadata, and save clips for project integration. Key: `stock.py`
- [scripts/reel_edit](areas/engine--scripts--reel_edit.md) (12): Create, edit, and render talking‑head reels from raw footage, applying cuts, grading, and quality checks. Key: `cutplan.py`, `make.py`, `render.py`
- [scripts/research](areas/engine--scripts--research.md) (4): Collect, parse, and analyze external content feeds, social media posts, and video data for research. Key: `fetch.py`, `ig_fetch.py`, `reel_teardown.py`
- [scripts/shorts](areas/engine--scripts--shorts.md) (4): Create short videos with voice narration and sound effects from templates. Key: `render.py`, `voice.py`, `sound.py`
- [style-library](areas/engine--style-library.md) (11): Define, store, and validate visual style specifications, tokens, and registry metadata for content cards. Key: `registry.json`, `GUIDE.md`, `DESIGN.md`
- [style-templates](areas/engine--style-templates.md) (14): Provide reusable visual scene templates with design specs, assets, and agent workflow instructions. Key: `README.md`, `AGENTS.md`, `CLAUDE.md`
- [templates](areas/engine--templates.md) (1): Provide a package.json template for initializing Node projects with predefined scripts, dependencies, and metadata. Key: `package.json`
- [templates/carousel](areas/engine--templates--carousel.md) (5): Render weekly carousel templates with CSS and HTML for guide, checks, edits, and skill pages. Key: `week-series.css`, `guide-doc.html`, `week02-check.html`
- [templates/guide](areas/engine--templates--guide.md) (1): Provide a structured implementation guide template with sections for promise, source, steps, prompts, outputs, troubleshooting, limits, next steps. Key: `implementation-guide.md`
- [templates/three](areas/engine--templates--three.md) (2): Render 3D scenes deterministically using Three.js kit with colors, materials, rounded boxes, and stage template. Key: `kit.js`, `stage.html`
- [templates/video](areas/engine--templates--video.md) (12): Generate video templates for motion, reels, shorts, and night scenes. Key: `motion.html`, `cover.html`, `shorts.css`
- [tests](areas/engine--tests.md) (2): Validate carousel and studio functionalities, ensuring correct rendering, markup, AI draft retries, and brand compliance. Key: `test_carousel.py`, `test_studio.py`
- [topics](areas/engine--topics.md) (5): Manage topic lifecycle: generate, queue, post, track seeds and backlog. Key: `backlog.json`, `posted.json`, `queue.json`
- [video-projects](areas/engine--video-projects.md) (3): Produce, edit, and assemble week‑01 video project files via Python, JSON, and HTML. Key: `week1.py`, `broll.json`, `comp.html`
- [installed skills](areas/engine--installed-skills.md) (136, name + description per skill): 21st-ui, agent-reach, ai-seo, captions-and-clipping, claude-youtube, comment-mining, community-management, competitor-teardown, content-matrix, content-pillars, cross-platform-repurposing, cut-mistakes, cut-silences, dm-script-writer, edit-video, embedded-captions, engagement-routine, faceless-expla...
- [outputs](areas/engine--outputs.md) (59 folders): batch-01 (17), _samples (9), batch-02 (6), batch-03 (6), 2026-10-06-eu-ai-text-watermark (4), flagship (3), guides (3), 2026-10-06-meta-creator-hub (2), _batch (2), _review (2), shorts (2), week02 (2)

## memory

- [(root)](areas/memory--root.md) (7): Define, store, and enforce content creation policies, pipelines, and LLM access rules for automation. Key: `shorts-engine.md`, `linkedin-pipeline-state.md`, `shorts-reference-style.md`

## profile-pipeline

- [(root)](areas/profile-pipeline--root.md) (2): Showcase personal branding, badge links, and curated AI‑tool repositories while configuring Netlify deployment settings. Key: `README.md`, `netlify.toml`
- [linkedin](areas/profile-pipeline--linkedin.md) (11): Generate LinkedIn carousel PDFs, captions, and assets from JSON content with validation and preview images. Key: `theme.css`, `build.py`, `test_build.py`
- [portfolio](areas/profile-pipeline--portfolio.md) (2): Showcases Vish Kumbhar’s digital marketing, growth, and AI portfolio with SEO-friendly index and robots file. Key: `index.html`, `robots.txt`
- [installed skills](areas/profile-pipeline--installed-skills.md) (11, name + description per skill): li-audit, li-carousel, li-comment, li-dm, li-human, li-inbox, li-plan, li-post, li-profile, li-reply, li-repurpose

## project-files

- [linkedin-profile](areas/project-files--linkedin-profile.md) (1): Define LinkedIn cover assets, export script, mockups, evidence map, and source verification for profile. Key: `README.md`
- [shorts](areas/project-files--shorts.md) (9): Organize research, transcripts, metadata, and guides to produce data‑driven YouTube Shorts efficiently. Key: `transcript.json`, `TEARDOWN.md`, `top-reels.json`
