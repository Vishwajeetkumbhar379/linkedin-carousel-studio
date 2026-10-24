# The v9 edit recipe (Week 1 intro, 22 Oct 2026)

Vish, on v9: "I love this version… everything is so good, so perfect." This is the baseline for every talking-head reel from now on. Start from it; improve on it, never below it.

v11 (23 Oct): the reel opens on "Hey, I'm Vish" (a wave full screen, the frame settles), then the freeze-frame sticker edit on its own, then "I'm 27" into the passport photos, then the 40K hook. His past relationship is never mentioned. The sound design is unchanged from v9; only the silences moved with the story.

Code: `video-projects/week-01-intro/edit/week1.py` (edit decision list, frame prep, sound map, mix) and `edit/comp.html` (compositor). Commands:
- `python edit/week1.py prep`
- `python edit/week1.py stills t,t`
- `python edit/week1.py render --jobs=3`
- `python edit/week1.py mix`

## The standard from v12 (Vish, 23 Oct: "I loved everything"): every reel gets all of this
- **The 70/30 style (24 Oct).** 70% @charles.zhengg's 3D explainer grammar (PLAYBOOK §4, `research/creators/charles-zheng-2026-10-24.md`), 30% this recipe. Sound moves from "a sound on every event" to a music bed, whooshes on camera moves and dropouts on the key beats.
- **Never on his face; words behind him (23 Oct).**
  - Titles, key words, numbers and stickers go behind him: cue `z` 20, under the `#cut` layer at z 30, so they look 3D.
  - Captions stay in front but below his chin, and in split layouts in the gap above his box, never across it.
  - `safe_zones.py check` fails any frame with text on his face (Week 1: 16 moments).
- **Safe zones before every render (23 Oct).** No text in the top 14%, the bottom 35%, the outer 6% or the button column (right 14%, from 40% down). Titles live in the 14 to 35% band, captions at 58 to 66%. Run `python scripts/reel_edit/safe_zones.py check video-projects/<slug>` (it must PASS) and `preview` for the review copy. The Week 1 week label and its top titles were hidden on Vish's phone.
- **From Week 2 (23 Oct): the freeze lands on the hook line.** The first spoken words are the hook, not "Hey, I'm Vish" (Week 1 reached about 50 views in its first hours; see PLAYBOOK §3 and §11). Episodes run 35 to 45 s.
- **Open on him, frozen as a sticker.** Week 1 opened with "Hey, I'm Vish" and a wave full screen, settling into the frame. Every episode keeps the move. In the first two seconds the frame freezes on its own with a camera shutter, and he becomes a white-outlined sticker while that week's labels pop on. Then the hook facts.
- **Keep it clean:** no "Edited by AI" card. The AI story lives in the caption PS, the stats row and the end credit. His past relationship is never mentioned.
- **Let the music breathe.** When the song is the payoff (the "travel the world" chorus), give it a real montage: about 14 s, four quick cuts on the drop, then two beats a clip, fun and real clips only, never a stranger's close-up.
- **Every episode ends on a "Next week" card.** A cream page slides up, an ElevenLabs narrator says one line, each word lands as he says it, the next week fills on the 52-week bar, and "Follow for week N" sits underneath. The song ducks under him, and he matches Vish's loudness.
  - Voice: George (premade), `eleven_multilingual_v2`, `mp3_44100_128`, `convert_with_timestamps`.
  - The line only promises the episode that is already scripted.
- **Covers follow the series template** (`video-projects/week-01-intro/work/cover12/cover.html`):
  - a deep textured red, alternating with navy each week;
  - "Week N of 52" in serif on top;
  - his best frame as a white-bordered print in a glossy plastic sleeve, eye contact;
  - three white stickers on the print's edges, never over his face;
  - one serif line under the print with an amber italic word;
  - everything inside the 3:4 grid crop.
- **Before rendering, check the disk** (`df -h /`; renders need about 3 GB free). If it's tight, delete unused `work/fr` shot folders, which are rebuilt on demand.

## How the edit is built
- **Transcript first.** faster-whisper word times; every line is cut on word boundaries snapped to the audio onsets.
- **His takes stay whole.**
  - No chopping inside a take ("join" continues the take); takes change only at a full sentence.
  - One steady speed for everything (1.1×), never ramps.
  - Natural asides stay.
  - Pauses where he looks away get no hold, and a line gets a short LAND beat only where it should land.
