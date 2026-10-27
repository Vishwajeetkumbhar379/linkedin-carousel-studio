# Content OS: locked 27 Oct 2026 (Vish's 20 answers)

This file overrides every earlier plan where they differ. Change it only when Vish says "from the next batch, do X".

## Goal and audience
- **Goal:** equal mix of followers, clients or a job, and brand deals. Every post is also portfolio.
- **Audience:** wide on purpose. People starting over, plus marketers, creators and brands.
- **The viewer should think:**
  - "I'm learning so much."
  - "What does he do next?"
  - "I have to comment on this."
- **Priority order:**
  1. Storytelling.
  2. Emotion: hope, anger, recognition, curiosity.
  3. Value.
  4. Motion design.
- **Originality comes second for now.** Take what is proven viral and fill it with Vish's true story.

## Spine: The 52-Week Bet
- **The setup:** 27. He did everything "right", then got 220 rejections and 40k of debt.
- **The bet:** building his own job with AI, in public, for 3,000 € a month from anywhere within 52 weeks.
- **The arcs:**
  - **November:** "the hunt", in Germany. Tests, rejections, first offers.
  - **December 6 to January 6:** "the leap", in Sri Lanka. Working remotely for real, filmed in cafés and while travelling.

## Pillars (IG daily, LinkedIn 5 a week, every reel mirrored to YouTube Shorts)
| Pillar | Format | Per week |
|---|---|---|
| The Bet | "Week N of 52" episode and progress updates with real numbers | 1 to 2 |
| Real Talk / Hot Take | Raw confessionals and spicy-but-true takes. Famous ideas get challenged, never mocked. | 2 |
| Reacts | Green-screen cut-out over a viral clip (5 to 8 s, credited), then his take. "I tried it": a viral AI claim, run for real for 3 to 7 days | 2 |
| Brand-Side | Insider calls from 850+ deals | 1 |
| Built with AI | Tool tests and the machine, in the 3D or Kallaway look. A clone-narrated explainer is allowed when the animation is top level. | 1 |

## Series (each with its own recurring cover and opener)
- **Week N of 52:** the Bet episodes.
- **Real Talk:** confessionals.
- **Hot Take:** "tell me I'm wrong".
- **Reacts:** green-screen cut-out over a viral clip.
- **Worth It or Slop?:** he tests a viral AI tool or claim for real, shows the real cost and result, then gives a verdict.
  - On screen: two tick boxes, WORTH IT and SLOP. The verdict lands on one at the end.
  - Model: @itstundeanthony "Fact or Hype?" (DeKHCW7iBvJ: 8,992 likes, 3,448 comments). Proof first, live cost on screen, a comment keyword for the setup guide.
- **Brand-Side.**
- **Animated chapters (1 a week):** his story, painted, with his own voice. For example "How I ended up 40k in debt".
  - **Model:** @ink.industries_ (Ddd2Z3sPDEA, 23,994 likes). A painterly gouache character on light paper, simple scenes.
  - **Free route only:**
    - FLUX stills through `NVIDIA_API_KEY`, in one locked style prompt.
    - A character sheet of the painted Vish, made from his real photos, so he looks the same in every shot.
    - Motion done in code: parallax layers, camera moves, small character moves, brush transitions.
    - Free Hugging Face image-to-video only when the quota allows.
  - **Limits:** it won't move as smoothly as paid Seedance, and that has been accepted. The painted Vish appears only in these videos and always gets the AI label.

## Hooks: the Triple Hook (from @kallawaymarketing De_5mQ0R8PE, locked)
Every hook has three beats inside the first 1 or 2 sentences. Say each one, show it and write it on screen.
1. **Context, immediately.** What the video is about, in the first words. Delaying it even to the second half of the first sentence raises the skip rate.
2. **Lean.** Make them curious in one direction: proof or a stat, their pain or the benefit they want, or something shocking or unexpected.
3. **Contrarian snapback.** Then yank them the other way: the twist that breaks the direction they were leaning.

Example: "220 companies said no. [context + lean] So I stopped applying. [snapback]"

On top of the Triple Hook, every hook must also be:
- Controversial or emotional (spicy but true).
- 12 words or fewer.
- Readable on frame one.

## Rules
- **No topic twice on Instagram.** LinkedIn and Shorts may reuse a topic in a new form.
- **Openness:** debt and money numbers, low moments and weekly real numbers are OK. **Family is not shown.** His past relationship is never shown.
- **Clone voice:**
  - Bridges and extra lines are fine. A few fully narrated explainers are fine.
  - He jumps in on camera for the personal lines ("but trust me...").
  - Never use it for the hook unless the whole video is narrated.
  - Always add the AI label.
- **Audio first:**
  - A clip-on mic (Lightning, for the iPhone 13) from shoot 1.
  - The Voice Isolator and the week2.py fixes. No speed-up.
  - Level-matched to -14 LUFS. No jumps in loudness.
  - Sound design at podcast-studio level: music follows the story (the "slow down time" moment slows the music down too).
- **Music:**
  - The trending song is cut into our mix to fit the edit.
  - Vish adds the same song in Edits at volume 0, so Instagram counts it as trending audio.
  - Our composed track is the fallback.
  - Risk: Instagram may mute a reel. Keep the clean file as a backup.
- **Recall (one brand):**
  - Locked colours: night #14161B, lamp amber #E7A15A, paper #F3EEE5, accent #3049E0.
  - Fonts: Instrument Serif headlines with one amber italic word, Inter Tight / Geist.
  - The same caption style, the same "Hey, I'm Vish" sticker opener, and the "Week N of 52" mark.
  - Styles may vary per pillar. The palette, type and opener never do.
- **Formats:** 9:16 by default. Test 3:4 and 4:5 reels, and keep what performs.
- **Length follows the script:** takes and reacts 15 to 30 s, stories 35 to 60 s.
- **Comments:**
  - Teaching posts carry a keyword and a guide.
  - Stories end on an easy question.
  - Hot takes end on "tell me I'm wrong".

## How we work
- **One shoot every 2 weeks, 3 to 5 h,** using the modular pack (`content/shoot-sheets/SHOOT-SESSION-1.md`). Each shoot gives 30 to 45 posts.
- **Weekly batch:** files, covers, captions, song pick with start time, posting times. Vish approves once and schedules. Ready to post, no drafts.
- **Feedback:** one round per batch, applied from the next batch. Only a broken file (wrong word, audio bug) gets fixed inside the current batch.
- **Self-review before delivery:** the post-scorer skill on hooks and captions, word-for-word transcript check, loudness, one contact sheet. Nothing ships below the bar.
- **Token rule:**
  - Short chat, results only. Detail only when Vish asks.
  - Python scripts do the work. Look things up with graphify (`graphify query`), not by reading whole files.
- **Offers he's building toward:**
  - AI content systems.
  - Influencer marketing consulting.
  - A full-time role.
  - Brand sponsorships from AI tools.
  - Travel and yoga brand work. He has taught yoga, and Sri Lanka in December is a showcase for both.

## Decision log (add one line per change Vish asks for; newest last)
- **27 Oct:**
  - No topic repeats on Instagram.
  - Audio fixes in week2.py.
  - Clip-on mic.
  - Trending song cut into the mix and muted in Edits.
  - Free route for animation.
  - The painted Vish only in animated chapters.
  - The series "Worth It or Slop?".
  - The Triple Hook.
  - Travel and yoga offers.
