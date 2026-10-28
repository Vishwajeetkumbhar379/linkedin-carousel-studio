# Build with Vish: the playbook (single source of truth)

Version 1, 23 Oct 2026. It merges the locked decisions (brand-profile.md, voice.md, content-pillars.md, the v12 edit recipe, the attention playbook) with the 23 Oct research. Where new research changes a locked rule, it's marked **[changed 23 Oct]** with the reason; nothing locked was dropped silently. Details live in the linked files; this page is the summary every skill reads first.

## 1. Who, for whom, why
- **Vish**, 27, brand-side influencer marketing (850+ creator deals), moved to Germany, finishing his master's, building AI workflows as a non-engineer. Only facts from `brand-profile.md`. Never invent results, numbers, quotes or clients. Never mention his past relationship.
- **Instagram @buildwith.vish** is a weekly documentary, "Week N of 52": building a remote income (goal EUR 3,000 a month) to travel the world. It also teaches the AI and marketing skills he uses along the way.
- **Audience:** creators, marketers and early founders who want remote income and want to use AI without being engineers.
- **Accounts (decided 25 Oct):**
  - **@buildwith.vish is the only account the brand posts on.** It's a professional account with 1 follower; Week 1 got about 110 views there. Every reel, carousel and keyword lives here: it's his portfolio for brand work and freelance.
  - **@explorevishwa.jeet stays private and personal** (1,738 friends and followers, personal highlights). A Week 1 trial reel there also got about 110 views, so its followers didn't bring reach. Optional: share each new reel to its Story for friends; never post brand content on its grid.
  - **@explorewith.vish (35 followers, old travel reels):** not used for now. Its old reels reached 1,000 to 2,000 views when posted as collabs with the personal account.
  - **Why:** both accounts got about the same views, so the follower count is not what limits reach yet; the hook and the format are. One focused account teaches Instagram who to show it to. Never post the same video on two accounts.
- **Site:** https://buildwithvvish.com (Cloudflare Workers; the brief's "BuildWithWiz.com" is taken to mean this domain).
- **Writing:** British English, no em or en dashes, no banned words (voice.md), hooks of 12 words or fewer, SlopMonster on every script, caption and reply.

## 2. The weekly system **[changed 23 Oct: was 3 talking videos a week]**
Exactly 3 feed posts a week, and they support each other:

| Day (Berlin) | Post | Job | Goal metric |
|---|---|---|---|
| Thu | **Reel**: Week N of 52 episode | Story, reach to non-followers, follows | Watch time, shares, follows |
| Mon | **Teaching Reel (Kallaway style)** from Week 3 **[changed 23 Oct, Vish asked for this topic, animation and editing style]**: a named framework from the week's theme, filmed in the same session. Week 2 keeps Carousel A | Reach to non-followers, keyword comments, saves | Views, comments, shares, site clicks |
| Sat | **Carousel B**: brand-side or AI-workflow lesson from Vish's 850+ deals | Credibility, leads | Saves, shares, profile visits |

