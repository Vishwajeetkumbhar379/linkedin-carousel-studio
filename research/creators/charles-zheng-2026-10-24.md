# @charles.zhengg: deep study of the 3D explainer style (24 Oct 2026)

Vish, 24 Oct: "I need this kind of clarity with the script and this kind of knowledge… people should feel, learn, get inspired… exactly animations like this… this style 70%, everything else 30%… study the sound design, scripting, hooks, framing, everything."

**The account:** 140K followers from only 20 posts (profile embed, 24 Oct). Every post is a big production.

**Studied:**
- De0BAl8B3mY, "How we taught sand to think": 2:21, 41,840 likes, 376 comments.
- Der5mJsBmwP, "How Instagram picked this video for you": 2:38, 17,482 likes, 224 comments.

**Tools:**
- `reel_teardown.py`: transcript and word times;
- 3-second contact sheets and 0.5-second strips;
- a per-second table of speech rate, picture motion and loudness (`scratchpad/cz/tempo.py`).

We copy the grammar, never his scripts, topics or footage.

## 1. The numbers
| | Sand (De0BAl8B3mY) | Algorithm (Der5mJsBmwP) |
|---|---|---|
| Length | 141 s | 158 s |
| Words | 543 | 650 |
| Speech, median and range | 3.7 words a second (2.3 to 6.3) | 4.2 words a second (2.7 to 5.7) |
| Hard cuts | 4 | 2 (one continuous 3D world; the camera never cuts) |
| Sound hits | 65, a median of 0.33 a second | 76, a median of 0.33 a second |
| Comments per like | 0.009 | 0.013 |

**What the numbers say:**
1. **The engagement is awe and shares, not comment keywords.** He never asks for a comment. Each video *is* the resource.
2. **The sync between speech and picture is literal, not global.** Across both videos, speech rate and picture motion don't correlate (-0.05 and -0.12), and sound hits don't follow motion either. The tempo moves only where the words name a tempo:
   - **"Let's zoom in. Further. Even further." (sand, 0:14 to 0:17):** three push-ins through real chip micrographs, each with a scale bar: 3 mm, 500 µm, 50 µm, 200 nm.
   - **"The chip is now moving so fast that everything around it is slowing down. Let's slow down time" (sand, 1:36 to 1:46):**
     - the music drops out: -31 dB at 1:41, with the bass almost gone;
     - a single light bead crawls along a wire;
     - a stopwatch reads "0:00, 1 tick = 1 second", then runs 0:01, 1:43, 4:13, 6:00;
     - then "Day 1, Day 2, Day 3" for storage;
     - a second dropout comes on "takes days".
   - **"Fetch, decode, execute, write back, then again, and again, three billion times every second" (sand, 1:28 to 1:33):** the loudest moment of the video (-10.7 dB) and the fastest motion. He slows his voice (2.7 words a second) so every step lands while the picture races.
   - **"In the time it took you to blink, the chip… made billions of calculations" (sand, 0:09):** his fastest speech (6.3 words a second). A giant counter, "1,134,000,000", pops over his head, then he lunges into the lens on "How is this even possible?".
   - **"So let's rewind" (algorithm, 0:09):** the camera reverses through the world of videos.
3. **Few sounds, but big ones.** There's a cinematic music bed all the way through, a whoosh on camera moves, and **dropouts (true silence or no bass) on the key beats**. That's the opposite of a sound on every visual.

## 2. Script DNA (what makes people learn, feel and share)
1. **Open on something you're touching or experiencing right now,** in the present tense and the second person:
   - "This is a grain of sand." He holds the object; the title card asks the question ("How we taught **sand** to think").
   - "Before this video started playing, Instagram already knew how long you would watch it." The video is about itself.
2. **A promise to see inside:** "let's zoom in", "let's rewind… and see how it actually works".
3. **A causal ladder.** Each sentence adds one step to the last:
   - "Put two switches in a row… Put them side by side… Add a NOT gate… Wire those together… If it can add, then it can also subtract… If it can do arithmetic, then it can do anything."
   - Each step introduces one name ("This is called the memory." "This is called the cache.").
4. **Scale you can feel:** "100 billion fit in the size of your nail", "three billion times every second", "one tick takes one second… six minutes… days".
5. **Analogies from daily life:** a library with addresses, a giant map, home cook vs programmer.
6. **One authority line:** "Instagram's head, Adam Mosseri, has said…". A real source, named.
7. **A late self-intro as a twist:** at about 65% of the video, "…Instagram connected you to me. Hi, I'm Charles."
8. **A loop ending:**
   - back to the opening object ("A grain of sand and the magic of human ingenuity…");
   - or a payoff about the viewer ("if you're still here, it guessed right").

   This invites a rewatch and a send.
9. **The emotion arc:** curiosity, then "how is this even possible?", then mastery, then awe.

## 3. Picture grammar
- **One continuous 3D world per video,** in warm gold light on deep blue (sand), or a dusk sky over an endless field of video cards (algorithm). The camera flies, dives and pulls back; there are no cuts.
- **His face lives inside the world.** His selfie video is a white-framed card standing on a post in the 3D field. The camera dollies into the card until it fills the screen (full talking head), then pulls back out into the world: a "portal" transition.
- **Talking-head shots:**
  - a handheld selfie, close, in a dark room with warm practical light;
  - a real prop in his hand (a chip, a mic);
  - big gestures, and a lunge into the lens on the key question.
