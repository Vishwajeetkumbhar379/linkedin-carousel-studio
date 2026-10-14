# Reference style: @kallawaymarketing (Format A) and @justyn.ai (Format B)

Measured 14 Oct 2026 from the 5 reels Vish sent (4 Kallaway, 1 Justyn) with `scripts/research/reel_teardown.py`
(shot cuts, word timings, sound hits, contact sheets per shot, 10 fps strips). Frames in `research/creators/teardown/<id>/`.
We copy the editing system, not their footage, scripts or wording.

## The numbers

| | Kallaway (4 reels) | Justyn (1 reel) | Vish take 1 |
|---|---|---|---|
| Length | 31 to 108 s | 54 s | 37 s |
| Speech pace | 209 to 242 wpm | 243 wpm | 165 wpm |
| Gap between phrases (median) | 0.16 to 0.22 s | 0.24 s | ~0.2 s after the edit |
| First word | 0.0 s | 0.0 s | 0.0 s after the edit |
| Sound hits | 4 to 5 per 10 s | 6 per 10 s | 2 per 10 s (too few) |
| Music under voice | about 4 to 6 dB | about 2 to 4 dB | 13 dB (too quiet) |
| Layout changes | every 3 to 5 s, graphics move inside every shot | every 2 to 7 s | every 3 to 4 s |

## Kallaway's three shots (they alternate the whole reel)

1. **Full-frame talking head.** His dark room (practical lights, neon strip), cap, medium close-up. Caption: ONE word at a time,
   white, bold grotesk, no box, centred at about 62% height. A key word now and then in italic serif instead ("*Application*").
   Used for the turn lines and the punchlines, 2 to 5 s each.
2. **Split.** Dark near-black canvas with a faint dot or square grid on top (about 72% of the height); the speaker in a ROUNDED
   RECTANGLE box at the bottom (about 88% of the width, 25% of the height, radius ~24 px), not a cut-out. The one-word caption
   sits just above the box. The canvas carries:
   - a section title at the top: small, white, Title Case, two lines, ONE word in italic serif ("This Is How AI *Changed*
     Social Media Forever"). It types in word by word, about 0.1 s per word, each word fading up from a blur.
   - the explainer graphic for the line: timelines with red dots and years (fast whip pan with motion blur between eras),
     a script document with the hook lines lighting up red, a numbered list with a highlight bar on the current item,
     cards of real example videos (rounded, thin white border) that pop in scale 0.6 to 1 in 0.3 s and keep playing,
     outlined pill labels ("Tactical Edu.", "Application"), dashed arrows with a label, glowing 3D objects (red infinity
     loop, casino chips, cards, light-trail roads), big numerals for steps (1 Stakes, 2 Big Question...) that build up a
     framework diagram step by step.
3. **Full-screen B-roll.** Cinematic stock or AI video that acts the word out (cards dealt on a casino table, a hand
   holding a phone scrolling, a person thinking, macro textures, boxes exploding). One-word caption centred on top. 1 to 3 s.

Light variant for the opener: pale grey grid canvas, black title with italic serif word, a collage of real example
thumbnails, speaker box at the bottom.

**CTA:** "Comment "*word*" to get the video link" title (italic serif on the keyword, sometimes a red highlight box behind
"To Get The Video"), a thumbnail card of the full resource (a YouTube-style card or a glowing framework render), speaker box below.

## Kallaway's scripts (same skeleton every time)

1. Hook: "Here's how to [outcome] so [extreme] it's [basically unskippable / scientifically impossible to skip]." or
   "There's a new type of [thing] that is starting to crush on [platform]." or "This is the best [resource] in the world for [job]."
2. Name it: "This is called the [Named Method]." (Desire Hook Method, Dopamine Addiction Loop, Application Content)
3. Size + borrowed authority: "It's only 4 steps, but it uses the exact same psychology casinos use..."
4. "Step one is [X]." One-line definition, the common mistake ("Most hooks tease secret information. But..."), "For example..."
5. Steps two to four, same shape. Visual: the framework builds up one numbered piece per step.
6. CTA: "Comment [WORD] and I'll send you [the full video / the link]."

## Justyn's tool demo (Format B)

- Proof first: "I didn't edit a single second of this video. Claude did." Then every claim is SHOWN as it is said
  ("make it moody and the colours go dark" and the grade goes dark on that word).
- Giant serif headline BEHIND him (cut-out depth: text sits between the wall and his body), cream on deep green.
- Captions: 2 to 4 words in a dark-green box, serif, the key word in a second colour.
- Multi-angle: desk medium shot, a wide shot squatting in the room, standing with a prop. Whip-blur transitions between angles.
- Social proof: a 3x3 grid of other creators' posts on the same trend, cards popping in.
- UI B-roll: the real editor timeline as a floating dark card; a YouTube-style card for the CTA resource.
- Big sans words in a coloured box for emphasis ("BIGGER").

## What this means for Vish's edits (applies from 14 Oct)

- Default layout set = Kallaway's three shots, recoloured to the night-studio palette (night #14161B canvas with a faint grid,
  lamp #E7A15A for the red-dot role, accent #3049E0 for highlights). Speaker box at the bottom, not a cut-out, for splits.
  Cut-out only for the Justyn-style text-behind-subject hook.
- Captions: one word at a time, white bold, no box; key words in italic Newsreader.
- Every line gets a visual that MOVES: whip pans with motion blur, pop-in cards, type-on titles, red-dot indicators.
- B-roll in every reel: full-screen clips 1 to 3 s at least every 10 s. Sources in order: Vish's own B-roll from the shoot
  sheet shot list, real screen recordings of the tools named, process footage from our own pipeline, free stock
  (Pexels/Pixabay API key needed), never invented results.
- Sound: a music bed 5 to 6 dB under the voice, a hit every ~2 s on a visible move (whoosh on whips, pop on cards, click on
  UI, impact on big numbers), real recorded SFX from `.claude/skills/media-use/audio/assets/sfx` (Pixabay licence).
- Delivery: aim for 190 to 210 wpm on camera; the edit tightens gaps to ~0.15 s but never speeds the voice.
- Shoot sheets add a B-roll shot list (3 to 5 clips, 3 to 5 s each, filmed on the same phone) and one alternate angle.
