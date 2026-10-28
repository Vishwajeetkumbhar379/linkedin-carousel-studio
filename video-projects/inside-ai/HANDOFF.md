# Inside AI EP 3 to 9: handoff (28 Oct 2026)

Vish asked to move all YouTube Shorts work to the "viral YouTube Shorts" chat. This session has stopped work on it.
Repo: `vishwajeetkumbhar379/linkedin-carousel-studio`, branch `claude/content-engine-test-gate`, folder `video-projects/inside-ai/`.

## What exists
- `build.py` → `scripts.json` and `beats.json`: 7 episodes on the EP 1 formula (one everyday AI moment, a hook that turns on "but", short lines,
  one surprising number, a loop question at the end).
  - EP 3: plane, 143,000 km.
  - EP 4: strawberry and tokens.
  - EP 5: same question, two answers.
  - EP 6: the P in GPT.
  - EP 7: six fake court cases.
  - EP 8: "Thinking" is a hidden essay.
  - EP 9: it re-reads your whole chat.
- `facts.txt`: the fact checks. `posting.txt`: YouTube titles and description.
- Voices are generated locally (ElevenLabs George, `JBFqnCBsd6RMkjVDRZzb`, multilingual v2, as in EP 1). The mp3 files are not in git; `voices.sh`
  rebuilds them (needs `CLAUDEELEVENLABS_API`). Word timings `a*_words.json` are in git.
- Engine: `templates/video/series3` in faceless mode (`"faceless": true`), dark chapters, dark 3D studio shots, captions and the counter
  130 px inside the edges (Instagram crops ~100 px a side on tall phones). Render: `bash render3.sh` (three lanes, about 50 min for all 7);
  outputs `inside-ai-a3-9x16.mp4` to `inside-ai-a9-9x16.mp4`.

## Numbering (Vish's screenshot, 28 Oct)
The "Viral animated YouTube Shorts" thread already made EP 3, "Your phone can crash this plane?" (flight mode, Drew voice, keyword FLIGHT).
So the scripts here are drafts for EP 4 onwards. The "a3" plane script (your message travels 143,000 km) is close to that EP 3: drop it,
or post it much later as a follow-up. The voice there is Drew; the voices here were made with George, so re-voice the scripts to match.

## Status
- Not rendered: the render was stopped on purpose; nothing has been sent to Vish.
- Stills were checked for EP 3 and EP 4 (dark look, safe zone OK).
- If that chat has its own Inside AI pipeline (the one that made EP 1 and EP 2), use only the scripts and facts from here.

## Unknowns
- EP 1 and EP 2 were made in another session; their source isn't in this repo. YouTube (from a cloud server) refused to give the video files
  for study, so the look of EP 3 to 9 is our own, not a copy of EP 1 and EP 2.
