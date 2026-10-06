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
