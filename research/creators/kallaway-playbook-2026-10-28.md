# Kallaway and Paritosh Anand: the playbook (28 Oct 2026)

What this is: the methods two creators teach, written as rules Vish can use, plus a script checklist, a template, 12 ideas and 3 full scripts.
- **Kallaway** (@kallawaymarketing) for hooks, scripting, storytelling and retention, plus packaging and finding ideas.
- **Paritosh Anand** (@iamparitoshanand), the main creator alongside Kallaway (Vish, 28 Oct), for fun scripts, stakes, delivery and topics.

We learn the method, never the wording. Every script still goes through `voice.md`, the CONTENT-OS quality gate and SlopMonster.

Builds on, and doesn't repeat: `kallaway-2026-10-23.md`, `charles-zheng-2026-10-24.md`, `../viral/consistent-viral-2026-10-27.md`, `../viral/attention-playbook-2026-10-15.md`.

## 0. Sources and limits (read first)

**What worked:**
- **YouTube channel listings.** Titles and view counts for every video on @kallawaymarketing and on Paritosh's two channels, read on 28 Oct 2026 with `yt-dlp --flat-playlist`.
- **Kallaway, 20 long-form videos:**
  - 12 read as full transcripts from public transcript pages on sozai.app. These are third-party auto-transcripts, so they're second-hand and may have small errors.
  - 8 read as public AI summaries on videohighlight.com. Treat these as summaries, not his exact words.
- **Kallaway, 6 Instagram reels:**
  - 4 transcripts were already in `teardown/`.
  - 2 were new: DcqiQesO_R9 and Db-zJhiuXP3, fetched with `ig_fetch.py` and transcribed with `reel_teardown.py`.
- **Paritosh:**
  - about 1,000 titles with view counts (672 Shorts, 344 long videos)
  - public descriptions and chapter lists of his teaching videos
  - the description of his First Principles podcast episode.

**What was blocked (skipped, no workarounds):**
- **YouTube subtitles and watch pages:** every video returned "Sign in to confirm you're not a bot" after HTTP 429. No cookies, no other route.
- **Paritosh's Instagram:**
  - his reel links aren't indexed by search
  - rendering his public profile page to list reel codes was refused as a bot-check workaround, so it was dropped.
- **Paritosh's spoken words:** we have no transcript of any of his videos, and most of them are in Hindi or Hinglish. His rules below therefore come from his packaging data, his own chapter names and what he says he does. They don't come from his exact lines.
  - **To confirm his beats and pacing:** Vish sends 3 to 5 reel links he loves, and we run `ig_fetch.py` and `reel_teardown.py` on them. The public embed works when we have the code.

**Not used:**
- the Bengali-only transcript of "How to Become A Master Storyteller (It'll Blow Up Your Business)"
- the thumbnail video, which is long-form only and doesn't apply to us.

