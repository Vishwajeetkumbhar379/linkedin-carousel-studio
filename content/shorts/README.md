# Inside AI: animated Shorts (YouTube Shorts + Instagram Reels, one file)

Faceless animated explainers about the AI people use every day, shown from the inside. Zack D. Films' formula
(an everyday action, x-ray view, calm narrator, loop ending) in Vish's night-studio look with speedy_devv-style
word-box captions. Research: `research/shorts/viral-animated-explainers-2026-10-23.md`; measured teardown of the top Shorts
(Zack D. Films, Kallaway, speedy_devv) in project files `shorts/research/SUMMARY.md` (not in git: others' media).

## Format (locked 23 Oct 2026)
- **One file for both apps:** 1080x1920, 30 fps, H.264 + AAC 48 kHz, -14 LUFS, 35 to 50 s (always under 60 s).
- **Safe zones:** key visuals between y 230 and 1270, captions at y 1300 to 1470, nothing important below 1500
  (both apps put the username, caption and buttons there) or in the right 120 px from y 900 down.
- **Look:** ink background with a drifting grid, film grain, vignette; one amber accent #E7A15A; Inter Tight caps for
  captions, Instrument Serif italic for the one "turn" line, Geist Mono for labels and sources. Series tag
  `INSIDE AI · EP N` top left, `@BUILDWITH.VISH` top right.
- **Captions:** up to 3 words at a time, each word flips up in 3D as it's said, an amber box with corner handles
  slides to the spoken word.
- **Voice:** ElevenLabs George (premade), `eleven_multilingual_v2`, the whole script in one request, lines re-spaced
  with 0.2 to 0.28 s gaps and 0.45 to 0.5 s at scene breaks (`pause_after`).
- **Sound:** a sound on every visual event, a dark pulsing bed ducked under the voice (`scripts/shorts/sound.py`).

## Script rules
1. Hook line: 12 words or fewer, second person, names the everyday action ("the second you hit send").
   Frame 0 is already mid-action (no intro, no logo, no name).
2. 8 to 11 lines, 95 to 120 words, spoken at about 160 to 170 wpm (30 to 45 s). One visual idea per line.
   **A new picture every 1.5 to 2 s, never a static frame** (measured 23 Oct: Kallaway's organic winners hold
   1.5 to 2.0 s a shot, his boosted posts 2.4 to 4.1 s; Zack has few hard cuts but the camera never stops: dives
   into a cross-section, zooms out to a scale reveal). Lines over 4 s get a second beat (camera move or new prop).
3. An open loop by 30% ("Here's the weird part"), the biggest number or reveal after 60%.
4. Close on a number people will argue with, then the two-sided question that leads back into line 1 (the loop).
   No spoken call to action; a comment keyword, if any, goes in the caption only.
5. Every number has a source and date in `facts`. Illustrations (like token picks) carry no fake numbers.
6. British spelling in captions and posts, no em dashes, no hype words.

## Make one
```
python scripts/shorts/voice.py content/shorts/<slug>            # needs ELEVENLABS_API_KEY (or CLAUDEELEVENLABS_API)
python scripts/shorts/render.py content/shorts/<slug> --stills  # QA stills in out/shorts/<slug>/stills
python scripts/shorts/render.py content/shorts/<slug> --jobs=4  # out/shorts/<slug>/video.mp4
```
`--estimate` on voice.py writes silent timings so the animation can be built before the voice exists.
Each episode has its own animation page, `templates/video/shorts/<template>.html` (shared look in `shorts.css`).

## Posting
Same MP4 on both. YouTube: title from `publish.title`, description = caption, tags. Instagram: caption, cover = a
clean frame, share to feed. Pin `publish.pinned_comment` on both. Never post without Vish's go-ahead.

## Episode ideas (queue)
- What happens when you ask AI to make an image (noise to picture, step by step)
- Why AI confidently makes things up (it guesses, it never checks)
- What an AI agent does when you say "book me a table"
- Where your ChatGPT chats actually go
- Why AI is bad at counting the r's in strawberry (tokens again)
- What happens when you talk to ChatGPT voice mode
