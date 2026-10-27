# Week 2 of 52: post kit (3 posts, one theme)

**Theme: the plan, 3 bets for a remote income.**
- The episode lives it.
- Carousel A teaches bet two (AI: how Claude edited the Week 1 reel).
- Carousel B gives the insider angle on bet one (brands: what they check before they pay a creator).

Built 23 Oct 2026. Every caption is SlopMonster clean, and every claim comes from `brand-profile.md` or the Week 1 project files.

**Times:** post at 18:30 Berlin for now. After 2 weeks, switch to the best hour in Insights (Professional dashboard > Total followers > Most active times).

| Day | Post | File | Keyword | Status |
|---|---|---|---|---|
| Mon 27 Oct | Carousel A: "I didn't edit my intro reel. Claude did." | `out/week02/carousel-a-edit/slides.zip` (10 slides) | EDIT | Ready to post. DM link live once the buildwithvish branch is merged |
| Thu 30 Oct | Reel 2: "How AI edited this video" (3D explainer) | `video-projects/how-ai-edit/out/how-ai-edit-v1.mp4` | EDIT | Footage in, rendering 27 Oct |
| Sun 2 Nov | Reel 3: Week 2 of 52, "220 companies said no." | `video-projects/week-02-episode/out/week2-9x16.mp4` | FRICTION | Footage in (25 to 26 Oct), edit 27 Oct |
| Sat 1 Nov | Carousel B: "Brands don't pay for followers." | `out/week02/carousel-b-check/slides.zip` (10 slides) | CHECK | Ready to post. DM link is live already |

## Mon 27 Oct · Carousel A (EDIT)
**Caption:**
```
I didn't edit my intro reel. Claude did. Every cut, caption and sound.

I'm Vish. Last week I posted Week 1 of 52: 40K in debt, no job, building a remote income so I can travel the world.

I've never been an editor. So I filmed it on my phone and let Claude Code do the edit as code: it transcribed every word, cut my best takes, built every sticker and caption as a small web page, and laid a sound under each one.

My part was the feedback. 12 drafts of plain English, like "start with Hey, I'm Vish" and "don't make it look cheap".

The tools are free and open source: faster-whisper, FFmpeg, Playwright. Claude Code needs a paid plan.

Want the setup and the five prompts I used? Comment EDIT and I'll DM you the free guide.

#claudeai #aivideoediting #contentcreation #buildinpublic #remotework
```
- **Alt text:** "A 10-slide guide: how Claude Code edited Vish's Week 1 reel from phone footage with free tools: transcribe, cut on word boundaries, one visual per line, graphics as web pages, a sound for every visual, and 12 rounds of feedback."
- **Pinned comment:** "Comment EDIT for the free guide. On Thursday I'll show you, step by step, how the AI did it."
- **Music:** none, or something quiet from Instagram's library (carousels can carry a song).

## Thu 30 Oct · Reel 2: How AI edited this video (changed 27 Oct: footage in, film rendered)
File: `video-projects/how-ai-edit/out/how-ai-edit-v1.mp4` (9:16, -14 LUFS). Lines 8 and 9 are his ElevenLabs clone: turn on Instagram's **AI info** label when posting.

**Caption:**
```
My Week 1 reel was 39 clips on my phone. No editing app touched it.

I filmed. Claude did the rest:
1. It listened to every word and gave each one a start and an end time.
2. It cut between the words, not between the sentences.
3. It cut me out of every frame, so the captions sit behind me.
4. Every caption and sticker is a tiny web page, photographed 30 times a second.
5. It took 12 rounds of my feedback to get it right.

Two lines in this video are my AI voice clone, because I didn't film them. Everything else is me.

Comment EDIT and I'll send you the prompts.

#claudeai #aivideoediting #contentcreation #buildinpublic #aitools
```
- **Pinned comment:** "Comment EDIT for the free guide with the prompts. Sunday: Week 2 of 52."
- **Alt text:** "A 3D explainer by Vish: how Claude turned 39 phone clips into his Week 1 reel, from word timestamps to cuts, cut-outs, captions rendered as web pages, sound and 12 rounds of feedback."

## Sun 2 Nov · Reel 3: Week 2 of 52 (final, 27 Oct: built from his voice note and his answers)
The edit is `video-projects/week-02-episode/edit/week2.py`, about 48 s:
1. The hook has no face.
2. He walks in at the barber.
3. The haircut on the beat.
4. The music drops, then the rewind.
5. The 3,000 euro goal.
6. Reduce friction.
7. FRICTION and the "Next week" card.

**Files:**
- **Instagram:** `out/week2-instagram-9x16.mp4` (no music in it, on purpose).
- **LinkedIn and YouTube Shorts:** `out/week2-9x16.mp4` (our own music, with the hard drop).
- **Cover:** `out/week2-cover.jpg`.

**Trending song (Instagram only):**
1. When posting, tap the music note, search **"What You Waiting For?" (Gwen Stefani)** and pick the chorus ("What you waiting for?").
2. Set the volume to **Original audio 100, Music about 15**, so the song sits under his voice.
3. Check for the trending arrow first. If it's gone, pick another arrowed song that fits "take a chance".