### Kallaway sources (views on 28 Oct 2026)
| Video | Views | Read as |
|---|---|---|
| [How To Become A Master Storyteller](https://www.youtube.com/watch?v=t5Z-Q1bg1tU) | 2.9M | transcript |
| [How Social Media Algorithms Actually Work](https://www.youtube.com/watch?v=8cQidXgtGmU) | 1.2M | summary |
| [Give me 15 mins, and I'll make your hooks impossible to skip](https://www.youtube.com/watch?v=2byPP_9F0-Q) | 1.1M | summary |
| [How to Create Irresistible Hooks](https://www.youtube.com/watch?v=LmXpbP7dD48) | 869K | transcript |
| [How to Become a Storytelling Genius (Dopamine Ladders)](https://www.youtube.com/watch?v=jtmstMt4WLc) | 675K | transcript |
| [The Neuroscience of Addictive Storytelling](https://www.youtube.com/watch?v=KyC8r-zitVE) | 364K | transcript |
| [I Studied 100 Viral Hooks, These 6 Will Make You Go Viral](https://www.youtube.com/watch?v=xnOe8aA9Pmw) | 328K | summary |
| [Game Theory Is The Cheat Code to Social Media](https://www.youtube.com/watch?v=o2nP0lfIsso) | 214K | transcript (key parts) |
| [How to Build an Audience That's Obsessed With You](https://www.youtube.com/watch?v=cuVyTmbOZjk) | 195K | transcript (key parts) |
| [The Psychology of Killer Hooks](https://www.youtube.com/watch?v=pNIYikmYsyw) | 193K | transcript |
| [The ONLY 6 Words You Need to Hook ANY Viewer](https://www.youtube.com/watch?v=S9FlxFv9dxg) | 193K | transcript |
| [7 Storytelling Mistakes That Are KILLING Small Creators](https://www.youtube.com/watch?v=wgXGimZvDa4) | 156K | transcript |
| [Say This in Your Videos, It'll Improve Your Storytelling by 10x](https://www.youtube.com/watch?v=pcnrzBwoVUk) | 146K | summary |
| [How to Speedrun Social Media](https://www.youtube.com/watch?v=fk6LExgMPxI) | 122K | transcript (key parts) |
| [How to Script Viral Videos 10x Faster](https://www.youtube.com/watch?v=_Z11mjFh2zY) | 116K | summary |
| [The Science-Based Method To Create Irresistible Ideas](https://www.youtube.com/watch?v=pirnGDCZD3Y) | 93K | summary |
| [Copy This Hook, It'll Blow Up Your Social Media](https://www.youtube.com/watch?v=8VolLwMCLuY) | 80K | transcript |
| [How to write a script so good viewers can't stop watching](https://www.youtube.com/watch?v=0f6_pRAIJjI) | 72K | summary |
| [The 'Invisible' Hook That Makes Your Videos Impossible to Skip](https://www.youtube.com/watch?v=vmsDhY9ITlI) | 67K | transcript |
| [Why The Smartest Creators I Know Focus on Packaging, Not Content](https://www.youtube.com/watch?v=jZCupmAOMAE) | 57K | summary |

Reels (likes and comments from the public embed):
- [DaiCxAkOpNb](https://www.instagram.com/reel/DaiCxAkOpNb/), the dopamine addiction loop: 54,415 likes, 11,933 comments.
- [DcqiQesO_R9](https://www.instagram.com/reel/DcqiQesO_R9/), the script format: 18,060 likes, 20,172 comments (28 Oct).
- [Db-zJhiuXP3](https://www.instagram.com/reel/Db-zJhiuXP3/), the Illusion of Novelty: 12,808 likes, 4,331 comments (28 Oct).
- [Dac3WJ-Ov3b](https://www.instagram.com/reel/Dac3WJ-Ov3b/), the desire hook.
- [DdEPZQSOsx2](https://www.instagram.com/reel/DdEPZQSOsx2/), application content.
- [DauxXTtu2v_](https://www.instagram.com/reel/DauxXTtu2v_/), the reference database.

**A naming note.** CONTENT-OS calls the 3-beat hook the "Triple Hook" (from his reel De_5mQ0R8PE). In his long-form videos, though, "triple hook" means the three hook *components*: text, visual and spoken. He calls the three *beats* context lean-in, scroll-stop interjection and contrarian snapback. Both ideas are below, under their own names.

---

## A. Kallaway: the rules

### A1. Ideas and research ("idea mining", scraping outliers)

**K1. Mine outliers. Don't brainstorm from a blank page.**
- His Idea Mining System has 3 steps:
  1. Find outliers.
  2. Break them into the 7 "idea Lego bricks": topic, angle, hook, story structure, visual format, key visuals, audio.
  3. Hold the winning bricks and remix the rest.
- **Why:** proven ideas beat gut feel, because audiences repeat their behaviour.
- **Source:** [The Science-Based Method To Create Irresistible Ideas](https://www.youtube.com/watch?v=pirnGDCZD3Y).

**K2. An outlier is measured against its own channel, not against the world.**
- Outlier score = a video's views divided by that channel's normal views.
- His filters: 5x or more, 5% engagement or more, and a recency window that suits the topic.
- Look in this order:
  1. same content type, same platform
  2. same type, other platform.

  Tweets and blogs don't transfer to video.
- **Why:** a 5x video on a small account teaches more than an average video on a big one.
- **Source:** the same video.
- **For us:** YouTube view counts are public, so `yt-dlp --flat-playlist` gives the views, and the score is views divided by the channel median. On Instagram we rank by likes and comments (PLAYBOOK §12).

**K3. The law of interesting: shock is the gap between what they know and what you tell them.**
- Before writing, collect 5 to 10 facts.
- Score each one from 1 to 100 for "would most people not know this?".
- Build the script on the top scores.
- **Why:** a weak fact kills a good hook.
- **Source:** [How to Script Viral Videos 10x Faster](https://www.youtube.com/watch?v=_Z11mjFh2zY).

**K4. Use a story lens: your angle on a common topic.**
- **His example:** when everyone covered Taylor Swift at the Super Bowl, he covered her business impact on the NFL.
- **Why:** the topic is shared; the lens is yours.
- **Source:** [How To Become A Master Storyteller](https://www.youtube.com/watch?v=t5Z-Q1bg1tU).

**K5. New information or new delivery, at least one.**
- If the niche is crowded, change the examples, the metaphors or the format, or borrow from another category.
- **Why:** otherwise nothing cuts through.
- **Source:** [How to Speedrun Social Media](https://www.youtube.com/watch?v=fk6LExgMPxI).

**K6. Make boring topics feel new with the Illusion of Novelty.** Four steps:
1. **New Reveal:** something has changed.
2. **Contrast Framing:** old belief against the new one.
3. **Urgency:** it just happened, or it's about to close.
4. **Bullseye Proof:** why they should believe you.
- **Why:** novelty is a feeling you can build.
- **Source:** [reel Db-zJhiuXP3](https://www.instagram.com/reel/Db-zJhiuXP3/).

**K7. Pick the content type that's working now.**
- His 2026 map:
  - **"Edu slop"** (just saying words with no insight) has largely stopped working.
  - **Tactical education** still works, but only with novel topics.
  - **"Application content"** has the most room: the creator shows the skill in the video (case studies, hypotheticals, live builds).
- **Why:** proof inside the video beats a claim.
- **Source:** [reel DdEPZQSOsx2](https://www.instagram.com/reel/DdEPZQSOsx2/).

**K8. Stay in one lane so the algorithm can match you.**
- Each video is first shown to a small sample of mostly non-followers. Wider reach depends on how that sample reacts.
- Mixed topics blur who your sample should be.
- **Why:** the algorithm can't place a scattered account.
- **Source:** [How Social Media Algorithms Actually Work](https://www.youtube.com/watch?v=8cQidXgtGmU).

### A2. Hooks

**K9. Interrupt theory.**
- **What the hook is for:** it triggers a "freeze point", an orienting response, the "wait, what was that?".
- **The two answers it gives:** what this is about (subject) and what I get if I stay (outcome).
- **The 4 S's:**
  - **Subject:** crystal clear.
  - **Stakes:** a reason to care.
  - **Speed:** compression, not talking fast.
  - **Super clear:** one possible meaning.
- **Why:** if a viewer has to think for half a second, they swipe.
- **Source:** [The Psychology of Killer Hooks](https://www.youtube.com/watch?v=pNIYikmYsyw).

**K10. The 3-step hook formula.**
1. **Context lean-in:** the topic in the first line, plus a reason to lean in. Use common ground, a benefit or pain, a metaphor, or something that blows their mind.
2. **Scroll-stop interjection:** one "but" line that stuns them.
3. **Contrarian snapback:** still on topic, but the opposite direction to the lean.
- **Why:** curiosity comes from being pulled one way and yanked back.
- **Source:** [How to Create Irresistible Hooks](https://www.youtube.com/watch?v=LmXpbP7dD48).

**K11. The 6 hook power words.** A good hook stacks:
- **The 4 core ones:**
  1. a subject (I, we, you, or a name)
  2. an action
  3. an end state
  4. a contrast (from A to B).
- **The 2 optional ones:**
  5. a proof word (for example "again")
  6. a time word ("in 5 months").
- **Why:** each brick adds curiosity; missing one leaves a hole.
- **Source:** [The ONLY 6 Words You Need to Hook ANY Viewer](https://www.youtube.com/watch?v=S9FlxFv9dxg).

**K12. The desire hook: a dream outcome plus a relatable character with no unfair advantage.**
- **Variations:**
  - **"About Me":** I did X using Y.
  - **"If I":** if I had to do X, I'd do Y.
  - **"To You."**
  - **"Can You":** is it possible to do X under Y conditions?

  He says there are 5; the transcript names these 4.
- Add "one simple thing" or "3 steps" so it feels possible.
- **Why:** buyers lock onto a dream outcome, then drop it if the character had an edge they don't.
- **Sources:**
  - [Copy This Hook, It'll Blow Up Your Social Media](https://www.youtube.com/watch?v=8VolLwMCLuY)
  - [reel Dac3WJ-Ov3b](https://www.instagram.com/reel/Dac3WJ-Ov3b/).

**K13. Know the archetypes, then choose.**
- **The 6 hook archetypes:**
  - Fortune Teller (the future)
  - Experimenter (I tried it)
  - Teacher (here's how)
  - Magician (a visual stun)
  - Investigator (a hidden secret)
  - Contrarian (against common belief).
- **The 9 formats:**
  - secret reveal
  - case study
  - comparison
  - question
  - education
  - list
  - contrarian
  - personal experience
  - problem.
- In each niche, 1 or 2 formats win, so check your outliers.
- **Why:** each niche already rewards one or two formats, so you start from those.
- **Sources:**
  - [I Studied 100 Viral Hooks](https://www.youtube.com/watch?v=xnOe8aA9Pmw)
  - [How to Script Viral Videos 10x Faster](https://www.youtube.com/watch?v=_Z11mjFh2zY).

**K14. The 4 hook killers, and their fixes.**

| Killer | Fix |
|---|---|
| Delay | Topic in the first 1 to 2 s |
| Confusion | Sixth-grade words, active voice, one meaning |
| Irrelevance | Say "you" and "your", and name a pain they have |
| Disinterest | Build a contrast, stated (A against B) or implied |

- **Why:** each killer is a different reason people swipe in the first 2 seconds, so each needs its own fix.
- **Source:** [Give me 15 mins, and I'll make your hooks impossible to skip](https://www.youtube.com/watch?v=2byPP_9F0-Q).

**K15. Sharpen the hook.**
- **Speed to value:** short form has a 4-second timer.
- **Lead with the benefit:** "If you want better sleep, take magnesium", not "magnesium is one of 21 minerals".
- **Borrow a known name:** a brand, a celebrity or a movement makes the unknown feel familiar (the transcript calls this "cult hopping").
- **Staccato:** hook sentences go short, then later ones grow longer.
- **Why:** in short form you have about 4 seconds before people decide.
- **Source:** [How to Create Irresistible Hooks](https://www.youtube.com/watch?v=LmXpbP7dD48).

**K16. Text hook rules.** He calls this the most important hook component, because eyes hunt for text.
- **What it says:** the subject's name, plus one of:
  - a pain reminder
  - a dream-outcome teaser
  - a "future changed" line.
- **How to write it:**
  - Use specific numbers ("22 days", not "a few weeks").
  - Use power words.
  - Keep it to 2 lines at most, broken where the phrase breaks naturally.
  - No punctuation except quotation marks or brackets.
  - No "and", "that", "but" or "therefore".
- **How to place it:**
  - It stays on screen about 3 s.
  - It sits about a third down from the top, never over eyes or mouth.
- **Why:** people read faster than they listen, so the text decides first.
- **Source:** [The Psychology of Killer Hooks](https://www.youtube.com/watch?v=pNIYikmYsyw).

**K17. Mine and remix power words.**
1. List your own best hooks.
2. Find phrases that repeat in the winners. He found "scientifically impossible to skip" in two of his top four.
3. Twist them ("psychologically impossible to resist"). Never copy them.
- **Why:** they're validated, but still yours.
- **Source:** the same video.

**K18. Align the three hooks.**
- **The test:** text, visual and spoken must say the same thing. Muted, the visual should tell you roughly what's said.
- **The 5 types of visual hook:**
  - graphic or text overlay
  - pattern interrupt
  - subject motion
  - effect or transition
  - visual selection.
- **The 80/20:** move your body, move the visual, or move text. Not too much motion, not too little ("like a deer noticing movement").
- **Why:** misalignment is the mistake he sees business owners make most.
- **Sources:**
  - [The Psychology of Killer Hooks](https://www.youtube.com/watch?v=pNIYikmYsyw)
  - [How to Create Irresistible Hooks](https://www.youtube.com/watch?v=LmXpbP7dD48).

### A3. The lock-in zone (the 1 to 3 sentences after the hook)

**K19. The lock-in zone matters as much as the hook.**
- **What has to happen there:**
  - the hook claim is confirmed, so it's no bait and switch
  - the viewer runs a rapid trust check.
- **Four things raise trust:**
  - how you look
  - production quality ("care equals trust")
  - how much you resemble the viewer
  - proof, the "trust anchor", which matters most.
- **Why:** with so many fake gurus, a strong claim alone doesn't hold anyone.
- **Source:** [The Psychology of Killer Hooks](https://www.youtube.com/watch?v=pNIYikmYsyw).

**K20. Six ways to fill the lock-in zone.** Combine them where they fit.
1. **Tease the proof:** a concrete number. Only when it's real.
2. **Tease the result they want,** when there's no hard proof.
3. **Rapid contrast:** the common belief against yours. Use it when the topic is "mid".
4. **The magic box:** name the method ("It's called the dopamine addiction loop"). His go-to.
5. **Objection handling:** answer the first reason to scroll.
6. **Bold-claim double down:** repeat the load-bearing word ("boring topics... boring businesses").
- **Why:** the hook only buys a chance. These lines earn the stay.
- **Source:** [The 'Invisible' Hook That Makes Your Videos Impossible to Skip](https://www.youtube.com/watch?v=vmsDhY9ITlI).

### A4. Script structure

**K21. The short-form script format.**
1. Hook.
2. Lock-in zone.
3. Body block 1.
4. Rehook 1.
5. Body block 2.
6. Rehook 2.
7. (Optional) body block 3.
8. (Optional) close.
9. CTA to an aligned lead magnet.
- He says this structure alone did "billions of views".
- **Why:** a fixed skeleton means you only fill the blocks, and the rehooks are already built in.
- **Source:** [reel DcqiQesO_R9](https://www.instagram.com/reel/DcqiQesO_R9/).

**K22. Write in 4 steps, and name the emotion first.**
1. Collect the interesting facts (K3).
2. Write one target emotion at the top of the page. His 6 buckets:
   - awe
   - amusement
   - excitement
   - anger
   - surprise
   - sadness or empathy.
3. Choose a hook structure, then a story structure.
4. Write it. Then ask:
   - Is it interesting?
   - Is it as compressed as possible?
   - Does the hook work?
   - What do I feel at the end?
- **Why:** emotion is what gets the like and the share.
- **Source:** [How to Script Viral Videos 10x Faster](https://www.youtube.com/watch?v=_Z11mjFh2zY).

**K23. Choose one of 7 story structures.**

| Structure | Outline |
|---|---|
| Breakdown | hook → context shock → explanation → why it matters → outro |
| Newscaster | hook → full context → short analysis → outro |
| Case study explainer | hook → framework in 2 to 4 pieces → outro |
| Listicle | hook → 3 to 5 separate items → outro |
| Problem solver | problem → agitate → solve |
| Tutorial | hook → dependent steps → outro |
| Personal story | hook → beginning, middle, end → outro |

- **Why:** beginners do best on a structure their niche has already proven.
- **Source:** [How to Script Viral Videos 10x Faster](https://www.youtube.com/watch?v=_Z11mjFh2zY).

**K24. Don't jumble the W's.**
- **School order:** where, when, who, what, how, why.
- **Online order:**
  1. what and why
  2. who and how
  3. when and where.
- **Example:** "The future of entertainment is going to look different. Disney's CEO is worried. He said it at a conference."
- **Why:** half the viewers are gone by 30 s, so lead with what matters to them.
- **Source:** [7 Storytelling Mistakes](https://www.youtube.com/watch?v=wgXGimZvDa4).

**K25. Use the modern story arc, not the school bell curve.**
- Open at about 70 out of 100 intensity.
- Spike the first conflict early, to about 90.
- Release, then build to the next peak, and repeat.
- **Why:** most viewers leave before a slow "rising action" gets good.
- **Source:** the same video.

**K26. Write the last line first.**
- He calls it "the last dab": memorable enough to share on its own.
- In short form it should set up the first line, because the video loops.
- Write the first and last lines, then fill the middle.
- **Why:** you can only build tension towards an ending you already know.
- **Source:** [How To Become A Master Storyteller](https://www.youtube.com/watch?v=t5Z-Q1bg1tU).

**K27. One through line.**
- Read every line and ask: does it add needed context, or is it a tangent?
- Use sixth-grade words, short sentences and active voice.
- Restate the key point.
- Name your concepts.
- **Why:** every tangent is a moment where people get lost and leave.
- **Source:** [How to write a script so good viewers can't stop watching](https://www.youtube.com/watch?v=0f6_pRAIJjI).

**K28. Atomic sharability.**
- Shrink the idea to a unit a viewer can repeat to a friend after one watch. His example is Paul Revere: "the British are coming".
- Say a complex point twice: once as you'd tell a colleague, once as a metaphor for a child.
- **Why:** if they can't retell it, they won't share it.
- **Source:** [7 Storytelling Mistakes](https://www.youtube.com/watch?v=wgXGimZvDa4).

### A5. Storytelling devices

**K29. The dance between context and conflict.**
- **The rule:** between beats, the joining word is "but" or "therefore", never "and then". He takes it from the South Park creators' talk at NYU.
- **His example:** his Stanley Cup video has four "but then" loops in the first 30 s.
- **Why:** conflict opens a loop, context closes it, and "and then" just piles up detail.
- **Source:** [How To Become A Master Storyteller](https://www.youtube.com/watch?v=t5Z-Q1bg1tU).

**K30. The addiction loop: stakes, big question, head fake, rehook.**
- **Stakes** need three things:
  - a character to root for
  - something at risk
  - urgency ("within a week" beats "eventually").

  They don't have to be life and death, just relevant to the viewer.
- **The big question** must be specific enough for a viewer to guess the answer. "Something crazy happened" doesn't work.
- **The head fake** breaks that guess, but is logical in hindsight ("the dragon was a prisoner, not a guard"). A random twist is a cheap one.
- **The rehook** closes one loop and opens the next in the same breath. Joining phrases:
  - "which would have been great, except..."
  - "but here's the problem with that..."
  - "and that's when I realised...".
- **Why:** dopamine fires on prediction, not on the reward.
- **Sources:**
  - [The Neuroscience of Addictive Storytelling](https://www.youtube.com/watch?v=KyC8r-zitVE)
  - [reel DaiCxAkOpNb](https://www.instagram.com/reel/DaiCxAkOpNb/).

**K31. The dopamine ladder: 6 rungs.**
1. **Stimulation:** colour, motion, brightness in the first 1 to 2 s.
2. **Captivation:** an open question.
3. **Anticipation:** the viewer guesses the answer.
4. **Validation:** you close the loop with something non-obvious.
5. **Affection:** they like the messenger.
6. **Revelation:** "this person reliably helps me".
- **Why:** rungs 5 and 6 are why faces build fans faster than faceless accounts.
- **Source:** [How to Become a Storytelling Genius (Dopamine Ladders)](https://www.youtube.com/watch?v=jtmstMt4WLc).

**K32. A villain, and someone to root for.**
- **The villain:** it can be an idea, a system or a group, not only a person.
- **The hero:** build common ground with the viewer so they root for them.
- **Why:** the gap between hero and villain is contrast, and contrast makes people curious.
- **Source:** [7 Storytelling Mistakes](https://www.youtube.com/watch?v=wgXGimZvDa4).

**K33. Rhythm and tone.**
- **Rhythm:** vary sentence length: some short, some medium, the odd long one. His example is Gary Provost's "Don't just write words. Write music."
  - Put one sentence per line; the right edge should look jagged.
- **Tone:** write and film as if to one close friend, like a voice note.
- **Why:** sentences of the same length drone, and people swipe on the drone. A friend's tone feels like a chat, not a pitch.
- **Source:** [How To Become A Master Storyteller](https://www.youtube.com/watch?v=t5Z-Q1bg1tU).

**K34. Story locks.**
- **Term branding:** name the thing.
- **Embedded truths:** "when you try this", not "if".
- **Thought narration:** say what the viewer is thinking.
- **Negative frames:** "Stop doing X" beats "Do Y", because of loss aversion.
- **Loop openers:** one every 20 to 30 s in short form.
- **Contrast words:** but, actually, instead, turns out, except, yet.
- **Why:** these small word choices close the gaps where doubt creeps in.
- **Source:** [Say This in Your Videos](https://www.youtube.com/watch?v=pcnrzBwoVUk).

### A6. Retention and pacing

**K35. Front-load value.**
- Give the first real hit of value inside the hook, or right after it.
- "Anything after they click off might as well be a black screen."
- **Why:** you're not aiming for full completion. You're buying the next 30 seconds.
- **Source:** [How to Create Irresistible Hooks](https://www.youtube.com/watch?v=LmXpbP7dD48).

**K36. Rehook at about 20 to 25 s in short form.**
- Remind them of the pain, and hint that a better answer is coming.
- **Why:** attention runs on a timer, and the rehook resets it.
- **Sources:**
  - [How to write a script so good viewers can't stop watching](https://www.youtube.com/watch?v=0f6_pRAIJjI)
  - [Say This in Your Videos](https://www.youtube.com/watch?v=pcnrzBwoVUk).

**K37. The three numbers that matter.**
- average watch time
- engagement rate (likes, comments and shares over views)
- share of the viewer's session.
- **Why:** these are the signals the platform reads before it shows you to more people.
- **Source:** [How Social Media Algorithms Actually Work](https://www.youtube.com/watch?v=8cQidXgtGmU).

### A7. Visual hooks and the signature look

**K38. Own your stimulation.**
- If everyone copies the same colours and motion, viewers go numb to them.
- A palette and motion of your own cut through.
- **Why:** stimulation earns the first second, and a copied look stops earning it.
- **Source:** [Dopamine Ladders](https://www.youtube.com/watch?v=jtmstMt4WLc).

**K39. The signature visual style has four parts: look, set, shot framing and edit.**
- Dial it in once, then stop reinventing it.
- Choose a story structure that plays to your strength: visual-led if the visuals are your edge, talk-led if your words are.
- **Why:** a look people recognise stops the scroll before they've read a word.
- **Source:** [How to Speedrun Social Media](https://www.youtube.com/watch?v=fk6LExgMPxI).

### A8. Packaging

**K40. Short-form packaging has three parts:**
- the hook (first 3 to 5 s)
- the cover
- the first caption line.

**Why the cover matters:**
- It's what people see when a reel is sent in a DM.
- It's what they see on the profile grid, which drives binges and follows.

**The caption line:** it should tease what's coming.
- **Source:** [Why The Smartest Creators I Know Focus on Packaging](https://www.youtube.com/watch?v=jZCupmAOMAE).

**K41. A series makes people binge.**
- About 4 to 5 minutes watched earns a follow.
- **Hard series:** numbered ("30 lessons before 30").
- **Soft series:** the same opener and look every time.
- If you can't keep up a daily hard series, run a soft one.
- **Why:** one view becomes several when the next episode is obvious.
- **Source:** [How to Speedrun Social Media](https://www.youtube.com/watch?v=fk6LExgMPxI).

### A9. CTA and the comment engine

**K42. CTA to an aligned lead magnet.**
- The free thing directly continues the video's topic.
- The keyword is one word.
- His best comment rates come when the free thing is a tool:
  - a database: [DauxXTtu2v_](https://www.instagram.com/reel/DauxXTtu2v_/), 2.87 comments per like
  - a doc for a script format: [DcqiQesO_R9](https://www.instagram.com/reel/DcqiQesO_R9/), 1.12 comments per like.
- **Why:** the viewer already wants the next step, so the CTA just hands it over.
- **Sources:** those reels and [Db-zJhiuXP3](https://www.instagram.com/reel/Db-zJhiuXP3/).

**K43. Shares come from a strong emotional payoff at the end, plus a "super share".**
- **A super share:** when another creator reposts you because your idea is novel enough to make them look good.
- **Why:** a passive viewer's share reaches a few people. A creator's reaches thousands.
- **Source:** [Game Theory Is The Cheat Code to Social Media](https://www.youtube.com/watch?v=o2nP0lfIsso).

**K44. Fans form in layers.**
- **Layer 1, signal:**
  - relevant topics
  - a non-obvious frame
  - proof.
- **Layer 2, belief:** the viewer walks away thinking differently. A relatable character who has already done it helps, as does a big change for little effort.
- **Why:** high signal earns attention, and changed beliefs earn loyalty.
- **Source:** [How to Build an Audience That's Obsessed With You](https://www.youtube.com/watch?v=cuVyTmbOZjk).

---

## P. Paritosh Anand: the rules (main creator, alongside Kallaway)

**Who:** Paritosh Anand, @iamparitoshanand.
- **Two YouTube channels:** I AM PARITOSH ANAND, and Paritosh Anand: Raw & Unfiltered.
- **How he describes himself:** a 27-year-old entrepreneur and storyteller from India, running a communication course (Introvert to Icon) and a clothing brand.

**The numbers below** are YouTube views read on 28 Oct 2026, across his 672 Shorts and 344 long videos. The methods come from his own chapter names and descriptions. Each one says how sure we are.

**P1. Fun is on purpose.**
- **What he says he does:**
  - he plays a character online
  - he mixes knowledge with "bakchodi" (Hindi slang for banter and fooling around)
  - his stories are "calculated".
- **The data:** on his main channel, his playful personal videos have a median of 34K views, against 18K for everything else. These are titles with mother, prank, Bali, Goa or vlog in them, and the biggest is 2M ("INDIAN Mother REACTS to Bali Vlog").
- **Why:** the laugh keeps people there long enough for the lesson.
- **Source:** the First Principles episode chapters at 18:56, 22:17 and 24:25 ([MeXoBQQ8nVQ](https://www.youtube.com/watch?v=MeXoBQQ8nVQ)), and the channel list.
- **Vish's version:**
  - the fun comes from himself
  - his AI as a sidekick
  - travel mishaps and small self-mocking lines.
- **Never family** (CONTENT-OS).

**P2. Call out one identity in the first line.**
- **His lines:** "For every introvert out there", "if you're in your 20s", "if you're ambitious but lazy".
- **The data:** his "introvert" Shorts have a median of 24K, against 13K for all his Shorts.
- **Why:** people self-select in. It's the same job as Kallaway's topic clarity, but aimed at a person, not a subject.
- **Source:** the Shorts lists on both channels.

**P3. Promise a small count.**
- **His titles:** "3 things", "3 friends", "3 signs", "3 doors", "2 sides".
- **The data:**
  - numbered Shorts have a median of 20K, against 13K for all his Shorts
  - his top Short, at 3.5M, is "Your Life will change if you do these 3 things".
- **Why:** it's finite, easy to finish, and a loop stays open until number 3.
- **Source:** [wMOfq1QeIsY](https://www.youtube.com/watch?v=wMOfq1QeIsY) and the Shorts lists.

**P4. Say it, don't ask it.**
- **The data:** Shorts titled as questions have a median of 8K, the weakest pattern in his catalogue. Commands and statements do better ("Stop Chasing Your Goals.", 206K).
- **Why:** a question asks the viewer to work; a statement gives them something to react to.
- **Source:** the Shorts lists.

**P5. Time-box the promise.**
- **His long-form packaging:** "watch these 22 minutes if you want to stop overthinking" (1.1M), "give me 19 minutes and I'll make you dangerously confident".
- **The data:** his 14 time-boxed titles have a median of 128.5K, against 22K for the channel. That's almost 6 times as much.
- **The formula:** time + the viewer's condition + outcome. It's Kallaway's time word (K11) and desire hook (K12) in one.
- **Why:** people commit more easily to a short, fixed time with a clear payoff.
- **Source:** [rjqm7rErug8](https://www.youtube.com/watch?v=rjqm7rErug8), [cid00ELnzTk](https://www.youtube.com/watch?v=cid00ELnzTk).
- **Vish's version:** on covers and first lines, only when the video really delivers in that time.

**P6. Your own life is the proof.**
- **His arc:** trek guide, then working with Raj Shamani, then owning businesses; no money in 2019; a Bali trip planned with ₹0. He repeats it in his descriptions and podcast chapters.
- **Why:** it's the "relatable character who did it" from K12, and it's the stakes from K30, built into the creator.
- **Sources:**
  - the descriptions of [rjqm7rErug8](https://www.youtube.com/watch?v=rjqm7rErug8) and [cid00ELnzTk](https://www.youtube.com/watch?v=cid00ELnzTk)
  - [MeXoBQQ8nVQ](https://www.youtube.com/watch?v=MeXoBQQ8nVQ) chapters 08:44 and 11:46.
- **Vish's version:**
  - quit a good job
  - 4 years remote in India
  - stuck 6 months in a 9 to 5
  - 220 rejections
  - a flight booked to Sri Lanka.

**P7. One stupidly simple rule, said like a catchphrase.**
- **His examples:**
  - His 1.1M overthinking video is built on "Bhaad mein. Dekhi jayegi." (roughly "to hell with it, we'll see").
  - Another rule of his: "Jeet gaya toh zindagi badlegi, aur haar gaya toh? Main." (roughly "if I win, my life changes; if I lose? I've still got me"). These are my rough translations.
- **Why:** it's the atomic, quotable line from K28, and the line people repeat to each other.
- **Source:** the descriptions of [rjqm7rErug8](https://www.youtube.com/watch?v=rjqm7rErug8) and [cid00ELnzTk](https://www.youtube.com/watch?v=cid00ELnzTk).
- **Vish's version:** only his real lines, from brand-profile.

**P8. Paint a picture.**
- **His masterclass chapters:**
  - "The concept of Painting A Picture"
  - "Definition of a 'Good Story'"
  - "The Elements"
  - "The Format of a Story"
  - "The Most Important Part of a Story".
- We have the chapter names, not the content. The plain reading: a scene the viewer can see (a place, an object, a moment). It's the same as Kallaway's "paint the picture" (K28 source, mistake 7).
- **Why:** a picture in the viewer's head holds attention better than an abstract point.
- **Source:** [Learn STORYTELLING in 46 minutes](https://www.youtube.com/watch?v=Lx_rPy9fyx0) (210K).

**P9. Three golden keys: relatability, one core emotion, voice dynamics.** Plus a warning: "Stop trying to sound 'interesting'".
- **Why:** one feeling per piece, carried by the delivery, not the vocabulary. This matches K22.
- **Source:** the chapters at 09:20 and 28:10 of [give me 57 minutes, i'll make you a master at communication & storytelling](https://www.youtube.com/watch?v=9E4V51p2bKM).

**P10. The voice is an instrument: pitch and cadence, plus pauses placed on purpose.**
- **Why:** the same words land differently depending on how they're said.
- **Source:** the chapter at 39:40 of the same masterclass, and [Master Voice Modulation: 3 Secrets](https://www.youtube.com/watch?v=V-QnqwHEG94).
- **Vish's version:**
  - faster on the setup
  - slower and a little quieter on the honest line
  - a short breath after the stakes line
  - never a pause before the punchline (PLAYBOOK §11).

**P11. Brand the framework with letters.**
- **His frameworks:**
  - P.R.O.O.F. (a 90-day plan)
  - Q.U.I.T. (when to quit)
  - O.R.S. (Observe, Reflect, Shoot) for starting conversations
  - Speed-Demand-Proof for choosing a skill.
- **Why:** this is Kallaway's term branding (K34) and magic box (K20). A name makes it ownable and easy to remember.
- **Sources:** [pA7eCdHaz8w](https://www.youtube.com/watch?v=pA7eCdHaz8w), [4QgX1dub7Rc](https://www.youtube.com/watch?v=4QgX1dub7Rc), [9E4V51p2bKM](https://www.youtube.com/watch?v=9E4V51p2bKM), [f83GmBGeSlE](https://www.youtube.com/watch?v=f83GmBGeSlE).

**P12. A raw shelf, and volume.**
- **The data:** his "Raw & Unfiltered" Shorts have a median of 17K, against 3.5K on his main channel's Shorts, and his 3.5M Short is a RAW one. The RAW channel is also newer, so part of that gap may be timing.
- **His system** (his own figures, not checked):
  - he describes 113 pieces of content a week: long recordings cut into shorts, 4 Instagram content types, Trial Reels, a 7-day life cycle per short, master sheets and SOPs
  - his podcast description talks about nearly 900 posts a week across his distribution.
- **Why:** raw, simple and frequent beats polished and rare. That's what CONTENT-OS already decided with the Daily Take.
- **Sources:** [How I Create 113 Pieces of Content Every Week](https://www.youtube.com/watch?v=RATfR2fMcEI) chapters, and [MeXoBQQ8nVQ](https://www.youtube.com/watch?v=MeXoBQQ8nVQ).

**Not for Vish:**
- the "Indian mother" reaction and prank format (family is never shown)
- Hinglish slang
- anything from his "Clean Lie" storytelling module that bends facts (we only state true things)
- the long keyword lists he pastes into Shorts descriptions, which include other creators' names.

---

## B. Five other creators: core lessons

### @charles.zhengg (3D code explainers)
Source: our study `charles-zheng-2026-10-24.md`, covering:
- De0BAl8B3mY: 41,840 likes
- Der5mJsBmwP: 17,482 likes
- De818_Hh51D: 63.2K likes (`references-2026-10-27.md`).

**The rules:**
1. **Open on something the viewer is touching or experiencing right now,** in the present tense ("This is a grain of sand").
2. **Promise to see inside** ("let's zoom in"), then climb a causal ladder. Each sentence adds one step and one new name.
3. **Make scale physical:** "in the time it took you to blink", "100 billion fit on your nail".
4. **Change tempo only where the words name a tempo.** Drop the music out on the key beat.
5. **End where you began,** so the video loops and gets sent on.

### @100xengineers
Source: [DY2GRVfN4bZ](https://www.instagram.com/reel/DY2GRVfN4bZ/), 134,657 likes and 94,404 comments; transcript in `teardown/`.

**The rules:**
1. **Line 1 is a loss plus a borrowed giant:** "Everyone uploading PDFs to Claude is basically wasting their tokens, and Microsoft had a free solution to this for months."
2. **Explain the mechanism with exact numbers** (tokens per page), so the loss feels real.
3. **Name the fix, then stack authority on it:** a free tool, its GitHub stars, "a Microsoft tool".
4. **Give the benefit as a figure,** then a second reason it works.
5. **CTA: one keyword for a specific asset** ("the link and the full guide").

### @avigrondin
Source: [DeNZCx2uINC](https://www.instagram.com/reel/DeNZCx2uINC/), 20,117 likes and 49,139 comments; transcript in `teardown/`.

**The rules:**
1. **A villain verb in 4 words:** "Claude just murdered LinkedIn."
2. **Free, plus a count that grows:** "it's not one skill, it's over 11".
3. **Run through the list fast,** and say out loud which item is your favourite.
4. **Answer the fear before they raise it.** For him, it's AI detection.
5. **An effort cap, then one keyword:** "super easy to install", "comment LinkedIn".

### @justyn.ai
Source: [DeUUFJQu8cw](https://www.instagram.com/reel/DeUUFJQu8cw/), with its transcript in `teardown/` and `style-guide-2026-10-14.md`.

**The rules:**
1. **Proof first, and the video is the proof:** "I didn't edit a single second of this video. Claude did."
2. **Show each claim at the moment you say it** ("make it moody, and the colours go dark").
3. **Get ahead of the disbelief:** "I know nothing about video editing."
4. **Name the difference:** "lots of people are doing this right now. My way is a little different because..."
5. **One keyword for a specific asset** (a walkthrough video), then a follow line.

### Greg Isenberg
**Sources:**
- his reel DezH6sPRIvY ("How to not write AI slop", in `references-2026-10-27.md`)
- two episodes of his YouTube show, read as public summaries:
  - [$30M Writer: Never write AI slop again](https://www.youtube.com/watch?v=YuOSyRj3sXg) (173K, guest Nicolas Cole)
  - [How I use Google Veo3 to create viral videos](https://www.youtube.com/watch?v=gWkhUd-LWTs) (345K, guest PJ).

  Rules 3 to 5 are the guests' lessons, as presented on his show.

**The rules:**
1. **No slop in 3 moves:**
   - pick a side
   - write in your own voice
   - use your own data.
2. **Make every step a physical prop** that acts out the idea. He uses a paper desk with dark devices.
3. **Commodity content is what everyone says; personality and original content are yours.**
   - Write from "I", not "you should".
   - Personal stories can beat credentials.
4. **You "own" a topic by being associated with it.** That comes from volume on one subject, plus a recognisable format.
5. **Find the twist before you produce anything.**
   - Ask AI for many twists.
   - Expect most to be bad, and keep pushing.

---

## C. The script checklist (every script must pass all of these)

Tick each one. A single "no" means the script goes back.

**Hook (0 to 3 s)**
- [ ] 1. The subject is named in the first 5 words (K9, K14).
- [ ] 2. The hook is 12 words or fewer and holds context, lean and snapback within the first 2 sentences (CONTENT-OS, K10).
- [ ] 3. It has a subject, an action, an end state and a contrast, plus a proof or time word if one is true (K11).
- [ ] 4. **Identity callout:** the hook or line 2 names who it's for (P2).
- [ ] 5. It's a statement or a command, not a question (P4).
- [ ] 6. **Text hook:**
  - 2 lines at most, 3 to 7 words
  - no punctuation except quotation marks
  - no and, that, but or therefore
  - on screen 3 s (K16).
- [ ] 7. **Mute test:** the frame-1 visual tells you the topic, and text, visual and voice say the same thing (K18).

**Lock-in (3 to 10 s)**
- [ ] 8. Sentences 2 and 3 use one of the six lock-in methods, and any proof is a fact from brand-profile (K20).
- [ ] 9. **Stakes are clear:** who, what's at risk, and why now (K30).

**Body**
- [ ] 10. There's one specific big question the viewer can try to answer (K30).
- [ ] 11. There's at least one head fake that makes sense in hindsight (K30).
- [ ] 12. Zero "and then" between beats, and at least 2 "but", "so" or "therefore" turns (K29).
- [ ] 13. A rehook lands by 20 s, about word 65 (K36).
- [ ] 14. The first useful thing or honest feeling arrives by 8 s (K35).
- [ ] 15. There's one fun beat before the end: a self-mocking line, an absurd contrast or a sidekick moment (P1).
- [ ] 16. A scene the viewer can picture: a place, an object or a moment (P8).

**Words**
- [ ] 17. One target emotion is written at the top of the script, and the read-through still produces it (K22, P9).
- [ ] 18. One sentence per line, the line lengths vary (a jagged right edge), and no three lines in a row are the same length (K33).
- [ ] 19. Everyday words only, and any technical word is explained in 5 words or fewer (K27, voice.md).
- [ ] 20. There's an atomic line a viewer could repeat to a friend, ideally the last line, and the last line leads back into the first (K26, K28, P7).
- [ ] 21. **Vish's voice:**
  - contractions
  - his openers allowed ("So...", "Honestly...")
  - no slogans of our own (his real quotes are fine)
  - no banned words
  - British spelling
  - no em or en dashes
  - digits for numbers.

**Facts and ending**
- [ ] 22. **Every fact about Vish is in brand-profile.md or marked [Vish to confirm].**
  - No family, no past relationship, no city.
  - Debt at most once every 2 weeks.
- [ ] 23. **One CTA only, and it matches the post type:**
  - a keyword for a free asset that's already live (teaching)
  - an easy question (story)
  - "tell me I'm wrong" (hot take).
- [ ] 24. **Length:**
  - 90 to 110 words for 30 to 45 s
  - 25 to 60 words for a Daily Take.
- [ ] 25. **Read-aloud test:** Vish can say each line in one breath without stumbling.
- [ ] 26. SlopMonster passes (`python3 .claude/skills/slopmonster/tools/deslop.py --text "..."`).

---

## D. The script template (fill in, then run C)

```
EMOTION (one): ______   WHO IT'S FOR: ______   POST TYPE: teach / story / hot take
LAST LINE (write first): ______________________________

HOOK, 12 words or fewer, 0 to 3 s
  Context + lean:  [subject] [action] [end state or number] ______
  Snapback:        [But / So / turn the opposite way] ______
  Text hook:       [2 lines, 3 to 7 words, no punctuation] ______
  Visual, frame 1: [what moves, what we see] ______

LOCK-IN, 3 to 10 s (pick one: proof / result / contrast / magic box / objection / double down)
  "For anyone who ______."                       (identity callout, if not in the hook)
  ______________________________                (true proof from brand-profile, or the named method)

STAKES
  Character: me / you / a third person   At risk: ______   Why now: ______

BODY 1
  Scene: [place, object, moment] ______
  Big question the viewer can guess at: ______
  Head fake (logical in hindsight): ______

REHOOK by 20 s (pick one)
  "But here's the problem with that." / "Which would have been fine, except..." / "And that's when I realised..."

BODY 2 (or the list: 1 ___ / 2 ___ / 3 ___)
  ______________________________
  Fun beat: ______

ATOMIC LINE (his real words where possible): ______
CTA (one): keyword ______ for ______ / easy question ______ / "tell me I'm wrong"

CHECK: word count ___ (90 to 110)   "and then" count 0   facts flagged ___   SlopMonster pass
```

---

## E. 12 script ideas for Vish

- **P** = Paritosh style (7 ideas). **K** = Kallaway style (5).
- Facts are from brand-profile.md unless they're flagged.
- English for an international audience.

| # | Hook (12 words or fewer) | Angle (one line) | Framework | Facts and flags |
|---|---|---|---|---|
| 1 P | I cancelled 2 flights for 1 meeting. It cost me 6 months. | The worst travel moment, and why he now wants euros and the road. | P6 stakes from his life, P2 identity callout, K30 addiction loop | All in brand-profile. Full script 1 below. |
| 2 P | I kept quitting content. The problem was the voice in my head. | The 3 lines he tells himself now about confidence. | P3 count of 3, P2 callout, P7 his own line, K12 "About Me" | His confidence quotes and yoga are in brand-profile. The link between self-talk and the years of stopping: [Vish to confirm]. Full script 2 below. |
| 3 P | Thinking of moving abroad? The country matters more than the job. | His real read on Germany: structure and paid overtime, but not built for remote workers. | P2 callout, P4 statement (the "?" is the identity line only), K10 snapback | brand-profile. Fair to Germany, never mocking (CONTENT-OS). |
| 4 P | The biggest hustle is figuring out how not to hustle. | AI does the heavy work, so what's left is psychology, taste and creativity. | P7 his catchphrase, K10 contrarian snapback | His quote and his AI view are in brand-profile. |
| 5 P | Hate me for this, but in Bali every next person is a coach. | He doesn't want a career that's only valid for a year. | P12 raw Daily Take, P1 fun, K34 negative frame | brand-profile. Ends "I'm ending this one here" (Daily Take). |
| 6 P | 3 things yoga taught me that I use on bad days. | Self-awareness, self-control, staying calm in any situation. | P3 count of 3, P2 callout ("if you lose your cool easily"), K21 format | Yoga lessons are in brand-profile. Which bad days: [Vish to confirm] the examples. |
| 7 P | If I hit 3,000 euros a month, this is what I'd do first. | Save, invest, book a flight, and why that order. | K12 "If I" desire hook, P5 promise, P1 fun | brand-profile. Not back-to-back with any debt post. |
| 8 K | A brand made us redo one creator shortlist 22 times. Overnight. | They wanted originality, then changed every line. | K30 loop, K20 tease the proof (850+), K20 double down | brand-profile. Full script 3 below. |
| 9 K | AI won't replace marketers. It'll replace the heavy part of the job. | What he hands to Claude Code, Claude, ChatGPT, ElevenLabs and Gemini, and what he keeps. | K10 3-step hook, K7 application content (show the screen) | The tools are in brand-profile. Which task goes to which tool: [Vish to confirm]. |
| 10 K | Most of my 220 rejections never came from a person. | Automated rejections, so he built his own AI job-search agent. | K13 Investigator, K6 Illusion of Novelty, K7 application | brand-profile. What the agent does and its results: [Vish to confirm]. Counts as back-story: space it out. |
| 11 K | Copy-paste content is why brands can't tell creators apart. | From the brand side: original personal brands are what shortlists look for. | K4 story lens, K32 villain (copy-paste), K10 | His pet peeve and the shortlist story are in brand-profile. Don't name the brand. |
| 12 K | Worth It or Slop? I let AI hunt jobs for me. | Run his job-search agent for real, show the cost and the result, then give the verdict. | K7 application content, K13 Experimenter, the CONTENT-OS series | Cost, run time and result: [Vish to confirm]. Needs a guide if it uses a keyword. |

---

## F. Three full scripts (30 to 45 s each)

They're written for his mouth, one line per beat. The captions follow what he actually says, never the script.

### Script 1: the cancelled flights (Paritosh style)
**Emotion:** recognition, then hope.
**For:** anyone whose job keeps pulling them away from travelling.
**Post type:** story.

```
I cancelled 2 flights for 1 meeting. It cost me 6 months.
This one's for anyone whose job keeps pulling them back.
I'd worked remotely in India for about 4 years.
But then a big meeting came up.
So I cancelled my next 2 flights. For one meeting.
But more client work came. And more.
I was stuck in India for 6 months. In a 9 to 5.
For someone obsessed with travelling, that was hell.
When I'm not travelling, my life feels on autopilot.
When I'm travelling, I count every single day.
Sri Lanka's booked. Let's see if I get on this one.
Would you have cancelled those flights?
```

**Text hook:** "Cancelled 2 flights for 1 meeting".
**Frame 1:** him at a laptop with a boarding pass on screen, pushing the laptop shut.

**How it passes C:**
- **Hook:** context (flights, meeting), lean (why), snapback (6 months).
- **Identity:** line 2.
- **Stakes:** his travel life, the booked flights, the meeting.
- **Big question and head fake:** will one meeting matter? Yes, it became 6 months.
- **Rehook:** "But more client work came" at about 15 s.
- **Fun beat:** "Let's see if I get on this one."
- **Atomic line:** his autopilot quote.
- **CTA:** an easy question.
- **Length:** 110 words, about 40 s.
- **Facts:** all from brand-profile.

### Script 2: the voice in my head (Paritosh style)
**Emotion:** recognition.
**For:** anyone who keeps starting and stopping.
**Post type:** story, with a list.

```
I kept quitting content. The problem was the voice in my head.
If you start and stop too, here are the 3 lines I use.
For years I wanted to make videos.
I'd start. I'd doubt myself. I'd stop.
I never really found the confidence.
So, one. The way you speak to yourself defines how confident you are.
Two. Confidence is a character you play.
You repeat it, you act as one, and you become it.
Three. Stay calm. Yoga taught me that, even in front of a camera.
And yes, I'm mostly saying this to myself.
Which one do you need to hear today?
```

**Text hook:** "The voice in my head".
**Frame 1:** a tight shot, him looking at the phone screen, then a small shrug.

**How it passes C:**
- **Hook:** context (quitting content), lean (why), snapback (it was the voice in his head).
- **Identity:** line 2.
- **The count of 3:** an open loop until "Three".
- **Rehook:** "Two" at about 20 s.
- **Fun beat:** "mostly saying this to myself".
- **His lines:** his own confidence quotes (lines 6 and 8).
- **CTA:** an easy question.
- **Length:** 105 words, about 38 s.
- **Flag:** [Vish to confirm] that self-talk was what kept stopping him.

### Script 3: 22 shortlists (Kallaway style)
**Emotion:** surprise, then mild anger.
**For:** creators and marketers.
**Post type:** Brand-Side story.

```
A brand made us redo one creator shortlist 22 times. Overnight.
I've signed 850+ creator deals on the brand side, and this one explains a lot.
They wanted creators with strong, original personal brands.
So the list went back. And back. 22 times.
So you'd think they'd let those creators be themselves, right?
No. They changed every single line of their videos.
Every line.
They want originality but don't give the freedom to do so.
And if you're a marketer, be honest. You've seen this too.
So who should get the final say on the script, the brand or the creator?
```

**Text hook:** "22 shortlists in one night".
**Frame 1:** a stack of printed creator lists, each one stamped and pushed aside.

**How it passes C:**
- **Hook:** context (a brand, a shortlist), lean (22 times), snapback (overnight).
- **Lock-in:** tease the proof (850+ deals).
- **Stakes:** an overnight deadline.
- **Big question:** "you'd think they'd let them be themselves".
- **Head fake:** they changed every line.
- **Double down:** "Every line."
- **Atomic line:** his own quote.
- **CTA:** a question that gets people to take a side.
- **Length:** 101 words, about 37 s.
- **Facts:** all from brand-profile, and no brand named.

---

## G. Next steps
1. **Vish sends 3 to 5 Paritosh reel links** he loves. We transcribe them (public embed and the local tool) and confirm P1, P8, P9 and P10 against his real beats and pacing.
2. **Build a small outlier script from YouTube channel listings** (views divided by channel median) for the reference creators who post Shorts. It's text only and free, and it follows K2.
3. **Scripts 1 to 3** go to Vish as text for approval (CONTENT-OS: scripts are approved before anything is built).
