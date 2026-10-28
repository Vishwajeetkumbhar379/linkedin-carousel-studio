# Inside AI batch 2: seven episodes (Vish, 28 Oct 2026: "double down")

Eps 1 and 2 passed 1,000 views each within days on a brand-new channel (@Buildwithvish, 3 subscribers).
Vish wants seven more of the same kind, built and voiced end to end. This file is the brief for each episode build.

## What worked (eps 1 and 2) and is now the rule
1. **The first line contradicts what the viewer believes**, in under 2 s: "you think it reads your message. It can't."
   / "One isn't." No intro, no name, frame 0 already mid-action.
2. **The real answer is held back** until about 40 to 60% in, with a "here's the weird part" open loop by 30%.
3. **One big, real number** shown huge in the headline layer ($30,000 chip, $2.7B, 1991).
4. **Ends on a two-sided question** people argue about in the comments, looping back to the first shot.
5. **One bright object on a dark world** in every frame, readable on a phone at a glance. A new picture or camera move
   every 1.5 to 2 s.
6. **Drew's voice** (eleven_v3, audio tags), word-box captions, a sound on every visual event.
7. **Clickbait cover** (scripts/shorts/cover.py): 3-line provocative headline, one amber pill word, a circle around the thing.

## How to build one episode (each build runs in its own session)
Read first: `content/shorts/README.md` (format, reference look, script rules), `content/shorts/flight-mode/`
(script.json, guide.md: the model to copy) and `templates/video/shorts/flight-mode.html` (the model template: one
three.js world, navy #001A2D + one amber #FDB33E emissive, bloom + depth of field, camera keyframes from line timings,
headline layer, Captions, SFX map, `window.COVER_CAM` support).

1. **Research.** WebSearch/WebFetch every fact in your brief below. Keep only facts with a primary or reputable source
   and a date; put each in `facts` with the URL. Drop any claim you can't source. British English, no em dashes.
2. **Script** `content/shorts/<slug>/script.json` (same schema as flight-mode, `episode` number below, voice block copied
   from flight-mode): 9 to 11 lines, 100 to 120 words, hook line 12 words or fewer, per-line `see` and optional `tag`,
   `pause_after` on 1 or 2 scene breaks, a `publish` block (title with #shorts, caption with the comment keyword and
   "I'll send you the 1-page guide with every source", 5 hashtags, a provocative pinned comment, tags) and a `cover`
   block (3 short headline lines with one [pill] word, kicker, circle, optional `cam`).
3. **Guide** `content/shorts/<slug>/guide.md` in the 8-section format of flight-mode/guide.md, every point sourced.
4. **Template** `templates/video/shorts/<slug>.html`: a NEW world for this topic built to the reference look (copy the
   flight-mode structure: renderer, composer, camAt, hl(), SFX, frame(t)). One continuous camera journey, a concept
   ladder, the process shown as moving light, the last shot = the first shot.
   Test with `python scripts/shorts/voice.py content/shorts/<slug> --estimate` then
   `python scripts/shorts/render.py content/shorts/<slug> --stills` and LOOK at the stills; fix anything that is black,
   blown out white, empty, or where text overlaps text. Two rounds of fixes at most.
5. **Voice** `python scripts/shorts/voice.py content/shorts/<slug>` (ElevenLabs key in ELEVENLABS_API_KEY or
   CLAUDEELEVENLABS_API; never print it). Then stills again, then `python scripts/shorts/render.py content/shorts/<slug> --jobs=4`
   and `python scripts/shorts/cover.py content/shorts/<slug>`.
6. **Deliver**: copy `out/shorts/<slug>/video.mp4` to `/mnt/project-files/shorts/batch2/inside-ai-ep<N>-<slug>.mp4`,
   `cover.png` to `.../inside-ai-ep<N>-<slug>-cover.png`, `guide.md` to `.../guide-<KEYWORD>.md`.
7. **Commit** only your own files (script, guide, template, `git add -f out/shorts/<slug>/voice.* out/shorts/<slug>/cover.png`),
   never mp4s. `git pull --rebase origin claude/project-thread-k1b03i` then push; retry on conflict.
8. End with a short summary: duration, keyword, anything you dropped or could not verify.

## The seven episodes

