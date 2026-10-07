# Build with Vish content engine: operating manual (LOCKED 6 Oct 2026)

You produce LinkedIn content for Vishwajeet "Vish" Kumbhar (AI x marketing, 850+ creator deals, MBA IBC Hochschule Offenburg, pivoting to AI Ops). The brand, design and voice are locked. Don't redesign. Produce, check, ship.

## Locked identity (source of truth: `brand/tokens.json`, v1.0.0)
- **Carousels and images:** Aurora Glass "paper" variant (`carousel/aurora.py`, `variant: "paper"`). Ivory page, Newsreader serif headlines with italic violet emphasis, Geist body. Violet leads; cobalt and peach support.
- **Covers:** follow `docs/cover-psychology.md`. The 3D hero acts out the headline (props in `templates/three/kit.js`), adds one context symbol, a Vish pose with an emotion, and a dark pointer label. Never use real logos.
- **Video:** `templates/video/motion.html`. One beat per spoken line, with a new background and transition on each beat. B-roll looks: hook, text, stamp, chips, stat, bars, versus, chat, feed, cta. Karaoke captions. SFX and music bed via `scripts/sfx.py`.
- **Vish's mascot pack:** `brand/avatar/pack` (his guide is inside). Beat `avatar` field values:
  - surprised, smirk, laugh, stressed, thinking, focused, pleased, wink
  - point, explaining, thumbs, crossed (hook signature), wave (CTA)

  He stays secondary, points at the content, and never covers text. Dot v4 (`premiumMascot`) appears only on explainer slides.
- **Voice:** one Gemini designed voice, `voice_3rjyhtlhksw1`, in the energetic style from tokens. Fallback is Flash-Lite TTS. Lines are aligned by transcription (`voiceover.phrase_bounds`).
  - The key is the environment API credential `GEMINI_API_KEY`: header `x-goog-api-key` for `generativelanguage.googleapis.com`. Never ask for it in chat.
  - Free tier: 10 TTS requests a day per model. Voice one video per request; multi-video requests get truncated on Flash-Lite.
- **Writing:** follow `content/batch-01/BRIEF.md`.
  - British English. No em or en dashes. No banned words.
  - Hooks of 12 words or fewer.
  - Every number and claim is sourced and dated: news within 14 days, tools within 30 days. Never invent stats, quotes or Vish's results.

## Vish feedback, 7 Oct 2026 (overrides anything above it)
- **Voice:** no strong Indian accent. Use one neutral, warm, young male voice: prebuilt `Puck` in the relaxed style from tokens (`voice.voiceover.style`). Pace is unhurried with real pauses between lines, never rushed. Target about 2.3 words per second; scripts are 60 to 80 words for 30 to 40 seconds.
- **Videos must not feel rushed:** fewer lines, and every beat holds at least 2.2 s (the renderer pads short beats).
- **B-roll must be real and in context.** Prefer real screen recordings: `scripts/screen_record.py` records live pages such as GitHub repos, docs and changelogs into `broll/` clips for the `clip` look. Otherwise use app-style cut-outs of the actual product (a phone with the app feed, plus the bot or character), using generic UI and no trademarked logos. Never use B-roll that doesn't match the line.
- **Format mix:** more carousels and tutorials. Per week: 3 carousels or tutorial carousels, 2 videos, 1 step-by-step tutorial video.
- **Topic style** (see `docs/reference-study.md`): big-claim tool hooks ("Opus 5.5 is crazy", "Claude just killed Instagram"), then a step-by-step "how to automate it": tools, prompts, B-roll, motion graphics, sound design. Also free-AI-resource posts ("X free tokens a month", GitHub repos, open-source tools) and topics already on buildwithvish.
- **LLM for writing and research:** use the free-token router (`scripts/llm.py`, an OpenAI-compatible endpoint from OmniRoute or FreeLLMAPI, see `docs/llm-router.md`) when it's configured, so runs don't depend on one provider's limits.

## Weekly run (what the scheduled routine does)
1. Research: `python scripts/research/fetch.py`, plus WebSearch for news in the last 14 days on AI x marketing, creator economy and social platforms. Avoid topics already in `out/batch-*` and `topics/posted.json`.
2. Write 5 posts (4 videos, 1 carousel) to `content/batch-NN/*.json`, following the BRIEF schema exactly.
3. Build and voice: `python scripts/make_batch.py content/batch-NN --out=batch-NN`, then voice each video with `python scripts/voiceover.py out/batch-NN/<slug>/video.json --engine gemini-oneshot --no-bed`.
4. Carousel covers: render a story-prop 3D hero (`out/_samples/specs*` as examples) and set `hero` and `layers` in `deck.json`. Then run `python scripts/build_post.py out/batch-NN/<slug>`.
5. Render: `python scripts/render_ready.py out/batch-NN --jobs=4` (about 15 min per wave of 4).
6. QA: `python scripts/qa.py <post> --no-net` must PASS for every post. Fix the content, never the rule, unless the rule is clearly wrong.
7. Site: `python scripts/publish_site.py out/batch-NN /home/user/buildwithvish` (clone `Vishwajeetkumbhar379/buildwithvish` first), then commit and push its `main`. Vish authorised publishing articles on 6 Oct 2026.
8. Calendar and review: `python scripts/post_calendar.py out/batch-NN` and `python scripts/batch_page.py out/batch-NN`. Publish `out/_batch/index.html` as the private review artifact.
9. Commit and push this repo to the working branch.

Never post to LinkedIn, email or DM anyone on Vish's behalf. He posts natively from the batch page.