- **A symbol of "you":** a golden figure made of tiles, sitting in a red cinema chair. Reactions orbit as icons (heart, comment, share, save); predictions are glass tubes that fill.
- **Data as objects:** cards in a field, glowing paths of light, rings of viewers, binary rain, huge counters in white, a stopwatch.
- **Real imagery where it matters:** chip micrographs with scale bars, so the zoom is true.
- **Captions:** 2 to 4 words, white bold, centred, with **one key word in a coloured pill** (orange in sand, red in algorithm).
- **Title card at 0 s:** the question, with one word in a pill.

## 4. What Vish's style becomes: 70% this, 30% the rest
**70%: the 3D explainer**
- Topics of the form "How X actually works", where X is something the viewer touches daily, in Vish's niche:
  - how a brand decides to pay a creator;
  - how a comment becomes a DM;
  - how AI edited this video;
  - what happens in the second after you tap "post".
- The script DNA above.
- One 3D world per video, with his face as a portal card.
- Tempo words performed by the edit.
- A music bed with dropouts.
- Keyword pills in the captions.

**30%: what we already locked**
- the v12 freeze-frame sticker and his real archive;
- Kallaway's named frameworks and split canvas;
- the hook first;
- the safe zones;
- never on his face; words behind him;
- the 52-week documentary episodes.

**Length:** he runs 2:20 to 2:40. A new account should start explainers at 60 to 90 s, with the same structure, fewer ladder steps and the loop ending. Lengthen only when Insights show people finishing. Episodes stay at 35 to 45 s.

**Production, honestly:**
- His worlds look like Blender or Cinema 4D renders, plus real micrographs.
- Ours: Three.js scenes rendered frame by frame (bloom, fog, instanced fields, video textures for Vish's portal card), driven by the same timeline as `comp.html`.
- The first proof is `templates/video/world/portal-test.html`.
- Stock or real imagery only where it's true and licensed.

## 5. How he actually makes them (his own reel DeV22xOBnRC, 24 Oct, plus his skills repo)
In that reel he shows his "photo your mom just sent" video at 9,799,110 views and a 54 s average watch time.

**His workflow:**
1. He writes the script.
2. Claude Code (Opus 5.5) plans key frames with his **animated-video** skill.
3. Claude builds the whole animation in code while he films the voiceover and the talking head.
4. His **video-edit** skill assembles everything: sound effects, music, visuals, clip picks.

**The skills:** github.com/goodnight000/cstack (MIT). I read them on 24 Oct; no network calls or secrets in the scripts.
- **animated-video:**
  - Remotion (React) + three.js (`@react-three/fiber`);
  - style packs: luminous-3d (his sand/chip look), realistic-3d, motion-graphics, editorial-collage, handmade-2d;
  - parts: a modelled iPhone, a globe, a motion kit, a realism kit, a finish pass with bloom, grain and vignette.
- **video-edit:** Resolve or FFmpeg, takes, captions, 60+ sound effects.
- **video-script:** the hook in 3 s, a second sentence that keeps viewers, proof on screen, retention curves.
- **asset-library:** a shared library of reusable assets.

**His process for each film:**
1. **Find the pictures:** one fresh agent brainstorms pictures per line (literal, analogy, impossible, change of scale, personified, a kid's drawing). A second fresh agent picks for clarity with the sound off, surprise ("would someone screenshot it?") and spectacle (scale, many parts moving, light).
2. **Concepts and a timed beat sheet,** approved by the creator.
3. **Style frames** of the same beat in different styles; the creator picks one.
4. **Audio spine:** every cue is derived from the words (`cue("phrase")`), so a new voiceover re-times the film. Sound events come from the same constants that draw the picture.
5. **A key-frame board** (one still per beat, built in the real scene files), plus an animatic when the meaning lives in motion. Approved before animating.
6. **Build:**
   - one canvas;
   - physical light (`MeshStandardMaterial` / `MeshPhysicalMaterial`, a `PMREMGenerator` environment, rim light);
   - modelled real objects (bevels, panel lines, ports);
   - fog depth and soft near-lens particles;
   - one brightest thing per shot;
   - a full frame to the edges.
7. **Review:**
   - frame strips for motion;
   - a hunt for holds (a voice explaining over a still picture);
   - flicker and determinism checks;
   - fresh judges;
   - a **mute test** (can a newcomer follow it with the sound off?).
8. **Presenter composites:** plan the world behind the person before filming, match blacks, grain and light, and test one clip first.

**His bar names our first test's failure exactly:** "glowing shapes on a flat dark field… primitives standing in for objects. The fix is content: a place, the objects in it, and something happening there."

**Status (24 Oct):**
- Installing cstack and running its Remotion templates needs Vish's explicit OK: this session's safety check blocked installing code from an outside repo.
- Until then, its documented method guides our own Three.js pipeline.