- **Locked camera.** A dead-zone head lock, no drifting reframes; static punch-ins only.
- **Film grade, not saturation.** `scripts/reel_edit/film.py`: LUT, light pool, halation, mist. It should look like an expensive camera, not a filter.
- **Type.**
  - Instrument Serif (emotional lines, italic accents) + Inter Tight (facts) + Geist Mono (small labels).
  - One amber accent (#E7A15A) on ink or cream.
- **Layouts.**
  - Full-screen cut-out for the hook, with words tucked behind his head.
  - A 4:5 framed speaker box for most of it.
  - A split (graphics on top, him below) for lists and stats.
  - Full screen for the montage.
  - Layouts change with a 0.6 s eased morph.

## What made v9 land (from his reference reels)
- **Freeze-frame intro** (@sakchham_films).
  - On "Hey, I'm Vish" the frame freezes: camera shutter, white flash.
  - The room dims, and he becomes a sticker: RVM matte with a 9 px white outline (`freeze_cut()`).
  - White labels and 3D-icon stickers spring on around him, each with a pop that climbs in pitch.
- **Hard silences** (@ayyitsjamie). The music cuts to true silence (12 ms edges) at the emotional beats: the childhood moment, the question, right after "220 job rejections", "but one thing is sure". Clicks are the only sound inside a silence.
- **Real archive.** His passport photos (pulled out of a phone pan with OpenCV) land on a cream page one by one, kid to now, each with a click: "27 years in passport photos".
- **Literal visuals** (@elijahsnider_). Every claim gets the matching picture: the city for "moved to a country", a plane plus boarding pass for "booked a flight", the handstand kick-up for "trials", the topple onto his back for "fails". If no footage exists, animate it rather than show something unrelated: friends' clips over "so many things to achieve" was wrong.
- **Animated ideas with 3D icons** (Microsoft Fluent Emoji 3D, MIT, `assets/emoji`).
  - 40K as an odometer.
  - "Life is all over the place": the stat card scatters, the words land at odd angles, and icons orbit.
  - A 3D juggler for interests and hobbies.
  - A to-do card with nothing ticked.
  - A debt counter at 0% paid.
- **3D captions** (@milindrao_, @speedy_devv). Words flip up into place, and an amber selection box with corner handles slides to the spoken word. It doubles as the "edited by AI" signature.
- **Strobe title** (@the.artexpo, @omgadrian). Week 1 flashes black and white four times, with a click on each, then settles.
- **The AI line.** A sticker on "this is my first video": "Edited 100% by AI. Every cut, sound and graphic: Claude". Plus a stats row and the end credit.

## Sound
- **Voice is king.**
  - Chain: highpass, light denoise, -3 dB at 250 Hz, +3 dB presence, de-ess, gentle compression.
  - Integrated level: voice −22.5, music −29, effects −31 LUFS before the final loudnorm to −14.
- **Music** (Vish's pick).
  - Held at one steady level under his voice; the level never pumps.
  - Low-passed under the hard part, opening at the turn.
  - The chorus lands on the payoff line, rises only for the montage, and the montage cuts on the song's beat.
- **A sound for every visual event, planned with the picture** (`S()` in `plan()`): pops, clicks, ticks, whooshes peaking on the cut, a sub boom on big hits, a thud for the fall. Short, bright and under the voice. Sources: synthesised in `_syn()`, Kenney CC0 (`assets/kenney`), `assets/sfx`.
- **The B-roll keeps its own natural sound**, low.

## Vish's no-list (all from his feedback)
- No abrupt or jump cuts.
- No random speed-ups.
- No camera wandering.
- No cheap saturation.
- No fonts that look like templates.
- No sad music he didn't pick.
- No pauses where he looks away.
- No B-roll that doesn't match the words.
- No overprocessed voice.

## Tools (`scripts/setup_tools.sh`)
- **Installed:** FFmpeg, faster-whisper, OpenAI Whisper, yt-dlp, OpenCV contrib (CSRT), Puppeteer (on `/opt/pw-browsers/chromium`) and HyperFrames 0.8.186 (skills synced from the repo).
- **Source clones:** `/home/user/tools`.
- **yt-dlp** downloads reference reels that the embed fetcher can't get.
- **ElevenLabs** (Vish's subscription, 22 Oct) can add:
  - custom sound effects from a text prompt;
  - voice isolation for noisy takes.

  Its key lives in `.env.local` (gitignored) or the environment secrets; never in chat or code. Verify with `npx -y @elevenlabs/cli@latest onboard check --env-path .env.local`.
- **ElevenLabs credits (Vish, 22 Oct).**
  - Check the remaining credits (GET `/v1/user/subscription`: `character_count` vs `character_limit`) before and after every batch of generations, and report what was used.
  - Tell Vish the moment they run low (under about 10% left) or out. He has a second student account with roughly 80,000 to 90,000 credits and will swap in its key.
  - Two keys, both environment secrets (Vish, 23 Oct):
    - `ELEVENLABS_API_KEY` is the main account;
    - `CLAUDEELEVENLABS_API` is the second student account (about 80,000 to 90,000 credits).
  - Use the main key first. When its credits run low or a call fails for quota, switch to the second key with `ElevenLabs(api_key=os.environ["CLAUDEELEVENLABS_API"])` and tell Vish you switched.
  - Never print, log or commit either key.
  - The main key can't read the account (no `user_read` permission), so the credit balance isn't readable. Count the characters each TTS request bills (1 per character on `eleven_multilingual_v2`) and keep a running total.
  - Used so far: 70 characters (the Week 1 "next week" line, George voice, 23 Oct).
