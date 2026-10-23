# Build with Vish: the playbook (single source of truth)

Version 1, 23 Oct 2026. It merges the locked decisions (brand-profile.md, voice.md, content-pillars.md, the v12 edit recipe, the attention playbook) with the 23 Oct research. Where new research changes a locked rule, it's marked **[changed 23 Oct]** with the reason; nothing locked was dropped silently. Details live in the linked files; this page is the summary every skill reads first.

## 1. Who, for whom, why
- **Vish**, 27, brand-side influencer marketing (850+ creator deals), moved to Germany, finishing his master's, building AI workflows as a non-engineer. Only facts from `brand-profile.md`. Never invent results, numbers, quotes or clients. Never mention his past relationship.
- **Instagram @buildwith.vish** is a weekly documentary, "Week N of 52": building a remote income (goal EUR 3,000 a month) to travel the world. It also teaches the AI and marketing skills he uses along the way.
- **Audience:** creators, marketers and early founders who want remote income and want to use AI without being engineers.
- **Site:** https://buildwithvvish.com (Cloudflare Workers; the brief's "BuildWithWiz.com" is taken to mean this domain).
- **Writing:** British English, no em or en dashes, no banned words (voice.md), hooks of 12 words or fewer, SlopMonster on every script, caption and reply.

## 2. The weekly system **[changed 23 Oct: was 3 talking videos a week]**
Exactly 3 feed posts a week, and they support each other:

| Day (Berlin) | Post | Job | Goal metric |
|---|---|---|---|
| Thu | **Reel**: Week N of 52 episode | Story, reach to non-followers, follows | Watch time, shares, follows |
| Mon | **Carousel A**: the skill or tool from the episode, as a how-to | Saves, keyword comments, resource clicks | Saves, comments, site clicks |
| Sat | **Carousel B**: brand-side or AI-workflow lesson from Vish's 850+ deals | Credibility, leads | Saves, shares, profile visits |

- **One theme per week.** The episode lives it, Carousel A teaches it, Carousel B adds the insider angle. Never repeat the same point twice in one week.
- **Buckets (Kallaway's 3-2-1, adapted):** one broad bucket (the documentary: travel, remote income) and two narrow ones (AI workflows for creators and marketers; brand-side secrets). Re-check the numbers every 2 weeks, and triple down on the bucket that wins.
- **Now:** the calendar for Weeks 2 to 5 is `content/calendar/2026-weeks-02-05.md`; the week's files and captions are in `content/instagram/week-NN-post-kit.md`; carousels use the series template `templates/carousel/week-series.css`.
- **Production:** one filming session every 2 weeks (two episodes). Carousels are built from the episode's real work, so there's nothing extra to film. Weekly approval loop: Vish approves the week once.

## 3. Hooks and scripts
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

  80 to 100 spoken words for teaching posts. Episodes run longer when the story earns it.
- **Retention moves** (peter.visuals, checked against our own edits):
  - show the result before the process;
  - give viewers something to figure out;
  - chain events with "but… so…";
  - re-hook just before attention drops;
  - save the strongest reveal for last.
- **Shoot sheets** for every topic: delivery marks, an on-screen cue per line, B-roll, cover and the next-week line (`content/shoot-sheets/*.json`, teleprompter page).

## 4. Edit standard (v12, see `research/creators/edit-recipe-v9-2026-10-22.md`)
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
- **Contrast:** text at least 4.5:1 against what's behind it (WCAG). Use a soft scrim behind captions over busy footage.
- **Faces pull the eye away from captions** (subtitle eye-tracking research). Keep captions close to the face line, not at the bottom edge.

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
- **Process:** check that the disk has about 3 GB free before rendering. Full disks crash the browser renderer.

## 12. Research sources and how reliable they are
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