### Ep 4 · `lift-button` · keyword LIFT
Hook: "That close door button? It probably does nothing." Truth to verify: in many US lifts the door-close button is
disabled in normal service (it works for firefighters/maintenance), linked to the Americans with Disabilities Act
1990 door-timing rules; NYT reported it in Oct 2016. Check what applies in the UK/Europe and say so honestly.
"Placebo buttons" angle: also pedestrian crossing buttons in New York (NYT 2004: most no longer worked).
World: a lift interior, the button pressed, light travels along the wire to a controller that ignores it, a timer
counts down, the camera rises up the shaft and out to a city of buttons. Close: "Would you rather know, or keep pressing?"

### Ep 5 · `plane-windows` · keyword WINDOWS
Hook: "Square windows made planes fall out of the sky." Verify: de Havilland Comet, first jet airliner, two crashes in
1954 (BOAC 781 off Elba in January, South African Airways 201 in April); metal fatigue from pressurisation cycles;
the inquiry and water-tank tests; stress concentrates at sharp corners, so windows became rounded. Check whether the
fatigue crack started at a window or the ADF aerial window/square cut-out, and say it exactly as the sources do.
World: a fuselage breathing as it pressurises, stress shown as amber light piling into the square corners, a crack
grows, then the same flow sliding round a rounded window. Close: back on a passenger at a round window.

### Ep 6 · `pigeon-head` · keyword PIGEON
Hook: "That pigeon isn't bobbing its head. It's standing still." Verify: Frost 1978 (Journal of Experimental Biology)
treadmill study: the head is locked in space during the "hold" phase while the body walks forward, then thrusts;
this stabilises the image on the retina. Other birds (chickens) do the same.
World: a pigeon walking on a pavement, a ghost trail freezes the head's positions to show it stays put, the camera
goes into the eye and the image stays sharp, then a treadmill shot. Close: "Now you can't unsee it."

### Ep 7 · `incognito` · keyword INCOGNITO
Hook: "Incognito mode doesn't make you invisible." Verify: Brown v. Google class action; settlement (April 2024)
in which Google agreed to delete or remediate billions of records and update the Incognito disclosure; what Incognito
actually does (no local history/cookies after the session) and who can still see you (sites, employer, ISP).
Use only what the court filings and Google's own help page say.
World: a browser window wearing a hat and glasses, data travels out as amber packets to servers that still log it,
the local history shreds, the servers don't. Close: "So who were you hiding from?"

### Ep 8 · `recaptcha` · keyword CAPTCHA
Hook: "You've been training Google's AI for free." Verify: reCAPTCHA (Luis von Ahn, Carnegie Mellon, 2007), used to
digitise words from books and the New York Times archive; Google acquired it in September 2009; later images from
Street View house numbers; image challenges and AI training (cite what Google or reputable outlets say, carefully).
World: a "click all the traffic lights" grid, each click is a tiny amber packet flying into a growing dataset, zoom out
to millions of clicks feeding a model, a self-driving car. Close: "Should they pay you?"

### Ep 9 · `microwave-wifi` · keyword WIFI
Hook: "Your microwave is slowing down your Wi-Fi." Verify: microwave ovens run at about 2.45 GHz, the same band as
2.4 GHz Wi-Fi; leakage within safety limits can still interfere; 5 GHz Wi-Fi avoids it. Use a regulator, vendor or
university source.
World: a kitchen at night, the microwave hums, amber waves leak through the door mesh and collide with Wi-Fi packets
flying to a phone, the video buffers. Zoom into the door mesh (holes smaller than the wavelength). Close: "2.4 or 5?"

### Ep 10 · `phone-listening` · keyword LISTENING
Hook: "Is your phone listening to you?" Verify: Cox Media Group's "Active Listening" pitch deck reported by 404 Media
(Dec 2023 and Sept 2024); Google removed CMG from its Partners programme; Meta's and Amazon's responses; what is
proven versus claimed. Be exact: a marketing firm claimed it; no proof that phones record you for ads.
World: a phone on a table, sound waves drift towards its microphone, ad cards appear; then the reveal of the pitch
deck as a glowing slide; then the real data trail (location, contacts, browsing) as light. Close: "Creepy coincidence, or not?"