- **Extras (format tests, outside the series) [Vish, 23 Oct]:** reaction and hot-take reels, such as reacting to a creator's take, then recreating their format to make a point. Respectful, credited, their clips 6 s at most, never their words. Sheets in `content/shoot-sheets/*extra*.json`. Compare each one with the series in the weekly report.
- **One theme per week.** The episode lives it, Carousel A teaches it, Carousel B adds the insider angle. Never repeat the same point twice in one week.
- **Buckets (Kallaway's 3-2-1, adapted):** one broad bucket (the documentary: travel, remote income) and two narrow ones (AI workflows for creators and marketers; brand-side secrets). Re-check the numbers every 2 weeks, and triple down on the bucket that wins.
- **Now:** the calendar for Weeks 2 to 5 is `content/calendar/2026-weeks-02-05.md`; the week's files and captions are in `content/instagram/week-NN-post-kit.md`; carousels use the series template `templates/carousel/week-series.css`.
- **Production:** one filming session every 2 weeks (two episodes). Carousels are built from the episode's real work, so there's nothing extra to film. Weekly approval loop: Vish approves the week once.

## 3. Hooks and scripts
- **Hook first, every time [changed 23 Oct, after Week 1 reached about 50 views in its first hours]:** the first spoken words are the hook (a number, a loss, tension). "Week N" and "Hey, I'm Vish" appear on screen as labels, never as the opening words: strangers decide in 1 to 2 seconds. The freeze-frame sticker lands on the hook line.
- **First second:** a face, a number or a visible change. The 9 levers (`research/viral/attention-playbook-2026-10-15.md`): use 3 or more per hook. The templates there are filled with true facts only.
- **Script shape** (Kallaway's format, matching our shoot sheets):
  1. Hook (12 words or fewer).
  2. Lock-in: 2 to 3 sentences on why it matters to the viewer.
  3. Body 1.
  4. Re-hook.
  5. Body 2.
  6. Re-hook.
  7. Optional body 3.
  8. Close.
  9. CTA tied to one lead magnet.

  80 to 100 spoken words for teaching posts. Episodes run 35 to 45 seconds **[changed 23 Oct: Week 1 ran 1:51]**; longer only when the data shows people finish them.
- **Retention moves** (peter.visuals, checked against our own edits):
  - show the result before the process;
  - give viewers something to figure out;
  - chain events with "but… so…";
  - re-hook just before attention drops;
  - save the strongest reveal for last.
- **Shoot sheets** for every topic: delivery marks, an on-screen cue per line, B-roll, cover and the next-week line (`content/shoot-sheets/*.json`, teleprompter page).

## 4. Edit standard
### The style mix [changed 24 Oct, Vish: "this style 70%, everything else 30%"]
- **70%: the 3D explainer grammar of @charles.zhengg** (study: `research/creators/charles-zheng-2026-10-24.md`).
  - **Script:**
    - open on something the viewer is touching or experiencing right now ("this video", "your phone");
    - "let's rewind / zoom in and see how it actually works";
    - a causal ladder, one step per sentence, each new thing named;
    - scale you can feel;
    - one named authority;
    - the self-intro late, as a twist ("…Hi, I'm Vish");
    - a loop ending back to the opening.
  - **Picture:**
    - one continuous 3D world per video (the camera flies; no cuts);
    - his face as a portal card inside the world, the camera diving in and out;
    - data as objects;
    - real imagery only where it's true;
    - captions of 2 to 4 words with one key word in a lamp-amber pill;
    - a title card at 0 s: the question, with one word in a pill.
  - **Tempo words are performed** (shoot-sheet marks `<slow>`, `<fast>`, `<zoom>`, `<rewind>`, `<freeze>`). When the line names a tempo, the picture *and* the sound do it: the music drops out, motion crawls, a clock runs, or the camera reverses.
  - **Sound** **[changed 24 Oct: was a sound on every visual]**:
    - a continuous music bed;
    - a whoosh on camera moves;
    - dropouts (true silence, or the bass gone) on the key beats;
    - small UI sounds only on the big reveals.
  - **Length:** explainers run 60 to 90 s; lengthen only when Insights show people finishing. Episodes stay at 35 to 45 s.
  - **Build:** `templates/video/world/*.html` (Three.js, rendered by `scripts/reel_edit/render_world.py`). The first proof is `portal-test.html`: the field of video cards, his real clip as a portal card, then "let's slow down time" with the music dropping out and a stopwatch.
- **30%: everything locked before:**
  - the v12 freeze-frame sticker and real archive;
  - Kallaway's named frameworks and split canvas;
  - the hook first;
  - the safe zones;
  - never on his face, and words behind him;
  - the "Next week" narrator card;
  - comment keywords that send a tool.

### The v12 base (see `research/creators/edit-recipe-v9-2026-10-22.md`)
- **Kept from v9 to v12:**
  - natural takes at one steady speed;
  - locked camera and a film grade;
  - the freeze-frame sticker move in the first 2 s;
  - hard silences at the emotional beats;
  - literal B-roll, or animation when no footage exists;
  - 3D-flip captions with a word box;
  - a sound on every visual event, with the voice always on top;
  - a long beat-cut montage when the song is the payoff;
  - every episode ends on the ElevenLabs "Next week" card.
- **New from the 23 Oct references:**
  - **Captions sit at 58 to 66% of the frame height [changed 23 Oct: was about 75 to 81%].** Instagram's UI covers the bottom ~35% and the right edge (Meta's ad specs, cited via Hopper HQ and Inro: keep 14% top, 35% bottom and 6% on each side free of key text).
  - **Hook lines get one or two giant words at a time,** in the middle third, sometimes behind the head (references: Abigail Daniella, Raelynn).
  - **Light-leak flashes** only on story turns, at most 3 per reel.
  - **Floating framed prints** (photos, screenshots, proof) beside him when he names something.
  - **Tutorial segments** on grid paper with cut-out photos, hand-drawn arrows and handwritten labels, ending with a "Save this" card.
  - **Tool reels:** show the real interface, light up each feature on a timeline as it's named, and close with "this video you just watched?" (riverisbuilding).
- **Safe zones are a hard gate [Vish, 23 Oct: on his phone the top bar hid "Life is" and the week label of the Week 1 reel]:** all text (titles, labels, stickers, captions, words on cards) stays inside the safe box:
  - from 14% to 65% of the height;
  - from 6% to 94% of the width;
  - left of 86% below 40% height, clear of the buttons.

  Faces and backgrounds may run under the UI. Before every render, `python scripts/reel_edit/safe_zones.py check video-projects/<slug>` must say PASS. The review copy comes with `safe_zones.py preview <video>`, a phone preview with the covered areas shaded. (Week 1 had 196 text items under the UI, including the "Week 01 of 52" label on screen for the whole reel.)
- **Never on his face [Vish, 23 Oct: "some of the captions were literally on my mouth… disrespectful and bad editing"]:** no caption, title, sticker or graphic is ever drawn over his face (eyes, mouth, chin). The same `safe_zones.py check` finds his face in every frame and fails the edit if anything is drawn on it. Week 1 had 16 moments, mostly captions across his mouth in the split layout at 39 to 56 s.
- **Depth by default [Vish, 23 Oct]:** big titles, key words, numbers and cut-outs sit **behind him**, with his cut-out (matte) on top. They look 3D and he stays the focus.
  - In `comp.html`, a cue with `z` below 30 goes under the cut-out layer `#cut`.
  - In framed shots, switch the cut-out on over the frame, or keep the words off the frame.
  - Only captions sit in front, always below his chin. In split layouts they go in the gap between the graphic and his box, never across the box.
- **Contrast:** text at least 4.5:1 against what's behind it (WCAG). Use a soft scrim behind captions over busy footage.
- **Faces pull the eye away from captions** (subtitle eye-tracking research). Keep captions close to the face line, not at the bottom edge.

### Teaching Reels (Kallaway style, from Week 3; study: `research/creators/kallaway-2026-10-23.md`)
- **Script:**
  1. a hook with an extreme but true promise;
  2. "It's called [Named Method]";
  3. one running example;
  4. numbered steps (3 to 5);
  5. a recap;
  6. "Comment KEYWORD for [a tool]".

  80 to 110 words.
- **Edit:** a split frame, with the graphics canvas on top and his speaker box below, plus full-frame shots for punchlines.
  - type-on document cards in sync with his words;
  - an "old way vs new way" split card;
  - a framework map (an amber node wired to step pills that light up as he names each step);
  - a canvas switch from night to paper for the proof or recap;
  - one-word captions, and a sound on every move.

  Our night-studio palette, with amber in the role of his red. Copy the system, never his wording or footage.

## 5. Carousels
- **Size and length:** 1080x1350 (4:5), 7 to 10 slides.
- **Slide 1:** the hook (12 words or fewer), with one concrete promise (number, tool, outcome).
- **Slide 2:** why it matters (loss or insider angle).
- **Middle slides:** one step per slide, with a real screenshot or example on every step slide.
- **Second-to-last:** the summary to save.
- **Last:** "Comment KEYWORD", what they get, and "Follow for Week N".
- **Design:** the brand paper look (ivory, Instrument Serif or Newsreader headline, Geist or Inter Tight body, lamp amber accent), a progress dot row, and his face on slide 1 or the last slide for recognition. Same template all week, so the grid reads as one series.
- **Tools:** bespoke HTML (`templates/carousel/<name>.html`, `scripts/render_slides.py`), plus the skills `viral-carousel` and `ig-carousel-planner` for structure.

## 6. Captions (the post text)
- **First line:** the hook in 125 characters or fewer, so it's whole before "more".
- **Body:** Sky Tan's storytelling structure, compressed:
  1. who he is (one line);
  2. the struggle;
  3. the rise or the insight;
  4. proof (his own, real);
  5. the free resource, plus the paid step when one exists.
- **Search keywords in plain words** (remote income, Claude, AI editing, creator deals). Instagram search reads captions.
- **Five hashtags at most** (Instagram's current cap), relevant and mid-sized.
- **One question that's easy to answer**, and the keyword repeated in the last line.

## 7. Covers
- **Template:** `video-projects/week-01-intro/work/cover12/cover.html`.
- **Layout:** "Week N of 52" in serif, a framed print in a plastic sleeve, three edge stickers, and one serif line with an amber italic word.
- **Background:** alternate red and navy each week.
- **Crop:** everything inside the 3:4 grid crop.

## 8. Funnel and monetisation
1. **Keyword on the post:** said in the reel, shown on the last carousel slide, and in the caption's last line.
2. **Comment → automation:** a varied public reply, plus one private reply (Instagram's official Private Replies, one per comment, within 7 days).
3. **Optional follow check:** the DM asks them to tap or reply. That opens a real conversation, which lets the API check whether they follow (`is_user_follow_business`). Non-followers get a friendly nudge and the link anyway. **We never hold a free resource hostage.**
4. **Link:** a tracked link (`/go/KEY`, UTM tagged), then the resource page on buildwithvvish.com, with email capture (MailerLite "Build Notes") for the PDF version.
4b. **The free resource is a tool, not tips** **[changed 23 Oct]**: a Claude skill, a template, a prompt pack or a GitHub repo. In the engagement data, tool giveaways drew 19K to 94K comments; advice posts drew a few thousand.
5. **Value ladder:**

   | Tier | What |
   |---|---|
   | Free | Article, checklist, prompt |
   | €1 | One ready-to-use template or workflow file |
   | €5 to €10 | Bundle: templates, video walkthrough, PDF guide |

   No fake "was €99" anchors. The value is shown by what's inside.
6. **Payments:** see `docs/monetisation.md`. No live charges, paid brand deals or freelance invoices until Vish has written permission for self-employment (§ 0 there), approves the products and connects his payment account.

## 9. Analytics (weekly, Monday)
- **Per post:** reach, non-follower reach %, average watch time and 3-second hold (Reels), saves, shares, comments, keyword comments, follows, profile visits.
- **Per week:** link clicks per keyword (`/go/` counters), email sign-ups, sales.
- **Tools:** the `social-analytics-report` skill turns the numbers into keep / test / change / stop. Re-check buckets every 2 weeks.
- **Never claim causation from one post.** Never invent data.

## 10. Pipeline and skills (master workflow: `.claude/skills/vish-studio/SKILL.md`)
Research → topic validation → hook → script → storyboard → edit → captions → carousel → publish → comment automation → lead magnet → website → sales → analytics. The master skill names the exact skill and script for each step.

## 11. Lessons learned (Vish's feedback, never repeat)
- **Week 1 result (23 Oct):** about 50 views in its first hours. Likely causes, to confirm with Insights:
  - the first 3 seconds were "Hey, I'm Vish", "I'm 27" and silent photos; the real hook came at about 5 s;
  - 1:51 is long for a new account;
  - the account had just gone public, with few followers;
  - possibly the two songs baked into the audio.

  Fixes from Week 2: hook first, 35 to 45 s, and the distribution routine below. Never promise "viral"; report the real numbers.
- **Distribution routine for every Reel:**
  - the same day, also post to YouTube Shorts and LinkedIn;
  - share it to the Story with a question sticker;
  - Vish sends it to 5 to 10 people who would genuinely care (sends per reach is one of Instagram's top signals);
  - Vish replies to every comment in the first hour;
  - use Trial Reels once the account is eligible (it needs a minimum follower count).
- **Cuts and speed:**
  - no jump cuts or random speed-ups;
  - no camera wandering;
  - no looking-away pauses left in;
  - no pause before a punchline.
- **Look:**
  - no cheap saturation;
  - no template-looking fonts;
  - no "Edited by AI" card.
- **Sound:**
  - no sad music he didn't pick;
  - no pumping music under the voice;
  - no overprocessed voice;
  - his chosen songs get room to breathe.
- **B-roll:**
  - never B-roll that doesn't match the words (friends' clips over "things to achieve" was wrong);
  - no strangers' close-ups.
- **Content:**
  - never his past relationship;
  - never a promise the next episode can't keep.
- **Volume, voice clone and B-roll (Vish, 27 Oct):** "I cannot just wait for one video and then wait the whole week."
  - **Volume:** every filming session now becomes an episode, shorts, cutdowns and carousels, on Instagram, LinkedIn and Shorts (`content/calendar/2026-11-month-plan.md`). The 3-posts-a-week table in §2 is the minimum, not the plan.
  - **His clone voice for lines he didn't film:** ElevenLabs "Young indian male" (`rRDZHYKovM5FXW92Zoxe`). At most 2 lines a reel, never the hook, never over his face (a card or B-roll carries those lines), and the post gets Instagram's AI info label and a line in the caption. This replaces "no AI voices" in `brand-profile.md` for his own clone only.
  - **B-roll for every place or thing he names** ("if you're saying beach, then the beach should be there"): his own clips first, then real public-domain archive film from movingimagearchive.com, re-cut at 640x480 from the Internet Archive source (`video-projects/week-02-talks/broll_search.py`, `broll_hires.py`, credits in `broll/credits.json`). Archive film shows as a framed print with its year, never as fake modern footage.
  - **Audio:** clean his voice with the ElevenLabs Voice Isolator (echo and room noise out), then only a gentle polish. It must still sound like him.
  - **Picture:** crisp, natural skin, no heavy saturation: the film.py looks ("night", "day", "soft"), never a beauty filter. Instagram plays 1080x1920, so that is the export size.
  - **Safe zones from Week 2:** the week label sits at 288 px (below the top bar), captions at about 1190 px (above the bottom 35%), and in a split layout just above his box.
- **Process:** check that the disk has about 3 GB free before rendering. Full disks crash the browser renderer.
- **Sound (Vish, 27 Oct, "I shouldn't have to tell again and again"):** he heard echo, missed audio, weird cuts and bad music in Week 2. The fixes are now in `week2.py` (every edit inherits them):
  - **Speed:** no time-stretch on his voice. Speeding up isolated speech makes the echo.
  - **Cut points:** every edge is checked against the cleaned audio. If he runs words together, the cut moves to the real quiet between them (`quiet()`). The first word is never clipped (`onset()`).
  - **Pauses:** held pauses are silent, so the next word never leaks in.
  - **Sound effects:** from the studio library (`video-projects/sfx-library`), whooshes peaking on the cut.
  - **Music:** composed per video in one brand sound (ElevenLabs Music, 110 bpm, warm plucks and tight drums), ducked under his voice.
  - **Files:** one file per video.
  - **QA before sending:**
    - Transcribe the final file and compare it word for word with the script.
    - Loudness at -14 LUFS.
    - One contact sheet.
- **One brand look (Vish, 27 Oct):** "it should look like a good brand design, not every video different." Two families only:
  - **Warm paper (learn):** the carousels, and the motion reels made from them with `scripts/carousel_reel.py`.
  - **Navy framed print (story):** the cover of every talking reel, from `scripts/print_cover.py`.

- **Clone narration and generated music (Vish, 27 Oct, pottery reel: "robotic, no emotion, random pauses everywhere, the music is shit"; then: "I speak slow, speed it up", reference @adilet.fndr DdyqycEINNe at 214 wpm):**
  - Never read the script line by line with break tags. Generate one continuous take written for speech.
  - Pace 190 to 210 words a minute: eleven_v3 with emotion tags (stability 0), or multilingual_v2 (stability 0.3, style 0.55, speed 1.2). Trim long gaps and atempo to pace (pitch kept), never rubberband.
  - Check every new setting with a 10 second sample he approves before building a reel on it. Transcribe it: every word must land.
  - No ElevenLabs Music beds on story reels. Deliver the voice mix clean; he adds trending audio in the Instagram app.
  - Real voice notes still win for personal stories; speed them up the same way.

- **Voice and sound (Vish, 28 Oct, final word; replaces the earlier clone and music notes):**
  - His real voice first, wherever a recording exists. It carries the emotion (the Week 1 intro is the benchmark). The clone only fills lines he never recorded, and uses voice B (multilingual v2, expressive settings).
  - Real voice at 1.2x with ffmpeg atempo (pitch kept). Never rubberband: it put echo on him.
  - A breath of about 0.5 s between lines, words fading in and out softly (25 ms in, 100 ms out), never dead air or 12 ms chops.
  - Clean every voice with `scripts/voice_polish.py` (isolator, soft joins, close-mic tone).
  - Music and sound design ship inside the file. He has no time to add music later, and audio added in the app never matches the cuts.
  - Pace of the picture: no beat-per-shot montages; at least two beats a shot, smooth zoom transitions, slow push-ins.

- **The mascot (Vish, 27 Oct: "that doesn't look like me"):** any animated Vish uses the real PNGs in `brand/avatar/pack` (read `Vish_Mascot_Claude_Guide.md`). Never a drawn or generated face.

## 12. Research sources and how reliable they are
- **"Viral first" rule [Vish, 23 Oct]:** before choosing any topic or format, rank candidate reels by real engagement and model only the winners:
  1. `python scripts/research/ig_fetch.py <codes> --out=<dir> --meta-only` reads likes and comments from the public embed, no login.
  2. The thresholds: 50K+ likes, or 20K+ comments, or more than 1 comment per like with 10K+ likes. These usually mean millions of views (an estimate). Where Vish can see real views, prefer 3 to 4 million.
  3. Take apart the top 3 with `reel_teardown.py`, then fill the pattern with Vish's true facts.

  The ranked table and the patterns are in `research/creators/kallaway-2026-10-23.md`.
- **Reference reels taken apart on 23 Oct** (frames, transcripts, cuts, sound hits):
  - `DYwset0R5kP`, `Dep0wuhvizo` (riverisbuilding, OpenFilm), `DZWLhE3uEhO`, `DbqEke7oewm`;
  - `DexJ-qWiWdY` (Sky Tan, the caption structure), `Da0hP-vxxL1` (Abigail Daniella, captions);
  - `DcOkFDSuf1E` and `DcqiQesO_R9` (Kallaway: the 3-2-1 plan and the script format);
  - `DcOdfDXJE57` (omgadrian, batch filming), `DewuhNfPypt` (peter.visuals, retention).
- **Not accessible:**
  - **@minolee.mp4 profile:** needs a login.
  - **YouTube SVikuuB2vkU and bpR1ePAYuI0:** "how I create hooks…" and "how I script videos…" by Mino Lee. YouTube blocks this server; titles only.
- **Reliable:**
  - **Meta's 14/35/6% safe zones** (ad specs, via third parties);
  - **WCAG 4.5:1 contrast;**
  - **69% watch without sound in public** (Verizon Media and Publicis, cited in Szarkowska et al., PLoS One 2024).
- **Unverified (don't quote as fact):**
  - "+40% views with captions";
  - "+12% watch time with captions".
- **Method:** Stiles Dichter's "Build one AI setup from everything you've saved" (2 Oct 2026): collect, compare and dedupe, write one playbook, turn it into skills, add one master skill, and update weekly.
- **Motion prompt bank:** github.com/yihui-dev/awesome-opus5-5-videos (703 prompts: motion, 3D, explainer, interactive).
