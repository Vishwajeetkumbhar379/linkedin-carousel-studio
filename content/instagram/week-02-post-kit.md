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
| Thu 30 Oct | Reel 2: "How AI edited this video" (3D explainer) | Film this weekend (shoot sheet HOW-AI-EDIT) | EDIT | Board approved, footage needed |
| Sun 2 Nov | Reel 3: Week 2 of 52, "220 companies said no." | Film this weekend (shoot sheet WEEK2), then the v12 edit | (question: 1, 2 or 3) | Script ready, footage needed |
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

## Sun 2 Nov · Reel 3: Week 2 of 52
Script, delivery marks, B-roll and cover: `content/shoot-sheets/2026-10-week-2.json` (key WEEK2), also on the teleprompter page. The edit follows the v12 standard (freeze-frame sticker on "still zero", ending on the "Next week" narrator card).

**Caption** (finalise after filming, keeping only lines you actually said):
```
Week 2 of 52. Remote income so far: zero. So here's my plan.

I'm Vish, 27. I moved to Germany, I've had 220 job rejections, and I'm done waiting for a company to say yes.

Making it, for me, is 3,000 euros a month from anywhere. Three bets:
1. Brands. 850+ creator deals on the brand side, and I can do that work remotely.
2. AI. My last video? Claude edited all of it, and I can build that for other people.
3. This account. I'll show you every week whether it's working.

Which one pays first? Comment 1, 2 or 3 👇

Next week: bet one, I pitch brands for remote work.

#remotework #digitalnomad #buildinpublic #workfromanywhere #startingover
```
- **Cover:** navy framed-print template; stickers "€0 remote income", "220 rejections", "3 bets"; the line "So here's my *plan.*" Build it with `cover.html` once the footage is in.
- **Alt text:** "Vish, week 2 of 52: remote income still at zero, and his three bets to reach 3,000 euros a month from anywhere: brand work, AI workflows and this account."
- **Pinned comment:** "Which bet pays first? 1, 2 or 3. I'll show you the answer in the coming weeks."
- **Audio name:** "Week 2 of 52 · Vish".

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