Why: the reel then shows on the song's page. It's discovery, not a guaranteed boost (`research/viral/trending-audio-2026-10-27.md`).

**AI label:** turn on "AI info". Two lines are his clone: "220 rejections. Honestly, I'm done waiting…" and "This week: profiles, portfolio, plan…"

**Caption:**
```
220 companies said no. So I'm building my own job.

Week 2 of 52. The goal: 3,000 euros a month, from anywhere.

Step one wasn't a laptop. It was a haircut. Then, before I chase a single client, I'm reducing friction:
1. Profiles on the freelancing platforms
2. A one-page portfolio
3. A plan for what I sell

Two lines in this video are my AI voice clone, because I didn't film them. Everything else is me.

Comment FRICTION and I'll send you my checklist.

#buildinpublic #remotework #freelancing #startingover #jobsearch
```
- **Alt text:** "Vish, week 2 of 52: after 220 job rejections he decides to build his own job. He gets a haircut, sets a goal of 3,000 euros a month from anywhere, and starts by reducing friction: freelance profiles, a portfolio and a plan."
- **Pinned comment:** "Comment FRICTION for the checklist. Next week: did it work?"
- **Keyword:** FRICTION. The guide is `/resources/reduce-friction`, on the buildwithvish branch, and goes live with "merge".
- **Story the same day:** share the reel with a poll, "Would you quit waiting for a yes? Yes / Not yet".

## Sat 1 Nov · Carousel B (CHECK)
**Caption:**
```
Brands don't pay for followers. After 850+ creator deals on the brand side, these 5 checks decided who got paid.

I'm Vish. I worked on the brand side of influencer marketing, and the creators who delivered were rarely the biggest. They were the best fit.

1. Audience fit (30%): country, age, language, interests vs the brief
2. Content fit (25%): would the product look natural in their last 12 posts?
3. Engagement health (20%): real comments, steady numbers
4. Cost (15%): the rate against the reach
5. Brand safety (10%): past controversies, rival deals, tone

Brands: score creators this way. Creators: make your media kit answer these five.

Comment CHECK and I'll DM you the full rubric, the prompt and how to build the scoring sheet.

#influencermarketing #brandpartnerships #ugc #creatoreconomy #contentcreator
```
- **Alt text:** "A 10-slide guide by Vish: the five checks brands use before paying a creator, with weights: audience fit 30%, content fit 25%, engagement health 20%, cost 15%, brand safety 10%. The numbers on the example slides are illustrations."
- **Pinned comment:** "Comment CHECK for the rubric. Next week I pitch brands myself, and you'll see every reply."

## Comment automation for this week
- **EDIT:** goes to `buildwithvvish.com/go/edit`, then `/resources/ai-edit-stack`. Live after the `claude/autodm-v2-resources` branch is merged.
- **CHECK:** goes to `/go/check`, then `/#read-shortlist-creators-with-ai`. Live already on v1 (plain link DM); the follow-check button comes with the merge.
- **The 1, 2, 3 answers on the Reel aren't keywords.** Reply to them yourself; they're the best conversation starters this week.
- Until Meta App Review is approved, DMs only reach accounts with a role on the app, so send the guide link by hand to anyone the bot can't reach yet.

## After posting
- Reply to the first comments within the hour, in your own words. Never automate replies on other people's posts.
- **Monday 3 Nov, weekly report:**
  - from Insights: reach, non-follower reach %, saves, shares, comments, follows;
  - from `/api/autodm-stats`: keyword comments, DMs, clicks.

  Then keep / test / change / stop.

## LinkedIn this week (changed 27 Oct: LinkedIn gets its own posts, `content/calendar/2026-11-month-plan.md`)
LinkedIn has no auto-DM: answer keyword comments yourself with the guide link. Post at 08:30 Berlin.

**Tue 28 Oct · text story (T4):**
```
220 companies said no.

So I'm building my own job.

I moved to Germany a year ago to do my master's. Before that, I spent 5 years in social media and influencer marketing and signed 850+ creator deals on the brand side.

Since I got here: 220 job rejections.

So I started a 52-week challenge. The goal fits on one line: 3,000 euros a month, from anywhere.

Week 2 starts with one rule. Reduce friction before you chase anything:

1. Profiles. Be findable in two places: one freelance marketplace, and here.
2. Portfolio. One page, three pieces of proof, real numbers only.
3. Plan. Three offers, and four weeks I can actually do next to my thesis.

No tripod, no mic, no new camera. I'm not spending money before I earn it.

If you hire for influencer marketing or AI in marketing: what makes a profile worth a reply?

#buildinpublic #influencermarketing #careerchange
```
**Wed 29 Oct · PDF carousel:** upload `out/week02/carousel-a-edit/carousel.pdf` as a document, title "How AI edited my intro reel". Text: the Instagram caption of Carousel A, with "Comment EDIT and I'll send you the guide" as the last line.

**Fri 31 Oct · native video:** the How AI edited this video reel as a 4:5 MP4 (exported after the render), with the Instagram caption.
